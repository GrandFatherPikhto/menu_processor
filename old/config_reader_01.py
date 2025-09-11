import json

def flatten_menu_recursive(menu_data):
    flattened = []
    item_map = {}
    
    def process_node(node, parent_id=None, prev_sibling_id=None):
        node_id = node['name'].lower().replace(' ', '_')
        
        flat_item = {
            'id': node_id,
            'title': node['name'],
            'type': node['type'],
            'parent': parent_id,
            'prev_sibling': prev_sibling_id,
            'next_sibling': None
        }
        
        # Добавляем специфичные поля
        if node['type'] in ['action_int', 'action_int_factor']:
            for field in ['min', 'max', 'default']:
                if field in node:
                    flat_item[field] = node[field]
            
            if node['type'] == 'action_int_factor' and 'factors' in node:
                flat_item['factors'] = node['factors']
                flat_item['default_factor_idx'] = node.get('default_factor_idx', 0)
        
        elif node['type'] == 'action_callback' and 'callback' in node:
            flat_item['callback'] = node['callback']
        
        elif node['type'] == 'action_bool' and 'default' in node:
            flat_item['default'] = node['default']
        
        flattened.append(flat_item)
        item_map[node_id] = flat_item
        
        # Обрабатываем детей
        children = node.get('children', [])
        if children:
            first_child_id = children[0]['name'].lower().replace(' ', '_')
            flat_item['first_child'] = first_child_id
            
            prev_sib = None
            for child in children:
                child_id = process_node(child, node_id, prev_sib)
                if prev_sib:
                    item_map[prev_sib]['next_sibling'] = child_id
                prev_sib = child_id
        
        return node_id
    
    # Запускаем обработку с корневого элемента
    process_node(menu_data['menu'][0])
    
    return flattened

# Использование
with open('menu_config.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

flattened = flatten_menu_recursive(data)

# Сохранение результата
with open('menu_config_flattened.json', 'w', encoding='utf-8') as f:
    json.dump(flattened, f, indent=2, ensure_ascii=False)

print("Готово! Уплощенный конфиг сохранен в menu_config_flattened.json")