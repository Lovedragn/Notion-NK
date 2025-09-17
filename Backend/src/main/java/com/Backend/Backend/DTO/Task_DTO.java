package com.Backend.Backend.DTO;

public class Task_DTO {

    private Long id;
    private String title;
    private String taskDate;

    public Task_DTO() {}

    public Task_DTO(Long id, String title, String taskDate) {
        this.id = id;
        this.title = title;
        this.taskDate = taskDate;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getTaskDate() {
        return taskDate;
    }

    public void setTaskDate(String taskDate) {
        this.taskDate = taskDate;
    }
}
