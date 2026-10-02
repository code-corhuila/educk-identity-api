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
import org.springframework.test.context.jdbc.Sql;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Map;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
public class AuthIntegrationTest {

    @Container
    public static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine")
        .withDatabaseName("edutrack_identity")
        .withUsername("edutrack")
        .withPassword("secret");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    @Sql(statements = {
        "INSERT INTO identity_schema.users (id, first_name, last_name, email, password_hash, role) VALUES ('a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d', 'Integration', 'Test', 'test@example.com', '\\\.V4r4/A0L9U.Xq/5E/p7A3V/T0e6F2G6D0L4R6D0L4R', 'STUDENT') ON CONFLICT DO NOTHING;"
    })
    void testFullAuthFlow() {
        // 1. Login
        LoginRequest login = new LoginRequest();
        login.setEmail("test@example.com");
        // password for above hash is "password"
        login.setPassword("password");

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
