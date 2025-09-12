package com.Backend.Backend.Models;

import jakarta.persistence.*;
import lombok.Data;
import java.util.List;
import com.fasterxml.jackson.annotation.JsonIgnore;

@Entity
@Table(name = "users")
@Data // auto-generates getters, setters, toString, equals, hashCode
public class User {

    @Id
    private String email;

    private String password;

    private String urlHash;

    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonIgnore
    private List<Task> tasks;
}
