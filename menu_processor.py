import json
from collections import deque
from typing import Dict, List, Optional, Any


from menu_config import MenuConfig
from menu_error import MenuError
from menu_validator import MenuValidator
from menu_flattener import MenuFlattener

class MenuProcessor:
    """Основной класс для обработки всего меню"""
    
    def __init__(self):
        self.config = MenuConfig()
        self.validator = MenuValidator()
        self.flattener = MenuFlattener()
        self.menu_structure: Dict[str, Dict] = {}
        self.unique_types = set()
        self.click_items = set()
        self.position_items = set()
        self.factor_items = set()
    
    def load_menu_file(self, input_file: str) -> bool:
        """Загрузка и валидация всего файла меню"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                menu_data = json.load(f)
            
            # Загружаем конфигурацию
            if 'config' in menu_data:
                self.config.load_from_dict(menu_data['config'])
            
            # Валидируем конфигурацию
            config_errors = self.config.validate()
            if config_errors:
                print("❌ Ошибки конфигурации:")
                for error in config_errors:
                    print(f"   - {error}")
                return False
            
            # Валидируем структуру меню
            if not self.validator.validate(menu_data):
                self._print_validation_errors()
                return False
            
            # Уплощаем меню
            menu_items = menu_data.get('menu', [])
            self.menu_structure = self.flattener.flatten(menu_items)

            self.get_unique_types()
            self.separate_items_by_change_type()
            
            return True
            
        except FileNotFoundError:
            print(f"❌ Файл {input_file} не найден")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка JSON: {e}")
            return False
        except MenuError as e:
            print(f"❌ Ошибка обработки меню: {e}")
            return False
    
    def generate_output(self, output_file: str = None) -> bool:
        """Генерация выходных файлов"""
        if not self.menu_structure:
            print("❌ Нет данных меню для генерации")
            return False
        
        try:
            output_path = output_file or 'menu_output.json'
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.menu_structure, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Уплощенное меню сохранено в {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка генерации: {e}")
            return False
    
    def _print_validation_errors(self) -> None:
        """Вывод ошибок валидации"""
        print("❌ Ошибки валидации структуры меню:")
        for error in self.validator.get_errors():
            print(f"   - {error}")
    
    def print_summary(self) -> None:
        """Вывод сводной информации"""
        if not self.menu_structure:
            print("❌ Данные не загружены")
            return
        
        print("\n📊 Сводная информация:")
        print(f"   Элементов меню: {len(self.menu_structure)}")
        
        # Статистика по использованию ID
        explicit_ids = sum(1 for item in self.menu_structure.values() 
                          if 'original_id' in item)
        generated_ids = len(self.menu_structure) - explicit_ids - 1  # -1 для root
        
        print(f"   Явно указанных ID: {explicit_ids}")
        print(f"   Сгенерированных ID: {generated_ids}")
        
        # Проверяем root
        root = self.menu_structure.get('root')
        if root and 'first_child' in root:
            print(f"   Первый элемент меню: {root['first_child']}")

    def get_unique_types(self):
        self.unique_types = set()
        for item_id, item_data in self.menu_structure.items():
            if 'type' in item_data:
                self.unique_types.add(item_data['type'])
            else:
                print(f"Warning: Item {item_id} missing 'type' field")

    def separate_items_by_change_type(self):
        self.click_items = set()
        self.position_items = set()
        self.factor_items = set()
        for node_id, node in self.menu_structure.items():
            if node['type'] == 'action_menu' or node['type'] == 'action_callback': next
            change = node.get('change', None)
            if change == None: next
            if change == 'click': self.click_items.add(node['id'])
            if change == 'position' : self.position_items.add(node['id'])
            if change == 'factor' : self.factor_items.add(node['id'])
        

    def get_config(self) -> MenuConfig:
        """Геттер для конфигурации"""
        return self.config
    
    def get_flattened_menu(self) -> Dict[str, Dict]:
        """Геттер для уплощенного меню"""
        return self.menu_structure.copy()  # Возвращаем копию для безопасности
    
    def get_template_path(self, name: str) -> Optional[str]:
        """Геттер для пути к шаблону"""
        return self.config.get_template_path(name)
    
    def get_output_path(self, name: str) -> Optional[str]:
        """Геттер для пути к выходному файлу"""
        return self.config.get_output_path(name) 

    def get_includes(self) -> List[str] | None:
        """Геттер для включаемых файлов"""
        return self.config.get_includes()
        
    def get_callbacks(self) -> List[str] | None:
        return self.config.get_collbacks()
    
    def get_callback(self, name: str) -> Optional[str]:
        return self.config.get_collback(name)

# Пример использования
if __name__ == "__main__":
    processor = MenuProcessor()
    
    input_file = "config/menu_config.json"
    
    if processor.load_menu_file(input_file):
        print("✅ Файл успешно загружен и валидирован")
        
        # Показываем сводную информацию
        processor.print_summary()
        
        # Показываем корневой элемент
        root = processor.menu_structure.get('root')
        if root:
            print(f"\n🌳 Корневая нода:")
            print(f"   ID: {root['id']}")
            print(f"   Первый ребенок: {root.get('first_child', 'None')}")

        print(f'click_items: {processor.click_items}')
        print(f'position_items: {processor.position_items}')
        print(f'factor_items: {processor.factor_items}')
        
        # Генерируем выходной файл
        processor.generate_output("output/flattened_menu.json")

        print("\n🎉 Обработка завершена успешно!")
    else:
        print("\n💥 Ошибка загрузки файла")