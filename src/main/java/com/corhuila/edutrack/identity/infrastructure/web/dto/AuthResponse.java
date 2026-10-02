package com.corhuila.edutrack.identity.infrastructure.web.dto;

import com.corhuila.edutrack.identity.domain.model.User;
import java.util.UUID;

public class AuthResponse {
    private String token;
    private String refreshToken;
    private UUID userId;
    private String email;
    private String fullName;
    private String role;
    private UUID schoolId;

    public AuthResponse(String token, String refreshToken, UUID userId, String email, String fullName, String role, UUID schoolId) {
        this.token = token;
        this.refreshToken = refreshToken;
        this.userId = userId;
        this.email = email;
        this.fullName = fullName;
        this.role = role;
        this.schoolId = schoolId;
    }

    public static AuthResponse fromUser(User user, String token) {
        return new AuthResponse(
            token,
            null,
            user.getId(),
            user.getEmail(),
            user.getFullName(),
            user.getRole(),
            user.getSchoolId()
        );
    }

    public static AuthResponse fromUser(User user, String token, String refreshToken) {
        return new AuthResponse(
            token,
            refreshToken,
            user.getId(),
            user.getEmail(),
            user.getFullName(),
            user.getRole(),
            user.getSchoolId()
        );
    }

    public String getToken() { return token; }
    public String getRefreshToken() { return refreshToken; }
    public UUID getUserId() { return userId; }
    public String getEmail() { return email; }
    public String getFullName() { return fullName; }
    public String getRole() { return role; }
    public UUID getSchoolId() { return schoolId; }
}
