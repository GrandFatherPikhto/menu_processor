from typing import Dict, List, Set, Optional, Any
import json

from flat_node import FlatNode
from menu_validator import MenuValidator
from menu_config import MenuConfig, ConfigError
from menu_flattener import MenuFlattener, FlattenerError

class ProcessorError(Exception):
    """Исключение для ошибок конфигурации"""
    def __init__(self, message: str):
        super().__init__(message)

class MenuProcessor:
    def __init__(self, config_name: str):
        self._config_name = config_name
        self._config = MenuConfig(self._config_name)
        print(f"✅ Конфигурация {self._config_name} успешно загружена")
        self._validator = MenuValidator(config=self._config)
        errors = self._validator.validate()
        if errors:
            print(f"❌ Конфигурация содержит ошибки:")
            for id, items in errors.items():
                print(f"❌ {id}:")
                for item in items:
                    print(f"\t➤ {item}")
            raise ProcessorError(f"❌ Ошибка конфигурации")
        else:
            print("✅ и проверена")
            self._flattener = MenuFlattener(self._config)
            self._flat_nodes = self._flattener.flatten()
            for node in self._flat_nodes:
                print(f"- {node}")    

    @property
    def config(self)->Dict:
        return self._config

    @property
    def menu(self)->Dict[str,FlatNode] | None:
        return { n.id : n for n in self._flat_nodes if n.id != 'root' }
    
    @property
    def functions(self)->Dict[str,Any] | None:
        items = {}
        for node in self._flat_nodes:
            if node.type == "callback":
                continue
            if click_info := node.function_click_info:
                items[click_info["name"]] = click_info
            if position_info := node.function_position_info:
                items[position_info["name"]] = position_info
        return items
    
    @property
    def categories(self)->Dict[str, Any] | None:
        items = {}
        for node in self._flat_nodes:
            name = node.category_name
            props = node.category
            if name is not None and props is not None:
                items[name] = props
        return items
    
    @property
    def leafs(self)->Dict[str, FlatNode] | None:
        return { n.id : n for n in self._flat_nodes if n.is_leaf if n.id != 'root' }
    
    @property
    def branches(self)->Dict[str, FlatNode] | None:
        return { n.id : n for n in self._flat_nodes if n.is_branch  if n.id != 'root' }

    @property
    def first(self)->FlatNode | None:
        for node in self._flat_nodes:
            # Проверяем что все необходимые атрибуты существуют
            if (hasattr(node, 'prev_sibling') and 
                hasattr(node, 'parent') and
                node.parent is not None and
                hasattr(node.parent, 'id') and
                node.parent.id == 'root'):
                return node.parent.first_child
        return None



def main(config_name:str)->int:
    try:
        processor = MenuProcessor(config_name)
        for id, item in processor.categories.items():
            print(id, item)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main("./config/config.json")