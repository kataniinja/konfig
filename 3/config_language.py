import yaml
import sys
import re

class ConfigParser:
    def __init__(self):
        self.constants = {}

    def parse(self, yaml_data):
        return self._parse_node(yaml_data)

    def _parse_node(self, node):
        if isinstance(node, dict):
            return self._parse_dict(node)
        elif isinstance(node, list):
            return self._parse_list(node)
        elif isinstance(node, str):
            return self._parse_string(node)
        elif isinstance(node, bool):
            return "true" if node else "false"  # Обрабатываем булевы значения
        elif isinstance(node, int):
            return str(node)
        elif isinstance(node, float):
            return str(node)
        else:
            raise SyntaxError(f"Unsupported type: {type(node)}")

    def _parse_dict(self, node):
        result = []
        for key, value in node.items():
            if isinstance(value, dict) or isinstance(value, list):
                result.append(f"    {key} = {self._parse_node(value)};")
            else:
                result.append(f"    {key} = {self._parse_node(value)};")
        return "{\n" + "\n".join(result) + "\n}"  # Фигурные скобки для словарей

    def _parse_list(self, node):
        return f"({', '.join(self._parse_node(item) for item in node)})"

    def _parse_string(self, node):
        # Используем двойные кавычки для строк
        return f'"{node}"'

    def parse_yaml(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f)
        return self.parse(yaml_data)

    def parse_expression(self, expression, context):
        # Обрабатываем вычисления вида ?[имя + 1], используя eval
        expression = expression.strip()[2:-1]  # Убираем ?[ и ]
        try:
            # Используем eval для вычисления выражения в контексте данных
            result = eval(expression, {}, context)
            return str(result)  # Возвращаем результат вычисления как строку
        except Exception as e:
            raise SyntaxError(f"Error evaluating expression: {expression}") from e


def main():
    if len(sys.argv) != 2:
        print("Usage: python config_parser.py <path_to_yaml_file>")
        sys.exit(1)

    yaml_file = sys.argv[1]
    parser = ConfigParser()

    try:
        # Загружаем данные из YAML
        with open(yaml_file, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f)
        
        # Собираем все константы в один словарь для дальнейшей обработки
        context = {key: value for key, value in yaml_data.items()}
        
        result = []
        for key, value in yaml_data.items():
            if isinstance(value, str) and value.startswith("?["):
                # Обрабатываем выражения типа ?[test + 1]
                result.append(f"let {key} = {parser.parse_expression(value, context)};")
            else:
                result.append(f"let {key} = {parser._parse_node(value)};")
        
        # Выводим результат
        print("\n".join(result))

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
