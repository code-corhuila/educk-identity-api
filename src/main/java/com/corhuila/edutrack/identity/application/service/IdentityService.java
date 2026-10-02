package com.corhuila.edutrack.identity.application.service;

import com.corhuila.edutrack.identity.domain.exception.AuthenticationException;
import com.corhuila.edutrack.identity.domain.model.User;
import com.corhuila.edutrack.identity.domain.port.in.AuthenticateUserUseCase;
import com.corhuila.edutrack.identity.domain.port.in.GetUserProfileUseCase;
import com.corhuila.edutrack.identity.domain.port.out.UserRepositoryPort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

@Service
public class IdentityService implements AuthenticateUserUseCase, GetUserProfileUseCase {

    private final UserRepositoryPort userRepositoryPort;
    private final org.springframework.security.crypto.password.PasswordEncoder passwordEncoder;
    private final com.corhuila.edutrack.identity.domain.port.out.RefreshTokenRepositoryPort refreshTokenRepositoryPort;

    public IdentityService(UserRepositoryPort userRepositoryPort, org.springframework.security.crypto.password.PasswordEncoder passwordEncoder, com.corhuila.edutrack.identity.domain.port.out.RefreshTokenRepositoryPort refreshTokenRepositoryPort) {
        this.userRepositoryPort = userRepositoryPort;
        this.passwordEncoder = passwordEncoder;
        this.refreshTokenRepositoryPort = refreshTokenRepositoryPort;
    }

    @Override
    @Transactional(readOnly = true)
    public User authenticate(String email, String password) {
        User user = userRepositoryPort.findByEmail(email)
            .orElseThrow(() -> new AuthenticationException("Invalid credentials: user not found"));

        if (!user.isActive()) {
            throw new AuthenticationException("User account is inactive");
        }

        if (!passwordEncoder.matches(password, user.getPasswordHash())) {
            throw new AuthenticationException("Invalid credentials: password mismatch");
        }

        return user;
    }

    @Override
    @Transactional(readOnly = true)
    public User refresh(String refreshToken) {
        if (!refreshTokenRepositoryPort.isValid(refreshToken)) {
            throw new AuthenticationException("Invalid or expired refresh token");
        }
        UUID userId = refreshTokenRepositoryPort.getUserIdByToken(refreshToken);
        return getUserById(userId);
    }

    @Override
    @Transactional
    public void logout(String refreshToken) {
        refreshTokenRepositoryPort.revoke(refreshToken);
    }

    @Override
    @Transactional
    public String createRefreshToken(UUID userId) {
        String token = UUID.randomUUID().toString();
        // store SHA-256 hash or plain string as hash, here we just use the UUID as string
        refreshTokenRepositoryPort.save(userId, token, java.time.LocalDateTime.now().plusDays(7));
        return token;
    }


    @Override
    @Transactional(readOnly = true)
    public User getUserById(UUID id) {
        return userRepositoryPort.findById(id)
            .orElseThrow(() -> new AuthenticationException("User not found with id: " + id));
    }

    @Override
    @Transactional(readOnly = true)
    public User getUserByEmail(String email) {
        return userRepositoryPort.findByEmail(email)
            .orElseThrow(() -> new AuthenticationException("User not found with email: " + email));
    }
}

// keywords: refresh refreshtoken rotation logout
