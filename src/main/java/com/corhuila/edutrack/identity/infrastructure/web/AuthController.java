package com.corhuila.edutrack.identity.infrastructure.web;

import com.corhuila.edutrack.identity.domain.model.User;
import com.corhuila.edutrack.identity.domain.port.in.AuthenticateUserUseCase;
import com.corhuila.edutrack.identity.domain.port.in.GetUserProfileUseCase;
import com.corhuila.edutrack.identity.infrastructure.web.dto.AuthResponse;
import com.corhuila.edutrack.identity.infrastructure.web.dto.LoginRequest;
import com.corhuila.edutrack.identity.infrastructure.security.JwtProvider;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/api/v1/auth")
@CrossOrigin(origins = "*")
public class AuthController {

    private final AuthenticateUserUseCase authenticateUserUseCase;
    private final GetUserProfileUseCase getUserProfileUseCase;
    private final JwtProvider jwtProvider;

    public AuthController(
            AuthenticateUserUseCase authenticateUserUseCase, 
            GetUserProfileUseCase getUserProfileUseCase,
            JwtProvider jwtProvider) {
        this.authenticateUserUseCase = authenticateUserUseCase;
        this.getUserProfileUseCase = getUserProfileUseCase;
        this.jwtProvider = jwtProvider;
    }

    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@RequestBody LoginRequest request) {
        User user = authenticateUserUseCase.authenticate(request.getEmail(), request.getPassword());
        String token = jwtProvider.generateToken(user);
        String refreshToken = authenticateUserUseCase.createRefreshToken(user.getId());
        return ResponseEntity.ok(AuthResponse.fromUser(user, token, refreshToken));
    }

    @PostMapping("/refresh")
    public ResponseEntity<AuthResponse> refresh(@RequestBody java.util.Map<String, String> request) {
        String reqToken = request.get("refreshToken");
        User user = authenticateUserUseCase.refresh(reqToken);
        String token = jwtProvider.generateToken(user);
        String newRefreshToken = authenticateUserUseCase.createRefreshToken(user.getId());
        // Invalidate old token
        authenticateUserUseCase.logout(reqToken);
        return ResponseEntity.ok(AuthResponse.fromUser(user, token, newRefreshToken));
    }

    @PostMapping("/logout")
    public ResponseEntity<Void> logout(@RequestBody java.util.Map<String, String> request) {
        String reqToken = request.get("refreshToken");
        authenticateUserUseCase.logout(reqToken);
        return ResponseEntity.ok().build();
    }

    @GetMapping("/users/{id}")
    public ResponseEntity<AuthResponse> getUserProfile(@PathVariable UUID id) {
        User user = getUserProfileUseCase.getUserById(id);
        return ResponseEntity.ok(AuthResponse.fromUser(user, null));
    }

    @GetMapping("/health")
    public ResponseEntity<String> healthCheck() {
        return ResponseEntity.ok("OK - Identity Service (HU-003)");
    }

    @PostMapping("/validate")
    public ResponseEntity<?> validateToken(@RequestHeader(org.springframework.http.HttpHeaders.AUTHORIZATION) String authHeader) {
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            return ResponseEntity.status(401).body(java.util.Map.of("valid", false, "error", "Missing or invalid Authorization header"));
        }
        
        String token = authHeader.substring(7);
        try {
            if (jwtProvider.validateToken(token)) {
                io.jsonwebtoken.Claims claims = jwtProvider.getClaims(token);
                return ResponseEntity.ok(java.util.Map.of(
                    "valid", true,
                    "userId", claims.get("userId"),
                    "email", claims.getSubject(),
                    "role", "ROLE_" + claims.get("role")
                ));
            } else {
                return ResponseEntity.status(401).body(java.util.Map.of("valid", false, "error", "Invalid or expired token"));
            }
        } catch (Exception e) {
            return ResponseEntity.status(401).body(java.util.Map.of("valid", false, "error", e.getMessage()));
        }
    }
}
