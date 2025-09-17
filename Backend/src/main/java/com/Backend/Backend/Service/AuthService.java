package com.Backend.Backend.Service;

import com.Backend.Backend.Entity.User;
import com.Backend.Backend.Repository.UserRepository;
import com.Backend.Backend.Security.Hash;
import com.Backend.Backend.Security.JwtService;
import org.springframework.stereotype.Service;

@Service
public class AuthService {

    private final UserRepository userRepository;
    private final JwtService jwtService;
    private final Hash hasher;

    public AuthService(UserRepository userRepository, JwtService jwtService, Hash hasher) {
        this.userRepository = userRepository;
        this.jwtService = jwtService;
        this.hasher = hasher;
    }

    public AuthResult authenticateOrRegister(String email, String password) {
        User user = userRepository.findById(email).orElseGet(() -> {
            User u = new User();
            u.setEmail(email);
            u.setPassword(password);
            String hash = hasher.encode(email);
            u.setUrlHash(hash);
            return userRepository.save(u);
        });

        String token = jwtService.generateToken(email, user.getUrlHash());
        return new AuthResult(user.getEmail(), user.getUrlHash(), token);
    }

    public record AuthResult(String email, String hash, String token) {}
}


