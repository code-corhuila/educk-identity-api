package com.corhuila.edutrack.identity.domain.port.out;

public interface PasswordHasherPort {
    String hash(String rawText);
    boolean matches(String rawText, String encodedText);
}
