package com.Backend.Backend.Controller;
import com.Backend.Backend.Models.Task;
import com.Backend.Backend.Models.TaskRepository;
import com.Backend.Backend.Models.UserRepository;
import com.Backend.Backend.Security.JwtService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/tasks")
@CrossOrigin(origins = "http://localhost:5173")
public class TaskController {

    @Autowired
    private TaskRepository taskRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private JwtService jwtService;

    @PostMapping("/hash/{hash}")
    public Task createTask(@PathVariable String hash, @RequestBody Task task, @RequestHeader(name = "Authorization", required = false) String authorization) {
        if (authorization == null || !authorization.startsWith("Bearer ")) throw new RuntimeException("Missing token");
        String token = authorization.substring(7);
        String tokenHash = jwtService.verify(token).getClaim("hash").asString();
        if (!hash.equals(tokenHash)) throw new RuntimeException("Invalid token for hash");
        return userRepository.findByUrlHash(hash)
                .map(user -> {
                    task.setUser(user);
                    return taskRepository.save(task);
                })
                .orElseThrow(() -> new RuntimeException("User not found"));
    }

    @GetMapping("/hash/{hash}")
    public List<Task> getTasksByUser(@PathVariable String hash, @RequestHeader(name = "Authorization", required = false) String authorization) {
        if (authorization == null || !authorization.startsWith("Bearer ")) throw new RuntimeException("Missing token");
        String token = authorization.substring(7);
        String tokenHash = jwtService.verify(token).getClaim("hash").asString();
        if (!hash.equals(tokenHash)) throw new RuntimeException("Invalid token for hash");
        return taskRepository.findByUserUrlHash(hash);
    }

    @GetMapping
    public List<Task> getAllTasks(@RequestHeader(name = "Authorization", required = false) String authorization) {
        if (authorization == null || !authorization.startsWith("Bearer ")) throw new RuntimeException("Missing token");
        jwtService.verify(authorization.substring(7));
        return taskRepository.findAll();
    }

    @GetMapping("/id/{id}")
    public Task getTaskById(@PathVariable Long id) {
        return taskRepository.findById(id).orElseThrow(() -> new RuntimeException("Task not found"));
    }

    @PutMapping("/{id}")
    public Task updateTask(@PathVariable Long id, @RequestBody Task updated, @RequestHeader(name = "Authorization", required = false) String authorization) {
        if (authorization == null || !authorization.startsWith("Bearer ")) throw new RuntimeException("Missing token");
        String token = authorization.substring(7);
        String tokenHash = jwtService.verify(token).getClaim("hash").asString();
        Task existing = taskRepository.findById(id).orElseThrow(() -> new RuntimeException("Task not found"));
        if (existing.getUser() == null || existing.getUser().getUrlHash() == null || !existing.getUser().getUrlHash().equals(tokenHash)) {
            throw new RuntimeException("Invalid token for task");
        }
        existing.setTitle(updated.getTitle());
        existing.setTaskDate(updated.getTaskDate());
        return taskRepository.save(existing);
    }

    @DeleteMapping("/{id}")
    public void deleteTask(@PathVariable Long id, @RequestHeader(name = "Authorization", required = false) String authorization) {
        if (authorization == null || !authorization.startsWith("Bearer ")) throw new RuntimeException("Missing token");
        String token = authorization.substring(7);
        String tokenHash = jwtService.verify(token).getClaim("hash").asString();
        Task existing = taskRepository.findById(id).orElseThrow(() -> new RuntimeException("Task not found"));
        if (existing.getUser() == null || existing.getUser().getUrlHash() == null || !existing.getUser().getUrlHash().equals(tokenHash)) {
            throw new RuntimeException("Invalid token for task");
        }
        taskRepository.deleteById(id);
    }
}
