import json
from collections import deque
from typing import Dict, List, Optional, Any

class MenuConfig:
    """Класс для работы с конфигурацией шаблонов и выходных файлов"""
    
    def __init__(self):
        self.templates: Dict[str, str] = {}
        self.output_files: Dict[str, str] = {}
    
    def load_from_dict(self, config_data: Dict) -> None:
        """Загрузка конфигурации из словаря"""
        if 'templates' in config_data:
            self.templates = config_data['templates'].copy()
        
        if 'output' in config_data:
            self.output_files = config_data['output'].copy()
    
    def validate(self) -> List[str]:
        """Валидация конфигурации"""
        errors = []
        
        if 'c' not in self.templates:
            errors.append("Отсутствует template для .c файла")
        if 'h' not in self.templates:
            errors.append("Отсутствует template для .h файла")
        
        if 'c' not in self.output_files:
            errors.append("Отсутствует output файл для .c")
        if 'h' not in self.output_files:
            errors.append("Отсутствует output файл для .h")
        
        return errors
    
    def get_template_path(self, file_type: str) -> Optional[str]:
        """Получить путь к шаблону по типу файла"""
        return self.templates.get(file_type)
    
    def get_output_path(self, file_type: str) -> Optional[str]:
        """Получить путь к выходному файлу по типу файла"""
        return self.output_files.get(file_type)
    
    def get_templates(self) -> Dict[str, str]:
        """Геттер для всех шаблонов"""
        return self.templates.copy()
    
    def get_output_files(self) -> Dict[str, str]:
        """Геттер для всех выходных файлов"""
        return self.output_files.copy()    

class MenuError(Exception):
    """Базовое исключение для ошибок меню"""
    def __init__(self, message: str, node_path: List[str] = None):
        self.message = message
        self.node_path = node_path or []
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        path_str = ' -> '.join(self.node_path) if self.node_path else 'root'
        return f"{path_str}: {self.message}"

class MenuValidator:
    """Класс для валидации структуры меню"""
    
    VALID_TYPES = {'menu', 'action_int', 'action_int_factor', 
                  'action_callback', 'action_bool'}
    
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
            'action_bool': self._validate_action_bool
        }
        
        validator = type_validators.get(node['type'])
        if validator:
            validator(node, path)
    
    def _validate_action_int(self, node: Dict, path: List[str]) -> None:
        """Валидация action_int"""
        required_fields = ['min', 'max', 'default']
        for field in required_fields:
            if field not in node:
                self.errors.append(MenuError(
                    f"Для action_int обязательно поле '{field}'",
                    path
                ))
    
    def _validate_action_int_factor(self, node: Dict, path: List[str]) -> None:
        """Валидация action_int_factor"""
        required_fields = ['min', 'max', 'default', 'factors', 'default_factor_idx']
        for field in required_fields:
            if field not in node:
                self.errors.append(MenuError(
                    f"Для action_int_factor обязательно поле '{field}'",
                    path
                ))
    
    def _validate_action_callback(self, node: Dict, path: List[str]) -> None:
        """Валидация action_callback"""
        if 'callback' not in node:
            self.errors.append(MenuError(
                "Для action_callback обязательно поле 'callback'",
                path
            ))
    
    def _validate_action_bool(self, node: Dict, path: List[str]) -> None:
        """Валидация action_bool"""
        if 'default' not in node:
            self.errors.append(MenuError(
                "Для action_bool обязательно поле 'default'",
                path
            ))
    
    def get_errors(self) -> List[MenuError]:
        """Получить список ошибок"""
        return self.errors

class MenuFlattener:
    """Класс для преобразования древовидной структуры в плоскую"""
    
    def __init__(self):
        self.flattened: Dict[str, Dict] = {}
        self._auto_root_id = "root"
    
    def flatten(self, menu_data: List[Dict]) -> Dict[str, Dict]:
        """Основной метод уплощения"""
        self.flattened.clear()
        
        if not menu_data:
            raise MenuError("Нет данных меню для уплощения")
        
        # Автоматически создаем root ноду
        self._create_root_node(menu_data)
        
        # Обрабатываем все корневые элементы
        if len(menu_data) == 1:
            self._process_tree(menu_data[0], self._auto_root_id, None)
        else:
            prev_sibling_id = None
            for root_item in menu_data:
                root_item_id = self._get_or_generate_id(root_item)
                self._process_tree(root_item, self._auto_root_id, prev_sibling_id)
                prev_sibling_id = root_item_id
        
        return self.flattened
    
    def _create_root_node(self, menu_data: List[Dict]) -> None:
        """Создание автоматической root ноды с ссылкой на первый элемент"""
        first_child_id = None
        if menu_data:
            first_child_id = self._get_or_generate_id(menu_data[0])
        
        self.flattened[self._auto_root_id] = {
            'id': self._auto_root_id,
            'title': 'ROOT',
            'type': 'root',
            'first_child': first_child_id,
            'next_sibling': None,
            'prev_sibling': None
        }
    
    def _process_tree(self, node: Dict, parent_id: str, prev_sibling_id: Optional[str]) -> str:
        """Обработка дерева с использованием BFS"""
        queue = deque()
        node_id = self._get_or_generate_id(node)
        
        queue.append((node, parent_id, prev_sibling_id, node_id))
        
        while queue:
            current_node, current_parent_id, current_prev_sibling_id, current_node_id = queue.popleft()
            
            flat_item = self._create_flat_item(current_node, current_node_id, 
                                             current_parent_id, current_prev_sibling_id)
            self.flattened[current_node_id] = flat_item
            
            # Обновляем first_child у родителя, если это первый ребенок
            if (current_prev_sibling_id is None and 
                current_parent_id in self.flattened and 
                self.flattened[current_parent_id].get('first_child') is None):
                self.flattened[current_parent_id]['first_child'] = current_node_id
            
            # Обрабатываем дочерние элементы
            children = current_node.get('children', [])
            if children:
                prev_child_sibling_id = None
                for child in children:
                    child_id = self._get_or_generate_id(child)
                    queue.append((child, current_node_id, prev_child_sibling_id, child_id))
                    prev_child_sibling_id = child_id
        
        return node_id
    
    def _get_or_generate_id(self, node: Dict) -> str:
        """Получить ID из ноды или сгенерировать его"""
        if 'id' in node and node['id']:
            return node['id']
        
        # Генерируем ID из title, если явный ID не указан
        title = node.get('title', 'unknown')
        return self._generate_id_from_title(title)
    
    def _generate_id_from_title(self, title: str) -> str:
        """Генерация ID из title"""
        return title.lower().replace(' ', '_').replace('-', '_')
    
    def _create_flat_item(self, node: Dict, node_id: str, 
                         parent_id: Optional[str], prev_sibling_id: Optional[str]) -> Dict:
        """Создание уплощенного элемента меню"""
        item = {
            'id': node_id,
            'title': node['title'],
            'type': node['type']
        }
        
        # Добавляем связи
        if parent_id:
            item['parent'] = parent_id
        if prev_sibling_id:
            item['prev_sibling'] = prev_sibling_id
        
        # Добавляем специфичные поля
        self._add_type_specific_fields(item, node)
        
        # Сохраняем оригинальный ID, если он был указан
        if 'id' in node and node['id']:
            item['original_id'] = node['id']
        
        return item
    
    def _add_type_specific_fields(self, item: Dict, node: Dict) -> None:
        """Добавление полей, специфичных для типа"""
        type_processors = {
            'action_int': lambda: item.update({
                'min': node['min'],
                'max': node['max'],
                'default': node['default'],
                'step': node.get('step', 1)
            }),
            'action_int_factor': lambda: item.update({
                'min': node['min'],
                'max': node['max'],
                'default': node['default'],
                'factors': node['factors'],
                'default_factor_idx': node['default_factor_idx']
            }),
            'action_callback': lambda: item.update({
                'callback': node['callback']
            }),
            'action_bool': lambda: item.update({
                'default': node['default']
            })
        }
        
        processor = type_processors.get(node['type'])
        if processor:
            processor()

class MenuProcessor:
    """Основной класс для обработки всего меню"""
    
    def __init__(self):
        self.config = MenuConfig()
        self.validator = MenuValidator()
        self.flattener = MenuFlattener()
        self.menu_structure: Dict[str, Dict] = {}
    
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

    def get_config(self) -> MenuConfig:
        """Геттер для конфигурации"""
        return self.config
    
    def get_flattened_menu(self) -> Dict[str, Dict]:
        """Геттер для уплощенного меню"""
        return self.menu_structure.copy()  # Возвращаем копию для безопасности
    
    def get_template_path(self, file_type: str) -> Optional[str]:
        """Геттер для пути к шаблону"""
        return self.config.get_template_path(file_type)
    
    def get_output_path(self, file_type: str) -> Optional[str]:
        """Геттер для пути к выходному файлу"""
        return self.config.get_output_path(file_type)            

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
        
        # Генерируем выходной файл
        processor.generate_output("output/flattened_menu.json")

        print(processor.get_config().get_template_path('c'))
        print(processor.get_template_path('h'))
        
        print("\n🎉 Обработка завершена успешно!")
    else:
        print("\n💥 Ошибка загрузки файла")