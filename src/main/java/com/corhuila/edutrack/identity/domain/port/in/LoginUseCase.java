package com.corhuila.edutrack.identity.domain.port.in;

import com.corhuila.edutrack.identity.domain.model.User;

public interface LoginUseCase {
    User authenticate(String email, String password);
    User refresh(String refreshToken);
    void logout(String refreshToken);
    String createRefreshToken(java.util.UUID userId);
}
