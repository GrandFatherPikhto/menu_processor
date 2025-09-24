from typing import Dict, List, Optional, Any
from data_types import DataTypeConfig

class FlatNode:
    """Плоское представление узла с настраиваемыми циклическими связями"""
    
    def __init__(self, original_node: Dict[str, Any], data_type_config: Optional[DataTypeConfig] = None):
        self._original_node = original_node
        self._data_type_config = data_type_config
        
        # Базовые обязательные поля
        self.id = original_node['id']
        self.name = original_node['name']
        
        # Поля с приведением к умолчальным значениям
        self.type = original_node.get('type')
        self._init_type_info(data_type_config)
        self._init_control(original_node)
        self._init_numeric_values(original_node)
        self._init_boolean_values(original_node)
        self._init_fixed_values(original_node)
        self._init_factor_values(original_node)
        self._init_navigation(original_node)
        
        # Связи (инициализируются позже)
        self.parent: Optional['FlatNode'] = None
        self._prev_sibling: Optional['FlatNode'] = None
        self._next_sibling: Optional['FlatNode'] = None
        self.first_child: Optional['FlatNode'] = None
        self.last_child: Optional['FlatNode'] = None
        self.children: List['FlatNode'] = []

    def _init_type_info(self, data_type_config: Optional[DataTypeConfig]):
        """Инициализация информации о типе"""
        self.type_info = None
        if self.type and data_type_config:
            self.type_info = data_type_config.get_by_type(self.type)

    def _init_control(self, original_node: Dict[str, Any]):
        """Инициализация управления с умолчальными значениями"""
        self.control = original_node.get('control')
        if self.control is None and self.type_info is not None:
            if self.type == 'boolean':
                self.control = 'click'
            elif self.type_info.get('media_type') == 'number':
                self.control = 'position'
            elif self.type_info.get('media_type') == 'string' and self.type_info.get('category') == 'fixed':
                self.control = 'position'
    
    @property
    def function_cb(self):
        function_cb = None
        if self.control and self.type and self.type_info:
            function_cb = {
                'name': f"{self.control}_{self.type}",
                'type': self.type_info,
                'control': self.control,
            }
        return function_cb

    def _init_numeric_values(self, original_node: Dict[str, Any]):
        """Инициализация числовых значений"""
        self.min = original_node.get('min')
        self.max = original_node.get('max')
        self.step = original_node.get('step')
        
        # Умолчательный шаг для числовых типов
        if self.step is None and self.type_info and self.type_info.get('media') == 'number':
            self.step = 1

    def _init_boolean_values(self, original_node: Dict[str, Any]):
        """Инициализация boolean значений"""
        self.default = original_node.get('default')
        self.str_true = original_node.get('str_true', 'On')
        self.str_false = original_node.get('str_false', 'Off')
        
        # Умолчательное значение для boolean
        if self.type == 'boolean' and self.default is None:
            self.default = False

    def _init_fixed_values(self, original_node: Dict[str, Any]):
        """Инициализация fixed значений"""
        self.values = original_node.get('values', None)
        self.default_value_idx = None
        if self.values is None:
            return
        self.default_value_idx = original_node.get('default_idx', 0)
        # Валидация default_idx
        if self.default_value_idx >= len(self.values):
            self.default_value_idx = 0

    def _init_factor_values(self, original_node: Dict[str, Any]):
        """Инициализация factor значений"""
        self.factors = original_node.get('factors')
        self.default_factor_idx = None
        if self.factors is None:
            return
        self.default_factor_idx = original_node.get('default_idx', 0)
        
        # Валидация default_idx
        if self.factors and self.default_factor_idx >= len(self.factors):
            self.factor_default_idx = 0

    def _init_navigation(self, original_node: Dict[str, Any]):
        """Инициализация навигации"""
        self.navigate = original_node.get('navigate', None)  # По умолчанию cyclic
        if self.navigate is None and self.is_branch and self.is_branch:
            self.navigate = 'cyclic'

    @property
    def template_data(self) -> Dict[str, Any]:
        """Возвращает данные для шаблона - теперь просто возвращаем атрибуты"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'type_info': self.type_info,
            'control': self.control,
            'step': self.step,
            'min': self.min,
            'max': self.max,
            'default': self.default,
            'default_value_idx': self.default_value_idx,
            'factors': self.factors,
            'default_factor_idx': self.default_factor_idx,
            'values': self.values,
            'str_true': self.str_true,
            'str_false': self.str_false,
            'c_str_factors': self._get_c_str_values(self.factors),
            'c_str_values': self._get_c_str_values(self.values),
            'count': self._get_count(),
            'function_cb': None if self.function_cb is None else self.function_cb.get("name"),
            'parent': self.parent.id if self.parent else None,
            'next_sibling': self.next_sibling.id if self.next_sibling else None,
            'prev_sibling': self.prev_sibling.id if self.prev_sibling else None,
            'first_child': self.first_child.id if self.first_child else None,
            'last_child': self.last_child.id if self.last_child else None,
        }

    def _get_c_str_values(self, values: Optional[List]) -> Optional[str]:
        """Конвертация значений в C-строку"""
        if not values:
            return None
        
        str_values = []
        for value in values:
            if isinstance(value, str):
                str_values.append(f'"{value}"')
            else:
                str_values.append(str(value))
        return ', '.join(str_values)

    def _get_count(self) -> Optional[int]:
        """Получение количества элементов"""
        if self.factors:
            return len(self.factors)
        if self.values:
            return len(self.values)
        return None

    # Остальные свойства остаются без изменений, так как они работают со связями
    @property
    def prev_sibling(self) -> Optional['FlatNode']:
        if not self._prev_sibling and self.navigate == 'cyclic' and self.parent and self.parent.children:
            return self.parent.children[-1]
        return self._prev_sibling

    @property
    def next_sibling(self) -> Optional['FlatNode']:
        if not self._next_sibling and self.navigate == 'cyclic' and self.parent and self.parent.children:
            return self.parent.children[0]
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
        return self.navigate == 'cyclic' and self.parent and len(self.parent.children) > 1

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

    @property
    def is_leaf(self)->bool:
        if not hasattr(self, 'first_child'):
            return True
        else:
            return False

    @property
    def is_branch(self)->bool:
        if hasattr(self, 'first_child'):
            return True
        else:
            return False
    
    def __repr__(self):
        cyclic_flag = "🔁" if self.has_cyclic_siblings else "➡️"
        return f"FlatNode({self.id}, {cyclic_flag}, {self.sibling_index + 1}/{self.sibling_count})"
