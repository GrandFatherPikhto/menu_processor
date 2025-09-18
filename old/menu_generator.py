#!/usr/bin/env python3
import inspect
import logging
import json
import os
from jinja2 import Environment, FileSystemLoader, Template

class JinjaMenuGenerator:
    def __init__(self, config_path, output_c_path='output', output_h_path='output'):
        self.output_c_path = output_c_path
        self.output_h_path = output_h_path
        self.config_path = config_path
        self.config = None
        self.menu_items = {}
        self.menu_order = []
        logging.basicConfig(format='%(filename)s:%(lineno)d - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Настройка Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader('templates'),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        
        # Добавляем кастомные фильтры
        self.env.filters['to_upper'] = lambda s: s.upper()
        self.env.filters['c_safe'] = lambda s: s.replace('"', '\\"')
        
    def load_config(self):
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
        
        # Создаем словарь меню
        for item in self.config['menu_structure']:
            self.menu_items[item['id']] = item
        
        self._determine_menu_order()
    
    def _determine_menu_order(self):
        """Определяем порядок меню для компиляции"""
        root = next(item for item in self.config['menu_structure'] if item['type'] == 'root')
        self.menu_order.append(root['id'])
        
        queue = [root['id']]
        while queue:
            current_id = queue.pop(0)
            current_item = self.menu_items[current_id]
            
            if current_item['first_child']:
                child_id = current_item['first_child']
                if child_id not in self.menu_order:
                    self.menu_order.append(child_id)
                    queue.append(child_id)
            
            sibling_id = current_item.get('next_sibling')
            while sibling_id and sibling_id not in self.menu_order:
                self.menu_order.append(sibling_id)
                queue.append(sibling_id)
                self.logger.info(f"sibling_id: {sibling_id}")
                sibling_id = self.menu_items[sibling_id].get('next_sibling')
    
    def _build_navigation_context(self):
        """Строим контекст для шаблонов"""
        context = {
            'config': self.config,
            'menu_items': self.menu_items,
            'menu_order': self.menu_order,
            'nav_table': []
        }
        
        # Строим таблицу навигации
        for menu_id in self.menu_order:
            item = self.menu_items[menu_id]
            nav_item = {
                'id': item['id'],
                'title': item['title'],
                'type': item['type'],
                'enter_handler': f'menu_{item["id"]}_handler',
                'first_child': f'menu_{item["first_child"]}_handler' if item['first_child'] else 'NULL',
                'next_sibling': f'menu_{item["next_sibling"]}_handler' if item.get('next_sibling') else 'NULL',
                'data_ptr': f'&{item["variable"]}' if 'variable' in item else 'NULL'
            }
            
            # Находим parent
            parent_handler = 'NULL'
            for other_item in self.config['menu_structure']:
                if other_item['first_child'] == item['id'] or (
                    other_item.get('next_sibling') == item['id'] and other_item['id'] != item['id']):
                    parent_handler = f'menu_{other_item["id"]}_handler'
                    break
            nav_item['parent_handler'] = parent_handler
            
            # Находим previous sibling
            prev_sibling = 'NULL'
            for other_item in self.config['menu_structure']:
                if other_item.get('next_sibling') == item['id']:
                    prev_sibling = f'menu_{other_item["id"]}_handler'
                    break
            nav_item['prev_sibling'] = prev_sibling
            
            # Конфигурация
            if item['type'] in ['action_int', 'action_float']:
                nav_item['config'] = {
                    'min': item.get('min', 0),
                    'max': item.get('max', 0),
                    'step': item.get('step', 1)
                }
            elif 'callback' in item:
                nav_item['callback'] = item['callback']
            
            context['nav_table'].append(nav_item)
        
        return context
    
    def generate_code(self):
        self.load_config()
        context = self._build_navigation_context()
        
        # Генерация header
        header_template = self.env.get_template('menu.h.j2')
        header_content = header_template.render(**context)
        
        # Генерация source
        source_template = self.env.get_template('menu.c.j2')
        source_content = source_template.render(**context)
        
        # Создаем output directory если нужно
        os.makedirs(self.output_c_path, exist_ok=True)
        os.makedirs(self.output_h_path, exist_ok=True)
        
        # Сохраняем файлы
        output_header = f"{self.output_h_path}/{self.config['menu_name']}.h"
        output_source = f"{self.output_c_path}/{self.config['menu_name']}.c"
        
        with open(output_header, 'w') as f:
            f.write(header_content)
        
        with open(output_source, 'w') as f:
            f.write(source_content)
        
        print(f"✅ Generated: {output_header}")
        print(f"✅ Generated: {output_source}")
        print(f"📊 Menu items: {len(self.menu_order)}")
        print(f"💾 Estimated size: ~{len(self.menu_order) * 24} bytes")

def check_config(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    menu_ids = {item['id'] for item in config['menu_structure']}
    variable_names = set(config['variables'].keys())
    callback_names = set(config['callbacks'])
    
    print("🔍 Configuration Check:")
    print(f"Menu items: {len(menu_ids)}")
    print(f"Variables: {len(variable_names)}")
    print(f"Callbacks: {len(callback_names)}")
    
    # Проверка ссылок
    for item in config['menu_structure']:
        if item.get('first_child') and item['first_child'] not in menu_ids:
            print(f"❌ {item['id']}: first_child '{item['first_child']}' not found")
        if item.get('next_sibling') and item['next_sibling'] not in menu_ids:
            print(f"❌ {item['id']}: next_sibling '{item['next_sibling']}' not found")
        if 'variable' in item and item['variable'] not in variable_names:
            print(f"❌ {item['id']}: variable '{item['variable']}' not defined")
        if 'callback' in item and item['callback'] not in callback_names:
            print(f"❌ {item['id']}: callback '{item['callback']}' not defined")

if __name__ == "__main__":
    generator = JinjaMenuGenerator("./config/menu_config.json", '../menu/src/', '../menu/src/include/')
    generator.generate_code()