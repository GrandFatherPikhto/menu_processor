from typing import Dict, List, Optional, Any

from constants import SIMPLE_NUMBER_TYPES, FACTOR_NUMBER_TYPES, FIXED_NUMBER_TYPES, FIXED_COMPOSITE_TYPES, NUMBER_TYPES, COMPOSITE_TYPES, DATA_TYPES

class FlatNode:

    """Плоское представление узла с настраиваемыми циклическими связями"""
    def __init__(self, original_node: Dict[str, Any]):
        self.id = original_node['id']
        self.name = original_node['name']
        self.data_type = original_node.get('data_type')
        self.data_type_info = None if self.data_type is None else DATA_TYPES.get(self.data_type, None)
        self.control = original_node.get('control')
        self.min = original_node.get('min')
        self.max = original_node.get('max')
        self.step = original_node.get('step')
        self.default = original_node.get('default')
        self.default_idx = original_node.get('default_idx')
        self.factors = original_node.get('factors')
        self.values = original_node.get('values')
        self.str_true = original_node.get('str_true')
        self.str_false = original_node.get('str_false')
        self.cyclic_siblings = original_node.get('cyclic_siblings', False)  # Новая настройка
        
        # Связи
        self.parent: Optional['FlatNode'] = None
        self._prev_sibling: Optional['FlatNode'] = None
        self._next_sibling: Optional['FlatNode'] = None
        self.first_child: Optional['FlatNode'] = None
        self.last_child: Optional['FlatNode'] = None
        self.children: List['FlatNode'] = []

    @property
    def get_template_data(self) ->Dict[str, Dict]:
        item = {
            'id': None if self.id is None else self.id,
            'name': None if self.name is None else self.name,
            'data_type': None if self.data_type is None else self.data_type,
            'data_type_info': None if self.data_type_info is None else self.data_type_info,
            'control': None if self.control is None else self.control,
            'step': None if self.step is None else self.step,
            'min': None if self.min is None else self.min,
            'max': None if self.max is None else self.max,
            'default': None if self.default is None else self.default,
            'default_idx': self.get_default_idx,
            'factors': None if self.factors is None else self.factors,
            'values': None if self.values is None else self.values,
            'str_true': self.get_str_true,
            'str_false': self.get_str_false,
            'c_str_factors': self.get_c_str_factors,
            'c_str_num_values': self.get_c_str_num_values,
            'c_str_string_values': self.get_c_str_string_values,
            'count': self.get_count,
            #
            'parent': None if self.parent is None else self.parent.id,
            'next_sibling': self.get_next_sibling_id,
            'prev_sibling': self.get_prev_sibling_id,
            'first_child': None if self.first_child is None else self.first_child.id,
            'last_child': None if self.last_child is None else self.last_child.id,
        }

        return item

    @property
    def prev_sibling(self) -> Optional['FlatNode']:
        """Возвращает предыдущего sibling'а с учетом настройки cyclic_siblings"""
        if not self._prev_sibling:
            if self.cyclic_siblings and self.parent and self.parent.children:
                # Возвращаем последнего sibling'а при закольцовывании
                return self.parent.children[-1]
            return None
        return self._prev_sibling
    
    @property
    def next_sibling(self) -> Optional['FlatNode']:
        """Возвращает следующего sibling'а с учетом настройки cyclic_siblings"""
        if not self._next_sibling:
            if self.cyclic_siblings and self.parent and self.parent.children:
                # Возвращаем первого sibling'а при закольцовывании
                return self.parent.children[0]
            return None
        return self._next_sibling
    
    @prev_sibling.setter
    def prev_sibling(self, value: Optional['FlatNode']):
        """Устанавливает raw предыдущего sibling'а"""
        self._prev_sibling = value
    
    @next_sibling.setter
    def next_sibling(self, value: Optional['FlatNode']):
        """Устанавливает raw следующего sibling'а"""
        self._next_sibling = value
    
    @property
    def has_cyclic_siblings(self) -> bool:
        """Проверяет, включено ли закольцовывание для этой группы siblings"""
        # Должно проверять настройку РОДИТЕЛЯ, а не текущего узла
        if self.parent and hasattr(self.parent, 'cyclic_siblings'):
            return self.parent.cyclic_siblings and len(self.parent.children) > 1
        return False
    
    @property
    def first_sibling(self) -> Optional['FlatNode']:
        """Возвращает первого sibling'а в группе"""
        if not self.parent:
            return self
        return self.parent.first_child if self.parent.first_child else self
    
    @property
    def last_sibling(self) -> Optional['FlatNode']:
        """Возвращает последнего sibling'а в группе"""
        if not self.parent:
            return self
        return self.parent.last_child if self.parent.last_child else self
    
    @property
    def sibling_count(self) -> int:
        """Возвращает количество sibling'ов (включая себя)"""
        if not self.parent:
            return 1
        return len(self.parent.children) if self.parent.children else 1
    
    @property
    def sibling_index(self) -> int:
        """Возвращает индекс текущего sibling'а (0-based)"""
        if not self.parent or not self.parent.children:
            return 0
        for i, sibling in enumerate(self.parent.children):
            if sibling.id == self.id:
                return i
        return 0

    # @property
    # def has_cyclic_siblings(self)->bool:
    #     return False if not self.parent else self.parent.has_cyclic_siblings

    def get_sibling_at_index(self, index: int) -> Optional['FlatNode']:
        """Возвращает sibling'а по индексу с учетом закольцовывания"""
        if not self.parent or not self.parent.children:
            return self
        
        if self.has_cyclic_siblings:
            # Циклический доступ
            wrapped_index = index % len(self.parent.children)
            return self.parent.children[wrapped_index]
        else:
            # Линейный доступ с проверкой границ
            if 0 <= index < len(self.parent.children):
                return self.parent.children[index]
    
            return None
    
    
    @property
    def get_next_sibling_id(self)->Dict|None:
        if self.next_sibling and self.prev_sibling and self.next_sibling == self.prev_sibling:
            return None
        if self.next_sibling is not None:
            return self.next_sibling.id
        return None

    @property
    def get_prev_sibling_id(self)->Dict|None:
        if self.next_sibling and self.prev_sibling and self.next_sibling == self.prev_sibling:
            return None
        if self.prev_sibling is not None:
            return self.prev_sibling.id
        return None

    @property
    def get_count(self)->int|None:
        if self.data_type is None:
            return None
        if self.data_type in FIXED_NUMBER_TYPES and self.values is not None:
            return len(self.values)
        if self.data_type in FACTOR_NUMBER_TYPES and self.factors is not None:
            return len(self.factors)
        if self.data_type in COMPOSITE_TYPES and self.values is not None:
            return len(self.values)
        return None

    @property
    def get_min(self)->int|None:
        if self.data_type is None:
            return None
        if self.min is not None:
            return self.min
        return None
            
    @property
    def get_max(self)->int|None:
        if self.data_type is None:
            return None
        if self.min is not None:
            return self.min        
        return None    
    
    @property
    def get_step(self)->int|None:
        if self.data_type is None:
            return None
        if self.step is not None:
            return self.step
        if self.data_type in SIMPLE_NUMBER_TYPES or self.data_type in FACTOR_NUMBER_TYPES:
            return 1

    @property
    def get_default_idx(self)->int|None:
        if self.default_idx is not None:
            return self.default_idx    
        if self.data_type in FACTOR_NUMBER_TYPES or self.data_type in FIXED_NUMBER_TYPES or self.data_type in FIXED_COMPOSITE_TYPES:
            return 0
        
    @property
    def get_control(self)->str|None:
        if self.data_type is None:
            return None
        if self.control is not None:
            return self.control
        if self.data_type in SIMPLE_NUMBER_TYPES:
            return 'position'
        if self.data_type in FACTOR_NUMBER_TYPES:
            return 'position'
        if self.data_type == 'boolean':
            return 'click'

    @property
    def get_str_true(self)->str|None:
        if self.data_type is not None or self.data_type == 'boolean':
            if self.str_true is not None:
                return self.str_true
            return 'On'
        return None        

    @property
    def get_str_false(self)->str|None:
        if self.data_type is not None or self.data_type == 'boolean':
            if self.str_false is not None:
                return self.str_false
            return 'Off'
        return None        
    
    @property
    def get_c_str_factors(self)->str|None:
        if self.factors is not None:
            return ', '.join(map(str, self.factors))
        
    @property
    def get_c_str_string_values(self)->str|None:
        if self.data_type is None:
            return None
        if self.data_type != 'string_fixed':
            return None
        if self.values is None:
            return None
        values = []
    
        for value in self.values:
                if isinstance(value, str):
                    values.append(f'"{value}"')
                else:
                    values.append(str(value))
        return ', '.join(values)

    @property
    def get_c_str_num_values(self)->str|None:
        if self.data_type is None:
            return None
        if self.data_type not in SIMPLE_NUMBER_TYPES or self.data_type not in FIXED_NUMBER_TYPES:
            return None
        if self.values is None:
            return None
        values = []
    
        for value in self.values:
                if isinstance(value, str):
                    values.append(f'"{value}"')
                else:
                    values.append(str(value))
        return ', '.join(values)

    @property
    def get_is_leaf(self)->bool:
        if self.first_child is None:
            return True
        else:
            return False

    
    def __repr__(self):
        cyclic_flag = "🔁" if self.has_cyclic_siblings else "➡️"
        return f"FlatNode({self.id}, {cyclic_flag}, {self.sibling_index}/{self.sibling_count-1})"
