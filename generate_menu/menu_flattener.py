import json
import logging
from typing import Dict, List, Optional, Any

from .i18n import _
from .flat_node import FlatNode
from .menu_config import MenuConfig
from .menu_data import MenuData
from .base_flat_node import BaseFlatNode

logger = logging.getLogger(__name__)

class FlattenerError(Exception):
    """Exception for configuration errors."""
    def __init__(self, message: str):
        super().__init__(message)

class MenuFlattener:
    """Flattens a menu tree into a flat structure with configurable cyclic links."""
    
    def __init__(self, config: MenuConfig):
        self.flat_nodes: List[FlatNode] = []
        self.node_dict: Dict[str, FlatNode] = {}
        self._config = config
        self._menu_data = MenuData(self._config)
        
    def flatten(self, menu_tree: List[Dict[str, Any]] | None = None) -> List[BaseFlatNode]:
        """Flattens the tree into a flat list with established links."""
        self.flat_nodes.clear()
        self.node_dict.clear()

        menu = menu_tree
        if menu is None:
            menu = self._config.menu_tree

        if menu is None:
            raise FlattenerError(_("Menu tree is empty!"))

        # Create the root node as a BaseFlatNode
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
        
        # Recursively traverse the tree
        self._process_node(self.root_node, None, menu)

        # Apply navigation rules for branches
        self._apply_branch_navigation_rules()
        
        # Create cyclic links
        self._make_cyclic_links()
        
        return self.flat_nodes
    
    def _make_cyclic_links(self):
        """Closes cyclic links for siblings based on parent settings."""
        processed_parents = set()
        
        for node in self.flat_nodes:
            parent = node.parent
            
            # Skip if there is no parent or the parent was already processed
            if not parent or parent.id in processed_parents:
                continue
                
            # Process only if the parent has navigate=cyclic and children
            if parent.navigate == "cyclic" and parent.children:
                processed_parents.add(parent.id)
                self._create_cyclic_siblings(parent)
                
    def _create_cyclic_siblings(self, parent: FlatNode):
        """Creates cyclic links for children of a parent with navigate=cyclic."""
        if len(parent.children) < 2:
            return  # At least 2 children are required for a cyclic link
            
        first_child = parent.children[0]
        last_child = parent.children[-1]
        
        # Close the cyclic links
        first_child._prev_sibling = last_child
        last_child._next_sibling = first_child
        
        logger.debug(f"🔁 {_('Created cyclic links for children of parent {id} (first<->last)').format(id=parent.id)}")

    def _process_node(self, parent: Optional[FlatNode], prev_sibling: Optional[FlatNode],
                     nodes: List[Dict[str, Any]]) -> Optional[FlatNode]:
        """Recursively processes nodes and establishes links."""
        last_node = None
        
        for i, node_data in enumerate(nodes):
            # Create a flat node (using the updated FlatNode)
            flat_node = FlatNode(node_data, self._config, self._menu_data)

            # Set default navigation for leaf nodes only. Branches keep
            # navigate=None here so that the branch navigation rule can apply
            # default_branch_navigate in _apply_branch_navigation_rules.
            if flat_node.navigate is None and 'items' not in node_data:
                flat_node.navigate = self._config.default_navigate

            self.flat_nodes.append(flat_node)
            self.node_dict[flat_node.id] = flat_node
            
            # Establish links through the navigation manager
            flat_node.parent = parent
            flat_node.prev_sibling = prev_sibling  # Uses the property that delegates to the navigation manager
            
            # Set next_sibling for the previous sibling
            if prev_sibling:
                prev_sibling.next_sibling = flat_node  # Uses the property that delegates to the navigation manager
            
            # Add to the parent's children
            if parent:
                parent.children.append(flat_node)
                if not parent.first_child:
                    parent.first_child = flat_node
                parent.last_child = flat_node
            
            # Process children if present
            if 'items' in node_data and node_data['items']:
                self._process_children(flat_node, node_data['items'])
            
            # Update the pointers for the next iteration
            prev_sibling = flat_node
            last_node = flat_node
        
        return last_node

    def _apply_branch_navigation_rules(self):
        """Applies navigation rules for branches (nodes with children)."""
        for node in self.flat_nodes:
            # If the node is a branch (has children) and navigation is not set
            if node.is_branch and node.navigate is None:
                # Use default_branch_navigate from the config, or 'limit' by default
                node.navigate = self._config.default_branch_navigate or 'limit'
                logger.debug("🔧 " + _("Set navigate='{navigate}' for branch {id}").format(navigate=node.navigate, id=node.id))

    def _process_children(self, parent: FlatNode, children_data: List[Dict[str, Any]]):
        """Processes the child nodes."""
        prev_sibling = None
        
        for child_data in children_data:
            flat_child = FlatNode(child_data, self._config, self._menu_data)

            # Set default navigation for leaf nodes only. Branches keep
            # navigate=None here so that the branch navigation rule can apply
            # default_branch_navigate in _apply_branch_navigation_rules.
            if flat_child.navigate is None and 'items' not in child_data:
                flat_child.navigate = self._config.default_navigate

            self.flat_nodes.append(flat_child)
            self.node_dict[flat_child.id] = flat_child
            
            # Establish links through the navigation manager
            flat_child.parent = parent
            flat_child.prev_sibling = prev_sibling  # Uses the property
            
            if prev_sibling:
                prev_sibling.next_sibling = flat_child  # Uses the property
            
            # Add to the parent's children
            parent.children.append(flat_child)
            if not parent.first_child:
                parent.first_child = flat_child
            parent.last_child = flat_child
            
            # Recursively process grandchildren
            if 'items' in child_data and child_data["items"]:
                self._process_children(flat_child, child_data["items"])
            
            prev_sibling = flat_child
    
    def get_node_by_id(self, node_id: str) -> Optional[FlatNode]:
        """Returns a node by its ID."""
        return self.node_dict.get(node_id)
    
    def print_sibling_chain(self, node_id: str, count: int = 5):
        """Prints the sibling chain to demonstrate circular linking."""
        node = self.get_node_by_id(node_id)
        if not node:
            logger.debug(_("Node {id} not found").format(id=node_id))
            return
        
        parent_navigate = node.parent.navigate if node.parent else 'N/A'
        logger.debug(_("Sibling chain for {id} (parent navigate: {parent_navigate}):").format(
            id=node_id, parent_navigate=parent_navigate))
        
        current = node
        visited = set()
        
        for i in range(count):
            if current.id in visited:
                logger.debug(_("  ... cycle detected ..."))
                break
                
            visited.add(current.id)
            prev_id = current.prev_sibling.id if current.prev_sibling else 'None'
            next_id = current.next_sibling.id if current.next_sibling else 'None'
            logger.debug(f"  {i}: {current.id} (prev: {prev_id}, next: {next_id})")
            
            if not current.next_sibling or current.next_sibling == node:
                break
                
            current = current.next_sibling

    def print_navigation_summary(self):
        """Prints the navigation summary."""
        logger.debug(f"\n🧭 {_('Navigation summary:')}")
        logger.debug(_("  Root node (root): {navigate}").format(navigate=self.root_node.navigate))
        
        branches = [node for node in self.flat_nodes if node.is_branch and node.id != 'root']
        if branches:
            logger.debug(_("  Parent branches ({count}):").format(count=len(branches)))
            for branch in branches:
                children_count = len(branch.children) if branch.children else 0
                logger.debug(_("    - {id}: {navigate} ({count} children)").format(
                    id=branch.id, navigate=branch.navigate, count=children_count))
        
        cyclic_parents = [node for node in self.flat_nodes if node.navigate == "cyclic" and node.children]
        if cyclic_parents:
            logger.debug(_("  Cyclic parents ({count}):").format(count=len(cyclic_parents)))
            for parent in cyclic_parents:
                logger.debug(_("    - {id}: {count} children").format(id=parent.id, count=len(parent.children)))

