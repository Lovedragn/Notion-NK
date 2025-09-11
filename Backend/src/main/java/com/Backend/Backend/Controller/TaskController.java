package com.Backend.Backend.Controller;
import com.Backend.Backend.Models.Task;
import com.Backend.Backend.Models.TaskRepository;
import com.Backend.Backend.Models.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/tasks")
public class TaskController {

    @Autowired
    private TaskRepository taskRepository;

    @Autowired
    private UserRepository userRepository;

    @PostMapping("/{email}")
    public Task createTask(@PathVariable String email, @RequestBody Task task) {
        return userRepository.findById(email)
                .map(user -> {
                    task.setUser(user);
                    return taskRepository.save(task);
                })
                .orElseThrow(() -> new RuntimeException("User not found"));
    }

    @GetMapping("/{email}")
    public List<Task> getTasksByUser(@PathVariable String email) {
        return taskRepository.findByUserEmail(email);
    }
}
