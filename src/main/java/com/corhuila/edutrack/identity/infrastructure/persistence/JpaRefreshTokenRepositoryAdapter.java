package com.corhuila.edutrack.identity.infrastructure.persistence;

import com.corhuila.edutrack.identity.domain.port.out.RefreshTokenRepositoryPort;
import org.springframework.stereotype.Component;
import java.time.LocalDateTime;
import java.util.Optional;
import java.util.UUID;

@Component
public class JpaRefreshTokenRepositoryAdapter implements RefreshTokenRepositoryPort {
    private final SpringDataRefreshTokenRepository repository;

    public JpaRefreshTokenRepositoryAdapter(SpringDataRefreshTokenRepository repository) {
        this.repository = repository;
    }

    @Override
    public void save(UUID userId, String tokenHash, LocalDateTime expiresAt) {
        repository.save(new RefreshTokenJpaEntity(userId, tokenHash, expiresAt));
    }

    @Override
    public void revoke(String tokenHash) {
        repository.findByTokenHash(tokenHash).ifPresent(token -> {
            token.setRevoked(true);
            repository.save(token);
        });
    }

    @Override
    public boolean isValid(String tokenHash) {
        return repository.findByTokenHash(tokenHash)
                .map(t -> !t.isRevoked() && t.getExpiresAt().isAfter(LocalDateTime.now()))
                .orElse(false);
    }

    @Override
    public UUID getUserIdByToken(String tokenHash) {
        return repository.findByTokenHash(tokenHash)
                .map(RefreshTokenJpaEntity::getUserId)
                .orElse(null);
    }
}
