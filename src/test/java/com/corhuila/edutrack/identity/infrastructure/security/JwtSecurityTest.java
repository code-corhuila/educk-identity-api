package com.corhuila.edutrack.identity.infrastructure.security;

import com.corhuila.edutrack.identity.domain.model.User;
import com.corhuila.edutrack.identity.domain.port.in.GetUserProfileUseCase;
import com.corhuila.edutrack.identity.domain.port.in.LoginUseCase;
import com.corhuila.edutrack.identity.infrastructure.web.AuthController;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.springframework.security.core.Authentication;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import java.nio.charset.StandardCharsets;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.time.Instant;
import java.time.LocalDateTime;
import java.util.Base64;
import java.util.Date;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

class JwtSecurityTest {

    private static String privatePem;
    private static String publicPem;
    private static KeyPair keyPair;
    private static JwtProvider jwtProvider;
    private static final ObjectMapper JSON = new ObjectMapper();

    @BeforeAll
    static void initKeys() throws Exception {
        KeyPairGenerator generator = KeyPairGenerator.getInstance("RSA");
        generator.initialize(2048);
        keyPair = generator.generateKeyPair();
        privatePem = toPem("PRIVATE KEY", keyPair.getPrivate().getEncoded());
        publicPem = toPem("PUBLIC KEY", keyPair.getPublic().getEncoded());
        jwtProvider = new JwtProvider(privatePem, publicPem, 900L);
    }

    private static String toPem(String label, byte[] der) {
        return "-----BEGIN " + label + "-----\n"
                + Base64.getMimeEncoder(64, "\n".getBytes(StandardCharsets.US_ASCII)).encodeToString(der)
                + "\n-----END " + label + "-----";
    }

    @Test
    void issuesRs256TokenWithRequiredClaimsAndKid() throws Exception {
        UUID userId = UUID.randomUUID();
        User user = new User(userId, "teacher@edutrack.edu.co", "hash", "TEACHER",
                UUID.randomUUID(), "Carlos Ramírez", true, LocalDateTime.now());

        String token = jwtProvider.generateToken(user);
        String[] parts = token.split("\\.");
        assertEquals(3, parts.length);

        JsonNode header = JSON.readTree(Base64.getUrlDecoder().decode(parts[0]));
        assertEquals("RS256", header.path("alg").asText());
        assertEquals("JWT", header.path("typ").asText());
        assertEquals(JwtProvider.KEY_ID, header.path("kid").asText());

        Claims claims = jwtProvider.getClaims(token);
        assertEquals(JwtProvider.EXPECTED_ISSUER, claims.getIssuer());
        assertTrue(claims.getAudience().contains(JwtProvider.EXPECTED_AUDIENCE));
        assertEquals(userId.toString(), claims.getSubject());
        assertEquals(userId.toString(), claims.get("userId", String.class));
        assertEquals("teacher@edutrack.edu.co", claims.get("email", String.class));
        assertEquals("TEACHER", claims.get("role", String.class));

        long ttl = (claims.getExpiration().getTime() - claims.getIssuedAt().getTime()) / 1000L;
        assertEquals(900L, ttl);

        Authentication auth = jwtProvider.getAuthentication(token);
        assertEquals(userId.toString(), auth.getName());
        assertTrue(auth.getAuthorities().stream().anyMatch(a -> a.getAuthority().equals("ROLE_TEACHER")));
    }

    @Test
    void failsFastOnMissingKeysOrExcessiveExpiration() {
        assertThrows(IllegalArgumentException.class, () -> new JwtProvider("", publicPem, 900));
        assertThrows(IllegalArgumentException.class, () -> new JwtProvider(privatePem, "", 900));
        assertThrows(IllegalArgumentException.class, () -> new JwtProvider(privatePem, publicPem, 3601));
        assertThrows(IllegalArgumentException.class, () -> new JwtProvider(privatePem, publicPem, 0));
    }

    @Test
    void rejectsHs256AlgNoneExpiredAndWrongAudienceTokens() {
        String hs256Token = Jwts.builder()
                .issuer(JwtProvider.EXPECTED_ISSUER)
                .audience().add(JwtProvider.EXPECTED_AUDIENCE).and()
                .subject(UUID.randomUUID().toString())
                .claim("role", "ADMIN")
                .expiration(Date.from(Instant.now().plusSeconds(600)))
                .signWith(Keys.hmacShaKeyFor("01234567890123456789012345678901".getBytes(StandardCharsets.UTF_8)))
                .compact();
        assertFalse(jwtProvider.validateToken(hs256Token));

        String noneHeader = Base64.getUrlEncoder().withoutPadding()
                .encodeToString("{\"alg\":\"none\",\"typ\":\"JWT\"}".getBytes(StandardCharsets.UTF_8));
        String nonePayload = Base64.getUrlEncoder().withoutPadding()
                .encodeToString(("{\"iss\":\"educk-identity-api\",\"aud\":\"edutrack\",\"sub\":\"" + UUID.randomUUID()
                        + "\",\"role\":\"ADMIN\",\"exp\":" + Instant.now().plusSeconds(600).getEpochSecond() + "}")
                        .getBytes(StandardCharsets.UTF_8));
        assertFalse(jwtProvider.validateToken(noneHeader + "." + nonePayload + ".sig"));

        String expired = Jwts.builder()
                .issuer(JwtProvider.EXPECTED_ISSUER)
                .audience().add(JwtProvider.EXPECTED_AUDIENCE).and()
                .subject(UUID.randomUUID().toString())
                .claim("role", "PARENT")
                .expiration(Date.from(Instant.now().minusSeconds(120)))
                .signWith(keyPair.getPrivate(), Jwts.SIG.RS256)
                .compact();
        assertFalse(jwtProvider.validateToken(expired));

        String wrongAud = Jwts.builder()
                .issuer(JwtProvider.EXPECTED_ISSUER)
                .audience().add("other-app").and()
                .subject(UUID.randomUUID().toString())
                .claim("role", "PARENT")
                .expiration(Date.from(Instant.now().plusSeconds(600)))
                .signWith(keyPair.getPrivate(), Jwts.SIG.RS256)
                .compact();
        assertFalse(jwtProvider.validateToken(wrongAud));
    }

    @Test
    void filterReturns401JsonOnProtectedEndpointsAndPermitsValidBearerOrLogin() throws Exception {
        UUID userId = UUID.randomUUID();
        User user = new User(userId, "parent@edutrack.edu.co", "hash", "PARENT",
                UUID.randomUUID(), "María López", true, LocalDateTime.now());
        LoginUseCase loginUseCase = mock(LoginUseCase.class);
        GetUserProfileUseCase profileUseCase = mock(GetUserProfileUseCase.class);
        when(loginUseCase.authenticate(any(), any())).thenReturn(user);
        when(loginUseCase.createRefreshToken(userId)).thenReturn("refresh-1");
        when(profileUseCase.getUserById(userId)).thenReturn(user);

        AuthController controller = new AuthController(loginUseCase, profileUseCase, jwtProvider);
        JwtAuthenticationFilter filter = new JwtAuthenticationFilter(jwtProvider, JSON);
        MockMvc mockMvc = MockMvcBuilders.standaloneSetup(controller).addFilters(filter).build();

        // Missing token on protected endpoint -> 401 JSON
        mockMvc.perform(get("/api/v1/auth/users/" + userId))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.error").value("UNAUTHORIZED"));

        // HS256 token rejected on protected endpoint -> 401 JSON
        String hsToken = Jwts.builder()
                .subject(userId.toString())
                .expiration(Date.from(Instant.now().plusSeconds(300)))
                .signWith(Keys.hmacShaKeyFor("01234567890123456789012345678901".getBytes(StandardCharsets.UTF_8)))
                .compact();
        mockMvc.perform(get("/api/v1/auth/users/" + userId).header("Authorization", "Bearer " + hsToken))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.error").value("UNAUTHORIZED"));

        // Valid RS256 token succeeds
        String validToken = jwtProvider.generateToken(user);
        mockMvc.perform(get("/api/v1/auth/users/" + userId).header("Authorization", "Bearer " + validToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.email").value("parent@edutrack.edu.co"));

        // Login remains public without bearer token
        mockMvc.perform(post("/api/v1/auth/login")
                        .contentType("application/json")
                        .content("{\"email\":\"parent@edutrack.edu.co\",\"password\":\"secret123\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.expiresIn").value(900))
                .andExpect(jsonPath("$.tokenType").value("Bearer"));
    }
}
