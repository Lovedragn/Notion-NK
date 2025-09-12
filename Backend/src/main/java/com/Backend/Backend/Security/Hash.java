package com.Backend.Backend.Security;
import java.util.UUID;

public class Hash {
    public String Hash(String str){
        UUID uuid = UUID.randomUUID();
        String url = str + uuid;

        return url;
    }
}
