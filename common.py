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
