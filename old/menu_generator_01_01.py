#!/usr/bin/env python3
import inspect
import logging
import sys
import json
import os
from jinja2 import Environment, FileSystemLoader, Template

class JinjaMenuGenerator:
    def __init__(self, config_path, output={'c': 'otput/system_menu.c', 'h' : 'output/system_menu.h'}):
        self.output = output
        self.config_path = config_path
        self.config = None
        self.menu_items = {}
        self.menu_order = []
        
        self.env = Environment(
            loader=FileSystemLoader('templates'),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        
        self.env.filters['to_upper'] = lambda s: s.upper()
        self.env.filters['c_safe'] = lambda s: s.replace('"', '\\"')
        
    def load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            
            # Создаем словарь меню
            for item in self.config['menu_structure']:
                self.menu_items[item['id']] = item
            
            return True
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return False
    
    def validate_config(self):
        """Валидация конфигурации меню"""
        errors = []
        menu_ids = set(self.menu_items.keys())
        
        for item_id, item in self.menu_items.items():
            # Проверка first_child
            if item['first_child'] and item['first_child'] not in menu_ids:
                errors.append(f"Item '{item_id}': first_child '{item['first_child']}' does not exist")
            
            # Проверка next_sibling
            if item.get('next_sibling') and item['next_sibling'] not in menu_ids:
                errors.append(f"Item '{item_id}': next_sibling '{item['next_sibling']}' does not exist")
            
            # Проверка переменных
            if 'variable' in item and item['variable'] not in self.config['variables']:
                errors.append(f"Item '{item_id}': variable '{item['variable']}' not defined in variables")
            
            # Проверка callback
            if 'callback' in item and item['callback'] not in self.config['callbacks']:
                errors.append(f"Item '{item_id}': callback '{item['callback']}' not defined in callbacks")
        
        # Проверка наличия root элемента
        roots = [item for item in self.config['menu_structure'] if item['type'] == 'root']
        if len(roots) != 1:
            errors.append("Must have exactly one root menu item")
        
        if errors:
            print("❌ Configuration validation errors:")
            for error in errors:
                print(f"   - {error}")
            return False
        
        print("✅ Configuration validation passed")
        return True
    
    def _determine_menu_order(self):
        """Определяем порядок меню с улучшенной логикой"""
        try:
            root = next(item for item in self.config['menu_structure'] if item['type'] == 'root')
            self.menu_order.append(root['id'])
            
            queue = [root['id']]
            visited = set([root['id']])
            
            while queue:
                current_id = queue.pop(0)
                current_item = self.menu_items[current_id]
                
                # Добавляем первого ребенка
                if current_item['first_child'] and current_item['first_child'] not in visited:
                    child_id = current_item['first_child']
                    self.menu_order.append(child_id)
                    visited.add(child_id)
                    queue.append(child_id)
                
                # Добавляем siblings
                sibling_id = current_item.get('next_sibling')
                while sibling_id and sibling_id not in visited:
                    self.menu_order.append(sibling_id)
                    visited.add(sibling_id)
                    queue.append(sibling_id)
                    sibling_id = self.menu_items[sibling_id].get('next_sibling')
            
            # Проверяем, все ли элементы включены
            all_ids = set(self.menu_items.keys())
            missing_ids = all_ids - visited
            if missing_ids:
                print(f"⚠️  Warning: {len(missing_ids)} menu items not reachable from root: {missing_ids}")
                
        except Exception as e:
            print(f"❌ Error determining menu order: {e}")
            raise
    
    def _build_navigation_context(self):
        """Строим контекст для шаблонов с улучшенной логикой поиска parent"""
        context = {
            'config': self.config,
            'menu_items': self.menu_items,
            'menu_order': self.menu_order,
            'nav_table': []
        }
        
        # Предварительно находим всех родителей для каждого элемента
        parent_map = {}
        for menu_id in self.menu_order:
            item = self.menu_items[menu_id]
            
            # Ищем parent через first_child
            for potential_parent_id, potential_parent in self.menu_items.items():
                if potential_parent['first_child'] == menu_id:
                    parent_map[menu_id] = potential_parent_id
                    break
            
            # Ищем parent через next_sibling chain
            if menu_id not in parent_map:
                for potential_parent_id, potential_parent in self.menu_items.items():
                    sibling_id = potential_parent.get('next_sibling')
                    while sibling_id:
                        if sibling_id == menu_id:
                            parent_map[menu_id] = potential_parent_id
                            break
                        sibling_id = self.menu_items[sibling_id].get('next_sibling')
                    if menu_id in parent_map:
                        break
        
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
            
            # Находим parent используя pre-calculated map
            parent_handler = 'NULL'
            if menu_id in parent_map:
                parent_handler = f'menu_{parent_map[menu_id]}_handler'
            nav_item['parent_handler'] = parent_handler
            
            # Находим previous sibling
            prev_sibling = 'NULL'
            for other_id, other_item in self.menu_items.items():
                if other_item.get('next_sibling') == menu_id:
                    prev_sibling = f'menu_{other_id}_handler'
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
        if not self.load_config():
            sys.exit(1)
        
        if not self.validate_config():
            sys.exit(1)
        
        self._determine_menu_order()
        context = self._build_navigation_context()
        
        # Генерация файлов
        try:
            header_template = self.env.get_template('menu.h.j2')
            source_template = self.env.get_template('menu.c.j2')
            
            output_c = self.output['c']
            output_h = self.output['h']

            os.makedirs(output_c, exist_ok=True)
            os.makedirs(output_h, exist_ok=True)
            
            with open(f"{output_h}/{self.config['menu_name']}.h", 'w') as f:
                f.write(header_template.render(**context))
            
            with open(f"{output_c}/{self.config['menu_name']}.c", 'w') as f:
                f.write(source_template.render(**context))
            
            print(f"✅ Generated: {output_h}/{self.config['menu_name']}.h")
            print(f"✅ Generated: {output_c}/{self.config['menu_name']}.c")
            print(f"📊 Menu items: {len(self.menu_order)}")
            print(f"💾 Estimated size: ~{len(self.menu_order) * 24} bytes")
            
        except Exception as e:
            print(f"❌ Error generating code: {e}")
            sys.exit(1)

if __name__ == "__main__":
    config_file = "config/menu_config.json"
    output = {
        'c' : '../menu/src/',
        'h' : '../menu/src/include/'
    }

    
    generator = JinjaMenuGenerator(config_file, output)
    generator.generate_code()