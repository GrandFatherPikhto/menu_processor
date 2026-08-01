from jsonschema import Draft7Validator, ValidationError
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

from common import load_json_data, save_json_data
from i18n import _
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
            errors["schema"] = [_("Schema validation failed: {message}").format(message=e.message)]
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
            errors.append(_("Id {id} not unique").format(id=item.get('id')))
        
        # Check: a branch must not have 'type'
        if 'items' in item and 'type' in item:
            errors.append(_("Branch element cannot have 'type'"))
        
        # Check: a leaf must have 'type'
        if 'items' not in item and 'type' not in item:
            errors.append(_("Leaf element must have 'type'"))
        
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
        """Validates the default value."""
        errors = []
        
        # Check for numeric types
        if 'min' in item and 'max' in item:
            if not (item['min'] <= item['default'] <= item['max']):
                errors.append(_("default value {default} out of range [{min}, {max}]").format(
                    default=item['default'], min=item['min'], max=item['max']))
        
        # Check for fixed types
        if 'values' in item and 'default' in item:
            if item['default'] not in item['values']:
                errors.append(_("default value {default} not in allowed values").format(
                    default=item['default']))
        
        return errors

    def _validate_data_type(self, item: Dict):
        return []

    def _validate_factors(self, item: Dict) -> List[str]:
        """Validates factors."""
        errors = []
        
        if 'default_idx' in item and item['default_idx'] >= len(item['factors']):
            errors.append(_("default_idx {idx} out of bounds for factors array").format(
                idx=item['default_idx']))
        
        return errors
    
    def _validate_values(self, item: Dict) -> List[str]:
        """Validates values."""
        errors = []
        
        if 'default_idx' in item and item['default_idx'] >= len(item['values']):
            errors.append(_("default_idx {idx} out of bounds for values array").format(
                idx=item['default_idx']))
        
        return errors


def main(config_file):
    try:
        config = MenuConfig(config_file)
        print(f"✅ {_('Configuration {path} loaded successfully').format(path=config_file)}")
        validator = MenuValidator(config=config)
        errors = validator.validate()
        if errors:
            print(f"❌ {_('Configuration contains errors:')}")
            for id, items in errors.items():
                print(f"❌ {id}:")
                for item in items:
                    print(f"\t➤ {item}")
        else:
            print(f"✅ {_('and validated')}")


    except ConfigError as e:
        print(f"❌ {e}")
        return 1
    except Exception as e:
        print(f"💥 {_('Unexpected error: {error}').format(error=e)}")
        return 1

if __name__ == "__main__":
    main('./config/config.yaml')