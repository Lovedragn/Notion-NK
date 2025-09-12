package com.Backend.Backend.Controller;

import com.Backend.Backend.Models.User;
import com.Backend.Backend.Models.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@CrossOrigin("http://localhost:5173")
public class LoginController {
    public record LoginRequest(String email, String password) {}

    @Autowired
    private UserRepository userRepository;

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

        return Map.of("email", email);
    }

}


