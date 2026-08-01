from typing import Dict, List, Optional, Any
from menu_data import MenuData, ControlType
from i18n import _

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
        self._auto_click_info = None
        self._auto_position_info = None

    def set_auto_functions(self, click_info: Optional[Dict] = None, 
                          position_info: Optional[Dict] = None):
        """Устанавливает автоматически сгенерированные функции с дополнительной информацией"""
        self._auto_click_info = click_info
        self._auto_position_info = position_info
        
        # Устанавливаем имена функций для обратной совместимости
        self._auto_click_function = click_info["name"] if click_info and "name" in click_info else None
        self._auto_position_function = position_info["name"] if position_info and "name" in position_info else None

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
                    auto_info = self._auto_click_info
                else:  # position_cb
                    callback_value = self._auto_position_function
                    auto_info = self._auto_position_info
                is_custom = False
            else:
                auto_info = None
        else:
            # Для остальных callback-типов
            callback_value = getattr(self, callback_type, None)
            is_custom = callback_value is not None
            
            # Для draw_value_cb может быть автоматическая функция
            if callback_type == 'draw_value_cb' and not is_custom:
                callback_value = self.auto_draw_value_cb_name
                is_custom = False
                auto_info = None
            else:
                auto_info = None
        
        if not callback_value:
            return None
        
        # Базовая информация
        info = {
            "name": callback_value,
            "type": self._node_type,
            "role": self._node_role,
            "c_type": self._node_category.get("c_type") if self._node_category else None,
            "category": self._node_category.get("name") if self._node_category else None,
            "custom": is_custom,
            "callback_type": callback_type,
            "node_id": self._original_node.get("id"),
            "event_type": callback_type.replace('_cb', '')  # click_cb -> click
        }
        
        # Добавляем информацию о навигации для автоматических функций
        if not is_custom and auto_info:
            info["navigate"] = auto_info.get("navigate")
            info["purpose"] = auto_info.get("purpose")
        
        return info

    # Добавляем свойство для получения информации о всех автоматических функциях
    @property
    def auto_functions_info(self) -> List[Dict[str, Any]]:
        """Информация о всех автоматически сгенерированных функциях"""
        auto_funcs = []
        
        if self._auto_click_function and self._auto_click_info:
            auto_funcs.append({
                "name": self._auto_click_function,
                "event_type": "click",
                "navigate": self._auto_click_info.get("navigate"),
                "purpose": self._auto_click_info.get("purpose"),
                "node_id": self._original_node.get("id"),
                "category": self._node_category.get("name") if self._node_category else None
            })
        
        if self._auto_position_function and self._auto_position_info:
            auto_funcs.append({
                "name": self._auto_position_function,
                "event_type": "position", 
                "navigate": self._auto_position_info.get("navigate"),
                "purpose": self._auto_position_info.get("purpose"),
                "node_id": self._original_node.get("id"),
                "category": self._node_category.get("name") if self._node_category else None
            })
        
        # Автоматическая функция отрисовки
        if self.auto_draw_value_cb_name and not self.draw_value_cb:
            auto_funcs.append({
                "name": self.auto_draw_value_cb_name,
                "event_type": "draw_value",
                "navigate": None,  # Для отрисовки навигация не применима
                "purpose": "draw_value",
                "node_id": self._original_node.get("id"),
                "category": self._node_category.get("name") if self._node_category else None
            })
        
        return auto_funcs
    
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
        print("📋 " + _("Detailed callback info for {node_id} ({type}_{role}):").format(
            node_id=node_id, type=self._node_type, role=self._node_role))
        
        for cb_type, info in self.all_callback_infos.items():
            if info:
                custom_flag = "🎛️ CUSTOM" if info["custom"] else "⚙️ AUTO"
                print("  " + _("{cb_type}:").format(cb_type=cb_type))
                print("    " + _("Name: {name} ({flag})").format(name=info['name'], flag=custom_flag))
                print("    " + _("Type: {type}").format(type=info['type']))
                print("    " + _("Role: {role}").format(role=info['role']))
                print("    " + _("C Type: {c_type}").format(c_type=info['c_type']))
                print("    " + _("Category: {category}").format(category=info['category']))
            else:
                print("  " + _("{cb_type}: None").format(cb_type=cb_type))

    def print_control_info(self, node_id: str, node_role: str, controls_config: List[str] = None):
        """Печатает информацию о контролах для отладки"""
        print(_("Control info for {id} (role: {role}):").format(id=node_id, role=node_role))
        if controls_config:
            print("  " + _("Config from JSON: {config}").format(config=controls_config))
        
        # Показываем пользовательские callback'ы
        if self.has_custom_callbacks:
            print("  " + _("Custom callbacks:"))
            for cb_name, cb_value in self.custom_callbacks_summary.items():
                if cb_value and cb_name != "auto_draw_value_cb":
                    print("    " + _("- {cb_name}: {cb_value}").format(cb_name=cb_name, cb_value=cb_value))
        
        # Показываем автоматические функции
        if self._auto_click_function:
            print("  " + _("Auto click function: {name}").format(name=self._auto_click_function))
        if self._auto_position_function:
            print("  " + _("Auto position function: {name}").format(name=self._auto_position_function))
        
        # Показываем функцию отрисовки
        if self.effective_draw_value_cb:
            source = "custom" if self.draw_value_cb else "auto"
            print("  " + _("Draw value function: {name} ({source})").format(
                name=self.effective_draw_value_cb, source=source))