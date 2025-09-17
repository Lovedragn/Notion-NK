package com.Backend.Backend.Controller;

import com.Backend.Backend.DTO.AuthRequest;
import com.Backend.Backend.DTO.AuthResponse;
import com.Backend.Backend.Service.AuthService;
import org.springframework.web.bind.annotation.*;

@RestController
@CrossOrigin("http://localhost:5173")
public class LoginController {

    private final AuthService authService;

    public LoginController(AuthService authService) {
        this.authService = authService;
    }

    @PostMapping("/v1/auth")
    public AuthResponse login(@RequestBody AuthRequest request) {
        var result = authService.authenticateOrRegister(request.getEmail(), request.getPassword());
        return new AuthResponse(result.email(), result.hash(), result.token());
    }

}


