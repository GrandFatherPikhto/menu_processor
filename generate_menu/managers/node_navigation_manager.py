from __future__ import annotations
import logging
from typing import Optional, List, Dict, Any

from ..i18n import _

logger = logging.getLogger(__name__)

class NodeNavigationManager:
    """Manager for navigation links and cyclic logic."""
    
    def __init__(self, node: 'BaseFlatNode'):
        self._node = node
        
        # Raw navigation links (set by the MenuFlattener)
        self._prev_sibling: Optional['BaseFlatNode'] = None
        self._next_sibling: Optional['BaseFlatNode'] = None

    # Setting raw links
    @property
    def prev_sibling(self) -> Optional['BaseFlatNode']:
        """Raw reference to the previous sibling."""
        return self._prev_sibling

    @prev_sibling.setter
    def prev_sibling(self, value: Optional['BaseFlatNode']):
        self._prev_sibling = value

    @property
    def next_sibling(self) -> Optional['BaseFlatNode']:
        """Raw reference to the next sibling."""
        return self._next_sibling

    @next_sibling.setter
    def next_sibling(self, value: Optional['BaseFlatNode']):
        self._next_sibling = value

    # Computed properties with cyclic navigation support
    @property
    def effective_prev_sibling(self) -> Optional['BaseFlatNode']:
        """Previous sibling considering the parent's cyclic navigation."""
        if self._prev_sibling:
            return self._prev_sibling
        
        # If navigation is cyclic and the parent has children
        if (self._node.parent and self._node.parent.navigate == 'cyclic' and
            self._node.parent.children and len(self._node.parent.children) > 1):
            # The first element references the last one
            if self._node == self._node.parent.children[0]:
                return self._node.parent.children[-1]
        
        return None

    @property
    def effective_next_sibling(self) -> Optional['BaseFlatNode']:
        """Next sibling considering the parent's cyclic navigation."""
        if self._next_sibling:
            return self._next_sibling
        
        # If navigation is cyclic and the parent has children
        if (self._node.parent and self._node.parent.navigate == 'cyclic' and
            self._node.parent.children and len(self._node.parent.children) > 1):
            # The last element references the first one
            if self._node == self._node.parent.children[-1]:
                return self._node.parent.children[0]
        
        return None

    @property
    def has_cyclic_siblings(self) -> bool:
        """Whether the node has cyclic links with its siblings."""
        return (self._node.parent is not None and 
                self._node.parent.navigate == 'cyclic' and 
                len(self._node.parent.children) > 1)

    # Tree structure properties
    @property
    def sibling_count(self) -> int:
        """Number of siblings (including this node)."""
        if not self._node.parent:
            return 1
        return len(self._node.parent.children) if self._node.parent.children else 1
    
    @property
    def sibling_index(self) -> int:
        """Index of the current sibling (0-based)."""
        if not self._node.parent or not self._node.parent.children:
            return 0
        for i, sibling in enumerate(self._node.parent.children):
            if sibling.id == self._node.id:
                return i
        return 0

    @property
    def is_first_child(self) -> bool:
        """Whether the node is the first child of its parent."""
        return self.sibling_index == 0

    @property
    def is_last_child(self) -> bool:
        """Whether the node is the last child of its parent."""
        return self.sibling_index == self.sibling_count - 1

    @property
    def is_only_child(self) -> bool:
        """Whether the node is the only child."""
        return self.sibling_count == 1

    # Navigation utilities
    def get_sibling_chain(self, count: int = 5) -> List['BaseFlatNode']:
        """Returns a chain of siblings to demonstrate navigation."""
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
        """Navigation information about the node for debugging."""
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
        """Prints navigation debug information."""
        info = self.get_navigation_info()
        logger.debug(_("Navigation debug for {id}:").format(id=self._node.id))
        logger.debug("  " + _("Parent navigate: {value}").format(value=info['parent_navigate']))
        logger.debug("  " + _("Siblings: {index}/{count}").format(
            index=info['sibling_index'] + 1, count=info['sibling_count']))
        logger.debug("  " + _("Position: {position}").format(
            position='first' if info['is_first_child'] else 'last' if info['is_last_child'] else 'middle'))
        logger.debug("  " + _("Cyclic: {value}").format(value=info['has_cyclic_siblings']))
        logger.debug("  " + _("Raw prev: {value}").format(value=info['raw_prev_sibling']))
        logger.debug("  " + _("Raw next: {value}").format(value=info['raw_next_sibling']))
        logger.debug("  " + _("Effective prev: {value}").format(value=info['effective_prev_sibling']))
        logger.debug("  " + _("Effective next: {value}").format(value=info['effective_next_sibling']))

    def __repr__(self):
        """String representation for debugging."""
        cyclic_flag = "🔁" if self.has_cyclic_siblings else "➡️"
        return (f"NodeNavigationManager({self._node.id}, {cyclic_flag}, "
                f"siblings={self.sibling_index + 1}/{self.sibling_count})")