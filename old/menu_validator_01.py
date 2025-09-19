from typing import Dict, List, Optional, Any
from jsonschema import validate, Draft7Validator
import json

class ParserError(Exception):
    """Выбрасывается при ошибках валидации меню"""
    def __init__(self, errors: List[str]):
        super().__init__("Menu validation failed")
        self.errors = errors

# Поля, требуемые для каждой ноды
REQUIRED_FIELDS=['id', 'name']
ALLOWED_FIELDS={'id', 'name', 'data_type'}

# Базовые data_types
DATA_TYPES = [
    "boolean", "byte", "ubyte",
    "word", "uword", "dword", "udword",
    "string",
    # расширенные варианты
    "byte_factor", "ubyte_factor",
    "word_factor", "uword_factor",
    "dword_factor", "udword_factor",
    "byte_fixed", "ubyte_fixed",
    "word_fixed", "uword_fixed",
    "dword_fixed", "udword_fixed",
    "string_fixed",
    # Только функция обратного вызова
    "callback"
]

CONTROL_TYPES = ["click", "position"]

# Настраиваемая таблица допустимых комбинаций
RULES = {
    "boolean": {
        "required": ["default"],
        "allowed": ["control", "default", "str_true", "str_false"],
        "forbid": ["min", "max", "step", "factors", "values", "cyclic_siblings"]
    },
    "string": {
        "required": ["values", "default"],
        "allowed": ["values", "default", "control"],
        "forbid": ["min", "max", "step", "factors", "cyclic_siblings"]
    },
    "byte": {
        "required": ["factors", "min", "max", "default"],
        "allowed": ["id", "name", "data_type","min", "max", "step", "default", "control"],
        "forbid": ["factors", "values", "cyclic_siblings"]
    },
    "byte_factor": {
        "required": ["factors", "min", "max", "default"],
        "allowed": ["min", "max", "step", "default", "factors"],
        "forbid": ["control", "values", "cyclic_siblings"]
    },
    "byte_fixed": {
        "required": ["values", "default"],
        "allowed": ["values", "default"],
        "forbid": ["min", "max", "step", "factors", "control", "cyclic_siblings"]
    },
    "ubyte": {
        "required": ["factors", "min", "max", "default"],
        "allowed": ["min", "max", "step", "default", "control"],
        "forbid": ["factors", "values", "cyclic_siblings"]
    },
    "ubyte_factor": {
        "required": ["factors", "min", "max", "default"],
        "allowed": ["min", "max", "step", "default", "factors"],
        "forbid": ["control", "values", "cyclic_siblings"]
    },
    "ubyte_fixed": {
        "required": ["values", "default"],
        "allowed": ["values", "default"],
        "forbid": ["min", "max", "step", "factors", "control", "cyclic_siblings"]
    },
    "uword": {
        "required": ["factors", "min", "max", "default"],
        "allowed": ["min", "max", "step", "default", "control"],
        "forbid": ["factors", "values", "cyclic_siblings"]
    },
    "uword_factor": {
        "required": ["factors", "min", "max", "default"],
        "allowed": ["min", "max", "step", "default", "factors"],
        "forbid": ["control", "values", "cyclic_siblings"]
    },
    "uword_fixed": {
        "required": ["values", "min", "max", "default"],
        "allowed": ["values", "default"],
        "forbid": ["min", "max", "step", "factors", "control", "cyclic_siblings"]
    },
    "dword": {
        "required": ["min", "max", "default"],
        "allowed": ["min", "max", "step", "default", "control"],
        "forbid": ["factors", "values", "cyclic_siblings"]
    },
    "dword_factor": {
        "required": ["factors", "min", "max", "default"],
        "allowed": ["min", "max", "step", "default", "factors"],
        "forbid": ["control", "values", "cyclic_siblings"]
    },
    "dword_fixed": {
        "required": ["values", "min", "max", "default"],
        "allowed": ["values", "default"],
        "forbid": ["min", "max", "step", "factors", "control", "cyclic_siblings"]
    },
    "udword": {
        "required": ["factors", "min", "max", "default"],
        "allowed": ["min", "max", "step", "default", "control"],
        "forbid": ["factors", "values", "cyclic_siblings"]
    },
    "udword_factor": {
        "required": ["factors", "min", "max", "default"],
        "allowed": ["min", "max", "step", "default", "factors"],
        "forbid": ["control", "values", "cyclic_siblings"]
    },
    "udword_fixed": {
        "required": ["values", "min", "max", "default"],
        "allowed": ["values", "default"],
        "forbid": ["min", "max", "step", "factors", "control", "cyclic_siblings"]
    },
    "callback" : {
        "required": [],
        "allowed": ["value"],
        "forbid": ["min", "max", "step", "factors", "control", "cyclic_siblings"]
    }
}

# Правило для callback-узлов (без data_type)
CALLBACK_RULE = {
    "allowed": ["control", "value", "data_type"],
    "forbid": ["min", "max", "step", "default", "factors", "values", "cyclic_siblings"]
}

# Правило для групповых узлов (без data_type, с items)
GROUP_RULE = {
    "allowed": ["cyclic_siblings", "items"],
    "forbid": ["data_type", "control", "min", "max", "step", "default", "factors", "values"]
}

class MenuValidator:
    """Класс для проверки меню с поддержкой callback-узлов"""

    def __init__(self, 
                 rules: Dict[str, Dict[str, List[str]]] = None, 
                 callback_rule: Dict[str, List[str]] = None,
                 group_rule: Dict[str, List[str]] = None):
        self.rules = rules or RULES
        self.callback_rule = callback_rule or CALLBACK_RULE
        self.group_rule = group_rule or GROUP_RULE
        self.schema = {
            "type": "array",
            "items": {"$ref": "#/definitions/node"},
            "definitions": {
                "node": {
                    "type": "object",
                    "required": ["name", "id"],
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "data_type": {"enum": DATA_TYPES},
                        "control": {"enum": CONTROL_TYPES},
                        "min": {"type": "integer"},
                        "max": {"type": "integer"},
                        "step": {"type": "integer"},
                        "default_idx": {"type": "integer"},
                        "default": {},
                        "factors": {"type": "array", "items": {"type": "integer"}},
                        "values": {"type": "array", "items": {}},
                        "cyclic_siblings": {"type": "boolean"},
                        "str_false": {"type": "string"},
                        "str_true": {"type": "string"},
                        "items": {
                            "type": "array",
                            "items": {"$ref": "#/definitions/node"}
                        }
                    },
                    "additionalProperties": False,
                    "oneOf": [
                        {
                            # Узел с вложенными элементами (не лист)
                            "required": ["items"],
                            "not": {"required": ["data_type"]},
                            "error_message": "Group nodes must have 'items' and must NOT have 'data_type'"
                        },
                        {
                            # Конечный узел (лист) - должен иметь data_type
                            "required": ["data_type"],
                            "not": {"required": ["items"]},
                            "error_message": "Leaf nodes must have 'data_type' and must NOT have 'items'"
                        }
                    ]
                }
            }
        }

    def validate(self, menu: List[Dict[str, Any]]):
        errors: List[str] = []

        # --- jsonschema ---
        validator = Draft7Validator(self.schema)
        for error in validator.iter_errors(menu):
            error_message = self._get_detailed_error_message(error)
            errors.append(f"Schema error at {list(error.path)}: {error_message}")

        # --- семантика ---
        self._check_recursive(menu, errors, path="ROOT")

        if errors:
            raise ParserError(errors)

    def _get_detailed_error_message(self, error) -> str:
        """Получает детализированное сообщение об ошибке"""
        if error.validator == 'oneOf':
            # Анализируем, какое именно правило не выполнено
            node = error.instance
            has_data_type = 'data_type' in node
            has_items = 'items' in node
            
            if has_data_type and has_items:
                return "Node cannot have both 'data_type' and 'items'"
            elif not has_data_type and not has_items:
                return "Node must have either 'data_type' (for leaf nodes) or 'items' (for group nodes)"
            elif has_data_type:
                return "Leaf node with 'data_type' cannot have 'items'"
            else:
                return "Group node with 'items' cannot have 'data_type'"
        
        return error.message
    
    def _check_recursive(self, nodes: List[Dict[str, Any]], errors: List[str], path: str):
        """Рекурсивные проверки + правила"""
        names_seen = set()
        for node in nodes:
            name = node["name"]
            full_path = f"{path}/{name}"
            
            # уникальность имён
            if name in names_seen:
                errors.append(f"Duplicate name '{name}' under {path}")
            names_seen.add(name)

            # Определяем тип узла и применяем соответствующие правила
            if "data_type" in node:
                # Конечный узел с data_type (обычный параметр)
                self._validate_parameter_node(node, full_path, errors)
                
            elif "items" in node:
                # Групповой узел
                self._validate_group_node(node, full_path, errors)
                
            else:
                # Callback-узел (без data_type и без items)
                self._validate_callback_node(node, full_path, errors)

            # рекурсия для вложенных элементов
            if "items" in node:
                self._check_recursive(node["items"], errors, full_path)

    def _validate_parameter_node(self, node: Dict[str, Any], full_path: str, errors: List[str]):
        """Валидация конечного узла с data_type"""
        dtype = node["data_type"]
        
        if dtype in self.rules:
            rule = self.rules[dtype]
            allowed = set(rule.get("allowed", []))
            forbidden = set(rule.get("forbid", []))
            required = set(rule.get("required", []))
            present = set(node.keys()) - {"name", "data_type", "items", "id"}
            
            # Проверяем запрещенные поля
            for field in present:
                if field in forbidden:
                    errors.append(f"Field '{field}' not allowed for {dtype} at {full_path}")
            
            # Проверяем обязательные поля, специфичные для данного data_type
            for field in required:
                if field.endswith("*") and not any(x.startswith(field[:-1]) for x in present):
                    errors.append(f"Expected at least one field '{field}' for {dtype} at {full_path}")

        # диапазоны
        if "min" in node and "max" in node and node["min"] > node["max"]:
            errors.append(f"Invalid range at {full_path}: min > max")

        if "default" in node and "min" in node and "max" in node:
            d = node["default"]
            if not (node["min"] <= d <= node["max"]):
                errors.append(f"Default {d} out of range [{node['min']}, {node['max']}] at {full_path}")

    def _validate_group_node(self, node: Dict[str, Any], full_path: str, errors: List[str]):
        """Валидация группового узла"""
        rule = self.group_rule
        allowed = set(rule.get("allowed", []))
        forbidden = set(rule.get("forbid", []))
        present = set(node.keys()) - {"name", "id"}
        
        # Проверяем запрещенные поля для групп
        for field in present:
            if field in forbidden:
                errors.append(f"Field '{field}' not allowed for group nodes at {full_path}")
        
        # Проверяем, что у группы есть items и они не пустые
        if not node.get("items"):
            errors.append(f"Group node must have non-empty 'items' at {full_path}")

    def _validate_callback_node(self, node: Dict[str, Any], full_path: str, errors: List[str]):
        """Валидация callback-узла (без data_type и items)"""
        rule = self.callback_rule
        allowed = set(rule.get("allowed", []))
        print(f'Allowed: {allowed}')
        forbidden = set(rule.get("forbid", []))
        print(f'Forbidden: {forbidden}')
        present = set(node.keys()) - {"name", "id"}
        
        # Проверяем запрещенные поля для callback-узлов
        for field in present:
            if field in forbidden:
                errors.append(f"Field '{field}' not allowed for callback nodes at {full_path}")
        
        # Проверяем разрешенные поля
        for field in allowed:
            if field.endswith("*") and not any(x.startswith(field[:-1]) for x in present):
                errors.append(f"Expected at least one field '{field}' for callback nodes at {full_path}")
        
        # # Специальная проверка: callback-узлы должны иметь control
        # if "control" not in node:
        #     errors.append(f"Callback node must have 'control' field at {full_path}")


def main(input_file: str) -> bool:
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            menu_data = json.load(f)
            if menu_data.get('menu', None) is not None:
                validator = MenuValidator()
                validator.validate(menu_data.get('menu', None))
                print("✅ Конфигурация валидна!")
                return True
            
    except ParserError as error:
        print(f"❌ Ошибка синтаксиса:")
        for err in error.errors:
            print(f"   - {err}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка JSON: {e}")
        return False
    except Exception as error:
        print(f"❌ Ошибка загрузки: {error}")
        return False


# Пример валидной конфигурации
EXAMPLE_CONFIG = {
    "menu": [
        {
            "id": "group1",
            "name": "Основные настройки",
            "items": [
                {
                    "id": "param1",
                    "name": "Скорость",
                    "data_type": "uword",
                    "min": 0,
                    "max": 1000,
                    "default": 500
                },
                {
                    "id": "callback1",
                    "name": "Сброс настроек",
                    "control": "click"  # Callback-узел
                }
            ]
        },
        {
            "id": "callback2", 
            "name": "Экстренная остановка",
            "control": "click"  # Callback-узел в корне
        }
    ]
}

if __name__ == "__main__":
    # Тестируем на примере
    # validator = MenuValidator()
    # try:
    #     validator.validate(EXAMPLE_CONFIG["menu"])
    #     print("✅ Пример конфигурации валиден!")
    # except ParserError as e:
    #     print("❌ Ошибки в примере:")
    #     for error in e.errors:
    #         print(f"   - {error}")
    main('config/menu.json')