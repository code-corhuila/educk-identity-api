package com.corhuila.edutrack.identity.domain.port.out;

import java.time.LocalDateTime;
import java.util.UUID;

public interface RefreshTokenRepositoryPort {
    void save(UUID userId, String tokenHash, LocalDateTime expiresAt);
    void revoke(String tokenHash);
    boolean isValid(String tokenHash);
    UUID getUserIdByToken(String tokenHash);
}
