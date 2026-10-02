package com.corhuila.edutrack.identity.infrastructure.security;

import com.corhuila.edutrack.identity.domain.port.out.PasswordHasherPort;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

@Component
public class BCryptPasswordHasherAdapter implements PasswordHasherPort {
    private final PasswordEncoder passwordEncoder;

    public BCryptPasswordHasherAdapter(PasswordEncoder passwordEncoder) {
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public String hash(String rawText) {
        return passwordEncoder.encode(rawText);
    }

    @Override
    public boolean matches(String rawText, String encodedText) {
        return passwordEncoder.matches(rawText, encodedText);
    }
}
