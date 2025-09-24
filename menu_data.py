import json
from typing import Dict, Any, Set, List, Optional
from pathlib import Path

from menu_config import MenuConfig, ConfigError
from menu_validator import MenuValidator

class MenuData:
    def __init__(self, config: MenuConfig):
        self._config = config
        self._data_config = config.data_config
        self._roles = self._data_config.get("roles")
        self._types = self._data_config.get("types")
        self._numbers = self._data_config.get("numbers")

    def type(self, name: str)->Dict | None:
        return self._types.get(name)
    
    def role(self, name: str)->Dict | None:
        return self._roles.get(name)

    def role_types(self, name: str)->List | None:
        if self._roles.get(name) is None:
            return None
        return self._roles[name]

    @property
    def roles(self)->Set[str]:
        return { role for role in self._roles }
    
    @property
    def types(self)->Set[str]:
        return { type for type in self._types }
    
    @property 
    def numbers(self)->Set[str]:
        return self._numbers

def main(config_file: str):
    try:
        config = MenuConfig(config_file)
        print(f"✅ Конфигурация {config_file} успешно загружена")
        data = MenuData(config)
        print("Roles:")
        print(data.roles)
        print("Types:")
        print(data.types)
        print("Numbers:")
        print(data.numbers)

        print("Byte config:")
        print(data.type('byte'))
        print("Simple types:")
        print(data.role_types("simple"))

    except ConfigError as e:
        print(f"❌ {e}")
        return 1
    # except Exception as e:
    #     print(f"💥 Неожиданная ошибка: {e}")
    #     return 1


if __name__ == "__main__":
    main('./config/config.json')