import json
from collections import deque
import sys

# ООП подход для вашей задачи с меню
class MenuValidator:
    def __init__(self):
        self.errors = []
        self.valid_types = {'root', 'submenu', 'action_int', 
                           'action_int_factor', 'action_callback', 'action_bool'}
    
    def validate_node(self, node, path=None, line_info=None):
        if path is None:
            path = []
        
        current_path = path + [node.get('name', 'unknown')]
        
        # Проверка обязательных полей
        if 'name' not in node:
            self._add_error(f"Отсутствует поле 'name'", current_path, line_info)
        
        if 'type' not in node:
            self._add_error(f"Отсутствует поле 'type'", current_path, line_info)
        elif node['type'] not in self.valid_types:
            self._add_error(f"Неверный тип '{node['type']}'", current_path, line_info)
        
        # Проверка специфичных полей по типу
        self._validate_type_specific_fields(node, current_path, line_info)
        
        # Рекурсивная проверка детей
        for child in node.get('children', []):
            self.validate_node(child, current_path, line_info)
    
    def _validate_type_specific_fields(self, node, path, line_info):
        type_validators = {
            'action_int': self._validate_action_int,
            'action_int_factor': self._validate_action_int_factor,
            'action_callback': self._validate_action_callback,
            'action_bool': self._validate_action_bool
        }
        
        validator = type_validators.get(node.get('type'))
        if validator:
            validator(node, path, line_info)
    
    def _validate_action_int(self, node, path, line_info):
        required_fields = ['min', 'max', 'default']
        for field in required_fields:
            if field not in node:
                self._add_error(f"Отсутствует поле '{field}' для action_int", path, line_info)
    
    def _validate_action_int_factor(self, node, path, line_info):
        required_fields = ['min', 'max', 'default', 'factors', 'default_factor_idx']
        for field in required_fields:
            if field not in node:
                self._add_error(f"Отсутствует поле '{field}' для action_int_factor", path, line_info)
    
    def _validate_action_callback(self, node, path, line_info):
        if 'callback' not in node:
            self._add_error("Отсутствует поле 'callback' для action_callback", path, line_info)
    
    def _validate_action_bool(self, node, path, line_info):
        if 'default' not in node:
            self._add_error("Отсутствует поле 'default' для action_bool", path, line_info)
    
    def _add_error(self, message, path, line_info):
        error_msg = f"{' -> '.join(path)}: {message}"
        if line_info:
            error_msg += f" (строка {line_info})"
        self.errors.append(error_msg)
    
    def get_errors(self):
        return self.errors


class MenuFlattener:
    def __init__(self):
        self.flattened = {}
    
    def flatten(self, menu_data):
        from collections import deque
        
        queue = deque([(menu_data['menu'][0], None, None)])
        
        while queue:
            node, parent_id, prev_sibling_id = queue.popleft()
            self._process_node(node, parent_id, prev_sibling_id)
            
            # Добавляем детей в очередь
            children = node.get('children', [])
            if children:
                prev_id = None
                for child in children:
                    child_id = child['name'].lower().replace(' ', '_')
                    queue.append((child, self._get_node_id(node), prev_id))
                    prev_id = child_id
        
        self._add_sibling_links()
        return self.flattened
    
    def _process_node(self, node, parent_id, prev_sibling_id):
        node_id = self._get_node_id(node)
        
        item = {
            'id': node_id,
            'title': node['name'],
            'type': node['type']
        }
        
        if parent_id:
            item['parent'] = parent_id
        if prev_sibling_id:
            item['prev_sibling'] = prev_sibling_id
        
        # Добавляем специфичные поля
        self._add_type_specific_fields(item, node)
        
        self.flattened[node_id] = item
    
    def _get_node_id(self, node):
        return node['name'].lower().replace(' ', '_')
    
    def _add_type_specific_fields(self, item, node):
        type_processors = {
            'action_int': lambda i, n: i.update({
                'min': n['min'], 'max': n['max'], 'default': n['default']
            }),
            'action_int_factor': lambda i, n: i.update({
                'min': n['min'], 'max': n['max'], 'default': n['default'],
                'factors': n['factors'], 'default_factor_idx': n['default_factor_idx']
            }),
            'action_callback': lambda i, n: i.update({'callback': n['callback']}),
            'action_bool': lambda i, n: i.update({'default': n['default']})
        }
        
        processor = type_processors.get(node['type'])
        if processor:
            processor(item, node)
    
    def _add_sibling_links(self):
        for item_id, item in self.flattened.items():
            if 'prev_sibling' in item:
                prev_id = item['prev_sibling']
                if prev_id in self.flattened:
                    self.flattened[prev_id]['next_sibling'] = item_id


# Использование ООП подхода
def main():
    # Чтение файла
    with open('config/menu_config.json', 'r') as f:
        data = json.load(f)
    
    # Валидация
    validator = MenuValidator()
    validator.validate_node(data['menu'][0])
    
    if validator.errors:
        print("Ошибки валидации:")
        for error in validator.errors:
            print(f"  - {error}")
        return
    
    # Уплощение
    flattener = MenuFlattener()
    flattened_menu = flattener.flatten(data)
    
    print("✅ Меню успешно обработано!")
    print(f"📊 Элементов: {len(flattened_menu)}")

if __name__ == "__main__":
    main()