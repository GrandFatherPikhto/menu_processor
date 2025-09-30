import json
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigError(Exception):
    """Исключение для ошибок конфигурации"""
    def __init__(self, message: str, file_path: Optional[Path] = None):
        self.file_path = file_path
        self.message = message
        if file_path:
            super().__init__(f"{message} (файл: {file_path})")
        else:
            super().__init__(message)

class MenuConfig:
    def __init__(self, file_path: str):
        self._generation_files = {}
        self._config_path = Path(file_path)
        self._main_config = self._load_json_file(self._config_path, "основной конфиг")
        
        self._menu_schema = self._load_required_file("menu_schema", "схема меню")
        self._menu_data = self._load_required_file("menu", "данные меню")
        self._menu_tree = self._menu_data.get("menu")
        self._data_config = self._load_required_file("menu_config", "данные и роли элементов меню")
        self._generation_config = self._load_required_file("generation_files", "данные и роли элементов меню")
        self._generation_files = self._generation_config.get("files")
        self._templates_path = self._generation_config.get("templates")
    
    def _load_required_file(self, config_key: str, description: str) -> Dict[str, Any]:
        """Загружает обязательный файл из пути, указанного в конфиге"""
        file_path_str = self._main_config.get(config_key)
        if not file_path_str:
            raise ConfigError(f"Отсутствует путь к {description} '{config_key}'")
        
        # Создаем путь относительно основного конфиг-файла
        file_path = self._config_path.parent / file_path_str
        return self._load_json_file(file_path, description)
        
    def _load_json_file(self, file_path: Path, description: str) -> Dict[str, Any]:
        """Загружает и валидирует JSON файл"""
        try:
            if not file_path.exists():
                raise ConfigError(f"Файл не найден", file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, dict):
                raise ConfigError(f"JSON должен быть объектом, а не {type(data).__name__}", file_path)
                
            return data
            
        except json.JSONDecodeError as e:
            raise ConfigError(f"Ошибка формата JSON: {e}", file_path)
        except PermissionError:
            raise ConfigError("Нет прав для чтения файла", file_path)
        except Exception as e:
            raise ConfigError(f"Ошибка загрузки: {e}", file_path)
        
    def _check_file_path(self, file_path: Path):
        if not file_path.exists():
            raise ConfigError(f"Файл не найден", file_path)
    
    def menu_config_param(self, param_name: str, default_value: str) -> str:
        if self._menu_data.get("config") is None:
            return default_value
        config = self._menu_data["config"]
        if config.get(param_name) is None:
            return default_value
        return config[param_name]

    @property
    def default_navigate(self) -> str:
        return self.menu_config_param("default_navigate", "cyclic")
    
    @property
    def default_control(self) -> str:
        return self.menu_config_param("default_control", "position")
    
    @property
    def default_branch_navigate(self) -> str:
        return self.menu_config_param("default_branch_navigate", "limit")
    
    @property
    def root_navigate(self) -> str:
        return self.menu_config_param("root_navigate", "limit")

    @property
    def menu_schema(self) -> Dict[str, Any]:
        return self._menu_schema
    
    @property
    def menu_data(self) -> Dict[str, Any]:
        return self._menu_data
    
    @menu_data.setter
    def menu_data(self, menu_data: Dict[str, Any]):
        self._menu_data = menu_data
    
    @property
    def main_config(self) -> Dict[str, Any]:
        return self._main_config
    
    @property
    def data_config(self) -> Dict[str, Any]:
        return self._data_config
    
    @property
    def generatrion_files(self) -> Dict[str, Any] | None:
        return self._generation_files
    
    @property
    def menu_tree(self) -> Dict[str, Any] | None:
        return self._menu_tree
        
    @property
    def templates_path(self)->Path | None:
        return self._templates_path
    
    @property
    def output_flattern(self)->str | None:
        return self._main_config.get("output_flattern")

def main(json_file: str):
    try:
        config = MenuConfig(json_file)
        print("✅ Конфигурация успешно загружена")
        print(config._main_config)
        
    except ConfigError as e:
        print(f"❌ {e}")
        return 1
    except Exception as e:
        print(f"💥 Неожиданная ошибка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main("./config/config.json"))