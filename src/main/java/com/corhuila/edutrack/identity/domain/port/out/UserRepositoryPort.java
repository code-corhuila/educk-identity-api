package com.corhuila.edutrack.identity.domain.port.out;

import com.corhuila.edutrack.identity.domain.model.User;
import java.util.Optional;
import java.util.UUID;

public interface UserRepositoryPort {
    User save(User user);
    Optional<User> findById(UUID id);
    Optional<User> findByEmail(String email);
}
