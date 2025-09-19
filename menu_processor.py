from typing import Dict, Set, List, Optional, Any
import json

from menu_flattener import FlatNode, Flattener
from menu_validator import MenuValidator
from data_types import DataTypeConfig
from common import load_json_data

class ProcessorError(Exception):
    """Выбрасывается при ошибках валидации меню"""
    def __init__(self, errors: List[str]):
        super().__init__("Menu validation failed")
        self.errors = errors


class MenuProcessor:

    def __init__(self, config:Dict, data_types_config: DataTypeConfig = None, validator: MenuValidator = None):

        self.config = config

        if data_types_config is None:
            self._data_types_config = DataTypeConfig(self.config.get('data_types'))
        else:
            self._data_types_config = data_types_config

        if validator is None:
            self._validator = MenuValidator(self.config.get('menu_schema'))
            self._validator.load_data_type_config(self._data_types_config)
        else:
            self._validator = validator

        self._flattener = Flattener(config=config, data_types_config=data_types_config)
        self._nodes = []
        self._menu_config = []
        self._menu_data = []
        self.errors = []
        self._leaf_items = {}
        self.first_item = None
        self.first_item_template = None

    def process(self, nodes: List[FlatNode]):
        self._nodes = nodes
        self._generate_leaf_items()

    def load_config(self, input_file: str = None):
        self._menu_config = load_json_data(self.config.get('menu_config'))
        self._menu_data = self._menu_config.get('menu', None)

        if self._menu_config is None:
            raise('Ошибка загрузки конфигурации меню')
        
        if not self._menu_data:
            raise('Отсутствует дерево меню')
        
        if not self._validate_config():
            raise('Ошибка валидации меню')
            
        if not self._flattern_menu():
            raise('Ошибка уплощения меню')

    def _validate_config(self)->bool:
        if self._menu_data == None:
            return False

        try:
            self.errors = self._validator.validate_menu(self._menu_config)
            if self.errors:
                for error in self.errors:
                    print(error)
                raise('Ошибка синтаксического разбора')
            return True
        except Exception as error:
            print(f"❌ Общая ошибка: {error}")
            return False

    def _flattern_menu(self)->bool:
        try:
            self._nodes = self._flattener.flatten(self._menu_data)
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
        
    def save_flattern_json(self, output_path: str = None)->bool:
        try:
            with open(self.config.get('output_flattern') if output_path is None else output_path, 'w', encoding='utf-8') as f:
                json.dump(self.get_template_nodes, f, indent=2, ensure_ascii=False)
                pass
            print(f"✅ Конфигурация сохранена в {output_path}")
        except Exception as e:
            print(f'❌ Ошибка сохранения файла: {e}')

    @property
    def get_unique_types(self) -> Dict[str, Dict] | None:
        if not self._nodes:
            return None
        return {
            type_name: self._data_types_config.get_by_type(type_name) 
            for type_name in {n.type for n in self._nodes if n.type is not None}
        }
    
    def get_unique_meta_list(self, meta_name:str)->List[str] | None:
        if not self._nodes:
            return None
        return  {n.type_info.get(meta_name) for n in self._nodes if n.type_info and n.type_info.get(meta_name, None) is not None}

    @property 
    def get_unique_categories(self)->Set[str] | None:
        if not self._nodes:
            return None
        return self.get_unique_meta_list('category')
        
    @property 
    def get_unique_medias(self)->Set[str] | None:
        if not self._nodes:
            return None
        return self.get_unique_meta_list('media')

    @property 
    def get_unique_media_types(self)->Set[str] | None:
        if not self._nodes:
            return None
        return self.get_unique_meta_list('media_type')
    
    @property
    def get_types_config(self):
        return self._data_types_config.get_config()
    
    @property
    def get_nodes(self)->Dict[str, FlatNode] | None:
        if not self._nodes:
            return None
        return {n.id: n for n in self._nodes if n.id != 'root'}
    
    @property
    def get_leafs(self)->Dict[str, FlatNode] |None:
        if not self._nodes:
            return None
        return {n.id: n for n in self._nodes if n.id != 'root' and n.first_child is None}
    
    @property
    def get_branches(self)->Dict[str, FlatNode] | None:
        if not self._nodes:
            return None
        return {n.id: n for n in self._nodes if n.id != 'root' and n.first_child is not None}
    
    @property
    def get_template_nodes(self)->Dict[str, Dict]|None:
        if not self._nodes:
            return None
        return {n.id: n.get_template_data for n in self._nodes if n.id != 'root'}

    @property
    def get_template_leafs(self)->Dict[str, Dict]|None:
        if not self._nodes:
            return None
        return {n.id: n.get_template_data for n in self._nodes if n.id != 'root' and n.first_child is None}

    @property
    def get_template_branches(self)->Dict[str, Dict]|None:
        if not self._nodes:
            return None
        return {n.id: n.get_template_data for n in self._nodes if n.id != 'root' and n.first_child is not None}

    @property
    def get_first_node(self)->str | None:
        for node in self._nodes:
            # Проверяем что все необходимые атрибуты существуют
            if (hasattr(node, 'prev_sibling') and 
                hasattr(node, 'parent') and 
                node.prev_sibling is None and 
                node.parent is not None and
                hasattr(node.parent, 'id') and
                node.parent.id == 'root'):
                return node.id
        return None

def main() -> bool:
    config = load_json_data('config/config.json')
    processor = MenuProcessor(config=config)
    processor.load_config()
    processor.save_flattern_json()

    for node in processor._nodes:
        print(node)

    print(processor.get_unique_categories)
    print(processor.get_unique_medias)
    print(processor.get_unique_media_types)

    return True


if __name__ == '__main__':
    main()