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
        return ResponseEntity.ok(AuthResponse.fromUser(user, token));
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
}
