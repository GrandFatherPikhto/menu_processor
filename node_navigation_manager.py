from __future__ import annotations
from typing import Optional, List, Dict, Any

class NodeNavigationManager:
    """Менеджер для управления навигационными связями и циклической логикой"""
    
    def __init__(self, node: 'BaseFlatNode'):
        self._node = node
        
        # Сырые навигационные связи (устанавливаются MenuFlattener)
        self._prev_sibling: Optional['BaseFlatNode'] = None
        self._next_sibling: Optional['BaseFlatNode'] = None

    # Установка сырых связей
    @property
    def prev_sibling(self) -> Optional['BaseFlatNode']:
        """Сырая ссылка на предыдущего sibling'а"""
        return self._prev_sibling

    @prev_sibling.setter
    def prev_sibling(self, value: Optional['BaseFlatNode']):
        self._prev_sibling = value

    @property
    def next_sibling(self) -> Optional['BaseFlatNode']:
        """Сырая ссылка на следующего sibling'а"""
        return self._next_sibling

    @next_sibling.setter
    def next_sibling(self, value: Optional['BaseFlatNode']):
        self._next_sibling = value

    # Вычисляемые свойства с учетом циклической навигации
    @property
    def effective_prev_sibling(self) -> Optional['BaseFlatNode']:
        """Предыдущий sibling с учетом циклической навигации родителя"""
        if self._prev_sibling:
            return self._prev_sibling
        
        # Если навигация циклическая и есть родитель с детьми
        if (self._node.parent and self._node.parent.navigate == 'cyclic' and 
            self._node.parent.children and len(self._node.parent.children) > 1):
            # Первый элемент ссылается на последний
            if self._node == self._node.parent.children[0]:
                return self._node.parent.children[-1]
        
        return None

    @property
    def effective_next_sibling(self) -> Optional['BaseFlatNode']:
        """Следующий sibling с учетом циклической навигации родителя"""
        if self._next_sibling:
            return self._next_sibling
        
        # Если навигация циклическая и есть родитель с детьми
        if (self._node.parent and self._node.parent.navigate == 'cyclic' and 
            self._node.parent.children and len(self._node.parent.children) > 1):
            # Последний элемент ссылается на первый
            if self._node == self._node.parent.children[-1]:
                return self._node.parent.children[0]
        
        return None

    @property
    def has_cyclic_siblings(self) -> bool:
        """Имеет ли узел циклические связи с sibling'ами"""
        return (self._node.parent is not None and 
                self._node.parent.navigate == 'cyclic' and 
                len(self._node.parent.children) > 1)

    # Свойства структуры дерева
    @property
    def sibling_count(self) -> int:
        """Количество sibling'ов (включая себя)"""
        if not self._node.parent:
            return 1
        return len(self._node.parent.children) if self._node.parent.children else 1
    
    @property
    def sibling_index(self) -> int:
        """Индекс текущего sibling'а (0-based)"""
        if not self._node.parent or not self._node.parent.children:
            return 0
        for i, sibling in enumerate(self._node.parent.children):
            if sibling.id == self._node.id:
                return i
        return 0

    @property
    def is_first_child(self) -> bool:
        """Является ли узел первым ребенком у родителя"""
        return self.sibling_index == 0

    @property
    def is_last_child(self) -> bool:
        """Является ли узел последним ребенком у родителя"""
        return self.sibling_index == self.sibling_count - 1

    @property
    def is_only_child(self) -> bool:
        """Является ли узел единственным ребенком"""
        return self.sibling_count == 1

    # Навигационные утилиты
    def get_sibling_chain(self, count: int = 5) -> List['BaseFlatNode']:
        """Возвращает цепочку sibling'ов для демонстрации навигации"""
        chain = []
        current = self._node
        visited = set()
        
        for i in range(count):
            if current.id in visited:
                break
                
            visited.add(current.id)
            chain.append(current)
            
            if not current.navigation_manager.effective_next_sibling:
                break
                
            current = current.navigation_manager.effective_next_sibling
        
        return chain

    def get_navigation_info(self) -> Dict[str, Any]:
        """Информация о навигации узла для отладки"""
        parent_navigate = self._node.parent.navigate if self._node.parent else None
        
        return {
            "node_id": self._node.id,
            "parent_navigate": parent_navigate,
            "has_cyclic_siblings": self.has_cyclic_siblings,
            "sibling_count": self.sibling_count,
            "sibling_index": self.sibling_index,
            "is_first_child": self.is_first_child,
            "is_last_child": self.is_last_child,
            "is_only_child": self.is_only_child,
            "raw_prev_sibling": self._prev_sibling.id if self._prev_sibling else None,
            "raw_next_sibling": self._next_sibling.id if self._next_sibling else None,
            "effective_prev_sibling": self.effective_prev_sibling.id if self.effective_prev_sibling else None,
            "effective_next_sibling": self.effective_next_sibling.id if self.effective_next_sibling else None
        }

    def print_navigation_debug(self):
        """Печатает отладочную информацию о навигации"""
        info = self.get_navigation_info()
        print(f"Navigation debug for {self._node.id}:")
        print(f"  Parent navigate: {info['parent_navigate']}")
        print(f"  Siblings: {info['sibling_index'] + 1}/{info['sibling_count']}")
        print(f"  Position: {'first' if info['is_first_child'] else 'last' if info['is_last_child'] else 'middle'}")
        print(f"  Cyclic: {info['has_cyclic_siblings']}")
        print(f"  Raw prev: {info['raw_prev_sibling']}")
        print(f"  Raw next: {info['raw_next_sibling']}")
        print(f"  Effective prev: {info['effective_prev_sibling']}")
        print(f"  Effective next: {info['effective_next_sibling']}")

    def __repr__(self):
        """Строковое представление для отладки"""
        cyclic_flag = "🔁" if self.has_cyclic_siblings else "➡️"
        return (f"NodeNavigationManager({self._node.id}, {cyclic_flag}, "
                f"siblings={self.sibling_index + 1}/{self.sibling_count})")