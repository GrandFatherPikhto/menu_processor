from typing import Dict, List, Optional, Any
import json

from flat_node import FlatNode
from menu_validator import MenuValidator
from menu_config import MenuConfig, ConfigError
from menu_data import MenuData
from base_flat_node import BaseFlatNode

class FlattenerError(Exception):
    """Исключение для ошибок конфигурации"""
    def __init__(self, message: str):
        super().__init__(message)

class MenuFlattener:
    """Преобразует дерево меню в плоскую структуру с настраиваемыми циклическими связями"""
    
    def __init__(self, config: MenuConfig):
        self.flat_nodes: List[FlatNode] = []
        self.node_dict: Dict[str, FlatNode] = {}
        self._config = config
        self._menu_data = MenuData(self._config)
        
    def flatten(self, menu_tree: List[Dict[str, Any]] | None = None) -> List[BaseFlatNode]:
        """Преобразует дерево в плоский список с установленными связями"""
        self.flat_nodes.clear()
        self.node_dict.clear()

        menu = menu_tree
        if menu is None:
            menu = self._config.menu_tree

        if menu is None:
            raise FlattenerError("Дерево меню пустое!")

        # Создаем корневую ноду как BaseFlatNode
        self.root_node = BaseFlatNode({
                "id": "root",
                "title": "root", 
                "items": menu,
            },
            self._config,
            self._menu_data
        )
        self.root_node.navigate = self._config.root_navigate

        self.flat_nodes.append(self.root_node)
        self.node_dict['root'] = self.root_node
        
        # Рекурсивный обход дерева (остается без изменений)
        self._process_node(self.root_node, None, menu)

        # Применяем правила навигации для ветвей
        self._apply_branch_navigation_rules()
        
        # Создаем циклические связи
        self._make_cyclic_links()
        
        return self.flat_nodes
    
    def _apply_parent_navigation_rules(self):
        """Применяет правила навигации для родительских ветвей"""
        for node in self.flat_nodes:
            # Если узел является ветвью (имеет детей) и у него не указано navigate
            if node.is_branch and node.navigate is None:
                # Используем default_branch_navigate из конфига
                node.navigate = self._config.default_branch_navigate
                print(f"🔧 Установлено navigate='{node.navigate}' для родительской ветви {node.id} (default_branch_navigate)")

    def _make_cyclic_links(self):
        """Замыкает циклические связи для sibling'ов на основе настроек родителей"""
        processed_parents = set()
        
        for node in self.flat_nodes:
            parent = node.parent
            
            # Пропускаем если нет родителя или родитель уже обработан
            if not parent or parent.id in processed_parents:
                continue
                
            # Обрабатываем только если у родителя navigate = cyclic и есть дети
            if parent.navigate == "cyclic" and parent.children:
                processed_parents.add(parent.id)
                self._create_cyclic_siblings(parent)
                
    def _create_cyclic_siblings(self, parent: FlatNode):
        """Создает циклические связи для детей родительского узла с navigate=cyclic"""
        if len(parent.children) < 2:
            return  # Нужно как минимум 2 ребенка для циклической связи
            
        first_child = parent.children[0]
        last_child = parent.children[-1]
        
        # Замыкаем циклические связи
        first_child._prev_sibling = last_child
        last_child._next_sibling = first_child
        
        print(f"🔁 Созданы циклические связи для детей родителя {parent.id} (first<->last)")

    def _process_node(self, parent: Optional[FlatNode], prev_sibling: Optional[FlatNode], 
                     nodes: List[Dict[str, Any]]) -> Optional[FlatNode]:
        """Рекурсивно обрабатывает узлы и устанавливает связи"""
        last_node = None
        
        for i, node_data in enumerate(nodes):
            # Создаем плоский узел (используем обновленный FlatNode)
            flat_node = FlatNode(node_data, self._config, self._menu_data)

            # Устанавливаем значения по умолчанию для навигации
            if flat_node.navigate is None:
                flat_node.navigate = self._config.default_navigate

            self.flat_nodes.append(flat_node)
            self.node_dict[flat_node.id] = flat_node
            
            # Устанавливаем связи через navigation_manager
            flat_node.parent = parent
            flat_node.prev_sibling = prev_sibling  # Используем свойство, которое делегирует к navigation_manager
            
            # Устанавливаем next_sibling для предыдущего sibling'а
            if prev_sibling:
                prev_sibling.next_sibling = flat_node  # Используем свойство, которое делегирует к navigation_manager
            
            # Добавляем к родительским детям
            if parent:
                parent.children.append(flat_node)
                if not parent.first_child:
                    parent.first_child = flat_node
                parent.last_child = flat_node
            
            # Обрабатываем детей, если есть
            if 'items' in node_data and node_data['items']:
                self._process_children(flat_node, node_data['items'])
            
            # Обновляем указатели для следующей итерации
            prev_sibling = flat_node
            last_node = flat_node
        
        return last_node

    def _apply_branch_navigation_rules(self):
        """Применяет правила навигации для ветвей (узлов с детьми)"""
        for node in self.flat_nodes:
            # Если узел является ветвью (имеет детей) и у него не указана навигация
            if node.is_branch and node.navigate is None:
                # Используем default_branch_navigate из конфига, или 'limit' по умолчанию
                node.navigate = self._config.default_branch_navigate or 'limit'
                print(f"🔧 Установлено navigate='{node.navigate}' для ветви {node.id}")    

    def _process_children(self, parent: FlatNode, children_data: List[Dict[str, Any]]):
        """Обрабатывает дочерние узлы"""
        prev_sibling = None
        
        for child_data in children_data:
            flat_child = FlatNode(child_data, self._config, self._menu_data)

            # Устанавливаем значения по умолчанию
            if flat_child.navigate is None:
                flat_child.navigate = self._config.default_navigate

            self.flat_nodes.append(flat_child)
            self.node_dict[flat_child.id] = flat_child
            
            # Устанавливаем связи через navigation_manager
            flat_child.parent = parent
            flat_child.prev_sibling = prev_sibling  # Используем свойство
            
            if prev_sibling:
                prev_sibling.next_sibling = flat_child  # Используем свойство
            
            # Добавляем к родительским детям
            parent.children.append(flat_child)
            if not parent.first_child:
                parent.first_child = flat_child
            parent.last_child = flat_child
            
            # Рекурсивно обрабатываем детей детей
            if 'items' in child_data and child_data["items"]:
                self._process_children(flat_child, child_data["items"])
            
            prev_sibling = flat_child
    
    def get_node_by_id(self, node_id: str) -> Optional[FlatNode]:
        """Возвращает узел по ID"""
        return self.node_dict.get(node_id)
    
    def print_sibling_chain(self, node_id: str, count: int = 5):
        """Печатает цепочку sibling'ов для демонстрации закольцовывания"""
        node = self.get_node_by_id(node_id)
        if not node:
            print(f"Узел {node_id} не найден")
            return
        
        parent_navigate = node.parent.navigate if node.parent else 'N/A'
        print(f"Цепочка sibling'ов для {node_id} (parent navigate: {parent_navigate}):")
        
        current = node
        visited = set()
        
        for i in range(count):
            if current.id in visited:
                print(f"  ... цикл обнаружен ...")
                break
                
            visited.add(current.id)
            prev_id = current.prev_sibling.id if current.prev_sibling else 'None'
            next_id = current.next_sibling.id if current.next_sibling else 'None'
            print(f"  {i}: {current.id} (prev: {prev_id}, next: {next_id})")
            
            if not current.next_sibling or current.next_sibling == node:
                break
                
            current = current.next_sibling

    def print_navigation_summary(self):
        """Печатает сводку по навигации"""
        print("\n🧭 Сводка по навигации:")
        print(f"  Корневая нода (root): {self.root_node.navigate}")
        
        branches = [node for node in self.flat_nodes if node.is_branch and node.id != 'root']
        if branches:
            print(f"  Родительские ветви ({len(branches)}):")
            for branch in branches:
                children_count = len(branch.children) if branch.children else 0
                print(f"    - {branch.id}: {branch.navigate} ({children_count} детей)")
        
        cyclic_parents = [node for node in self.flat_nodes if node.navigate == "cyclic" and node.children]
        if cyclic_parents:
            print(f"  Циклические родители ({len(cyclic_parents)}):")
            for parent in cyclic_parents:
                print(f"    - {parent.id}: {len(parent.children)} детей")


# Пример использования
def main(config_file: str):
    try:
        config = MenuConfig(config_file)
        print(f"✅ Конфигурация {config_file} успешно загружена")
        validator = MenuValidator(config=config)
        errors = validator.validate()
        if errors:
            print(f"❌ Конфигурация содержит ошибки:")
            for id, items in errors.items():
                print(f"❌ {id}:")
                for item in items:
                    print(f"\t➤ {item}")
            return 2
        else:
            print("✅ и проверена")
            flattener = MenuFlattener(config)
            flat_menu = flattener.flatten()
            for node in flat_menu:
                print(f"- {node}")    

    except ConfigError as e:
        print(f"❌ {e}")
        return 1
    # except Exception as e:
    #     print(f"💥 Неожиданная ошибка: {e}")
    #     return 1
    
if __name__ == "__main__":
    main('./config/config.json')