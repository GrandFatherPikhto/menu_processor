import json
import os
from pathlib import Path
from typing import Dict, Set, List, Optional, Any, Union

from .i18n import _

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


class ConfigLoadError(Exception):
    """Exception raised when loading/parsing configuration files fails."""

    def __init__(self, message: str, file_path: Union[str, Path, None] = None):
        self.file_path = str(file_path) if file_path is not None else None
        if self.file_path:
            super().__init__(f"{message} ({_('file')}: {self.file_path})")
        else:
            super().__init__(message)


def load_config_file(file_path: Union[str, Path]) -> Any:
    """Loads a configuration file in JSON or YAML format.

    The format is detected from the file extension:
    - ``.json`` → json.load
    - ``.yaml`` / ``.yml`` → yaml.safe_load

    Args:
        file_path: path to the configuration file.

    Returns:
        The parsed data (usually a ``dict``).

    Raises:
        ConfigLoadError: if the file is not found, is not readable,
            or its content is not valid JSON/YAML.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    try:
        if not path.exists():
            raise ConfigLoadError(_("File not found"), path)

        with open(path, "r", encoding="utf-8") as f:
            if suffix in (".yaml", ".yml"):
                if yaml is None:
                    raise ConfigLoadError(
                        _("PyYAML is not installed. Run: pip install PyYAML"), path
                    )
                data = yaml.safe_load(f)
            elif suffix == ".json":
                data = json.load(f)
            else:
                raise ConfigLoadError(
                    _("Unsupported config format '{suffix}'. "
                      "Use .json, .yaml or .yml").format(suffix=suffix),
                    path,
                )

        if isinstance(data, dict):
            return data

        if data is None:
            raise ConfigLoadError(_("File is empty"), path)

        raise ConfigLoadError(
            _("Config must be an object, not {type}").format(type=type(data).__name__),
            path,
        )

    except json.JSONDecodeError as e:
        raise ConfigLoadError(_("JSON format error: {error}").format(error=e), path)
    except yaml.YAMLError as e:  # type: ignore[union-attr]
        raise ConfigLoadError(_("YAML format error: {error}").format(error=e), path)
    except PermissionError:
        raise ConfigLoadError(_("No permission to read the file"), path)
    except ConfigLoadError:
        raise
    except Exception as e:
        raise ConfigLoadError(_("Load error: {error}").format(error=e), path)


def load_json_data(config_file: str) -> Optional[Dict]:
    """Loads a JSON file (compatibility with the old API).

    On error, prints a message and returns ``None``.
    For new code, use :func:`load_config_file`.
    """
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ {_('JSON error: {error}').format(error=e)}")
        return None
    except Exception as error:
        print(f"❌ {_('Load error: {error}').format(error=error)}")
        return None


def save_json_data(data: Union[Dict, Set], output_path: str = None) -> bool:
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"✅ {_('Data saved to file {path}').format(path=output_path)}")
        return True
    except Exception as e:
        print(f"❌ {_('File save error: {error}').format(error=e)}")
        return False
