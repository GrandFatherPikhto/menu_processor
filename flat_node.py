from typing import Dict, List, Optional, Set, Any
from menu_config import MenuConfig
from menu_data import MenuData, ControlType, NavigationType
from callback_manager import CallbackManager

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
        self._controls_config = self._original_node.get("controls")
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

        # Callback Manager
        self._callback_manager = CallbackManager(
            original_node, self.type, self.role, self.category, menu_data
        )

        # Связи (инициализируются позже)
        self.parent: Optional["FlatNode"] = None
        self._prev_sibling: Optional["FlatNode"] = None
        self._next_sibling: Optional["FlatNode"] = None
        self.first_child: Optional["FlatNode"] = None
        self.last_child: Optional["FlatNode"] = None
        self.children: List["FlatNode"] = []

        # Инициализация контролов
        self._init_controls()

    def _init_controls(self):
        """Инициализация контролов на основе роли, правил MenuData и конфигурации узла"""
        if self.type is None or self.role is None:
            return
            
        self._controls = []
        
        # Если заданы пользовательские callback'ы, игнорируем автоматические контролы для них
        use_auto_click = self._callback_manager.click_cb is None
        use_auto_position = self._callback_manager.position_cb is None
        
        # Для role=factor всегда используем оба контрола, если не заданы пользовательские callback'ы
        if self.role == "factor":
            controls_to_check = []
            if use_auto_click:
                controls_to_check.append(ControlType.CLICK)
            if use_auto_position:
                controls_to_check.append(ControlType.POSITION)
        else:
            # Для других ролей: если указаны controls в узле, используем их, иначе оба
            if self._controls_config:
                controls_to_check = [ControlType(ctrl) for ctrl in self._controls_config]
            else:
                controls_to_check = [ControlType.CLICK, ControlType.POSITION]
            
            # Фильтруем контролы в соответствии с пользовательскими callback'ами
            if not use_auto_click and ControlType.CLICK in controls_to_check:
                controls_to_check.remove(ControlType.CLICK)
            if not use_auto_position and ControlType.POSITION in controls_to_check:
                controls_to_check.remove(ControlType.POSITION)
        
        # Обрабатываем каждый контроль
        auto_click_function = None
        auto_position_function = None
        
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
                
                # Сохраняем имена автоматических функций
                function_name = self._generate_function_name(control_type, control_config)
                if control_type == ControlType.CLICK:
                    auto_click_function = function_name
                elif control_type == ControlType.POSITION:
                    auto_position_function = function_name
        
        # Устанавливаем автоматические функции в CallbackManager
        self._callback_manager.set_auto_functions(auto_click_function, auto_position_function)

    def _generate_function_name(self, control: ControlType, control_config: Dict) -> str:
        """Генерирует имя функции в соответствии с правилами"""
        base_name = f"{self.type}_{self.role}"
        
        # Специальный случай для factor роли при изменении индекса
        if self.role == "factor" and control_config["purpose"] == "change_factor_index":
            name = f"{base_name}_{control.value}_{control_config['navigate'].value}_factor"
        else:
            name = f"{base_name}_{control.value}_{control_config['navigate'].value}"
        
        # Добавляем постфикс _cb для автоматических функций
        return name + "_cb"

    # Делегирование методов CallbackManager
    @property
    def callback_manager(self) -> CallbackManager:
        return self._callback_manager

    def get_callback_info(self, callback_type: str) -> Optional[Dict[str, Any]]:
        return self._callback_manager.get_callback_info(callback_type)

    def get_draw_value_info(self) -> Optional[Dict[str, Any]]:
        return self._callback_manager.get_draw_value_info()

    def get_double_click_info(self) -> Optional[Dict[str, Any]]:
        return self._callback_manager.get_double_click_info()

    def get_long_click_info(self) -> Optional[Dict[str, Any]]:
        return self._callback_manager.get_long_click_info()

    def get_event_info(self) -> Optional[Dict[str, Any]]:
        return self._callback_manager.get_event_info()

    def get_click_info(self) -> Optional[Dict[str, Any]]:
        return self._callback_manager.get_click_info()

    def get_position_info(self) -> Optional[Dict[str, Any]]:
        return self._callback_manager.get_position_info()

    @property
    def all_callback_infos(self) -> Dict[str, Optional[Dict[str, Any]]]:
        return self._callback_manager.all_callback_infos

    @property
    def defined_callback_infos(self) -> Dict[str, Dict[str, Any]]:
        return self._callback_manager.defined_callback_infos

    @property
    def auto_generated_callbacks(self) -> Dict[str, Dict[str, Any]]:
        return self._callback_manager.auto_generated_callbacks

    @property
    def custom_callbacks(self) -> Dict[str, Dict[str, Any]]:
        return self._callback_manager.custom_callbacks

    @property
    def custom_callbacks_summary(self) -> Dict[str, Optional[str]]:
        return self._callback_manager.custom_callbacks_summary

    @property
    def has_custom_callbacks(self) -> bool:
        return self._callback_manager.has_custom_callbacks

    def print_detailed_callback_info(self):
        self._callback_manager.print_detailed_callback_info(self.id)

    def print_control_info(self):
        self._callback_manager.print_control_info(self.id, self.role, self._controls_config)
    
    @property
    def function_click_info(self) -> Optional[Dict[str, Any]]:
        """Информация для функции обработки клика (для обратной совместимости)"""
        return self._callback_manager.get_click_info()
    
    @property
    def function_position_info(self) -> Optional[Dict[str, Any]]:
        """Информация для функции обработки позиции энкодера (для обратной совместимости)"""
        return self._callback_manager.get_position_info()
    
    @property
    def function_click_name(self) -> Optional[str]:
        """Имя функции обработки клика (для обратной совместимости)"""
        info = self.function_click_info
        return info["name"] if info else None
    
    @property
    def function_position_name(self) -> Optional[str]:
        """Имя функции обработки позиции энкодера (для обратной совместимости)"""
        info = self.function_position_info
        return info["name"] if info else None
    
    @property
    def auto_draw_value_cb_name(self) -> Optional[str]:
        return self._callback_manager.auto_draw_value_cb_name

    @property
    def draw_value_cb(self) -> Optional[str]:
        return self._callback_manager.draw_value_cb    
    
    @property
    def all_function_infos(self) -> List[Dict[str, Any]]:
        """Все возможные функции обработки для этого узла (для обратной совместимости)"""
        infos = []
        click_info = self.function_click_info
        position_info = self.function_position_info
        if click_info:
            infos.append(click_info)
        if position_info:
            infos.append(position_info)
        return infos

    @property
    def effective_click_cb_name(self) -> Optional[str]:
        """Имя callback-функции для клика (пользовательская или автоматическая) с постфиксом _cb"""
        info = self.get_click_info()
        if not info:
            return None
        
        # Если это пользовательская функция, используем как есть (предполагаем, что пользователь уже добавил _cb)
        # Если это автоматическая функция, она уже имеет _cb из _generate_function_name
        return info["name"]

    @property
    def effective_position_cb_name(self) -> Optional[str]:
        """Имя callback-функции для позиции (пользовательская или автоматическая) с постфиксом _cb"""
        info = self.get_position_info()
        if not info:
            return None
        return info["name"]

    @property
    def effective_double_click_cb_name(self) -> Optional[str]:
        """Имя callback-функции для двойного клика с постфиксом _cb"""
        info = self.get_double_click_info()
        if not info:
            return None
        
        # Для пользовательских функций double_click_cb предполагаем, что имя уже содержит _cb
        return info["name"] if info else None

    @property
    def effective_long_click_cb_name(self) -> Optional[str]:
        """Имя callback-функции для долгого клика с постфиксом _cb"""
        info = self.get_long_click_info()
        if not info:
            return None
        return info["name"] if info else None

    @property
    def effective_event_cb_name(self) -> Optional[str]:
        """Имя callback-функции для событий с постфиксом _cb"""
        info = self.get_event_info()
        if not info:
            return None
        return info["name"] if info else None

    @property
    def effective_draw_value_cb_name(self) -> Optional[str]:
        """Имя callback-функции для отрисовки значения с постфиксом _cb"""
        info = self.get_draw_value_info()
        if not info:
            return None
    
        # Для автоматической функции отрисовки добавляем _cb
        if not info["custom"]:
            return info["name"]  # auto_draw_value_cb_name уже включает _cb
        else:
            # Для пользовательской предполагаем, что имя уже содержит _cb
            return info["name"]
    
    # ... остальные свойства и методы FlatNode
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

    # Базовые свойства 
    @property
    def prev_sibling(self) -> Optional['FlatNode']:
        """Возвращает предыдущего sibling с учетом навигации родителя"""
        if self._prev_sibling:
            return self._prev_sibling
        
        # Если навигация циклическая и есть родитель с детьми
        if (self.parent and self.parent.navigate == 'cyclic' and 
            self.parent.children and len(self.parent.children) > 1):
            # Первый элемент ссылается на последний
            if self == self.parent.children[0]:
                return self.parent.children[-1]
        
        return None

    @property
    def next_sibling(self) -> Optional['FlatNode']:
        """Возвращает следующего sibling с учетом навигации родителя"""
        if self._next_sibling:
            return self._next_sibling
        
        # Если навигация циклическая и есть родитель с детьми
        if (self.parent and self.parent.navigate == 'cyclic' and 
            self.parent.children and len(self.parent.children) > 1):
            # Последний элемент ссылается на первый
            if self == self.parent.children[-1]:
                return self.parent.children[0]
        
        return None

    @prev_sibling.setter
    def prev_sibling(self, value: Optional['FlatNode']):
        """Устанавливает предыдущего sibling'а"""
        self._prev_sibling = value

    @next_sibling.setter
    def next_sibling(self, value: Optional['FlatNode']):
        """Устанавливает следующего sibling'а"""
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
        
        # Показываем иконку пользовательских callback'ов
        callback_flag = "🎛️" if self.has_custom_callbacks else ""
        
        return f"FlatNode({tree_flag} {cyclic_flag} {self.id}{controls_str}{config_info} {callback_flag}, {self.sibling_index + 1}/{self.sibling_count})"

