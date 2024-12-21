import unittest
import subprocess
import tempfile
import os

class TestConfigLanguage(unittest.TestCase):
    
    def create_temp_yaml_file(self, yaml_content):
        """Создаем временный YAML файл с заданным содержимым."""
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.yaml') as temp_file:
            temp_file.write(yaml_content)
            return temp_file.name

    def run_config_parser(self, input_file):
        """Helper method to run the config parser script on an input YAML file."""
        result = subprocess.run(
            ['python', 'config_language.py', input_file], 
            capture_output=True, text=True
        )
        return result.stdout.strip()

    def test_web_server_config(self):
        yaml_content = """name: "Web Server Config"
version: 2.1
features:
  - logging
  - caching
  - compression
settings:
  host: "localhost"
  port: 8080
  ssl_enabled: true
max_connections: 100
expression: "?[max_connections + 10]"
"""
        temp_file = self.create_temp_yaml_file(yaml_content)
        expected_output = """
let name = "Web Server Config";
let version = 2.1;
let features = ("logging", "caching", "compression");
let settings = {
    host = "localhost";
    port = 8080;
    ssl_enabled = true;
};
let max_connections = 100;
let expression = 110;""".strip()
        
        output = self.run_config_parser(temp_file)
        
        # Выводим оба результата, если они не совпадают
        if output != expected_output:
            print(f"Expected Output:\n{expected_output}\n")
            print(f"Actual Output:\n{output}\n")
        
        self.assertEqual(output, expected_output)
        
        # Удаляем временный файл после теста
        os.remove(temp_file)

    def test_game_config(self):
        yaml_content = """name: "Game Config"
max_level: 50
difficulty: "medium"
settings:
  resolution: "1920x1080"
  fullscreen: true
player_health: 100
expression: "?[player_health - 20]"
"""
        temp_file = self.create_temp_yaml_file(yaml_content)
        expected_output = """
let name = "Game Config";
let max_level = 50;
let difficulty = "medium";
let settings = {
    resolution = "1920x1080";
    fullscreen = true;
};
let player_health = 100;
let expression = 80;""".strip()
        
        output = self.run_config_parser(temp_file)
        
        # Выводим оба результата, если они не совпадают
        if output != expected_output:
            print(f"Expected Output:\n{expected_output}\n")
            print(f"Actual Output:\n{output}\n")
        
        self.assertEqual(output, expected_output)
        
        # Удаляем временный файл после теста
        os.remove(temp_file)

if __name__ == "__main__":
    unittest.main()
