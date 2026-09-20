package com.corhuila.edutrack.identity.domain.model;

import java.time.LocalDateTime;
import java.util.UUID;

public class User {
    private UUID id;
    private String email;
    private String passwordHash;
    private String role; // ADMIN, TEACHER, PARENT, STUDENT
    private UUID schoolId;
    private String fullName;
    private boolean active;
    private LocalDateTime createdAt;

    public User(UUID id, String email, String passwordHash, String role, UUID schoolId, String fullName, boolean active, LocalDateTime createdAt) {
        this.id = id;
        this.email = email;
        this.passwordHash = passwordHash;
        this.role = role;
        this.schoolId = schoolId;
        this.fullName = fullName;
        this.active = active;
        this.createdAt = createdAt;
    }

    public UUID getId() { return id; }
    public String getEmail() { return email; }
    public String getPasswordHash() { return passwordHash; }
    public String getRole() { return role; }
    public UUID getSchoolId() { return schoolId; }
    public String getFullName() { return fullName; }
    public boolean isActive() { return active; }
    public LocalDateTime getCreatedAt() { return createdAt; }
}
