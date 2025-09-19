from typing import Dict, List, Optional, Any
import json

from flat_node import FlatNode
from data_types import DataTypeConfig
from common import load_json_data

class Flattener:
    """Преобразует дерево меню в плоскую структуру с настраиваемыми циклическими связями"""
    
    def __init__(self, config:Dict, data_types_config: DataTypeConfig | None = None):
        self.config = config
        self.flat_nodes: List[FlatNode] = []
        self.node_dict = {}
        self.node_dict: Dict[str, FlatNode] = {}
        if data_types_config is None:
            self.data_type_config = DataTypeConfig(config.get('data_types'))
        else:
            self.data_type_config = data_types_config
        
    def flatten(self, menu_tree: List[Dict[str, Any]]) -> List[FlatNode]:
        """Преобразует дерево в плоский список с установленными связями"""
        self.flat_nodes.clear()
        self.node_dict.clear()

        self.root_node = FlatNode({
            'id': 'root',
            'name': 'root',
            'items': menu_tree,
            'type_info': None
        })
        self.flat_nodes.append(self.root_node)
        self.node_dict['root'] = self.root_node
        
        # Рекурсивный обход дерева
        self._process_node(self.root_node, None, menu_tree)

        self._make_cyclic_links()
        
        return self.flat_nodes

    def _append_type_info(self, node_data: Dict[str, Any]) -> bool:
        if node_data.get('type', None) is not None:
            node_data['type_info'] = self.data_type_config.get_by_type(node_data['type'])
            return True
        return False


    def _process_node(self, parent: Optional[FlatNode], prev_sibling: Optional[FlatNode], 
                     nodes: List[Dict[str, Any]]) -> Optional[FlatNode]:
        """Рекурсивно обрабатывает узлы и устанавливает связи"""
        last_node = None
        
        for i, node_data in enumerate(nodes):
            # Создаем плоский узел
            self._append_type_info(node_data)
            flat_node = FlatNode(node_data)
            self.flat_nodes.append(flat_node)
            self.node_dict[flat_node.id] = flat_node
            
            # Устанавливаем связи
            flat_node.parent = parent
            flat_node.prev_sibling = prev_sibling
            
            # Устанавливаем next_sibling для предыдущего sibling'а
            if prev_sibling:
                prev_sibling.next_sibling = flat_node
            
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
    
    def _make_cyclic_links(self):
        """Замыкает циклические связи для всех sibling'ов на основе настроек родителей"""
        for node in self.flat_nodes:
            print(node.name, node.navigate)
            if node.parent and node.parent.navigate == "cyclic" and node.parent.children:
                print(f'Делаем цикличиские связи {node}')
                # Делаем циклические связи для siblings, если родитель имеет cyclic_siblings=True
                first_child = node.parent.children[0]
                last_child = node.parent.children[-1]
                
                if len(node.parent.children) > 1:
                    first_child._prev_sibling = last_child
                    last_child._next_sibling = first_child    

    def _process_children(self, parent: FlatNode, children_data: List[Dict[str, Any]]):
        """Обрабатывает дочерние узлы"""
        prev_sibling = None
        
        for child_data in children_data:
            self._append_type_info(child_data)
            flat_child = FlatNode(child_data)
            self.flat_nodes.append(flat_child)
            self.node_dict[flat_child.id] = flat_child
            
            # Устанавливаем связи
            flat_child.parent = parent
            flat_child.prev_sibling = prev_sibling
            
            if prev_sibling:
                prev_sibling.next_sibling = flat_child
            
            # Добавляем к родительским детям
            parent.children.append(flat_child)
            if not parent.first_child:
                parent.first_child = flat_child
            parent.last_child = flat_child
            
            # Рекурсивно обрабатываем детей детей
            if 'items' in child_data and child_data['items']:
                self._process_children(flat_child, child_data['items'])
            
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
        
        print(f"Цепочка sibling'ов для {node_id} (cyclic: {node.has_cyclic_siblings}):")
        current = node
        for i in range(count):
            print(f"  {i}: {current.id}")
            current = current.next_sibling
            if not current or current == node:
                break


def flat_menu(menu_tree):
    config = load_json_data('config/config.json')
    flattener = Flattener(config=config)
    flat_menu = flattener.flatten(menu_tree)
    
    print("Плоский список узлов:")
    for node in flat_menu:
        print(f"- {node}")    


# Пример использования
def main():
    menu_data = load_json_data('menu/menu.json')        
    if menu_data.get('menu', None) is not None:
        flat_menu(menu_data.get('menu', []))
    
if __name__ == "__main__":
    main()