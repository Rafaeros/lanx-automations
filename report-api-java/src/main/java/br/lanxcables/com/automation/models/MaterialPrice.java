package br.lanxcables.com.automation.models;

import java.util.Map;
import java.util.HashMap;
import java.util.List;

public class MaterialPrice {
    private Map<String, Object> attributes;

    private MaterialPrice(Map<String, Object> attributes) {
        this.attributes = attributes;
    }

    public Map<String, Object> getAttributes() {
        return attributes;
    }

    public static MaterialPrice fromList(List<String> list) {
        Map<String, Object> map = new HashMap<>();
        for (int i = 0; i < list.size(); i++) {
            map.put(list.get(i), "");
        }
        return new MaterialPrice(map);
    }

    // Factory method
    public static MaterialPrice fromJson(Map<String, Object> json) {
        return new MaterialPrice(json);
    }
}
