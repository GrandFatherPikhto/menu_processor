from menu_error import MenuError
from typing import Dict, List, Optional, Any

class MenuValidator:
    """Класс для валидации структуры меню"""
    
    VALID_TYPES = {'action_menu', 'action_int', 'action_int_factor', 
                  'action_callback', 'action_bool', 
                  'action_fixed_int', 'action_fixed_float', 'action_fixed_string'}
    
    def __init__(self):
        self.errors: List[MenuError] = []
        self.used_ids: set = set()
    
    def validate(self, menu_data: Dict) -> bool:
        """Основной метод валидации"""
        self.errors.clear()
        self.used_ids.clear()
        
        if 'menu' not in menu_data or not menu_data['menu']:
            self.errors.append(MenuError("Отсутствуют элементы меню"))
            return False
        
        for i, root_item in enumerate(menu_data['menu']):
            self._validate_node(root_item, [f"menu[{i}]"])
        
        return len(self.errors) == 0
    
    def _validate_node(self, node: Dict, path: List[str]) -> None:
        """Рекурсивная валидация узла"""
        current_path = path + [node.get('title', 'unknown')]
        
        # Проверка обязательных полей
        self._check_required_fields(node, current_path)
        
        # Проверка уникальности ID
        self._check_unique_id(node, current_path)
        
        # Проверка валидности типа
        if 'type' in node and node['type'] not in self.VALID_TYPES:
            self.errors.append(MenuError(
                f"Неверный тип '{node['type']}'. Допустимо: {sorted(self.VALID_TYPES)}",
                current_path
            ))
        
        # Проверка специфичных полей для типа
        self._validate_type_specific_fields(node, current_path)
        
        # Рекурсивная проверка дочерних элементов
        for j, child in enumerate(node.get('children', [])):
            self._validate_node(child, current_path + [f"children[{j}]"])
    
    def _check_required_fields(self, node: Dict, path: List[str]) -> None:
        """Проверка обязательных полей"""
        required_fields = ['title', 'type']
        for field in required_fields:
            if field not in node:
                self.errors.append(MenuError(
                    f"Отсутствует обязательное поле '{field}'",
                    path
                ))
    
    def _check_unique_id(self, node: Dict, path: List[str]) -> None:
        """Проверка уникальности ID"""
        node_id = node.get('id')
        if node_id:
            if node_id in self.used_ids:
                self.errors.append(MenuError(
                    f"Дублирующийся ID '{node_id}'",
                    path
                ))
            else:
                self.used_ids.add(node_id)
    
    def _validate_type_specific_fields(self, node: Dict, path: List[str]) -> None:
        """Валидация полей, специфичных для типа"""
        if 'type' not in node:
            return
        
        type_validators = {
            'action_int': self._validate_action_int,
            'action_int_factor': self._validate_action_int_factor,
            'action_callback': self._validate_action_callback,
            'action_bool': self._validate_action_bool,
            'action_fixed_int': self._validate_action_fixed_int,
            'action_fixed_float': self._validate_action_fixed_float,
            'action_fixed_string': self._validate_action_fixed_string
        }
        
        validator = type_validators.get(node['type'])
        if validator:
            validator(node, path)
    
    def _validate_action_int(self, node: Dict, path: List[str]) -> None:
        """Валидация action_int"""
        required_fields = ['min', 'max']
        for field in required_fields:
            if field not in node:
                self.errors.append(MenuError(
                    f"Для action_int обязательно поле '{field}'",
                    path
                ))
    
    def _validate_action_int_factor(self, node: Dict, path: List[str]) -> None:
        """Валидация action_int_factor"""
        required_fields = ['min', 'max', 'factors']
        for field in required_fields:
            if field not in node:
                self.errors.append(MenuError(
                    f"Для action_int_factor обязательно поле '{field}'",
                    path
                ))
    
    def _validate_action_callback(self, node: Dict, path: List[str]) -> None:
        """Валидация action_callback"""
        pass

    def _validate_action_fixed_int(self, node: Dict, path: List[str]) -> None:
        """Валидация action_fixed_int"""
        required_fields = ["massif"]
        for field in required_fields:
            if field not in node:
                self.errors.append(MenuError(
                    f"Для action_callback обязательно поле '{field}'",
                    path
                ))

    def _validate_action_fixed_float(self, node: Dict, path: List[str]) -> None:
        """Валидация action_fixed_float"""
        required_fields = ["massif"]
        for field in required_fields:
            if field not in node:
                self.errors.append(MenuError(
                    f"Для action_callback обязательно поле '{field}'",
                    path
                ))

    def _validate_action_fixed_string(self, node: Dict, path: List[str]) -> None:
        """Валидация action_fixed_string"""
        required_fields = ["ids", "massif", "ids"]
        for field in required_fields:
            if field not in node:
                self.errors.append(MenuError(
                    f"Для action_fixed_string обязательно поле '{field}'",
                    path
                ))

    def _validate_action_bool(self, node: Dict, path: List[str]) -> None:
        """Валидация action_bool"""
        pass
        # required_fields = ["default"]
        # for field in required_fields:
        #     if field not in node:
        #         self.errors.append(MenuError(
        #             f"Для action_bool обязательно поле '{field}'",
        #             path
        #         ))

    
    def get_errors(self) -> List[MenuError]:
        """Получить список ошибок"""
        return self.errors

