package com.Backend.Backend.Models;

import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRepository extends JpaRepository<User, String> {
    java.util.Optional<User> findByUrlHash(String urlHash);
}
