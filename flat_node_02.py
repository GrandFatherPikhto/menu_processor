from typing import Dict, List, Optional, Set, Any

from menu_config import MenuConfig
from menu_data import MenuData, ControlType, NavigationType

class FlatNode:
    """Плоское представление узла с настраиваемыми циклическими связями"""
    
    def __init__(self, original_node: Dict[str, Any], config: MenuConfig, menu_data: MenuData):
        self._original_node = original_node
        self._menu_config = config
        self._menu_data = menu_data
        
        # Базовые обязательные поля
        self.id = original_node["id"]
        self.name = original_node["title"]
        self.type = original_node.get("type")
        self.role = original_node.get("role")

        # Свойства
        self._navigate = self._original_node.get("navigate", None)
        self._controls_config = self._original_node.get("controls")  # ["click", "position"] или None
        self._controls = []

        self.min = self._original_node.get("min")
        self.max = self._original_node.get("max")
        self.default = self._original_node.get("default")
        self.default_idx = self._original_node.get("default_idx")
        self.factors = self._original_node.get("factors")
        self.values = self._original_node.get("values")
        self._step = self._original_node.get("step")
        
        self._type_info = None if self.type is None else self._menu_data.type(self.type)
        self._step: Optional["int"] = None

        # Связи (инициализируются позже)
        self.parent: Optional["FlatNode"] = None
        self._prev_sibling: Optional["FlatNode"] = None
        self._next_sibling: Optional["FlatNode"] = None
        self.first_child: Optional["FlatNode"] = None
        self.last_child: Optional["FlatNode"] = None
        self.children: List["FlatNode"] = []

        # Инициализация контролов на основе правил из MenuData и конфигурации узла
        self._init_controls()

    def _init_controls(self):
        """Инициализация контролов на основе роли, правил MenuData и конфигурации узла"""
        if self.type is None or self.role is None:
            return
            
        self._controls = []
        
        # Для role=factor всегда используем оба контрола, независимо от конфигурации
        if self.role == "factor":
            controls_to_check = [ControlType.CLICK, ControlType.POSITION]
        else:
            # Для других ролей: если указаны controls в узле, используем их, иначе оба
            if self._controls_config:
                controls_to_check = [ControlType(ctrl) for ctrl in self._controls_config]
            else:
                controls_to_check = [ControlType.CLICK, ControlType.POSITION]
        
        # Обрабатываем каждый контроль
        for control_type in controls_to_check:
            control_config = self._menu_data.get_control_config(
                self.role, control_type, self._controls_config, self.navigate
            )
            
            if control_config:
                self._controls.append({
                    "type": control_type,
                    "purpose": control_config["purpose"],
                    "navigate": control_config["navigate"],
                    "required": control_config["required"]
                })

    def _get_function_config(self, control: ControlType) -> Optional[Dict[str, Any]]:
        """Создает конфигурацию функции на основе установленных контролов"""
        # Находим соответствующий контроль
        control_info = next(
            (c for c in self._controls if c["type"] == control), 
            None
        )
        if not control_info:
            return None
            
        # Генерируем имя функции
        function_name = self._generate_function_name(control, control_info)
        
        return {
            "name": function_name,
            "category": self.category,
            "type": self.type,
            "role": self.role,
            "control": control.value,
            "navigate": control_info["navigate"].value,
            "purpose": control_info["purpose"]
        }

    def _generate_function_name(self, control: ControlType, control_info: Dict) -> str:
        """Генерирует имя функции в соответствии с правилами"""
        base_name = f"{self.type}_{self.role}"
        
        # Специальный случай для factor роли при изменении индекса
        if self.role == "factor" and control_info["purpose"] == "change_factor_index":
            return f"{base_name}_{control.value}_{control_info['navigate'].value}_factor"
        else:
            return f"{base_name}_{control.value}_{control_info['navigate'].value}"

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
        return self.navigate == 'cyclic' and self.parent is not None and len(self.parent.children) > 1

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
    def is_leaf(self) -> bool:
        if self.first_child:
            return False
        else:
            return True

    @property
    def is_branch(self) -> bool:
        if hasattr(self, 'first_child') and self.first_child:
            return True
        else:
            return False

    # Свойства для генерации C-кода
    def c_str_array(self, values: Set) -> str | None:
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
    def c_str_factors(self) -> str | None:
        if self.factors is None:
            return None
        return self.c_str_array(self.factors)

    @property
    def c_str_values(self) -> str | None:
        if self.values is None:
            return None
        return self.c_str_array(self.values)
    
    @property
    def fixed_count(self) -> int | None:
        if self.factors is None:
            return None
        return len(self.factors)
        
    @property
    def values_count(self) -> int | None:
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
    def step(self) -> int | None:
        if self._step is None:
            return 1
        else:
            return self._step
        
    @step.setter
    def step(self, step: int):
        self._step = step
        
    @property
    def navigate(self) -> str | None:
        return self._navigate

    @navigate.setter
    def navigate(self, value: str):
        self._navigate = value

    @property
    def controls_config(self) -> List[str] | None:
        """Возвращает конфигурацию контролов из JSON"""
        return self._controls_config

    @property
    def c_type(self) -> str | None:
        if self.type is None or self._menu_data is None:
            return None
        return self._menu_data.c_type(self.type)

    # Свойства для функций обработки
    @property
    def function_click_info(self) -> Optional[Dict[str, Any]]:
        """Информация для функции обработки клика"""
        return self._get_function_config(ControlType.CLICK)
    
    @property
    def function_position_info(self) -> Optional[Dict[str, Any]]:
        """Информация для функции обработки позиции энкодера"""
        return self._get_function_config(ControlType.POSITION)
    
    @property
    def function_click_name(self) -> Optional[str]:
        """Имя функции обработки клика"""
        info = self.function_click_info
        return info["name"] if info else None
    
    @property
    def function_position_name(self) -> Optional[str]:
        """Имя функции обработки позиции энкодера"""
        info = self.function_position_info
        return info["name"] if info else None
    
    @property
    def all_function_infos(self) -> List[Dict[str, Any]]:
        """Все возможные функции обработки для этого узла"""
        infos = []
        for control in [ControlType.CLICK, ControlType.POSITION]:
            info = self._get_function_config(control)
            if info:
                infos.append(info)
        return infos
            
    @property
    def category_name(self) -> str | None:
        if self.type is None or self.role is None:
            return None
        return f"{self.type}_{self.role}"

    @property
    def category(self) -> Dict[str, Any] | None:
        if self.type is None or self.role is None:
            return None
        return {
            "name": self.category_name,
            "type": self.type,
            "role": self.role,
            "c_type": self._menu_data.c_type(self.type)
        }

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
        
        # Показываем доступные контролы и конфигурацию
        controls_str = ""
        if self._controls:
            controls_str = " [" + ", ".join([c["type"].value for c in self._controls]) + "]"
        
        config_info = ""
        if self._controls_config:
            config_info = f" (config: {self._controls_config})"
        
        return f"FlatNode({tree_flag} {cyclic_flag} {self.id}{controls_str}{config_info}, {self.sibling_index + 1}/{self.sibling_count})"

    def print_control_info(self):
        """Печатает информацию о контролах для отладки"""
        print(f"Control info for {self.id} (role: {self.role}):")
        if self._controls_config:
            print(f"  Config from JSON: {self._controls_config}")
        
        for control in self._controls:
            print(f"  - {control['type'].value}: purpose={control['purpose']}, navigate={control['navigate'].value}")
        
        if self.function_click_info:
            print(f"  Click function: {self.function_click_info['name']}")
        if self.function_position_info:
            print(f"  Position function: {self.function_position_info['name']}")