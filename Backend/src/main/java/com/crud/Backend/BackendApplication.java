package com.crud.Backend;

import java.util.ArrayList;
import java.util.List;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

@SpringBootApplication
@RestController
public class BackendApplication {

	public static void main(String[] args) {
		SpringApplication.run(BackendApplication.class, args);
	}

	@GetMapping("/")
	public String getMethodName() {
		System.out.println("heloo");
		return "Sujith websote ";
	}

	@GetMapping("/details")
	public List<card> getNames() {
		List<card> list = new ArrayList<>();
		list.add(new card("Sujit ", 21));
		list.add(new card("kamal", 31));
		list.add(new card("Rohit ", 47));

		System.out.println("Hola");
		System.out.println(list.get(0).toString());
		return list;
	}

}
