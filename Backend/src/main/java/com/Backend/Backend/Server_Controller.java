package com.Backend.Backend;


import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class Server_Controller {

    @GetMapping("/")
    public String index(){
        return "Hello Sujith";
    }
}
