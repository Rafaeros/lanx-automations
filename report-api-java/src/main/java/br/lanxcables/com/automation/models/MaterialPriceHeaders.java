package br.lanxcables.com.automation.models;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class MaterialPriceHeaders {
    
    private Map<String, String> attributes;

    public  MaterialPriceHeaders(Map<String, String> attributes) {
        this.attributes = attributes;
    }

    public Map<String, String> getAttributes() {
        return attributes;
    }

    public static MaterialPriceHeaders fromHeadersList(List<String> headers) {
        Map<String, String> map = new HashMap<>();
        for (String header : headers) {
            map.put(header, ""); // inicializa vazio ou default
        }
        return new MaterialPriceHeaders(map);
    }
}
