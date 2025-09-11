import json
from collections import deque

def flatten_menu_to_dict(input_file):
    # Чтение JSON файла
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    flattened_dict = {}
    node_queue = deque()
    
    # Добавляем корневой элемент в очередь
    root = data['menu'][0]
    node_queue.append((root, None, None))  # (node, parent_id, prev_sibling_id)
    
    # Обход дерева в ширину
    while node_queue:
        node, parent_id, prev_sibling_id = node_queue.popleft()
        
        # Генерируем ID для текущего узла
        node_id = node['name'].lower().replace(' ', '_')
        
        # Создаем уплощенный элемент
        flat_item = {
            'id': node_id,
            'title': node['name'],
            'type': node['type']
        }
        
        # Добавляем дополнительные поля в зависимости от типа
        if node['type'] in ['action_int', 'action_int_factor']:
            flat_item['min'] = node.get('min', 0)
            flat_item['max'] = node.get('max', 100)
            flat_item['default'] = node.get('default', 0)
            
            if node['type'] == 'action_int_factor':
                flat_item['factors'] = node.get('factors', [1])
                flat_item['default_factor_idx'] = node.get('default_factor_idx', 0)
        
        elif node['type'] == 'action_callback':
            flat_item['callback'] = node.get('callback', '')
        
        elif node['type'] == 'action_bool':
            flat_item['default'] = node.get('default', False)
        
        # Добавляем связи
        if parent_id:
            flat_item['parent'] = parent_id
        
        if prev_sibling_id:
            flat_item['prev_sibling'] = prev_sibling_id
        
        # Добавляем элемент в словарь
        flattened_dict[node_id] = flat_item
        
        # Обрабатываем дочерние элементы
        children = node.get('children', [])
        if children:
            first_child_id = children[0]['name'].lower().replace(' ', '_')
            flat_item['first_child'] = first_child_id
            
            # Добавляем дочерние элементы в очередь
            prev_sibling = None
            for child in children:
                child_id = child['name'].lower().replace(' ', '_')
                node_queue.append((child, node_id, prev_sibling))
                prev_sibling = child_id
    
    # Добавляем связи next_sibling
    for item_id, item in flattened_dict.items():
        if 'prev_sibling' in item:
            prev_sibling_id = item['prev_sibling']
            if prev_sibling_id in flattened_dict:
                flattened_dict[prev_sibling_id]['next_sibling'] = item_id
    
    return flattened_dict

def save_flattened_dict(output_file, flattened_dict):
    # Сохраняем уплощенные данные в виде словаря
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(flattened_dict, f, indent=2, ensure_ascii=False)

# Использование
if __name__ == "__main__":
    input_filename = "config/menu_config.json"
    output_filename = "output/menu_config_flattened_dict.json"
    
    try:
        flattened_menu_dict = flatten_menu_to_dict(input_filename)
        save_flattened_dict(output_filename, flattened_menu_dict)
        print(f"Уплощенный конфиг в виде словаря сохранен в {output_filename}")
        
        # Вывод результата для проверки
        print("\nУплощенная структура меню (словарь):")
        for item_id, item_data in flattened_menu_dict.items():
            print(f"{item_id}: {json.dumps(item_data, indent=2)}")
            
    except FileNotFoundError:
        print(f"Файл {input_filename} не найден")
    except json.JSONDecodeError:
        print(f"Ошибка при чтении JSON файла {input_filename}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")