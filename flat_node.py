from typing import Dict, List, Optional, Set, Any
from base_flat_node import BaseFlatNode
from menu_config import MenuConfig
from menu_data import MenuData

class FlatNode(BaseFlatNode):
    """Финальный класс узла - использует композицию менеджеров из BaseFlatNode"""
    
    def __init__(self, original_node: Dict[str, Any], config: MenuConfig, menu_data: MenuData):
        # Используем наследование от BaseFlatNode
        super().__init__(original_node, config, menu_data)
        
        # Инициализируем менеджер контролов
        self._init_control_manager()

    # Сохраняем только обратно-совместимые свойства для временной поддержки
    @property
    def effective_click_cb_name(self) -> Optional[str]:
        """Имя callback-функции для клика (пользовательская или автоматическая) с постфиксом _cb"""
        info = self.get_click_info()
        if not info:
            return None
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
        return info["name"]