package com.Backend.Backend.Controller;

import com.Backend.Backend.Models.User;
import com.Backend.Backend.Models.UserRepository;
import com.Backend.Backend.Security.Hash;
import com.Backend.Backend.Security.JwtService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@CrossOrigin("http://localhost:5173")
public class LoginController {
    public record LoginRequest(String email, String password) {}

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private JwtService jwtService;

    private final Hash hasher = new Hash("hash-secret-change-me");

    @PostMapping("/v1/auth")
    public Map<String , String> login(@RequestBody LoginRequest request) {
        String email = request.email();
        String password = request.password();

        User user = userRepository.findById(email).orElseGet(() -> {
            User u = new User();
            u.setEmail(email);
            u.setPassword(password);
            return userRepository.save(u);
        });

        if (user.getPassword() == null || user.getPassword().isBlank()) {
            user.setPassword(password);
            userRepository.save(user);
        }

        if (user.getUrlHash() == null || user.getUrlHash().isBlank()) {
            String hash = hasher.encode(email);
            user.setUrlHash(hash);
            userRepository.save(user);
        }

        String token = jwtService.generateToken(email, user.getUrlHash());

        return Map.of("email", email, "hash", user.getUrlHash(), "token", token);
    }

}


