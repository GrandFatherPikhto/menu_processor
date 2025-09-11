import json
from collections import deque

def flatten_menu_config(input_file):
    # Чтение JSON файла
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    menu_items = []
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
        
        # Добавляем элемент в список
        menu_items.append(flat_item)
        
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
    
    # Добавляем связи next_sibling и prev_sibling
    item_dict = {item['id']: item for item in menu_items}
    
    for item in menu_items:
        if 'first_child' in item:
            # Устанавливаем parent для первого дочернего элемента
            first_child = item_dict[item['first_child']]
            first_child['parent'] = item['id']
        
        # Устанавливаем next_sibling на основе prev_sibling
        if 'prev_sibling' in item:
            prev_item = item_dict[item['prev_sibling']]
            prev_item['next_sibling'] = item['id']
    
    return menu_items

def save_flattened_config(output_file, flattened_data):
    # Сохраняем уплощенные данные
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(flattened_data, f, indent=2, ensure_ascii=False)

# Использование
if __name__ == "__main__":
    input_filename = "config/menu_config.json"
    output_filename = "config/menu_config_flattened.json"
    
    try:
        flattened_menu = flatten_menu_config(input_filename)
        save_flattened_config(output_filename, flattened_menu)
        print(f"Уплощенный конфиг сохранен в {output_filename}")
        
        # Вывод результата для проверки
        print("\nУплощенная структура меню:")
        for item in flattened_menu:
            print(json.dumps(item, indent=2))
            
    except FileNotFoundError:
        print(f"Файл {input_filename} не найден")
    except json.JSONDecodeError:
        print(f"Ошибка при чтении JSON файла {input_filename}")
    except Exception as e:
        print(f"Произошла чудовищная ошибка: {e}")