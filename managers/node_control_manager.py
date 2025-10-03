from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from menu_data import MenuData, ControlType
from managers.callback_manager import CallbackManager
from managers.function_info import FunctionInfo

class NodeControlManager:
    """Менеджер для управления контролами узла и генерации автоматических функций"""
    
    def __init__(self, node_id: str, node_type: str, node_role: str, node_c_type: str, 
                 original_node: Dict[str, Any], menu_data: MenuData, 
                 callback_manager: CallbackManager, node_navigate: Optional[str] = None):
        self._node_id = node_id
        self._node_type = node_type
        self._node_role = node_role
        self._node_c_type = node_c_type
        self._original_node = original_node
        self._menu_data = menu_data
        self._callback_manager = callback_manager
        self._node_navigate = node_navigate
        
        # Конфигурация контролов из JSON
        self._controls_config = original_node.get("controls")
        self._controls = []
        
        # Инициализация контролов
        self._init_controls()

    def _init_controls(self):
        """Инициализация контролов на основе роли, правил MenuData и конфигурации узла"""
        if self._node_type is None or self._node_role is None:
            return
            
        self._controls = []
        
        # Если заданы пользовательские callback'ы, игнорируем автоматические контролы для них
        use_auto_click = self._callback_manager.click_cb is None
        use_auto_position = self._callback_manager.position_cb is None
        
        # print(f"DEBUG {self._node_id}: use_auto_click={use_auto_click}, use_auto_position={use_auto_position}")
        
        # Для role=factor всегда используем оба контрола, если не заданы пользовательские callback'ы
        if self._node_role == "factor":
            controls_to_check = []
            if use_auto_click:
                controls_to_check.append(ControlType.CLICK)
            if use_auto_position:
                controls_to_check.append(ControlType.POSITION)
            # print(f"DEBUG {self._node_id}: factor role, controls_to_check={[c.value for c in controls_to_check]}")
        else:
            # Для других ролей: если указаны controls в узле, используем их, иначе оба
            if self._controls_config:
                controls_to_check = [ControlType(ctrl) for ctrl in self._controls_config]
            else:
                controls_to_check = [ControlType.CLICK, ControlType.POSITION]
            
            # print(f"DEBUG {self._node_id}: non-factor role, controls_config={self._controls_config}, controls_to_check={[c.value for c in controls_to_check]}")
            
            # Фильтруем контролы в соответствии с пользовательскими callback'ами
            if not use_auto_click and ControlType.CLICK in controls_to_check:
                controls_to_check.remove(ControlType.CLICK)
            if not use_auto_position and ControlType.POSITION in controls_to_check:
                controls_to_check.remove(ControlType.POSITION)
        
        # print(f"DEBUG {self._node_id}: final controls_to_check={[c.value for c in controls_to_check]}")
        
        # Обрабатываем каждый контроль
        auto_click_info = None
        auto_position_info = None
        
        for control_type in controls_to_check:
            control_config = self._menu_data.get_control_config(
                self._node_role, control_type, self._controls_config, self._node_navigate
            )
            
            # print(f"DEBUG {self._node_id}: control_type={control_type}, control_config={control_config}")
            
            if control_config:
                self._controls.append({
                    "type": control_type,
                    "purpose": control_config["purpose"],
                    "navigate": control_config["navigate"],
                    "required": control_config["required"]
                })
                
                # Генерируем имя функции и сохраняем информацию
                function_name = self._generate_function_name(control_type, control_config)
                auto_info = {
                    "name": function_name,
                    "navigate": control_config["navigate"].value,  # 'cyclic' или 'limit'
                    "purpose": control_config["purpose"],
                    "control_type": control_type.value
                }
                
                # print(f"DEBUG {self._node_id}: generated function {function_name} with navigate={auto_info['navigate']}")
                
                if control_type == ControlType.CLICK:
                    auto_click_info = auto_info
                elif control_type == ControlType.POSITION:
                    auto_position_info = auto_info
        
        # print(f"DEBUG {self._node_id}: calling set_auto_functions with click={auto_click_info}, position={auto_position_info}")
        
        # Устанавливаем автоматические функции в CallbackManager с дополнительной информацией
        self._callback_manager.set_auto_functions(auto_click_info, auto_position_info)

    def _generate_function_name(self, control: ControlType, control_config: Dict) -> str:
        """Генерирует имя функции в соответствии с правилами"""
        base_name = f"{self._node_type}_{self._node_role}"
        
        # Специальный случай для factor роли при изменении индекса
        if self._node_role == "factor" and control_config["purpose"] == "change_factor_index":
            name = f"{base_name}_{control.value}_{control_config['navigate'].value}_factor"
        else:
            name = f"{base_name}_{control.value}_{control_config['navigate'].value}"
        
        # Добавляем постфикс _cb для автоматических функций
        return name + "_cb"

    # Свойства для доступа к контролам
    @property
    def controls(self) -> List[Dict]:
        """Список контролов узла"""
        return self._controls

    @property
    def controls_config(self) -> Optional[List[str]]:
        """Конфигурация контролов из JSON"""
        return self._controls_config

    @property
    def has_controls(self) -> bool:
        """Имеет ли узел контролы"""
        return len(self._controls) > 0

    @property
    def required_controls(self) -> List[Dict]:
        """Обязательные контролы"""
        return [control for control in self._controls if control.get("required", False)]

    @property
    def has_required_controls(self) -> bool:
        """Имеет ли узел обязательные контролы"""
        return any(control.get("required", False) for control in self._controls)

    # Свойства для доступа к функциям
    # @property
    # def all_function_infos(self) -> List[Dict[str, Any]]:
    #     """Все возможные функции обработки для этого узла с полной информацией"""
    #     infos = []
        
    #     # Добавляем информацию из автоматических функций
    #     auto_funcs = self._callback_manager.auto_functions_info
    #     # print(f"DEBUG all_function_infos for {self._node_id}: auto_funcs = {auto_funcs}")
        
    #     for auto_func in auto_funcs:
    #         infos.append({
    #             "name": auto_func["name"],
    #             "node_id": self._node_id,
    #             "event_type": auto_func["event_type"],
    #             "navigate": auto_func["navigate"],
    #             "purpose": auto_func["purpose"],
    #             "source": "auto_generated",
    #             "type": self._node_type,
    #             "role": self._node_role,
    #             "c_type": self._node_c_type,
    #             "category": f"{self._node_type}_{self._node_role}"
    #         })

    @property
    def all_function_infos(self) -> List[Dict[str, Any]]:
        """Все возможные функции обработки для этого узла с полной информацией"""
        infos = []
        
        # Автоматические функции через dataclass
        for auto_func in self._callback_manager.auto_functions_info:
            function_info = FunctionInfo.create_auto(
                self._node_id, self._node_type, self._node_role, self._node_c_type,
                auto_func["name"], auto_func["event_type"], 
                auto_func["navigate"], auto_func["purpose"]
            )
            infos.append(asdict(function_info))
        
        # Пользовательские функции через dataclass
        for cb_type, cb_info in self._callback_manager.defined_callback_infos.items():
            if cb_info and cb_info["custom"]:
                # Проверяем, нет ли дублирования с автоматическими функциями
                if not any(info["name"] == cb_info["name"] for info in infos):
                    function_info = FunctionInfo.create_custom(
                        self._node_id, self._node_type, self._node_role, self._node_c_type,
                        cb_info
                    )
                    infos.append(asdict(function_info))
        
        return infos        
        # Добавляем пользовательские callback'и (кроме тех, что уже есть в auto_functions_info)
        for cb_type, cb_info in self._callback_manager.defined_callback_infos.items():
            if cb_info and cb_info["custom"]:
                # Проверяем, нет ли уже этой функции в auto_functions_info
                existing_func = next((f for f in infos if f["name"] == cb_info["name"]), None)
                if not existing_func:
                    # ИСПРАВЛЕНИЕ: безопасное извлечение категории
                    category_value = None
                    if cb_info.get("category"):
                        # Если category - это словарь, берем name, если строка - используем как есть
                        if isinstance(cb_info["category"], dict):
                            category_value = cb_info["category"].get("name")
                        else:
                            category_value = cb_info["category"]
                    
                    infos.append({
                        "name": cb_info["name"],
                        "node_id": self._node_id,
                        "event_type": cb_info["event_type"],
                        "navigate": cb_info.get("navigate"),
                        "purpose": cb_info.get("purpose", "user_defined"),
                        "source": "custom",
                        # ДОБАВЛЯЕМ type и role из cb_info
                        "type": cb_info.get("type"),
                        "role": cb_info.get("role"),
                        "category": category_value  # Используем безопасно извлеченное значение
                    })
        
        # print(f"DEBUG all_function_infos for {self._node_id}: result = {[info['name'] for info in infos]}")
        return infos

    @property
    def detailed_function_infos(self) -> Dict[str, Dict[str, Any]]:
        """Детальная информация о всех функциях, сгруппированная по именам"""
        return {info["name"]: info for info in self.all_function_infos}

    # Методы для проверки обязательных функций
    def validate_required_functions(self) -> List[Dict[str, str]]:
        """Проверяет, что все обязательные функции сгенерированы"""
        missing_functions = []
        
        for control in self._controls:
            if control.get("required", False):
                function_name = None
                if control["type"] == ControlType.CLICK:
                    function_name = self._callback_manager._auto_click_function
                elif control["type"] == ControlType.POSITION:
                    function_name = self._callback_manager._auto_position_function
                
                if not function_name:
                    missing_functions.append({
                        "node": self._node_id,
                        "control": control["type"].value,
                        "purpose": control["purpose"]
                    })
        
        return missing_functions

    def get_control_summary(self) -> Dict[str, Any]:
        """Сводка по контролам для отладки"""
        return {
            "node_id": self._node_id,
            "type": self._node_type,
            "role": self._node_role,
            "navigate": self._node_navigate,
            "controls_config": self._controls_config,
            "controls": [
                {
                    "type": control["type"].value,
                    "purpose": control["purpose"],
                    "navigate": control["navigate"].value,
                    "required": control["required"]
                }
                for control in self._controls
            ],
            "has_required_controls": self.has_required_controls,
            "required_controls_count": len(self.required_controls),
            "all_functions_count": len(self.all_function_infos),
            "auto_click_function": self._callback_manager._auto_click_function,
            "auto_position_function": self._callback_manager._auto_position_function
        }

    def print_control_info(self):
        """Печатает информацию о контролах для отладки"""
        summary = self.get_control_summary()
        print(f"Control info for {self._node_id} (role: {self._node_role}):")
        
        if summary["controls_config"]:
            print(f"  Config from JSON: {summary['controls_config']}")
        
        if summary["controls"]:
            print(f"  Active controls: {[ctrl['type'] for ctrl in summary['controls']]}")
        
        # Показываем пользовательские callback'ы
        if self._callback_manager.has_custom_callbacks:
            print("  Custom callbacks:")
            for cb_name, cb_value in self._callback_manager.custom_callbacks_summary.items():
                if cb_value and cb_name != "auto_draw_value_cb":
                    print(f"    - {cb_name}: {cb_value}")
        
        # Показываем автоматические функции
        if self._callback_manager._auto_click_function:
            print(f"  Auto click function: {self._callback_manager._auto_click_function}")
        if self._callback_manager._auto_position_function:
            print(f"  Auto position function: {self._callback_manager._auto_position_function}")
        
        # Показываем функцию отрисовки
        if self._callback_manager.effective_draw_value_cb:
            source = "custom" if self._callback_manager.draw_value_cb else "auto"
            print(f"  Draw value function: {self._callback_manager.effective_draw_value_cb} ({source})")

    def __repr__(self):
        """Строковое представление для отладки"""
        return (f"NodeControlManager({self._node_id}, controls={len(self._controls)}, "
                f"functions={len(self.all_function_infos)})")