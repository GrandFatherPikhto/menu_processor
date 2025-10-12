import inspect
import logging
import json
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Environment, Template, TemplateSyntaxError, UndefinedError, TemplateError
from jinja2.ext import Extension, debug
from typing import Dict, Set, List, Optional, Any
from common import load_json_data

from menu_processor import MenuProcessor
from menu_config import MenuConfig

class MenuGenerator:
    def __init__(self, config_json):
        self._processor = MenuProcessor(config_json)
        self._config:MenuConfig = self._processor.config
        self._env = Environment(
            loader=FileSystemLoader(str(self._config.templates_path)),
            trim_blocks=True,
            lstrip_blocks=True,
            extensions=['jinja2.ext.debug']
        )
        self._files = self._config.generation_files
        self._context = {}

        self._generate()

    def _generate(self):
        self._build_template_context()
        self._generate_code()

    def save_flatterned_menu(self, output_path: str | None = None):
        self._processor.save_flattern_json(output_path)
    
    def _build_template_context(self):
        self._context = {
            'menu': self._processor.menu,
            'first': self._processor.first,
            'leafs': self._processor.leafs,
            'categories': self._processor.categories,
            'functions': self._processor.functions,
            'wrap_by_name_functions': self._config.wrap_by_name_functions,
            'enable_node_names': self._config.enable_node_names,
            'include_files': self._config.include_files
        }


    def _generate_code(self):
        if self._files is not None:
            for template, output in self._files.items():
                print(f"Generate: {template} => {output}")
                self._generate_file(template, output, self._context)

    def _generate_file(self, template_name: str, output_path: str | Path, template_data):
        """Генерация конкретного файла"""
        print(f'Generate from {template_name} to {output_path}')
        
        try:
            # Загрузка шаблона
            template = self._env.get_template(str(template_name))
            
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

def main(config_file:str):
    generator = MenuGenerator(config_file)

if __name__ == '__main__':
    main('./config/config.json')
