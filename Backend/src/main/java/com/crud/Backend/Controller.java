package com.crud.Backend;

import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;




@RestController
public class Controller {

    @Value("${app.secret.db_projecturl}")
    private String db_project_url;

    @Value("${app.secret.db_api}")
    private String db_api;
    
    @PostMapping("/auth/v1/google")
    public String postMethodName(@RequestBody String entity) {
        return entity;
    }
    
}

@RestController
@RequestMapping("/auth/v1/google")
class Security_Controller{
    @GetMapping("/login")
    public List<String> getMethodName() {
        List<String> list = new ArrayList<>();
   
        return list;
    }
}