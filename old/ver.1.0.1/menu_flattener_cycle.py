from menu_error import MenuError
from collections import deque
from typing import Dict, List, Optional, Any

class MenuFlattener:
    """Класс для преобразования древовидной структуры в плоскую"""
    
    def __init__(self):
        self.flattened: Dict[str, Dict] = {}
        self._auto_root_id = "root"
    
    def flatten(self, menu_data: List[Dict]) -> Dict[str, Dict]:
        """Основной метод уплощения"""
        self.flattened.clear()
        
        if not menu_data:
            raise MenuError("Нет данных меню для уплощения")
        
        # Автоматически создаем root ноду
        self._create_root_node(menu_data)
        
        # Обрабатываем все корневые элементы
        if len(menu_data) == 1:
            self._process_tree(menu_data[0], self._auto_root_id, None)
        else:
            prev_sibling_id = None
            for root_item in menu_data:
                root_item_id = self._get_or_generate_id(root_item)
                self._process_tree(root_item, self._auto_root_id, prev_sibling_id)
                prev_sibling_id = root_item_id
        
        # Устанавливаем связи next_sibling
        self._add_next_sibling_links()
        
        # ДОБАВЛЕНО: Устанавливаем связи first_sibling и last_sibling
        self._add_sibling_boundaries()
        
        return self.flattened
    
    def _add_sibling_boundaries(self):
        """Установка связей first_sibling и last_sibling для всех узлов"""
        for item_id, item in self.flattened.items():
            if 'parent' in item and item['parent'] in self.flattened:
                parent_id = item['parent']
                parent = self.flattened[parent_id]
                
                # Если у родителя есть дети, устанавливаем first_sibling
                if 'first_child' in parent:
                    first_child_id = parent['first_child']
                    item['first_sibling'] = first_child_id
                    
                    # Находим last_sibling
                    last_sibling_id = first_child_id
                    while (last_sibling_id in self.flattened and 
                           'next_sibling' in self.flattened[last_sibling_id] and
                           self.flattened[last_sibling_id]['next_sibling'] is not None):
                        last_sibling_id = self.flattened[last_sibling_id]['next_sibling']
                    
                    item['last_sibling'] = last_sibling_id
    
    def _add_next_sibling_links(self):
        """Установка связей next_sibling на основе prev_sibling"""
        for item_id, item in self.flattened.items():
            if 'prev_sibling' in item:
                prev_id = item['prev_sibling']
                if prev_id in self.flattened:
                    self.flattened[prev_id]['next_sibling'] = item_id
    
    def _create_root_node(self, menu_data: List[Dict]) -> None:
        """Создание автоматической root ноды с ссылкой на первый элемент"""
        first_child_id = None
        if menu_data:
            first_child_id = self._get_or_generate_id(menu_data[0])
        
        self.flattened[self._auto_root_id] = {
            'id': self._auto_root_id,
            'title': 'ROOT',
            'type': 'root',
            'first_child': first_child_id,
            'next_sibling': None,
            'prev_sibling': None,
            'first_sibling': first_child_id,  # ДОБАВЛЕНО
            'last_sibling': None  # Будет установлено позже
        }
    
    def _process_tree(self, node: Dict, parent_id: str, prev_sibling_id: Optional[str]) -> str:
        """Обработка дерева с использованием BFS"""
        queue = deque()
        node_id = self._get_or_generate_id(node)
        
        queue.append((node, parent_id, prev_sibling_id, node_id))
        
        while queue:
            current_node, current_parent_id, current_prev_sibling_id, current_node_id = queue.popleft()
            
            flat_item = self._create_flat_item(current_node, current_node_id, 
                                             current_parent_id, current_prev_sibling_id)
            self.flattened[current_node_id] = flat_item
            
            # Обновляем first_child у родителя, если это первый ребенок
            if (current_prev_sibling_id is None and 
                current_parent_id in self.flattened and 
                self.flattened[current_parent_id].get('first_child') is None):
                self.flattened[current_parent_id]['first_child'] = current_node_id
            
            # Обрабатываем дочерние элементы
            children = current_node.get('children', [])
            if children:
                prev_child_sibling_id = None
                for child in children:
                    child_id = self._get_or_generate_id(child)
                    queue.append((child, current_node_id, prev_child_sibling_id, child_id))
                    prev_child_sibling_id = child_id
        
        return node_id
    
    def _get_or_generate_id(self, node: Dict) -> str:
        """Получить ID из ноды или сгенерировать его"""
        if 'id' in node and node['id']:
            return node['id']
        
        # Генерируем ID из title, если явный ID не указан
        title = node.get('title', 'unknown')
        return self._generate_id_from_title(title)
    
    def _generate_id_from_title(self, title: str) -> str:
        """Генерация ID из title"""
        return title.lower().replace(' ', '_').replace('-', '_')
    
    def _create_flat_item(self, node: Dict, node_id: str, 
                         parent_id: Optional[str], prev_sibling_id: Optional[str]) -> Dict:
        """Создание уплощенного элемента меню"""
        item = {
            'id': node_id,
            'title': node['title'],
            'type': node['type']
        }
        
        # Добавляем связи
        if parent_id:
            item['parent'] = parent_id
        if prev_sibling_id:
            item['prev_sibling'] = prev_sibling_id
        
        # Добавляем специфичные поля
        self._add_type_specific_fields(item, node)
        
        # Сохраняем оригинальный ID, если он был указан
        if 'id' in node and node['id']:
            item['original_id'] = node['id']
        
        return item
    
    def _add_type_specific_fields(self, item: Dict, node: Dict) -> None:
        """Добавление полей, специфичных для типа"""
        type_processors = {
            'action_int': lambda: item.update({
                'min': node['min'],
                'max': node['max'],
                'default': node['default'],
                'step': node.get('step', 1)
            }),
            'action_int_factor': lambda: item.update({
                'min': node['min'],
                'max': node['max'],
                'default': node['default'],
                'factors': node['factors'],
                'default_factor_idx': node['default_factor_idx']
            }),
            'action_callback': lambda: item.update({
                'callback': node['callback']
            }),
            'action_bool': lambda: item.update({
                'default': node['default']
            })
        }
        
        processor = type_processors.get(node['type'])
        if processor:
            processor()