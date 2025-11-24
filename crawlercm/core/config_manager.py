import json
from pathlib import Path


class ConfigManager:
    def __init__(self, file_path="configs.json"):
        self.file_path = Path(file_path)
        self.data = {}
        self.load()

    def load(self):
        if self.file_path.exists():
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = {
                "username": "",
                "password": "",
            }
            self.save()

    def save(self):
        print("Configs saved to ", self.file_path)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def remove(self, key):
        if key in self.data:
            del self.data[key]
            self.save()


class Configs(ConfigManager):
    def __init__(self):
        super().__init__()
        self.username = self.get("username")
        self.password = self.get("password")