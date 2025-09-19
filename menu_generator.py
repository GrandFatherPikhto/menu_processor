import inspect
import logging
import json
import os
from jinja2 import Environment, FileSystemLoader, Environment, Template, TemplateSyntaxError, UndefinedError, TemplateError
from jinja2.ext import Extension, debug

from menu_processor import MenuProcessor
import constants

FILES = {
    "struct": {
        "name": "struct",
        "template" : {
            "header": "struct.h.j2",
            "source": "struct.c.j2",
        },
        "output": {
            "header" : "../../CCPP/STM32/GeneratirveMenu/menu/src/include/menu_struct.h",
            "source" : "../../CCPP/STM32/GeneratirveMenu/menu/src/menu_struct.c",
        }
    },
    "config": {
        "name": "config",
        "template" : {
            "header": "config.h.j2",
            "source": "config.c.j2",
        },
        "output": {
            "header" : "../../CCPP/STM32/GeneratirveMenu/menu/src/include/menu_config.h",
            "source" : "../../CCPP/STM32/GeneratirveMenu/menu/src/menu_config.c",
        }
    },
    "engine": {
        "name": "engine",
        "template" : {
            "header": "engine.h.j2",
            "source": "engine.c.j2",
        },
        "output": {
            "header" : "../../CCPP/STM32/GeneratirveMenu/menu/src/include/menu_engine.h",
            "source" : "../../CCPP/STM32/GeneratirveMenu/menu/src/menu_engine.c",
        }
    },
}

class MenuGenerator:
    def __init__(self):
        self.context = {}
        self.menu_items = {}
        self.leaf_items = {}
        self.unique_data_types = {}

        self.processor = MenuProcessor()
        self.env = Environment(
            loader=FileSystemLoader('./templates/'),  # Ищем шаблоны в текущей директории
            trim_blocks=True,
            lstrip_blocks=True,
            extensions=['jinja2.ext.debug']
        )

        self.files = FILES


    def load_config(self, config_path)->bool:
        try:
            self.processor.load_config(config_path)
            return True
        except Exception as e:
            print(f'Ошибка загрузки конфигурации {e}')        
            return False

    def generate(self):
        self._generate_menu_items()
        self._generate_leaf_items()
        self._generate_unique_data_types()
        self._build_template_context()
        self._generate_code()

    def save_template(self, output_path: str):
        self.processor.save_template_json(output_path)

    def _generate_menu_items(self):
        self.menu_items.clear()
        for node in self.processor.flattern_nodes:
            if node.id == 'root':
                continue
            self.menu_items[node.id] = node.get_template_data
    
    def _generate_leaf_items(self):
        self.leaf_items.clear()
        for node in self.processor.flattern_nodes:
            if node.first_child is None and node.id != 'root' and node.data_type is not None:
                self.leaf_items[node.id] = node.get_template_data
    
    """Сейчас генерация типа callback отключена!!!"""
    def _generate_unique_data_types(self):
        self.unique_data_types.clear()

        for node in self.processor.flattern_nodes:
            if node.data_type is None:
                continue
            if constants.DATA_TYPES.get(node.data_type, None) is not None:
                if not self.unique_data_types or node.data_type not in self.unique_data_types.keys():
                    self.unique_data_types[node.data_type] = constants.DATA_TYPES[node.data_type]

    def _build_template_context(self):
        self.context = {
            'menu_items': self.menu_items,
            'first_item_id': self.processor.first_item.id,
            'leaf_items': self.leaf_items,
            'unique_data_types': self.unique_data_types,
            'data_types': constants.DATA_TYPES
        }

    def _generate_code(self):
        for name in self.files.keys():
            print('Generate: ' + name)
            self._generate_file(self.files[name]["template"]["header"], self.files[name]["output"]["header"], self.context)
            self._generate_file(self.files[name]["template"]["source"], self.files[name]["output"]["source"], self.context)

    def _generate_file(self, template_path: str, output_path: str, template_data):
        """Генерация конкретного файла"""
        print(f'Generate from {template_path} to {output_path}')
        
        try:
            # Загрузка шаблона
            template = self.env.get_template(template_path)
            
            # Рендеринг
            content = template.render(**template_data)
            
            # Сохранение
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Сгенерирован {output_path}")
            
        except TemplateSyntaxError as e:
            error_string = str(e)  # Get the error message as a string
            print(f"❌ Template Syntax Error: {error_string}")
        except UndefinedError as e:
            error_string = str(e)
            print(f"❌ Undefined Variable Error: {error_string}")
        except TemplateError as e:
            error_string = str(e)
            print(f"❌ General Template Error: {error_string}")
        except Exception as e:
            print(f"❌ Ошибка генерации {output_path} файла: {e}")


def main(config_path:str, output_path: str):
    generator = MenuGenerator()
    generator.load_config(config_path)
    generator.save_template(output_path)
    generator.generate()

if __name__ == '__main__':
    main('config/menu.json', 'config/template.json')
