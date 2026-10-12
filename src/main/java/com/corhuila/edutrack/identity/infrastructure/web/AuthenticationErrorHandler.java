package com.corhuila.edutrack.identity.infrastructure.web;

import com.corhuila.edutrack.identity.domain.exception.AuthenticationException;
import java.util.Map;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class AuthenticationErrorHandler {
    @ExceptionHandler(AuthenticationException.class)
    public ResponseEntity<Map<String, String>> unauthorized(AuthenticationException error) {
        return ResponseEntity.status(401).body(Map.of("error", "UNAUTHORIZED",
                "message", "Invalid credentials or refresh token"));
    }
}
