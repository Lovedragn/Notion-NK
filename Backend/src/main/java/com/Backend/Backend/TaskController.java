package com.Backend.Backend;

import com.Backend.Backend.Models.Task;
import com.Backend.Backend.Models.TaskRepository;
import com.Backend.Backend.Models.User;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/tasks")
public class TaskController {

    @Autowired
    private TaskRepository taskRepository;

    @Autowired
    private JwtUtil jwtUtil;

    // ✅ Get tasks of logged-in user
    @GetMapping
    public List<Task> getTasks(HttpServletRequest request) {
        String email = jwtUtil.extractUsername(getToken(request));
        return taskRepository.findByUserEmail(email);
    }

    // ✅ Create task
    @PostMapping
    public Task createTask(@RequestBody Task task, HttpServletRequest request) {
        String email = jwtUtil.extractUsername(getToken(request));
        User user = new User();
        user.setEmail(email);
        task.setUser(user);
        return taskRepository.save(task);
    }

    // ✅ Update task
    @PutMapping("/{id}")
    public ResponseEntity<Task> updateTask(@PathVariable Long id, @RequestBody Task updatedTask, HttpServletRequest request) {
        String email = jwtUtil.extractUsername(getToken(request));
        return taskRepository.findById(id)
            .filter(task -> task.getUser().getEmail().equals(email)) // check ownership
            .map(task -> {
                task.setTitle(updatedTask.getTitle());
                task.setDescription(updatedTask.getDescription());
                task.setDueDate(updatedTask.getDueDate());
                return ResponseEntity.ok(taskRepository.save(task));
            })
            .orElse(ResponseEntity.status(HttpStatus.FORBIDDEN).build());
    }

    // ✅ Delete task
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteTask(@PathVariable Long id, HttpServletRequest request) {
        String email = jwtUtil.extractUsername(getToken(request));
        return taskRepository.findById(id)
            .filter(task -> task.getUser().getEmail().equals(email)) // check ownership
            .map(task -> {
                taskRepository.delete(task);
                return ResponseEntity.noContent().build();
            })
            .orElse(ResponseEntity.status(HttpStatus.FORBIDDEN).build());
    }

    // Helper: extract token from Authorization header
    private String getToken(HttpServletRequest request) {
        String header = request.getHeader("Authorization");
        return header != null && header.startsWith("Bearer ") ? header.substring(7) : null;
    }
}

