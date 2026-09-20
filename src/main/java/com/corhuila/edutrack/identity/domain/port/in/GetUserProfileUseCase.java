package com.corhuila.edutrack.identity.domain.port.in;

import com.corhuila.edutrack.identity.domain.model.User;
import java.util.UUID;

public interface GetUserProfileUseCase {
    User getUserById(UUID id);
    User getUserByEmail(String email);
}
