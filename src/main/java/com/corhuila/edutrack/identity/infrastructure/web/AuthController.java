package com.corhuila.edutrack.identity.infrastructure.web;

import com.corhuila.edutrack.identity.domain.model.User;
import com.corhuila.edutrack.identity.domain.port.in.AuthenticateUserUseCase;
import com.corhuila.edutrack.identity.domain.port.in.GetUserProfileUseCase;
import com.corhuila.edutrack.identity.infrastructure.web.dto.AuthResponse;
import com.corhuila.edutrack.identity.infrastructure.web.dto.LoginRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/api/v1/auth")
@CrossOrigin(origins = "*")
public class AuthController {

    private final AuthenticateUserUseCase authenticateUserUseCase;
    private final GetUserProfileUseCase getUserProfileUseCase;

    public AuthController(AuthenticateUserUseCase authenticateUserUseCase, GetUserProfileUseCase getUserProfileUseCase) {
        this.authenticateUserUseCase = authenticateUserUseCase;
        this.getUserProfileUseCase = getUserProfileUseCase;
    }

    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@RequestBody LoginRequest request) {
        User user = authenticateUserUseCase.authenticate(request.getEmail(), request.getPassword());
        String demoJwt = "jwt-mock-" + UUID.randomUUID();
        return ResponseEntity.ok(AuthResponse.fromUser(user, demoJwt));
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
