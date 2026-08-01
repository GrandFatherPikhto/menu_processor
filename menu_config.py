from typing import Dict, Any, Set, List, Optional
from pathlib import Path

from common import load_config_file, ConfigLoadError

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
        self._main_config = self._load_data_file(self._config_path, "основной конфиг")

        self._menu_schema = self._load_required_file("menu_schema", "схема меню")
        self._menu_data = self._load_required_file("menu", "данные меню")
        self._menu_config = self._menu_data.get("config")
        self._menu_tree = self._menu_data.get("menu")
        self._data_config = self._load_required_file("menu_config", "данные и роли элементов меню")
        self._generation_config = self._load_required_file("generation_files", "данные и роли элементов меню")
        self._generation_files = self._generation_config.get("files")
        self._templates_path = self._generation_config.get("templates_path")
    
    def _load_required_file(self, config_key: str, description: str) -> Dict[str, Any]:
        """Загружает обязательный файл из пути, указанного в конфиге"""
        file_path_str = self._main_config.get(config_key)
        if not file_path_str:
            raise ConfigError(f"Отсутствует путь к {description} '{config_key}'")
        
        # Создаем путь относительно основного конфиг-файла
        file_path = self._config_path.parent / file_path_str
        return self._load_data_file(file_path, description)

    def _load_data_file(self, file_path: Path, description: str) -> Dict[str, Any]:
        """Загружает конфигурационный файл (JSON или YAML)"""
        try:
            return load_config_file(file_path)
        except ConfigLoadError as e:
            raise ConfigError(str(e)) from e
        
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
    def output_directory(self) -> str | None:
        if self._menu_config is None:
            return None
        return self._menu_config.get("output_directory")
    
    @property
    def templates_path(self) -> str | None:
        return self._templates_path

    @property
    def generation_files(self) -> Dict[str, Path] | None:
        generation_files = {}
        if self.output_directory is not None:
            output_directory = Path(self.output_directory)
            if self._generation_files is not None:
                for template, output in self._generation_files.items():
                    generation_files[template] = output_directory / output
        return generation_files

    def boolean_menu_config_value(self, param_name: str) -> bool:
        if self._menu_config is None or self._menu_config.get(param_name) is None:
            return False
        return self._menu_config.get(param_name)
    
    @property
    def include_files(self)->List[str]:
        if self._menu_config is None or self._menu_config.get("include_files") is None:
            return []
        return self._menu_config.get("include_files")

    @property
    def wrap_by_name_functions(self) -> bool:
        return self.boolean_menu_config_value("wrap_by_name_functions")
    
    @property
    def enable_node_names(self) -> bool:
        return self.boolean_menu_config_value("enable_node_names")
    
    @property
    def menu_tree(self) -> Dict[str, Any] | None:
        return self._menu_tree
            
    @property
    def output_flattern(self)->str | None:
        return self._main_config.get("output_flattern")

def main(json_file: str):
    try:
        config = MenuConfig(json_file)
        print("✅ Конфигурация успешно загружена")
        print(config.templates_path)
        print(f"Wrap By Name: {config.wrap_by_name_functions}")
        print(f"Include Files: {config.include_files}")
        
    except ConfigError as e:
        print(f"❌ {e}")
        return 1
    except Exception as e:
        print(f"💥 Неожиданная ошибка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main("./config/config.yaml"))