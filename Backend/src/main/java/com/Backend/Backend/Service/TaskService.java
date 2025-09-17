package com.Backend.Backend.Service;

import com.Backend.Backend.Entity.Task;
import com.Backend.Backend.Entity.User;
import com.Backend.Backend.Repository.TaskRepository;
import com.Backend.Backend.Repository.UserRepository;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;

@Service
public class TaskService {

    private final TaskRepository taskRepository;
    private final UserRepository userRepository;

    public TaskService(TaskRepository taskRepository, UserRepository userRepository) {
        this.taskRepository = taskRepository;
        this.userRepository = userRepository;
    }

    public Task createTaskForHash(String hash, String title, String taskDateIso) {
        User user = userRepository.findByUrlHash(hash).orElseThrow(() -> new RuntimeException("User not found"));
        Task task = new Task();
        task.setTitle(title);
        if (taskDateIso != null && !taskDateIso.isEmpty()) {
            task.setTaskDate(LocalDate.parse(taskDateIso));
        }
        task.setUser(user);
        return taskRepository.save(task);
    }

    public List<Task> getTasksByHash(String hash) {
        return taskRepository.findByUserUrlHash(hash);
    }

    public List<Task> getAllTasks() {
        return taskRepository.findAll();
    }

    public Task getTaskById(Long id) {
        return taskRepository.findById(id).orElseThrow(() -> new RuntimeException("Task not found"));
    }

    public Task updateTaskForOwner(Long id, String ownerHash, String title, String taskDateIso) {
        Task existing = getTaskById(id);
        if (existing.getUser() == null || existing.getUser().getUrlHash() == null || !existing.getUser().getUrlHash().equals(ownerHash)) {
            throw new RuntimeException("Invalid token for task");
        }
        existing.setTitle(title);
        if (taskDateIso != null && !taskDateIso.isEmpty()) {
            existing.setTaskDate(LocalDate.parse(taskDateIso));
        }
        return taskRepository.save(existing);
    }

    public void deleteTaskForOwner(Long id, String ownerHash) {
        Task existing = getTaskById(id);
        if (existing.getUser() == null || existing.getUser().getUrlHash() == null || !existing.getUser().getUrlHash().equals(ownerHash)) {
            throw new RuntimeException("Invalid token for task");
        }
        taskRepository.deleteById(id);
    }
}


