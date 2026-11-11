package com.corhuila.edutrack.identity.infrastructure;

import com.corhuila.edutrack.identity.infrastructure.persistence.SpringDataUserRepository;
import com.corhuila.edutrack.identity.infrastructure.persistence.UserJpaEntity;
import com.corhuila.edutrack.identity.infrastructure.web.dto.AuthResponse;
import com.corhuila.edutrack.identity.infrastructure.web.dto.LoginRequest;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.MountableFile;

import java.nio.file.Path;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.time.LocalDateTime;
import java.util.Base64;
import java.util.Map;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
@SuppressWarnings("null")
public class AuthIntegrationTest {

    private static final KeyPair RUNTIME_KEY_PAIR = generateRsaKeyPair();

    @Container
    public static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine")
        .withDatabaseName("edutrack_identity")
        .withUsername("edutrack")
        .withPassword(UUID.randomUUID().toString())
        .withCopyFileToContainer(schema("V1.1__create_identity_schema.sql"),
                "/docker-entrypoint-initdb.d/01-schema.sql")
        .withCopyFileToContainer(schema("V1.2__create_identity_tables.sql"),
                "/docker-entrypoint-initdb.d/02-tables.sql");

    private static MountableFile schema(String name) {
        String directory = System.getProperty("identity.db.path");
        if (directory == null) throw new IllegalStateException(
                "Set -Didentity.db.path to the official educk-identity-db checkout");
        return MountableFile.forHostPath(Path.of(directory, "01_ddl", name));
    }

    private static KeyPair generateRsaKeyPair() {
        try {
            KeyPairGenerator generator = KeyPairGenerator.getInstance("RSA");
            generator.initialize(2048);
            return generator.generateKeyPair();
        } catch (Exception e) {
            throw new IllegalStateException(e);
        }
    }

    private static String toPem(String type, byte[] encoded) {
        return "-----BEGIN " + type + "-----\n"
                + Base64.getMimeEncoder(64, "\n".getBytes()).encodeToString(encoded)
                + "\n-----END " + type + "-----";
    }

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
        registry.add("jwt.private-key", () -> toPem("PRIVATE KEY", RUNTIME_KEY_PAIR.getPrivate().getEncoded()));
        registry.add("jwt.public-key", () -> toPem("PUBLIC KEY", RUNTIME_KEY_PAIR.getPublic().getEncoded()));
        registry.add("jwt.expiration-seconds", () -> "900");
    }

    @Autowired
    private TestRestTemplate restTemplate;
    @Autowired private SpringDataUserRepository users;
    @Autowired private PasswordEncoder passwords;
    private final String testPassword = UUID.randomUUID().toString();

    @BeforeEach void seedUser() {
        restTemplate.getRestTemplate().setRequestFactory(
                new org.springframework.http.client.JdkClientHttpRequestFactory());
        users.save(new UserJpaEntity(UUID.randomUUID(), "test@example.com",
                passwords.encode(testPassword), "PARENT", null, "Integration Test", true,
                LocalDateTime.now()));
    }

    @Test
    void testFullAuthFlow() {
        LoginRequest login = new LoginRequest();
        login.setEmail("test@example.com");
        login.setPassword(testPassword);

        ResponseEntity<AuthResponse> loginResp = restTemplate.postForEntity("/api/v1/auth/login", login, AuthResponse.class);
        assertEquals(HttpStatus.OK, loginResp.getStatusCode());
        assertNotNull(loginResp.getBody().getToken());
        assertEquals("Bearer", loginResp.getBody().getTokenType());
        assertEquals(900L, loginResp.getBody().getExpiresIn());
        assertNotNull(loginResp.getBody().getRefreshToken());

        String refresh = loginResp.getBody().getRefreshToken();

        ResponseEntity<AuthResponse> refreshResp = restTemplate.postForEntity("/api/v1/auth/refresh", Map.of("refreshToken", refresh), AuthResponse.class);
        assertEquals(HttpStatus.OK, refreshResp.getStatusCode());
        assertNotNull(refreshResp.getBody().getToken());
        assertNotNull(refreshResp.getBody().getRefreshToken());

        String newRefresh = refreshResp.getBody().getRefreshToken();
        assertNotEquals(refresh, newRefresh);

        ResponseEntity<AuthResponse> failResp = restTemplate.postForEntity("/api/v1/auth/refresh", Map.of("refreshToken", refresh), AuthResponse.class);
        assertEquals(HttpStatus.UNAUTHORIZED, failResp.getStatusCode());

        ResponseEntity<Void> logoutResp = restTemplate.postForEntity("/api/v1/auth/logout", Map.of("refreshToken", newRefresh), Void.class);
        assertEquals(HttpStatus.OK, logoutResp.getStatusCode());

        ResponseEntity<AuthResponse> failResp2 = restTemplate.postForEntity("/api/v1/auth/refresh", Map.of("refreshToken", newRefresh), AuthResponse.class);
        assertEquals(HttpStatus.UNAUTHORIZED, failResp2.getStatusCode());
    }
}
