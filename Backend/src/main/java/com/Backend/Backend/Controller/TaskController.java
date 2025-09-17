package com.Backend.Backend.Controller;
import com.Backend.Backend.Entity.Task;
import com.Backend.Backend.DTO.Task_DTO;
import com.Backend.Backend.Security.JwtService;
import com.Backend.Backend.Service.TaskService;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/tasks")
@CrossOrigin(origins = "http://localhost:5173")
public class TaskController {

    private final TaskService taskService;
    private final JwtService jwtService;

    public TaskController(TaskService taskService, JwtService jwtService) {
        this.taskService = taskService;
        this.jwtService = jwtService;
    }

    // Helper: map Entity -> DTO for API responses
    private Task_DTO convertToDTO(Task task) {
        return new Task_DTO(
            task.getId(),
            task.getTitle(),
            task.getTaskDate() != null ? task.getTaskDate().toString() : null
        );
    }

    // Create a task for the user identified by URL hash in path
    @PostMapping("/hash/{hash}")
    public Task_DTO createTask(@PathVariable String hash, @RequestBody Task_DTO taskDto, @RequestHeader(name = "Authorization", required = false) String authorization) {
        if (authorization == null || !authorization.startsWith("Bearer ")) throw new RuntimeException("Missing token");
        String token = authorization.substring(7);
        String tokenHash = jwtService.verify(token).getClaim("hash").asString();
        if (!hash.equals(tokenHash)) throw new RuntimeException("Invalid token for hash");
        
        Task task = taskService.createTaskForHash(hash, taskDto.getTitle(), taskDto.getTaskDate());
        return convertToDTO(task);
    }

    // List tasks for the user identified by URL hash in path
    @GetMapping("/hash/{hash}")
    public List<Task_DTO> getTasksByUser(@PathVariable String hash, @RequestHeader(name = "Authorization", required = false) String authorization) {
        if (authorization == null || !authorization.startsWith("Bearer ")) throw new RuntimeException("Missing token");
        String token = authorization.substring(7);
        String tokenHash = jwtService.verify(token).getClaim("hash").asString();
        if (!hash.equals(tokenHash)) throw new RuntimeException("Invalid token for hash");
        
        return taskService.getTasksByHash(hash).stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    // Admin/debug: list all tasks (token required)
    @GetMapping
    public List<Task_DTO> getAllTasks(@RequestHeader(name = "Authorization", required = false) String authorization) {
        if (authorization == null || !authorization.startsWith("Bearer ")) throw new RuntimeException("Missing token");
        jwtService.verify(authorization.substring(7));
        
        return taskService.getAllTasks().stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    // Get single task by id
    @GetMapping("/id/{id}")
    public Task_DTO getTaskById(@PathVariable Long id) {
        return convertToDTO(taskService.getTaskById(id));
    }

    // Update a task if it belongs to the token owner
    @PutMapping("/{id}")
    public Task_DTO updateTask(@PathVariable Long id, @RequestBody Task_DTO updatedDto, @RequestHeader(name = "Authorization", required = false) String authorization) {
        if (authorization == null || !authorization.startsWith("Bearer ")) throw new RuntimeException("Missing token");
        String token = authorization.substring(7);
        String tokenHash = jwtService.verify(token).getClaim("hash").asString();
        
        Task savedTask = taskService.updateTaskForOwner(id, tokenHash, updatedDto.getTitle(), updatedDto.getTaskDate());
        return convertToDTO(savedTask);
    }

    // Delete a task if it belongs to the token owner
    @DeleteMapping("/{id}")
    public void deleteTask(@PathVariable Long id, @RequestHeader(name = "Authorization", required = false) String authorization) {
        if (authorization == null || !authorization.startsWith("Bearer ")) throw new RuntimeException("Missing token");
        String token = authorization.substring(7);
        String tokenHash = jwtService.verify(token).getClaim("hash").asString();
        taskService.deleteTaskForOwner(id, tokenHash);
    }
}
