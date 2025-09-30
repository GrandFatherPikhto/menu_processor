from typing import Dict, List, Optional, Set, Any

from menu_config import MenuConfig
from menu_data import MenuData, ControlType, NavigationType

class FlatNode:
    """Плоское представление узла с настраиваемыми циклическими связями"""
    ALL_CALLBACK_TYPES = [
        'click_cb', 'position_cb', 'double_click_cb', 
        'long_click_cb', 'event_cb', 'draw_value_cb'
    ]

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

        # Пользовательские callback-функции
        self.click_cb = original_node.get("click_cb")
        self.position_cb = original_node.get("position_cb")
        self.double_click_cb = original_node.get("double_click_cb")
        self.long_click_cb = original_node.get("long_click_cb")
        self.event_cb = original_node.get("event_cb")
        self.draw_value_cb = original_node.get("draw_value_cb")

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
        
        # Если заданы пользовательские callback'ы, игнорируем автоматические контролы для них
        use_auto_click = self.click_cb is None
        use_auto_position = self.position_cb is None
        
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
        # Если задан пользовательский callback, не генерируем автоматическую функцию
        if control == ControlType.CLICK and self.click_cb:
            return None
        if control == ControlType.POSITION and self.position_cb:
            return None
            
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

    # Свойства для callback-функций
    @property
    def auto_draw_value_cb_name(self) -> Optional[str]:
        """Автоматически сгенерированное имя функции отрисовки"""
        if self.category_name:
            return f"menu_draw_{self.category_name}_value_cb"
        return None

    @property
    def effective_draw_value_cb(self) -> Optional[str]:
        """Эффективное имя функции отрисовки (пользовательская или автоматическая)"""
        return self.draw_value_cb or self.auto_draw_value_cb_name

    @property
    def has_custom_callbacks(self) -> bool:
        """Имеет ли узел пользовательские callback'ы"""
        return any([
            self.click_cb, self.position_cb, self.double_click_cb,
            self.long_click_cb, self.event_cb, self.draw_value_cb
        ])

    @property
    def custom_callbacks_summary(self) -> Dict[str, Optional[str]]:
        """Сводка пользовательских callback'ов"""
        return {
            "click_cb": self.click_cb,
            "position_cb": self.position_cb,
            "double_click_cb": self.double_click_cb,
            "long_click_cb": self.long_click_cb,
            "event_cb": self.event_cb,
            "draw_value_cb": self.draw_value_cb,
            "auto_draw_value_cb": self.auto_draw_value_cb_name if not self.draw_value_cb else None
        }

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
    
    def get_callback_info(self, callback_type: str) -> Optional[Dict[str, Any]]:
        """
        Возвращает детальную информацию о ЛЮБОЙ callback-функции
        
        Args:
            callback_type: тип callback ('click_cb', 'position_cb', 'double_click_cb', 
                          'long_click_cb', 'event_cb', 'draw_value_cb')
        
        Returns:
            Словарь с информацией о callback или None если callback не определен
        """
        # Для click_cb и position_cb проверяем как пользовательские, так и автоматические
        if callback_type in ['click_cb', 'position_cb']:
            # Пользовательский callback
            callback_value = getattr(self, callback_type, None)
            is_custom = callback_value is not None
            
            # Если пользовательский не задан, проверяем автоматический
            if not is_custom:
                if callback_type == 'click_cb':
                    func_info = self.function_click_info
                else:  # position_cb
                    func_info = self.function_position_info
                
                if func_info:
                    callback_value = func_info['name']
                    is_custom = False
        else:
            # Для остальных callback-типов
            callback_value = getattr(self, callback_type, None)
            is_custom = callback_value is not None
            
            # Для draw_value_cb может быть автоматическая функция
            if callback_type == 'draw_value_cb' and not is_custom:
                callback_value = self.auto_draw_value_cb_name
                is_custom = False
        
        if not callback_value:
            return None
        
        return {
            "name": callback_value,
            "type": self.type,
            "role": self.role,
            "c_type": self.c_type,
            "category": self.category_name,
            "custom": is_custom,
            "callback_type": callback_type,
            "node_id": self.id
        }

    # Упрощаем специализированные методы - они теперь просто вызывают общий метод
    def get_draw_value_info(self) -> Optional[Dict[str, Any]]:
        """Информация о функции отрисовки значения"""
        return self.get_callback_info('draw_value_cb')

    def get_double_click_info(self) -> Optional[Dict[str, Any]]:
        """Информация о функции двойного клика"""
        return self.get_callback_info('double_click_cb')

    def get_long_click_info(self) -> Optional[Dict[str, Any]]:
        """Информация о функции долгого клика"""
        return self.get_callback_info('long_click_cb')

    def get_event_info(self) -> Optional[Dict[str, Any]]:
        """Информация о функции обработки событий"""
        return self.get_callback_info('event_cb')

    def get_click_info(self) -> Optional[Dict[str, Any]]:
        """Информация о функции клика"""
        return self.get_callback_info('click_cb')

    def get_position_info(self) -> Optional[Dict[str, Any]]:
        """Информация о функции позиции энкодера"""
        return self.get_callback_info('position_cb')

    @property
    def all_callback_infos(self) -> Dict[str, Optional[Dict[str, Any]]]:
        """ВСЕ callback-функции узла с детальной информацией (включая click_cb и position_cb)"""
        return {
            cb_type: self.get_callback_info(cb_type)
            for cb_type in self.ALL_CALLBACK_TYPES
        }

    @property
    def defined_callback_infos(self) -> Dict[str, Dict[str, Any]]:
        """Только определенные callback-функции (исключая None)"""
        return {
            cb_type: info for cb_type, info in self.all_callback_infos.items()
            if info is not None
        }

    @property
    def auto_generated_callbacks(self) -> Dict[str, Dict[str, Any]]:
        """Только автоматически сгенерированные callback-функции"""
        return {
            cb_type: info for cb_type, info in self.defined_callback_infos.items()
            if not info["custom"]
        }

    @property
    def custom_callbacks(self) -> Dict[str, Dict[str, Any]]:
        """Только пользовательские callback-функции"""
        return {
            cb_type: info for cb_type, info in self.defined_callback_infos.items()
            if info["custom"]
        }

    def print_detailed_callback_info(self):
        """Печатает детальную информацию о ВСЕХ callback-функциях узла"""
        print(f"📋 Detailed callback info for {self.id} ({self.type}_{self.role}):")
        
        for cb_type, info in self.all_callback_infos.items():
            if info:
                custom_flag = "🎛️ CUSTOM" if info["custom"] else "⚙️ AUTO"
                print(f"  {cb_type}:")
                print(f"    Name: {info['name']} ({custom_flag})")
                print(f"    Type: {info['type']}")
                print(f"    Role: {info['role']}")
                print(f"    C Type: {info['c_type']}")
                print(f"    Category: {info['category']}")
            else:
                print(f"  {cb_type}: None")

    def get_callbacks_by_auto_status(self, auto: bool = True) -> Dict[str, Dict[str, Any]]:
        """Получить callback-функции по статусу (автоматические или пользовательские)"""
        return {
            cb_type: info for cb_type, info in self.defined_callback_infos.items()
            if info["custom"] != auto
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
        
        # Показываем иконку пользовательских callback'ов
        callback_flag = "🎛️" if self.has_custom_callbacks else ""
        
        return f"FlatNode({tree_flag} {cyclic_flag} {self.id}{controls_str}{config_info} {callback_flag}, {self.sibling_index + 1}/{self.sibling_count})"

    def print_control_info(self):
        """Печатает информацию о контролах для отладки"""
        print(f"Control info for {self.id} (role: {self.role}):")
        if self._controls_config:
            print(f"  Config from JSON: {self._controls_config}")
        
        # Показываем пользовательские callback'ы
        if self.has_custom_callbacks:
            print("  Custom callbacks:")
            for cb_name, cb_value in self.custom_callbacks_summary.items():
                if cb_value:
                    print(f"    - {cb_name}: {cb_value}")
        
        for control in self._controls:
            print(f"  - {control['type'].value}: purpose={control['purpose']}, navigate={control['navigate'].value}")
        
        if self.function_click_info:
            print(f"  Click function: {self.function_click_info['name']}")
        if self.function_position_info:
            print(f"  Position function: {self.function_position_info['name']}")
        
        # Показываем функцию отрисовки
        if self.effective_draw_value_cb:
            source = "custom" if self.draw_value_cb else "auto"
            print(f"  Draw value function: {self.effective_draw_value_cb} ({source})")