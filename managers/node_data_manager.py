from typing import Dict, List, Optional, Set, Any
from menu_data import MenuData

class NodeDataManager:
    """Менеджер для управления данными узла: значения, факторы, типы данных и категории"""
    
    def __init__(self, original_node: Dict[str, Any], menu_data: MenuData):
        self._original_node = original_node
        self._menu_data = menu_data
        
        # Данные значения из JSON
        self.min = original_node.get("min")
        self.max = original_node.get("max")
        self.default = original_node.get("default")
        self.default_idx = original_node.get("default_idx")
        self.factors = original_node.get("factors")
        self.values = original_node.get("values")
        self._step = original_node.get("step")
        
        # Базовые свойства типа и роли
        self._node_type = original_node.get("type")
        self._node_role = original_node.get("role")

    # Свойства типа данных
    @property
    def type(self) -> Optional[str]:
        """Тип данных узла"""
        return self._node_type

    @property
    def role(self) -> Optional[str]:
        """Роль узла"""
        return self._node_role

    @property
    def c_type(self) -> Optional[str]:
        """C-тип данных для генерации кода"""
        if self._node_type is None:
            return None
        return self._menu_data.c_type(self._node_type)

    @property
    def category_name(self) -> Optional[str]:
        """Имя категории (type_role)"""
        if self._node_type is None or self._node_role is None:
            return None
        return f"{self._node_type}_{self._node_role}"

    @property
    def category(self) -> Optional[Dict[str, Any]]:
        """Полная информация о категории"""
        if self._node_type is None or self._node_role is None:
            return None
        return {
            "name": self.category_name,
            "type": self._node_type,
            "role": self._node_role,
            "c_type": self.c_type
        }

    # Свойства значений и факторов
    @property
    def step(self) -> int:
        """Шаг изменения значения"""
        if self._step is None:
            return 1
        return self._step

    @step.setter
    def step(self, step: int):
        """Установка шага изменения значения"""
        self._step = step

    @property
    def fixed_count(self) -> Optional[int]:
        """Количество факторов (для fixed типов)"""
        if self.factors is None:
            return None
        return len(self.factors)

    @property
    def values_count(self) -> Optional[int]:
        """Количество значений (для fixed типов)"""
        if self.values is None:
            return None
        return len(self.values)

    @property
    def values_default_idx(self) -> Optional[int]:
        """Индекс значения по умолчанию"""
        if self.values is None:
            return None
        if self.default_idx is None:
            return 0
        return self.default_idx

    @property
    def factors_default_idx(self) -> Optional[int]:
        """Индекс фактора по умолчанию"""
        if self.factors is None:
            return None
        if self.default_idx is None:
            return 0
        return self.default_idx

    # Методы для генерации C-кода
    def c_str_array(self, values: List) -> Optional[str]:
        """Конвертация значений в C-строку массива"""
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
    def c_str_factors(self) -> Optional[str]:
        """C-представление факторов"""
        if self.factors is None:
            return None
        return self.c_str_array(self.factors)

    @property
    def c_str_values(self) -> Optional[str]:
        """C-представление значений"""
        if self.values is None:
            return None
        return self.c_str_array(self.values)

    # Валидация данных
    def validate_numeric_range(self) -> List[str]:
        """Валидация числового диапазона"""
        errors = []
        if self.min is not None and self.max is not None:
            if self.min > self.max:
                errors.append(f"min ({self.min}) > max ({self.max})")
            if self.default is not None and not (self.min <= self.default <= self.max):
                errors.append(f"default ({self.default}) outside range [{self.min}, {self.max}]")
        return errors

    def validate_fixed_values(self) -> List[str]:
        """Валидация фиксированных значений"""
        errors = []
        if self.values is not None and self.default_idx is not None:
            if self.default_idx >= len(self.values):
                errors.append(f"default_idx ({self.default_idx}) out of bounds for values array (size: {len(self.values)})")
        if self.factors is not None and self.default_idx is not None:
            if self.default_idx >= len(self.factors):
                errors.append(f"default_idx ({self.default_idx}) out of bounds for factors array (size: {len(self.factors)})")
        return errors

    def get_data_summary(self) -> Dict[str, Any]:
        """Сводка данных узла для отладки"""
        return {
            "id": self._original_node.get("id"),
            "type": self._node_type,
            "role": self._node_role,
            "category": self.category_name,
            "c_type": self.c_type,
            "min": self.min,
            "max": self.max,
            "default": self.default,
            "default_idx": self.default_idx,
            "step": self.step,
            "factors_count": self.fixed_count,
            "values_count": self.values_count,
            "has_factors": self.factors is not None,
            "has_values": self.values is not None
        }

    def __repr__(self):
        """Строковое представление для отладки"""
        summary = self.get_data_summary()
        return (f"NodeDataManager({summary['id']}, type={summary['type']}, "
                f"role={summary['role']}, c_type={summary['c_type']})")