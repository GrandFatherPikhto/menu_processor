import json
from typing import Dict, List, Optional, Any, Set
from pathlib import Path

class DataTypeConfig:
    """Класс для работы с конфигурацией типов данных из JSON файла."""
    
    def __init__(self, config_file: str = "config/types.json"):
        """
        Инициализация класса с загрузкой конфигурации из JSON файла.
        
        Args:
            config_file: Путь к JSON файлу с конфигурацией
        """
        self.config_file = config_file
        self._types = self._load_config()
    
    def _load_config(self) -> Dict[str, Dict[str, Any]]:
        """
        Загрузка конфигурации из JSON файла.
        
        Returns:
            Словарь с конфигурацией типов данных
            
        Raises:
            FileNotFoundError: Если файл конфигурации не найден
            JSONDecodeError: Если файл содержит некорректный JSON
        """
        config_path = Path(self.config_file)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Конфигурационный файл '{self.config_file}' не найден")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_by_type(self, type: str) -> Optional[Dict[str, Any]]:
        """
        Получить конфигурацию по типу данных.
        
        Args:
            type: Название типа данных (например, 'byte', 'float')
            
        Returns:
            Словарь с конфигурацией или None, если тип не найден
        """
        return self._types.get(type)
    
    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Получить все конфигурации по категории.
        
        Args:
            category: Категория для поиска ('simple', 'fixed', 'factor', 'callback')
            
        Returns:
            Список конфигураций, удовлетворяющих критерию
        """
        return [config for config in self._types.values() 
                if config.get('category') == category]
    
    def get_by_media(self, media: str) -> List[Dict[str, Any]]:
        """
        Получить все конфигурации по медиа-типу.
        
        Args:
            media: Медиа-тип для поиска ('number', 'string', 'boolean', 'void')
            
        Returns:
            Список конфигураций, удовлетворяющих критерию
        """
        return [config for config in self._types.values() 
                if config.get('media') == media]
    
    def get_all_categories(self) -> Set[str]:
        """
        Получить все уникальные категории.
        
        Returns:
            Множество всех категорий
        """
        return {config.get('category') for config in self._types.values()}
    
    def get_all_media_types(self) -> Set[str]:
        """
        Получить все уникальные медиа-типы.
        
        Returns:
            Множество всех медиа-типов
        """
        return {config.get('media') for config in self._types.values()}
    
    def get_all_types(self) -> Set[str]:
        """
        Получить все уникальные типы данных.
        
        Returns:
            Множество всех типов данных
        """
        return {config.get('type') for config in self._types.values()}
    
    def get_all_config_names(self) -> List[str]:
        """
        Получить список всех имен конфигураций (ключей).
        
        Returns:
            Список названий типов данных
        """
        return list(self._types.keys())
    
    def get_all_configs(self) -> List[Dict[str, Any]]:
        """
        Получить все конфигурации.
        
        Returns:
            Список всех конфигураций
        """
        return list(self._types.values())
    
    def has_type(self, type: str) -> bool:
        """
        Проверить, существует ли тип данных.
        
        Args:
            type: Название типа данных для проверки
            
        Returns:
            True если тип существует, иначе False
        """
        return type in self._types
    
    def get_c_type(self, type: str) -> Optional[str]:
        """
        Получить C-тип для указанного типа данных.
        
        Args:
            type: Название типа данных
            
        Returns:
            Соответствующий C-тип или None
        """
        config = self.get_by_type(type)
        return config.get('c_type') if config else None
    
    def reload_config(self) -> None:
        """
        Перезагрузить конфигурацию из файла.
        """
        self._types = self._load_config()
    
    def get_stats(self) -> Dict[str, int]:
        """
        Получить статистику по конфигурации.
        
        Returns:
            Словарь со статистикой
        """
        return {
            'total_types': len(self._types),
            'categories_count': len(self.get_all_categories()),
            'media_types_count': len(self.get_all_media_types()),
            'unique_types': len(self.get_all_types())
        }

# Пример использования
if __name__ == "__main__":
    try:
        config = DataTypeConfig("config/types.json")
        
        # 1. Получение конфигурации по типу
        byte_config = config.get_by_type('byte')
        print("Конфигурация для 'byte':", byte_config)
        
        # 2. Поиск по категории
        simple_types = config.get_by_category('simple')
        print(f"\nПростые типы (simple) - {len(simple_types)} шт:")
        for item in simple_types:
            print(f"  - {item['type']}")
        
        # 3. Поиск по медиа-типу
        number_types = config.get_by_media('number')
        print(f"\nЧисловые типы (number) - {len(number_types)} шт:")
        for item in number_types[:5]:  # Покажем первые 5 для краткости
            print(f"  - {item['type']}")
        
        # 4. Получение всех категорий, медиа-типов и типов данных
        print(f"\nВсе категории: {config.get_all_categories()}")
        print(f"Все медиа-типы: {config.get_all_media_types()}")
        print(f"Все типы данных: {config.get_all_types()}")
        
        # 5. Статистика
        stats = config.get_stats()
        print(f"\nСтатистика:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # 6. Получение C-типа
        c_type = config.get_c_type('dword')
        print(f"\nC-тип для 'dword': {c_type}")
        
    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
    except json.JSONDecodeError as e:
        print(f"Ошибка парсинга JSON: {e}")