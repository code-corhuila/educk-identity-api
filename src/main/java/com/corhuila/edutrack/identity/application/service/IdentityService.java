package com.corhuila.edutrack.identity.application.service;

import com.corhuila.edutrack.identity.domain.exception.InvalidCredentialsException;
import com.corhuila.edutrack.identity.domain.model.User;
import com.corhuila.edutrack.identity.domain.port.in.AuthenticateUserUseCase;
import com.corhuila.edutrack.identity.domain.port.out.UserRepositoryPort;
import com.corhuila.edutrack.identity.domain.port.out.RefreshTokenRepositoryPort;
import com.corhuila.edutrack.identity.domain.port.out.PasswordHasherPort;
import com.corhuila.edutrack.identity.domain.port.out.TokenHasherPort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

@Service
public class IdentityService implements AuthenticateUserUseCase {

    private final UserRepositoryPort userRepositoryPort;
    private final RefreshTokenRepositoryPort refreshTokenRepositoryPort;
    private final PasswordHasherPort passwordHasherPort;
    private final TokenHasherPort tokenHasherPort;

    public IdentityService(UserRepositoryPort userRepositoryPort, RefreshTokenRepositoryPort refreshTokenRepositoryPort, PasswordHasherPort passwordHasherPort, TokenHasherPort tokenHasherPort) {
        this.userRepositoryPort = userRepositoryPort;
        this.refreshTokenRepositoryPort = refreshTokenRepositoryPort;
        this.passwordHasherPort = passwordHasherPort;
        this.tokenHasherPort = tokenHasherPort;
    }

    @Override
    public User authenticate(String email, String password) {
        User user = userRepositoryPort.findByEmail(email)
                .orElseThrow(() -> new InvalidCredentialsException("Invalid credentials"));

        if (!passwordHasherPort.matches(password, user.getPasswordHash())) {
            throw new InvalidCredentialsException("Invalid credentials");
        }
        return user;
    }

    @Override
    @Transactional
    public String createRefreshToken(UUID userId) {
        String plainToken = UUID.randomUUID().toString();
        String hashedToken = tokenHasherPort.hash(plainToken);
        refreshTokenRepositoryPort.save(userId, hashedToken);
        return plainToken;
    }

    @Override
    @Transactional
    public User refresh(String plainToken) {
        String hashedToken = tokenHasherPort.hash(plainToken);
        if (!refreshTokenRepositoryPort.isValid(hashedToken)) {
            throw new InvalidCredentialsException("Invalid or expired refresh token");
        }
        
        UUID userId = refreshTokenRepositoryPort.getUserIdByToken(hashedToken);
        if (userId == null) {
            throw new InvalidCredentialsException("Invalid or expired refresh token");
        }

        User user = userRepositoryPort.findById(userId)
                .orElseThrow(() -> new InvalidCredentialsException("User not found"));

        // Rotation: Invalidate old token immediately to prevent reuse
        refreshTokenRepositoryPort.invalidate(hashedToken);

        return user;
    }

    @Override
    @Transactional
    public void logout(String plainToken) {
        if (plainToken != null) {
            String hashedToken = tokenHasherPort.hash(plainToken);
            refreshTokenRepositoryPort.invalidate(hashedToken);
        }
    }
}
