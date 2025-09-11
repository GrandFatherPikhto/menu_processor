from jinja2 import Environment, FileSystemLoader, Template
import os
from typing import Dict, List, Any
from enum import Enum

class MenuState(Enum):
    NAVIGATION = 0
    EDIT = 1

class MenuType(Enum):
    ROOT = "root"
    SUBMENU = "submenu" 
    ACTION_BOOL = "action_bool"
    ACTION_INT = "action_int"
    ACTION_INT_FACTOR = "action_int_factor"
    ACTION_CALLBACK = "action_callback"
    ACTION_FLOAT = "action_float"
    ACTION_INT_STEP = "action_int_step"
    ACTION_FLOAT_STEP = "action_float_step"

class MenuGenerator:
    def __init__(self, processor):
        """
        Инициализация генератора меню
        
        Args:
            processor: Экземпляр MenuProcessor с уплощенными данными и конфигурацией
        """
        self.processor = processor
        self.flattened_menu = processor.get_flattened_menu()
        self.config = processor.get_config()
        
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
        self._generate_file('h', template_data)
        
        # Генерация .c файла  
        self._generate_file('c', template_data)
        
        print("✅ Генерация завершена!")
    
    def _prepare_template_data(self):
        """Подготовка данных для шаблонов Jinja2"""
        # Фильтруем root из меню
        menu_items = {k: v for k, v in self.flattened_menu.items() if k != 'root'}
        
        return {
            'menu_items': menu_items,
            'menu_states': {
                'NAVIGATION': 0,
                'EDIT': 1
            },
            'menu_types': {
                'ROOT': 'root',
                'MENU': 'submenu',
                'ACTION_BOOL': 'action_bool',
                'ACTION_INT': 'action_int',
                'ACTION_INT_FACTOR': 'action_int_factor',
                'ACTION_CALLBACK': 'action_callback',
                'ACTION_FLOAT': 'action_float',
                'ACTION_INT_STEP': 'action_int_step',
                'ACTION_FLOAT_STEP': 'action_float_step'
            },
            'first_menu_id': self._get_first_menu_id(),
            'config': {
                'templates': self.config.get_templates(),
                'output_files': self.config.get_output_files()
            }
        }
    
    def _get_first_menu_id(self):
        """Получить ID первого элемента меню (после root)"""
        root = self.flattened_menu.get('root', {})
        first_child_id = root.get('first_child')
        if first_child_id and first_child_id in self.flattened_menu:
            return first_child_id.upper()
        return 'SETTINGS'  # fallback
    
    def _generate_file(self, file_type: str, template_data: Dict):
        """Генерация конкретного файла"""
        template_path = self.config.get_template_path(file_type)
        output_path = self.config.get_output_path(file_type)
        
        if not template_path or not output_path:
            print(f"⚠️  Не указаны пути для {file_type} файла")
            return
        
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
            print(f"❌ Ошибка генерации {file_type} файла: {e}")
