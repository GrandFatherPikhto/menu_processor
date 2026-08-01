import json
import os
from pathlib import Path
from typing import Dict, Set, List, Optional, Any, Union

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


class ConfigLoadError(Exception):
    """Исключение при ошибках загрузки/парсинга конфигурационных файлов"""

    def __init__(self, message: str, file_path: Union[str, Path, None] = None):
        self.file_path = str(file_path) if file_path is not None else None
        if self.file_path:
            super().__init__(f"{message} (файл: {self.file_path})")
        else:
            super().__init__(message)


def load_config_file(file_path: Union[str, Path]) -> Any:
    """Загружает конфигурационный файл в формате JSON или YAML.

    Формат определяется по расширению файла:
    - ``.json`` → json.load
    - ``.yaml`` / ``.yml`` → yaml.safe_load

    Args:
        file_path: путь к файлу конфигурации.

    Returns:
        Распарсенные данные (обычно ``dict``).

    Raises:
        ConfigLoadError: если файл не найден, нет прав на чтение
            или содержимое не является корректным JSON/YAML.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    try:
        if not path.exists():
            raise ConfigLoadError("Файл не найден", path)

        with open(path, "r", encoding="utf-8") as f:
            if suffix in (".yaml", ".yml"):
                if yaml is None:
                    raise ConfigLoadError(
                        "PyYAML не установлен. Выполните: pip install PyYAML", path
                    )
                data = yaml.safe_load(f)
            elif suffix == ".json":
                data = json.load(f)
            else:
                raise ConfigLoadError(
                    f"Неподдерживаемый формат конфигурации '{suffix}'. "
                    "Используйте .json, .yaml или .yml",
                    path,
                )

        if isinstance(data, dict):
            return data

        if data is None:
            raise ConfigLoadError("Файл пуст", path)

        raise ConfigLoadError(
            f"Конфигурация должна быть объектом, а не {type(data).__name__}", path
        )

    except json.JSONDecodeError as e:
        raise ConfigLoadError(f"Ошибка формата JSON: {e}", path)
    except yaml.YAMLError as e:  # type: ignore[union-attr]
        raise ConfigLoadError(f"Ошибка формата YAML: {e}", path)
    except PermissionError:
        raise ConfigLoadError("Нет прав для чтения файла", path)
    except ConfigLoadError:
        raise
    except Exception as e:
        raise ConfigLoadError(f"Ошибка загрузки: {e}", path)


def load_json_data(config_file: str) -> Optional[Dict]:
    """Загружает JSON-файл (совместимость со старым API).

    В случае ошибки печатает сообщение и возвращает ``None``.
    Для нового кода используйте :func:`load_config_file`.
    """
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка JSON: {e}")
        return None
    except Exception as error:
        print(f"❌ Ошибка загрузки: {error}")
        return None


def save_json_data(data: Union[Dict, Set], output_path: str = None) -> bool:
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"✅ Данные сохранены в файл {output_path}")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения файла: {e}")
        return False
