#!/usr/bin/env python3
import json
import os
import sys
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError
from pathlib import Path

class AdvancedMenuGenerator:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = None
        self.menu_items = {}
        self.errors = []
        self.warnings = []
        
        self.env = Environment(
            loader=FileSystemLoader('templates'),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        
    def load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON syntax error at line {e.lineno}: {e.msg}")
            return False
        except Exception as e:
            self.errors.append(f"Error loading config: {e}")
            return False
    
    def validate_config(self):
        """Полная валидация конфигурации"""
        if not self.config:
            return False
            
        # Проверка обязательных полей
        required_fields = ['menu_name', 'menu_structure']
        for field in required_fields:
            if field not in self.config:
                self.errors.append(f"Missing required field: {field}")
        
        # Создаем словарь меню и проверяем уникальность ID
        menu_ids = set()
        for i, item in enumerate(self.config['menu_structure']):
            if 'id' not in item:
                self.errors.append(f"Menu item at index {i} missing 'id' field")
                continue
                
            if item['id'] in menu_ids:
                self.errors.append(f"Duplicate menu ID: {item['id']}")
            menu_ids.add(item['id'])
            
            self.menu_items[item['id']] = item
        
        # Проверка переменных
        if 'variables' in self.config:
            for var_name, var_config in self.config['variables'].items():
                if 'type' not in var_config:
                    self.errors.append(f"Variable '{var_name}' missing 'type'")
                if 'default' not in var_config:
                    self.errors.append(f"Variable '{var_name}' missing 'default'")
        
        # Проверка связности
        self._check_connectivity()
        
        return len(self.errors) == 0
    
    def _check_connectivity(self):
        """Проверка связности меню"""
        # Находим root элемент
        roots = [item for item in self.config['menu_structure'] if item.get('type') == 'root']
        if len(roots) != 1:
            self.errors.append("Must have exactly one root menu item")
            return
            
        root = roots[0]
        visited = set()
        queue = [root['id']]
        
        # Обход в ширину для проверки связности
        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue
                
            visited.add(current_id)
            current_item = self.menu_items[current_id]
            
            # Добавляем first_child
            if current_item.get('first_child'):
                child_id = current_item['first_child']
                if child_id not in self.menu_items:
                    self.errors.append(f"Item '{current_id}': first_child '{child_id}' not found")
                else:
                    queue.append(child_id)
            
            # Добавляем next_sibling
            if current_item.get('next_sibling'):
                sibling_id = current_item['next_sibling']
                if sibling_id not in self.menu_items:
                    self.errors.append(f"Item '{current_id}': next_sibling '{sibling_id}' not found")
                else:
                    queue.append(sibling_id)
        
        # Проверяем недостижимые элементы
        all_ids = set(self.menu_items.keys())
        unreachable = all_ids - visited
        if unreachable:
            self.warnings.append(f"Unreachable menu items: {unreachable}")
    
    def generate_code(self):
        if not self.load_config():
            return False
            
        if not self.validate_config():
            return False
            
        # Создаем выходные директории
        output_header = self.config.get('output', {}).get('header_file', 'output/menu.h')
        output_source = self.config.get('output', {}).get('source_file', 'output/menu.c')
        
        os.makedirs(os.path.dirname(output_header), exist_ok=True)
        os.makedirs(os.path.dirname(output_source), exist_ok=True)
        
        try:
            # Генерация header
            header_template = self.env.get_template('menu.h.j2')
            header_content = header_template.render(config=self.config, menu_items=self.menu_items)
            
            with open(output_header, 'w') as f:
                f.write(header_content)
            
            # Генерация source
            source_template = self.env.get_template('menu.c.j2')
            source_content = source_template.render(config=self.config, menu_items=self.menu_items)
            
            with open(output_source, 'w') as f:
                f.write(source_content)
                
            print(f"✅ Successfully generated:")
            print(f"   Header: {output_header}")
            print(f"   Source: {output_source}")
            
            if self.warnings:
                print("\n⚠️  Warnings:")
                for warning in self.warnings:
                    print(f"   - {warning}")
                    
            return True
            
        except TemplateSyntaxError as e:
            self.errors.append(f"Template syntax error at line {e.lineno}: {e.message}")
            return False
        except Exception as e:
            self.errors.append(f"Error generating code: {e}")
            return False
    
    def print_errors(self):
        if self.errors:
            print("❌ Errors:")
            for error in self.errors:
                print(f"   - {error}")

def main():
    # if len(sys.argv) < 2:
    #     print("Usage: python menu_generator.py <config_file.json>")
    #     sys.exit(1)
    
    # config_file = sys.argv[1]
    # if not os.path.exists(config_file):
    #     print(f"Error: Config file '{config_file}' not found")
    #     sys.exit(1)
    config_file='config/menu_config.json'
    generator = AdvancedMenuGenerator(config_file)
    if generator.generate_code():
        print("🎉 Generation completed successfully!")
    else:
        generator.print_errors()
        sys.exit(1)

if __name__ == "__main__":
    main()