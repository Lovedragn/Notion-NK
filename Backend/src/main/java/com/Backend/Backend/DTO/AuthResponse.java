package com.Backend.Backend.DTO;

public class AuthResponse {
    private String email;
    private String hash;
    private String token;

    public AuthResponse() {}

    public AuthResponse(String email, String hash, String token) {
        this.email = email;
        this.hash = hash;
        this.token = token;
    }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public String getHash() { return hash; }
    public void setHash(String hash) { this.hash = hash; }
    public String getToken() { return token; }
    public void setToken(String token) { this.token = token; }
}


