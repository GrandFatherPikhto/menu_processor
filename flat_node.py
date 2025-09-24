from typing import Dict, List, Optional, Set, Any

from menu_config import MenuConfig
from menu_data import MenuData

class FlatNode:
    """Плоское представление узла с настраиваемыми циклическими связями"""
    
    def __init__(self, original_node: Dict[str, Any], config: MenuConfig, data: MenuData):
        self._original_node = original_node
        self._menu_config = config
        self._data = data
        
        # Базовые обязательные поля
        self.id = original_node["id"]
        self.name = original_node["title"]
        self.type = original_node.get("type")
        self.role = original_node.get("role")

        # Свойства
        self._navigate = self._original_node.get("navigate", None)
        self._control = self._original_node.get("control", None)

        self.min = self._original_node.get("min")
        self.max = self._original_node.get("max")
        self.default = self._original_node.get("default")
        self.default_idx = self._original_node.get("default_idx")
        self.factors = self._original_node.get("factors")
        self.values = self._original_node.get("values")
        self._step = self._original_node.get("step")
        
        self._type_info = self._data.type(self.type)
        self.step: Optional["int"] = None

        # Связи (инициализируются позже)
        self.parent: Optional["FlatNode"] = None
        self._prev_sibling: Optional["FlatNode"] = None
        self._next_sibling: Optional["FlatNode"] = None
        self.first_child: Optional["FlatNode"] = None
        self.last_child: Optional["FlatNode"] = None
        self.children: List["FlatNode"] = []

    def c_str_array(self, values: Set)->str:
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
    
    @property
    def c_str_factors(self)-> str | None:
        return self.c_str_array(self.factors)

    @property
    def c_str_values(self)-> str | None:
        return self.c_str_array(self.values)

    @property
    def function_name(self)->str | None:
        if self.type is None or self.role is None or self.control is None or self.navigate is None:
            return None
        return f"{self.type}_{self.role}_{self.control}_{self.navigate}"
    
    @property 
    def click_function_name(self)->str | None:
        if self.type is None or self.role is None or self.control is None or self.navigate is None:
            return None
        if self.control != "click":
            return None
        return self.function_name
    
    @property 
    def position_function_name(self)->str | None:
        if self.type is None or self.role is None or self.control is None or self.navigate is None:
            return None
        if self.control != "position":
            return None
        return self.function_name
    
    @property
    def function_info(self)->Dict[str, Any] | None:
        if self.type is None or self.role is None or self.control is None or self.navigate is None:
            return None
        return {
                    "name": self.function_name,
                    "category": self.category,
                    "type": self.type,
                    "role": self.role,
                    "control": self.control,
                    "navigate": self.navigate
                }
    
    @property
    def category_name(self)->str | None:
        if self.type is None or self.role is None:
            return None
        return f"{self.type}_{self.role}"

    @property
    def category(self)->Dict[str, Any] | None:
        if self.type is None or self.role is None:
            return None, None
        return {
            "name": self.category_name,
            "type": self.type,
            "role": self.role,
            "c_type": self._data.type(self.type).get("c_type")
        }
        
    @property
    def fixed_count(self)->int | None:
        if self.factors is None:
            return None
        return len(self.factors)
        
    @property
    def values_count(self)->int | None:
        if self.values is None:
            return None
        return len(self.values)
    
    @property
    def values_default_idx(self):
        if self.values is None:
            return None
        if self.default_idx is None:
            return 0
        else:
            return self.default_idx
    
    @property
    def factors_default_idx(self):
        if self.factors is None:
            return None
        if self.default_idx is None:
            return 0
        else:
            return self.default_idx
        
    @property
    def step(self)->int | None:
        if self._step is None:
            return 1
        else:
            return self._step
        
    @step.setter
    def step(self, step:int):
        self._step = step
        
    @property
    def navigate(self)->str | None:
        return self._navigate

    @navigate.setter
    def navigate(self, value: str):
        self._navigate = value

    @property
    def control(self)->str | None:
        return self._control
    
    @control.setter
    def control(self, value: str):
        self._control = value

    @property
    def c_type(self)->str | None:
        if self.type is None:
            return None
        return self._data.type(self.type).get("c_type")

    # Базовые свойства 
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
        if self.first_child:
            return False
        else:
            return True

    @property
    def is_branch(self)->bool:
        if hasattr(self, 'first_child') and self.first_child:
            return True
        else:
            return False
    
    def __repr__(self):
        cyclic_flag = "🔁" if self.has_cyclic_siblings else "➡️ "
        tree_flag = "📁"
        match self.role:
            case "simple":
                tree_flag = "🟦"
            case "factor":
                tree_flag = "🟢"
            case "fixed": 
                tree_flag = "⚫"
            case "callback":
                tree_flag = "⚪"
            case _:
                if self.role is not None:
                    tree_flag = "✨"
        return f"FlatNode({tree_flag} {cyclic_flag}  {self.id}, {self.sibling_index + 1}/{self.sibling_count})"
