package com.corhuila.edutrack.identity.infrastructure.security;

import com.corhuila.edutrack.identity.domain.model.User;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.util.Collections;
import java.util.Date;

@Component
public class JwtProvider {

    private final SecretKey key;
    private final long expirationTime;

    public JwtProvider(
            @Value("${jwt.secret:defaultSecretKeyWithAtLeast256BitsLong0123456789}") String secret,
            @Value("${jwt.expiration:86400000}") long expirationTime) {
        this.key = Keys.hmacShaKeyFor(secret.getBytes());
        this.expirationTime = expirationTime;
    }

    public String generateToken(User user) {
        return Jwts.builder()
                .subject(user.getEmail())
                .claim("role", user.getRole())
                .claim("userId", user.getId().toString())
                .issuedAt(new Date())
                .expiration(new Date(System.currentTimeMillis() + expirationTime))
                .signWith(key)
                .compact();
    }

    public boolean validateToken(String token) {
        try {
            Jwts.parser().verifyWith(key).build().parseSignedClaims(token);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    public Claims getClaims(String token) {
        return Jwts.parser().verifyWith(key).build().parseSignedClaims(token).getPayload();
    }

    public Authentication getAuthentication(String token) {
        Claims claims = Jwts.parser().verifyWith(key).build().parseSignedClaims(token).getPayload();
        String username = claims.getSubject();
        String role = claims.get("role", String.class);
        
        return new UsernamePasswordAuthenticationToken(
                username, 
                null, 
                Collections.singletonList(new SimpleGrantedAuthority("ROLE_" + role))
        );
    }
}
