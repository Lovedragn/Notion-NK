package com.Backend.Backend.Models;

import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface TaskRepository extends JpaRepository<Task, Long> {
    List<Task> findByUserEmail(String email) ;
    List<Task> findByUserUrlHash(String urlHash);
}

