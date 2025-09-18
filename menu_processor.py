from typing import Dict, Set, List, Optional, Any
import json

from menu_flattener import FlatNode, Flattener
from menu_validator import MenuValidator, ParserError

class ProcessorError(Exception):
    """Выбрасывается при ошибках валидации меню"""
    def __init__(self, errors: List[str]):
        super().__init__("Menu validation failed")
        self.errors = errors


class MenuProcessor:

    def __init__(self):
        self.validator = MenuValidator()
        self.flattener = Flattener()
        self.menu_config = []
        self.menu_data = []
        self.errors = []
        self.nodes = []
        self.leaf_items = []
        self.template_items = []
        self.unique_data_types = []
        self.template_items = []
        self.first_item = None
        self.first_item_template = None

    def process(self, nodes: List[FlatNode]):
        self.flattern_nodes = nodes
        self._generate_unique_data_types()
        self._create_leaf_list()
        self._generate_template_items()

    def _generate_unique_data_types(self):
        self.unique_data_types.clear()
        for node in self.flattern_nodes:
            if node.data_type not in self.unique_data_types:
                self.unique_data_types.append(node.data_type)

    def _create_leaf_list(self):
        self.leaf_items.clear()
        for node in self.flattern_nodes:
            if node.first_child is None:
                self.leaf_items.append(node)

    def load_config(self, input_file: str)->bool:
        res = self._load_config(input_file)
        if res == False:
            return False
        res = self._validate_config()
        if res == False:
            return False
        res = self._flattern_menu()
        if res == False:
            return False
        self._generate_template_items()
        self._generate_unique_data_types()

        return True

    def _load_config(self, input_file: str)->bool:
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                self.menu_config = json.load(f)
                self.menu_data = self.menu_config.get('menu', None)
                return (self.menu_config is not None 
                        and self.menu_data is not None
                        and len(self.menu_data) != 0)
            
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка JSON: {e}")
            return False
        except Exception as error:
            print(f"❌ Ошибка загрузки: {error}")
            return False

    def _validate_config(self)->bool:
        if self.menu_data == None:
            return False

        try:
            self.validator.validate(self.menu_data)
            return True
        except ParserError as error:
            print(f"❌ Ошибка синтаксиса:")
            for err in error.errors:
                print(f"   - {err}")
            return False
        except Exception as error:
            print(f"❌ Общая ошибка: {error}")
            return False

    def _flattern_menu(self)->bool:
        try:
            self.flattern_nodes = self.flattener.flatten(self.menu_data)
            return True
        except Exception as e:
            print(f"❌ Ошибка уплощения меню: {e}")
            return False

    def _process_menu_data(data: List[Dict])->List[FlatNode] | None:
        preproc = MenuProcessor()
        try:
            preproc.process(data)
            return None
        except Exception as e:
            print(f"❌ Ошибка уплощения меню: {e}")
            return None
        
    def _generate_template_items(self):
        self.template_items.clear()
        self.first_item = None
        self.first_item_template = None
        for node in self.flattern_nodes:
            if node.id == 'root':
                continue
            if self.first_item == None:
                self.first_item = node
                self.first_item_template = node.get_template_data
            self.template_items.append(node.get_template_data)

    def save_template_json(self, output_path: str)->bool:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.template_items, f, indent=2, ensure_ascii=False)
            print(f"✅ Конфигурация сохранена в {output_path}")
        except Exception as e:
            print(f'❌ Ошибка сохранения файла: {e}')



def main(input_file, output_file) -> bool:
    processor = MenuProcessor()
    processor.load_config(input_file)
    processor.save_template_json(output_file)
    return True

if __name__ == '__main__':
    main('config/menu.json', 'output/template.json')