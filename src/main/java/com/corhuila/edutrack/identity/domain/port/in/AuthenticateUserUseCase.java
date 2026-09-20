package com.corhuila.edutrack.identity.domain.port.in;

import com.corhuila.edutrack.identity.domain.model.User;

public interface AuthenticateUserUseCase {
    User authenticate(String email, String password);
}
