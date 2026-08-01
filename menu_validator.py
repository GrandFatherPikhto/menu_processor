from jsonschema import Draft7Validator, ValidationError
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

from common import load_json_data, save_json_data
from menu_config import MenuConfig, ConfigError

class ParserError(Exception):
    """Выбрасывается при ошибках валидации меню"""
    def __init__(self, errors: List[str]):
        super().__init__("Menu validation failed")
        self.errors = errors

class MenuValidator:
    def __init__(self, config: MenuConfig, raise_exception = False):
        self._config = config
        self._raise_exception = raise_exception
        self._validator = Draft7Validator(self._config.menu_schema)
        self._ids = []
        self._errors = {}

    def validate(self, menu_data: Dict = None) -> Dict[str, List[str]]:
        """
        Полная валидация древовидного меню
        
        Returns:
            Dict[str, List[str]]: Ошибки по ID элементов
        """
        menu = self._config.menu_data if menu_data is None else menu_data

        errors = {}

        # Валидация JSON Schema
        try:
            self._validator.validate(menu)
        except ValidationError as e:
            errors["schema"] = [f"Schema validation failed: {e.message}"]
            return errors
        
        # Рекурсивная валидация элементов
        self._validate_tree(menu.get("menu", []), [], errors)
        
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

        if item.get("id") not in self._ids:
            self._ids.append(item.get("id"))
        else:
            errors.append(f"Id {item.get('id')} not unique")
        
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

    def _validate_data_type(self, item: Dict):
        return []

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


def main(config_file):
    try:
        config = MenuConfig(config_file)
        print(f"✅ Конфигурация {config_file} успешно загружена")
        validator = MenuValidator(config=config)
        errors = validator.validate()
        if errors:
            print(f"❌ Конфигурация содержит ошибки:")
            for id, items in errors.items():
                print(f"❌ {id}:")
                for item in items:
                    print(f"\t➤ {item}")
        else:
            print("✅ и проверена")


    except ConfigError as e:
        print(f"❌ {e}")
        return 1
    except Exception as e:
        print(f"💥 Неожиданная ошибка: {e}")
        return 1

if __name__ == "__main__":
    main('./config/config.yaml')