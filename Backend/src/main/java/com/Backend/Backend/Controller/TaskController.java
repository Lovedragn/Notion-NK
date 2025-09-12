package com.Backend.Backend.Controller;
import com.Backend.Backend.Models.Task;
import com.Backend.Backend.Models.TaskRepository;
import com.Backend.Backend.Models.UserRepository;
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

    @GetMapping("/id/{id}")
    public Task getTaskById(@PathVariable Long id) {
        return taskRepository.findById(id).orElseThrow(() -> new RuntimeException("Task not found"));
    }

    @PutMapping("/{id}")
    public Task updateTask(@PathVariable Long id, @RequestBody Task updated) {
        Task existing = taskRepository.findById(id).orElseThrow(() -> new RuntimeException("Task not found"));
        existing.setTitle(updated.getTitle());
        existing.setTaskDate(updated.getTaskDate());
        return taskRepository.save(existing);
    }

    @DeleteMapping("/{id}")
    public void deleteTask(@PathVariable Long id) {
        if (!taskRepository.existsById(id)) throw new RuntimeException("Task not found");
        taskRepository.deleteById(id);
    }
}
