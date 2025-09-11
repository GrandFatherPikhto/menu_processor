import json
from collections import deque
import sys

class MenuValidationError(Exception):
    """Кастомное исключение для ошибок валидации меню"""
    def __init__(self, message, node_path=None, line_info=None):
        self.message = message
        self.node_path = node_path or []
        self.line_info = line_info
        super().__init__(self._format_message())
    
    def _format_message(self):
        path_str = ' -> '.join(self.node_path) if self.node_path else 'root'
        line_info = f" (строка {self.line_info})" if self.line_info else ""
        return f"Ошибка в узле '{path_str}'{line_info}: {self.message}"

def node_is_root(node):
    if node.get('root', None):
        return False
    if node.get('root').lower().strip() == 'root':
        return True
    return False

class ReadConfig:
    def __init__(self, ):
        self.json_file = ''
        self.node_counter = 0
        self.errors = []

    def read_config(self):
        try:
            flattened_menu = flatten_menu_with_validation(self.json_file)
            
            if flattened_menu:
                print(f"✅ Валидация прошла успешно!")
                
                # Вывод статистики
                print(f"\n📊 Статистика:")
                print(f"   Всего элементов: {len(flattened_menu)}")
                types_count = {}
                for item in flattened_menu.values():
                    types_count[item['type']] = types_count.get(item['type'], 0) + 1
                
                for type_name, count in types_count.items():
                    print(f"   {type_name}: {count}")

                return flattened_menu                
            else:
                print("❌ Валидация не пройдена")
                return None
                
        except MenuValidationError as e:
            print(f"❌ Ошибка валидации: {e}")
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")

        return None


def validate_menu_node(node, path, line_offset=0):
    
    node_counter += 1
    current_path = path + [node.get('name', f'node_{node_counter}')]
    
    # Получаем информацию о строке для текущего узла
    node_line = None
    if hasattr(node, '__line__'):
        node_line = node.__line__ + line_offset
    
    # Проверяем обязательные поля
    if not node_is_root and 'id' not in node:
        errors.append(MenuValidationError(
            "Отсутствует обязательное поле 'id'",
            current_path,
            node_line
        ))

    if 'name' not in node:
        errors.append(MenuValidationError(
            "Отсутствует обязательное поле 'name'",
            current_path,
            node_line
        ))
    
    if 'type' not in node:
        errors.append(MenuValidationError(
            "Отсутствует обязательное поле 'type'",
            current_path,
            node_line
        ))
    
    # Проверяем валидность типа
    valid_types = ['root', 'submenu', 'action_int', 'action_int_factor', 
                    'action_callback', 'action_bool']
    if 'type' in node and node['type'] not in valid_types:
        errors.append(MenuValidationError(
            f"Неверный тип '{node['type']}'. Допустимые типы: {valid_types}",
            current_path,
            node_line
        ))
    
    # Проверяем обязательные поля для конкретных типов
    if node.get('type') == 'action_int':
        for field in ['min', 'max', 'default']:
            if field not in node:
                errors.append(MenuValidationError(
                    f"Для типа 'action_int' обязательно поле '{field}'",
                    current_path,
                    node_line
                ))
    
    elif node.get('type') == 'action_int_factor':
        for field in ['min', 'max', 'default', 'factors', 'default_factor_idx']:
            if field not in node:
                errors.append(MenuValidationError(
                    f"Для типа 'action_int_factor' обязательно поле '{field}'",
                    current_path,
                    node_line
                ))
    
    elif node.get('type') == 'action_callback' and 'callback' not in node:
        errors.append(MenuValidationError(
            "Для типа 'action_callback' обязательно поле 'callback'",
            current_path,
            node_line
        ))
    
    # Рекурсивно проверяем дочерние элементы
    for child in node.get('children', []):
        validate_node(child, current_path, line_offset)


def validate_menu_structure(menu_data, input_file):
    """
    Валидирует структуру меню, проверяя обязательные поля
    и возвращая информацию о строках для ошибок
    """
    errors = []
    node_counter = 0
    
    
    # Запускаем валидацию с корневого элемента
    if 'menu' in menu_data and menu_data['menu']:
        validate_node(menu_data['menu'][0], [])
    else:
        errors.append(MenuValidationError("Отсутствует корневой элемент меню"))
    
    return errors

def get_json_line_info(input_file):
    """
    Читает JSON файл и добавляет информацию о строках к каждому узлу
    """
    try:
        # Читаем файл как текст для получения номеров строк
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсим JSON с сохранением информации о позициях
        lines = content.split('\n')
        data = json.loads(content)
        
        # Функция для добавления информации о строках
        def add_line_info(obj, line_offset=0):
            if isinstance(obj, dict):
                # Добавляем информацию о строке для текущего объекта
                if hasattr(obj, '__line__'):
                    obj.__line__ += line_offset
                
                for key, value in obj.items():
                    if isinstance(value, (dict, list)):
                        add_line_info(value, line_offset)
            
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, (dict, list)):
                        add_line_info(item, line_offset)
        
        # Добавляем информацию о строках (упрощенная версия)
        # В реальном проекте лучше использовать json.decoder.JSONDecoder
        add_line_info(data)
        return data, lines
        
    except Exception as e:
        raise MenuValidationError(f"Ошибка чтения файла: {e}")

def flatten_menu_with_validation(input_file):
    """
    Читает и валидирует меню, затем уплощает его
    """
    try:
        # Читаем файл с информацией о строках
        menu_data, file_lines = get_json_line_info(input_file)
        
        # Валидируем структуру
        validation_errors = validate_menu_structure(menu_data, input_file)
        
        if validation_errors:
            print("Ошибки валидации:")
            for error in validation_errors:
                print(f"  - {error}")
            return None
        
        # Если валидация прошла успешно, уплощаем меню
        flattened_dict = {}
        node_queue = deque()
        
        # Добавляем корневой элемент в очередь
        root = menu_data['menu'][0]
        node_queue.append((root, None, None, []))  # (node, parent_id, prev_sibling_id, path)
        
        # Обход дерева в ширину
        while node_queue:
            node, parent_id, prev_sibling_id, path = node_queue.popleft()
            
            # Создаем ID элемента
            # item_id = node['name'].lower().replace(' ', '_')

            current_path = path + [node['name']]
            
            # Базовые поля
            item = {
                'id': item_id,
                'title': node['name'],
                'type': node['type']
            }
            
            # Добавляем связи
            if parent_id:
                item['parent'] = parent_id
            if prev_sibling_id:
                item['prev_sibling'] = prev_sibling_id
            
            # Добавляем специфичные поля
            if node['type'] in ['action_int', 'action_int_factor']:
                for field in ['min', 'max', 'default']:
                    if field in node:
                        item[field] = node[field]
                
                if node['type'] == 'action_int_factor':
                    for field in ['factors', 'default_factor_idx']:
                        if field in node:
                            item[field] = node[field]
            
            elif node['type'] == 'action_callback' and 'callback' in node:
                item['callback'] = node['callback']
            
            elif node['type'] == 'action_bool' and 'default' in node:
                item['default'] = node['default']
            
            # Сохраняем элемент
            flattened_dict[item_id] = item
            
            # Обрабатываем детей
            children = node.get('children', [])
            if children:
                item['first_child'] = children[0]['name'].lower().replace(' ', '_')
                
                prev_id = None
                for child in children:
                    child_id = child['name'].lower().replace(' ', '_')
                    node_queue.append((child, item_id, prev_id, current_path))
                    prev_id = child_id
        
        # Устанавливаем next_sibling связи
        for item_id, item in flattened_dict.items():
            if 'prev_sibling' in item:
                prev_id = item['prev_sibling']
                if prev_id in flattened_dict:
                    flattened_dict[prev_id]['next_sibling'] = item_id
        
        return flattened_dict
        
    except FileNotFoundError:
        raise MenuValidationError(f"Файл {input_file} не найден")
    except json.JSONDecodeError as e:
        raise MenuValidationError(f"Ошибка формата JSON: {e}")
    except Exception as e:
        raise MenuValidationError(f"Неожиданная ошибка: {e}")


def save_items(items: dict, filename):
    # Сохраняем результат
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    print(f"✅ Конфигурация сохранена в {filename}")


# Использование
if __name__ == "__main__":
    input_filename = "config/menu_config.json"
    output_filename = "output/menu_config_validated.json"
    items = read_config(input_filename)
    if items != None:
        save_items(items, output_filename)
