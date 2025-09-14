from jinja2 import Environment, FileSystemLoader, Template
import os
from typing import Dict, List, Any
from enum import Enum

from menu_config import MenuConfig
from menu_processor import MenuProcessor

class MenuState(Enum):
    NAVIGATION = 0
    EDIT = 1

class MenuType(Enum):
    ROOT = "root"
    SUBMENU = "action_menu" 
    ACTION_BOOL = "action_bool"
    ACTION_INT = "action_int"
    ACTION_INT_FACTOR = "action_int_factor"
    ACTION_CALLBACK = "action_callback"
    ACTION_FLOAT = "action_float"
    ACTION_FLOAT_FACTOR = "action_float_factor"

class MenuGenerator:
    def __init__(self, processor):
        """
        Инициализация генератора меню
        
        Args:
            processor: Экземпляр MenuProcessor с уплощенными данными и конфигурацией
        """
        self.processor : 'MenuProcessor' = processor
        self.flattened_menu = processor.get_flattened_menu()
        self.config : 'MenuConfig' = processor.get_config()
        
        # Настройка Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader('.'),  # Ищем шаблоны в текущей директории
            trim_blocks=True,
            lstrip_blocks=True
        )
        
    def generate(self):
        """Основной метод генерации файлов"""
        print("🔧 Генерация меню...")
        
        # Подготовка данных для шаблонов
        template_data = self._prepare_template_data()
        
        # Генерация .h файла
        template_path = self.config.get_template_path('menu_header')
        output_path = self.config.get_output_path('menu_header')

        self._generate_file(template_path, output_path, template_data)
        
        # Генерация .c файла  
        template_path = self.config.get_template_path('menu_source')
        output_path = self.config.get_output_path('menu_source')
        self._generate_file(template_path, output_path, template_data)
        
        print("✅ Генерация завершена!")
    
    def _prepare_template_data(self):
        """Подготовка данных для шаблонов Jinja2"""
        # Фильтруем root из меню
        menu_items = {k: v for k, v in self.flattened_menu.items() if k != 'root'}
        
        return {
            'includes' : self.processor.get_includes(),
            'menu_items': menu_items,
            'menu_states': {
                'NAVIGATION': 0,
                'EDIT': 1
            },
            'menu_types': {
                'ROOT': 'root',
                'ACTION_MENU': 'action_menu',
                'ACTION_BOOL': 'action_bool',
                'ACTION_INT': 'action_int',
                'ACTION_INT_FACTOR': 'action_int_factor',
                'ACTION_FLOAT': 'action_float',
                'ACTION_FLOAT_FACTOR': 'action_float_factor',
                'ACTION_CALLBACK': 'action_callback',
            },
            'first_menu_id': self._get_first_menu_id(),
            'config': {
                'templates': self.config.get_templates(),
                'output_files': self.config.get_output_files()
            },
            'event_cb': self.config.get_callback('event_cb'),
            'display_cb' : self.config.get_callback('display_cb')
        }
    
    def _get_first_menu_id(self):
        """Получить ID первого элемента меню (после root)"""
        root = self.flattened_menu.get('root', {})
        first_child_id = root.get('first_child')
        if first_child_id and first_child_id in self.flattened_menu:
            return first_child_id.upper()
        return 'SETTINGS'  # fallback
    
    def _generate_file(self, template_path: str, output_path: str, template_data: Dict):
        """Генерация конкретного файла"""
        
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
            
        except Exception as e:
            print(f"❌ Ошибка генерации {output_path} файла: {e}")
