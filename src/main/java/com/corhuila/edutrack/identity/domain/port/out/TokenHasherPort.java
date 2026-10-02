package com.corhuila.edutrack.identity.domain.port.out;

public interface TokenHasherPort {
    String hash(String rawToken);
}
