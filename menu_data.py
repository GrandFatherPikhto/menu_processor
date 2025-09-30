import json
from typing import Dict, Any, Set, List, Tuple, Optional
from pathlib import Path
from enum import Enum

from menu_config import MenuConfig, ConfigError

class ControlType(Enum):
    CLICK = "click"
    POSITION = "position"

class NavigationType(Enum):
    LIMIT = "limit"
    CYCLIC = "cyclic"

class MenuData:
    def __init__(self, config: MenuConfig):
        self._config = config
        self._data_config = config.data_config
        self._roles: Dict[str, List] = self._data_config.get("roles") or {}
        self._types: Dict[str, Dict[str, str]] = self._data_config.get("types") or {}
        self._controls: Dict[str, List[str]] = self._data_config.get("controls", {}) or {}
        self._navigation_rules: Dict[str, Dict[str, Any]] = self._data_config.get("navigation_rules", {}) or {}
        self._role_rules: Dict[str, Any] = self._data_config.get("role_rules", {}) or {}
        
        # Создаем обратное отображение: тип -> роль
        self._type_to_roles: Dict[str, List[str]] = self._build_type_to_role_mapping()

    def _build_type_to_role_mapping(self) -> Dict[str, List[str]]:
        """Создает отображение типа на список ролей"""
        mapping = {}
        for role, types in self._roles.items():
            for type_name in types:
                if type_name not in mapping:
                    mapping[type_name] = []
                mapping[type_name].append(role)
        return mapping

    def get_controls_for_type(self, type_name: str) -> Set[ControlType]:
        """Возвращает доступные контролы для типа"""
        roles = self.get_roles_for_type(type_name)
        if not roles:
            return set()
            
        # Просто собираем контролы из всех ролей типа
        all_controls = set()
        for role in roles:
            control_names = self._controls.get(role, [])
            all_controls.update({ControlType(name) for name in control_names})
                
        return all_controls

    def get_roles_for_type(self, type_name: str) -> List[str]:
        return self._type_to_roles.get(type_name, [])

    def get_navigation_rules(self, control: ControlType) -> Tuple[List[NavigationType], NavigationType]:
        """Возвращает правила навигации для контроля"""
        rules = self._navigation_rules.get(control.value, {})
        allowed_navigate = [NavigationType(nav) for nav in rules.get("allowed_navigate", [])]
        default_navigate = NavigationType(rules.get("default", "cyclic"))
        return allowed_navigate, default_navigate

    def is_valid_navigation(self, control: ControlType, navigate: NavigationType) -> bool:
        """Проверяет, допустима ли комбинация control + navigate"""
        allowed_navigate, _ = self.get_navigation_rules(control)
        return navigate in allowed_navigate

    def get_default_navigation(self, control: ControlType) -> NavigationType:
        """Возвращает navigate по умолчанию для контроля"""
        _, default_navigate = self.get_navigation_rules(control)
        return default_navigate
    
    def type(self, name: str) -> Dict[str, str] | None:
        return self._types.get(name)
    
    def c_type(self, name: str) -> str | None:
        type_data = self._types.get(name)
        if type_data is None:
            return None
        return type_data.get("c_type")
    
    def role(self, name: str) -> List | None:
        return self._roles.get(name)

    def role_types(self, name: str) -> List | None:
        if self._roles.get(name) is None:
            return None
        return self._roles[name]

    def get_role_rules(self, role: str) -> Optional[Dict[str, Any]]:
        """Возвращает правила для указанной роли"""
        return self._role_rules.get(role)

    def get_control_config(self, role: str, control: ControlType, 
                        node_controls: Optional[List[str]] = None,
                        node_navigate: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Возвращает конфигурацию контроля для роли с учетом переопределений"""
        rules = self.get_role_rules(role)
        if not rules:
            return None
        
        # Проверяем, разрешен ли данный контроль для роли
        allowed_controls = rules.get("allowed_controls", [])
        
        # Если в узле указаны конкретные контролы, проверяем по ним
        if node_controls is not None:
            if control.value not in node_controls:
                return None
        # Иначе проверяем по правилам роли по умолчанию
        elif control.value not in allowed_controls:
            return None
        
        # Получаем правила для конкретного контроля
        control_rules = rules.get(control.value, {})
        if not control_rules:
            return None
        
        # Для click всегда используем cyclic, для position можно переопределить
        if control == ControlType.CLICK:
            navigate = NavigationType.CYCLIC
        else:
            navigate_str = node_navigate if node_navigate else control_rules.get("navigate", "limit")
            navigate = NavigationType(navigate_str)
        
        return {
            "purpose": control_rules.get("purpose"),
            "navigate": navigate,
            "required": control_rules.get("required", False)
        }

    @property
    def roles(self) -> Set[str]:
        return {role for role in self._roles}
    
    @property
    def types(self) -> Set[str]:
        return {type for type in self._types}
    
    def navigation_rule(self, name: str) -> Dict[str, List[str]] | None:
        return self._navigation_rules.get(name, None)

    @property
    def navigation_rules(self) -> Dict[str, Dict[str, List[str]]] | None:
        return self._navigation_rules

def main(config_file: str):
    try:
        config = MenuConfig(config_file)
        print(f"✅ Конфигурация {config_file} успешно загружена")
        data = MenuData(config)
        print("Roles:")
        print(data.roles)
        print("Types:")
        print(data.types)

        print("Byte config:")
        print(data.type('byte'))
        print("Default Navigation 4 factor:")
        print(data.get_default_navigation(ControlType.POSITION))
        print("Controls 4 Type ubyte")
        print(data.get_controls_for_type("ubyte"))

        # Тестируем новые методы
        print("\n--- Role Rules Test ---")
        for role in data.roles:
            rules = data.get_role_rules(role)
            print(f"Role '{role}': {rules}")

        print("\n--- Control Config Test ---")
        test_role = "factor"
        for control in [ControlType.CLICK, ControlType.POSITION]:
            config = data.get_control_config(test_role, control, "limit")
            print(f"Role '{test_role}' + Control '{control.value}': {config}")

    except ConfigError as e:
        print(f"❌ {e}")
        return 1

if __name__ == "__main__":
    main('./config/config.json')
