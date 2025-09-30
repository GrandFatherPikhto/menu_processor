from typing import Dict, List, Optional, Any
from menu_data import MenuData, ControlType

class CallbackManager:
    """Менеджер для обработки callback-функций узла меню"""
    
    ALL_CALLBACK_TYPES = [
        'click_cb', 'position_cb', 'double_click_cb', 
        'long_click_cb', 'event_cb', 'draw_value_cb'
    ]

    def __init__(self, original_node: Dict[str, Any], node_type: str, node_role: str, 
                 node_category: Dict[str, Any], menu_data: MenuData):
        self._original_node = original_node
        self._node_type = node_type
        self._node_role = node_role
        self._node_category = node_category
        self._menu_data = menu_data

        # Пользовательские callback-функции из JSON
        self.click_cb = original_node.get("click_cb")
        self.position_cb = original_node.get("position_cb")
        self.double_click_cb = original_node.get("double_click_cb")
        self.long_click_cb = original_node.get("long_click_cb")
        self.event_cb = original_node.get("event_cb")
        self.draw_value_cb = original_node.get("draw_value_cb")

        # Автоматически сгенерированные функции (будут установлены позже)
        self._auto_click_function = None
        self._auto_position_function = None

    def set_auto_functions(self, click_function: Optional[str] = None, 
                          position_function: Optional[str] = None):
        """Устанавливает автоматически сгенерированные функции"""
        self._auto_click_function = click_function
        self._auto_position_function = position_function

    @property
    def auto_draw_value_cb_name(self) -> Optional[str]:
        """Автоматически сгенерированное имя функции отрисовки с постфиксом _cb"""
        if self._node_category and self._node_category.get("name"):
            return f"menu_draw_{self._node_category['name']}_value_cb"  # Уже содержит _cb
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

    def get_callback_info(self, callback_type: str) -> Optional[Dict[str, Any]]:
        """
        Возвращает детальную информацию о ЛЮБОЙ callback-функции
        """
        # Для click_cb и position_cb проверяем как пользовательские, так и автоматические
        if callback_type in ['click_cb', 'position_cb']:
            # Пользовательский callback
            callback_value = getattr(self, callback_type, None)
            is_custom = callback_value is not None
            
            # Если пользовательский не задан, проверяем автоматический
            if not is_custom:
                if callback_type == 'click_cb':
                    callback_value = self._auto_click_function
                else:  # position_cb
                    callback_value = self._auto_position_function
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
            "type": self._node_type,
            "role": self._node_role,
            "c_type": self._node_category.get("c_type") if self._node_category else None,
            "category": self._node_category.get("name") if self._node_category else None,
            "custom": is_custom,
            "callback_type": callback_type,
            "node_id": self._original_node.get("id")
        }

    # Специализированные методы для удобства
    def get_draw_value_info(self) -> Optional[Dict[str, Any]]:
        return self.get_callback_info('draw_value_cb')

    def get_double_click_info(self) -> Optional[Dict[str, Any]]:
        return self.get_callback_info('double_click_cb')

    def get_long_click_info(self) -> Optional[Dict[str, Any]]:
        return self.get_callback_info('long_click_cb')

    def get_event_info(self) -> Optional[Dict[str, Any]]:
        return self.get_callback_info('event_cb')

    def get_click_info(self) -> Optional[Dict[str, Any]]:
        return self.get_callback_info('click_cb')

    def get_position_info(self) -> Optional[Dict[str, Any]]:
        return self.get_callback_info('position_cb')

    @property
    def all_callback_infos(self) -> Dict[str, Optional[Dict[str, Any]]]:
        """ВСЕ callback-функции узла с детальной информацией"""
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

    def get_callbacks_by_auto_status(self, auto: bool = True) -> Dict[str, Dict[str, Any]]:
        """Получить callback-функции по статусу (автоматические или пользовательские)"""
        return {
            cb_type: info for cb_type, info in self.defined_callback_infos.items()
            if info["custom"] != auto
        }

    def print_detailed_callback_info(self, node_id: str):
        """Печатает детальную информацию о ВСЕХ callback-функциях узла"""
        print(f"📋 Detailed callback info for {node_id} ({self._node_type}_{self._node_role}):")
        
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

    def print_control_info(self, node_id: str, node_role: str, controls_config: List[str] = None):
        """Печатает информацию о контролах для отладки"""
        print(f"Control info for {node_id} (role: {node_role}):")
        if controls_config:
            print(f"  Config from JSON: {controls_config}")
        
        # Показываем пользовательские callback'ы
        if self.has_custom_callbacks:
            print("  Custom callbacks:")
            for cb_name, cb_value in self.custom_callbacks_summary.items():
                if cb_value and cb_name != "auto_draw_value_cb":
                    print(f"    - {cb_name}: {cb_value}")
        
        # Показываем автоматические функции
        if self._auto_click_function:
            print(f"  Auto click function: {self._auto_click_function}")
        if self._auto_position_function:
            print(f"  Auto position function: {self._auto_position_function}")
        
        # Показываем функцию отрисовки
        if self.effective_draw_value_cb:
            source = "custom" if self.draw_value_cb else "auto"
            print(f"  Draw value function: {self.effective_draw_value_cb} ({source})")