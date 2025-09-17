package com.Backend.Backend.Security;

import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.interfaces.DecodedJWT;
import com.auth0.jwt.interfaces.JWTVerifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.Date;

@Service
public class JwtService {
    @Value("${security.jwt.secret}")
    private String secret;

    @Value("${security.jwt.issuer}")
    private String issuer;

    public String generateToken(String email, String hash) {
        Algorithm algorithm = Algorithm.HMAC256(secret);
        Instant now = Instant.now();
        return JWT.create()
                .withIssuer(issuer)
                .withSubject(email)
                .withClaim("hash", hash)
                .withIssuedAt(Date.from(now))
                .withExpiresAt(Date.from(now.plusSeconds(60L * 24L * 7L)))
                .sign(algorithm);
    }

    public DecodedJWT verify(String token) {
        Algorithm algorithm = Algorithm.HMAC256(secret);
        JWTVerifier verifier = JWT.require(algorithm).withIssuer(issuer).build();

        return verifier.verify(token);
    }
}


