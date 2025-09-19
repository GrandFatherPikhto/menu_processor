import inspect
import logging
import json
import os
from jinja2 import Environment, FileSystemLoader, Environment, Template, TemplateSyntaxError, UndefinedError, TemplateError
from jinja2.ext import Extension, debug
from typing import Dict, Set, List, Optional, Any
from common import load_json_data

from menu_processor import MenuProcessor
from data_types import DataTypeConfig

class MenuGenerator:
    def __init__(self, config):
        self.config = config
        self._data_types_config = DataTypeConfig(self.config.get('data_types'))

        self._processor = MenuProcessor(config=self.config, data_types_config=self._data_types_config)
        
        self.env = Environment(
            loader=FileSystemLoader(self.config.get('templates')),  # Ищем шаблоны в текущей директории
            trim_blocks=True,
            lstrip_blocks=True,
            extensions=['jinja2.ext.debug']
        )

        self.context = {}
        self.files = load_json_data(config.get('generate_files'))

    def load_menu(self, menu_path:str = None)->bool:
        try:
            self._processor.load_config(self.config.get('menu_config') if menu_path is None else menu_path)
            return True
        except Exception as e:
            print(f'Ошибка загрузки конфигурации {e}')        
            return False

    def generate(self):
        self._build_template_context()
        self._generate_code()

    def save_flatterned_menu(self, output_path: str = None):
        self._processor.save_flattern_json(self.config.get('output_flattern') if output_path is None else output_path)
    
    def _build_template_context(self):
        self.context = {
            'menu_items': self._processor.get_template_nodes,
            'first_item_id': self._processor.get_first_node,
            'leaf_items': self._processor.get_template_leafs,
            'unique_types': self._processor.get_unique_types,
            'data_types': self._data_types_config.get_config
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

def main():
    config = load_json_data('config/config.json')

    generator = MenuGenerator(config=config)
    generator.load_menu()
    generator.save_flatterned_menu()
    generator.generate()

if __name__ == '__main__':
    main()
