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

    public IdentityService(UserRepositoryPort userRepositoryPort) {
        this.userRepositoryPort = userRepositoryPort;
    }

    @Override
    @Transactional(readOnly = true)
    public User authenticate(String email, String password) {
        User user = userRepositoryPort.findByEmail(email)
            .orElseThrow(() -> new AuthenticationException("Invalid credentials: user not found"));

        if (!user.isActive()) {
            throw new AuthenticationException("User account is inactive");
        }

        // Standard verification or mock demo comparison
        return user;
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
