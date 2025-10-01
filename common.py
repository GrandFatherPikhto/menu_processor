import json
import os
from typing import Dict, Set, List, Optional, Any

def load_json_data(config_file: str)->Dict | None:
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка JSON: {e}")
        return None
    except Exception as error:
        print(f"❌ Ошибка загрузки: {error}")
        return None

def save_json_data(data: Dict | Set, output_path: str = None)->bool:
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            pass
        print(f"✅ Данные сохранены в файл {output_path}")
        return True
    except Exception as e:
        print(f'❌ Ошибка сохранения файла: {e}')
        return False
