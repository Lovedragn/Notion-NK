package com.crud.Backend;
import java.util.*;

import org.springframework.web.bind.annotation.RestController;


public class card {
    private String name;
    private Integer age;


    public card (String name , Integer age ) {
        this.name = name;
        this.age = age;
    }
    public String getName() {
        return name;
    }
    public Integer getAge() {
        return age;
    }

}
