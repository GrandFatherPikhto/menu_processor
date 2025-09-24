from jsonschema import Draft7Validator, ValidationError
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

from data_types import DataTypeConfig

class MenuValidator:
    def __init__(self, schema_path: str = "config/menu_schema.json"):
        self.schema = self._load_schema(schema_path)
        self.validator = Draft7Validator(self.schema)
        self.data_type_config = None
        
    def _load_schema(self, schema_path: str) -> Dict:
        """Загрузка JSON Schema из файла"""
        with open(schema_path, 'r') as f:
            return json.load(f)
    
    def load_data_type_config(self, config: DataTypeConfig):
        """Загрузка конфигурации типов данных"""
        self.data_type_config = config
    
    def validate_menu(self, menu_config: Dict) -> Dict[str, List[str]]:
        """
        Полная валидация древовидного меню
        
        Returns:
            Dict[str, List[str]]: Ошибки по ID элементов
        """
        errors = {}
        
        # Валидация JSON Schema
        try:
            self.validator.validate(menu_config)
        except ValidationError as e:
            errors["root"] = [f"Schema validation failed: {e.message}"]
            return errors
        
        # Рекурсивная валидация элементов
        self._validate_tree(menu_config.get("menu", []), [], errors)
        
        return errors
    
    def _validate_tree(self, items: List[Dict], path: List[str], errors: Dict[str, List[str]]):
        """Рекурсивная валидация дерева меню"""
        for item in items:
            current_path = path + [item['id']]
            item_errors = []
            
            # Валидация элемента
            item_errors.extend(self._validate_item(item))
            
            # Рекурсивная валидация детей
            if 'items' in item:
                self._validate_tree(item['items'], current_path, errors)
            
            if item_errors:
                errors['->'.join(current_path)] = item_errors
    
    def _validate_item(self, item: Dict) -> List[str]:
        """Валидация отдельного элемента меню"""
        errors = []
        
        # Проверка: branch не должен иметь type
        if 'items' in item and 'type' in item:
            errors.append("Branch element cannot have 'type'")
        
        # Проверка: leaf должен иметь type
        if 'items' not in item and 'type' not in item:
            errors.append("Leaf element must have 'type'")
        
        # Валидация типа данных
        if 'type' in item:
            errors.extend(self._validate_data_type(item))
        
        # Валидация значений
        if 'default' in item:
            errors.extend(self._validate_default_value(item))
        
        # Валидация факторов и значений
        if 'factors' in item:
            errors.extend(self._validate_factors(item))
        if 'values' in item:
            errors.extend(self._validate_values(item))
        
        return errors
    
    def _validate_data_type(self, item: Dict) -> List[str]:
        """Валидация типа данных"""
        errors = []
        
        if self.data_type_config and not self.data_type_config.has_type(item['type']):
            errors.append(f"Unknown data type: {item['type']}")
        
        return errors
    
    def _validate_default_value(self, item: Dict) -> List[str]:
        """Валидация значения по умолчанию"""
        errors = []
        
        # Проверка для числовых типов
        if 'min' in item and 'max' in item:
            if not (item['min'] <= item['default'] <= item['max']):
                errors.append(f"default value {item['default']} out of range [{item['min']}, {item['max']}]")
        
        # Проверка для fixed типов
        if 'values' in item and 'default' in item:
            if item['default'] not in item['values']:
                errors.append(f"default value {item['default']} not in allowed values")
        
        return errors
    
    def _validate_factors(self, item: Dict) -> List[str]:
        """Валидация факторов"""
        errors = []
        
        if 'default_idx' in item and item['default_idx'] >= len(item['factors']):
            errors.append(f"default_idx {item['default_idx']} out of bounds for factors array")
        
        return errors
    
    def _validate_values(self, item: Dict) -> List[str]:
        """Валидация значений"""
        errors = []
        
        if 'default_idx' in item and item['default_idx'] >= len(item['values']):
            errors.append(f"default_idx {item['default_idx']} out of bounds for values array")
        
        return errors
    
    def get_validation_report(self, errors: Dict[str, List[str]]) -> str:
        """Генерация читаемого отчета об ошибках"""
        if not errors:
            return "✅ Validation passed successfully!"
        
        report = ["❌ Validation errors:"]
        for path, path_errors in errors.items():
            report.append(f"\nPath: {path}")
            for error in path_errors:
                report.append(f"  - {error}")
        
        return "\n".join(report)
    
def main():
    # Инициализация валидатора
    validator = MenuValidator("config/menu_schema.json")

    # Загрузка конфигурации типов данных
    data_type_config = DataTypeConfig("config/data_types.json")
    validator.load_data_type_config(data_type_config)

    # Загрузка и валидация меню
    with open("menu/menu.json", "r") as f:
        menu_config = json.load(f)

    errors = validator.validate_menu(menu_config)

    # Вывод результатов
    print(validator.get_validation_report(errors))

    if not errors:
        print("Menu configuration is valid!")
    else:
        print(f"Found {len(errors)} validation errors")    

if __name__ == '__main__':
    main()