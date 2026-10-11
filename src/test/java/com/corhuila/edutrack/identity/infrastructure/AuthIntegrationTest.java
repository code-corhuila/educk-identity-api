package com.corhuila.edutrack.identity.infrastructure;

import com.corhuila.edutrack.identity.infrastructure.web.dto.LoginRequest;
import com.corhuila.edutrack.identity.infrastructure.web.dto.AuthResponse;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.security.crypto.password.PasswordEncoder;
import com.corhuila.edutrack.identity.infrastructure.persistence.SpringDataUserRepository;
import com.corhuila.edutrack.identity.infrastructure.persistence.UserJpaEntity;
import org.testcontainers.utility.MountableFile;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Map;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
public class AuthIntegrationTest {

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

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
        registry.add("jwt.secret", () -> UUID.randomUUID().toString() + UUID.randomUUID());
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
        // 1. Login
        LoginRequest login = new LoginRequest();
        login.setEmail("test@example.com");
        // Credentials are generated for this disposable database.
        login.setPassword(testPassword);

        ResponseEntity<AuthResponse> loginResp = restTemplate.postForEntity("/api/v1/auth/login", login, AuthResponse.class);
        assertEquals(HttpStatus.OK, loginResp.getStatusCode());
        assertNotNull(loginResp.getBody().getToken());
        assertNotNull(loginResp.getBody().getRefreshToken());

        String refresh = loginResp.getBody().getRefreshToken();

        // 2. Refresh
        ResponseEntity<AuthResponse> refreshResp = restTemplate.postForEntity("/api/v1/auth/refresh", Map.of("refreshToken", refresh), AuthResponse.class);
        assertEquals(HttpStatus.OK, refreshResp.getStatusCode());
        assertNotNull(refreshResp.getBody().getToken());
        assertNotNull(refreshResp.getBody().getRefreshToken());

        String newRefresh = refreshResp.getBody().getRefreshToken();
        assertNotEquals(refresh, newRefresh);

        // 3. Old refresh token should be revoked (fails)
        ResponseEntity<AuthResponse> failResp = restTemplate.postForEntity("/api/v1/auth/refresh", Map.of("refreshToken", refresh), AuthResponse.class);
        assertEquals(HttpStatus.UNAUTHORIZED, failResp.getStatusCode());

        // 4. Logout new refresh token
        ResponseEntity<Void> logoutResp = restTemplate.postForEntity("/api/v1/auth/logout", Map.of("refreshToken", newRefresh), Void.class);
        assertEquals(HttpStatus.OK, logoutResp.getStatusCode());

        // 5. New refresh token is now revoked
        ResponseEntity<AuthResponse> failResp2 = restTemplate.postForEntity("/api/v1/auth/refresh", Map.of("refreshToken", newRefresh), AuthResponse.class);
        assertEquals(HttpStatus.UNAUTHORIZED, failResp2.getStatusCode());
    }
}
