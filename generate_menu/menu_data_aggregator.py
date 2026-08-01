"""Aggregated menu data derived from the flattened node list.

The aggregation logic was extracted from ``MenuCraft`` so that the
processor stays focused on orchestration (loading configuration, validating,
flattening, saving artifacts) while every derived menu structure (functions,
categories, leaves, branches, callbacks, ...) lives in one dedicated place.
"""

from functools import cached_property
from typing import Any, Dict, List, Optional

from .flat_node import FlatNode


class MenuDataAggregator:
    """Derives and caches aggregated menu structures from the flat node list.

    The aggregator is constructed once with the list of flattened nodes.
    Every property is computed lazily on first access and then memoized via
    ``functools.cached_property``, so the many template and summary readers
    do not rescan the node list on each access.

    The returned mappings are read-only from the consumers' point of view
    (templates and summaries only iterate them), so caching a single shared
    object is safe.
    """

    def __init__(self, flat_nodes: List[FlatNode]):
        self._flat_nodes = list(flat_nodes)

    @cached_property
    def menu(self) -> Dict[str, FlatNode]:
        """All menu nodes (excluding root)."""
        return {n.id: n for n in self._flat_nodes if n.id != 'root'}

    @cached_property
    def functions(self) -> Dict[str, Dict[str, Any]]:
        """All handler functions grouped by name with full information."""
        items = {}

        for node in self._flat_nodes:
            if node.id == 'root':
                continue

            # Add all available node functions with full information
            for function_info in node.all_function_infos:
                items[function_info["name"]] = function_info

            # For the callback role - add information about external callbacks
            if node.role == "callback":
                callback_info = {
                    "name": f"{node.id}_callback",
                    "category": node.category,
                    "type": node.type,
                    "role": node.role,
                    "purpose": "external_callback",
                    "node_id": node.id,
                    "event_type": "callback",
                    "navigate": None,
                    "source": "external"
                }
                items[callback_info["name"]] = callback_info

        return items

    @cached_property
    def categories(self) -> Dict[str, Dict[str, Any]]:
        """All menu categories (type + role)."""
        items = {}
        for node in self._flat_nodes:
            if node.id == 'root':
                continue

            category = node.category
            if category is not None:
                items[category["name"]] = category

                # Add information about the available controls for the category
                items[category["name"]]["available_controls"] = [
                    {
                        "type": control["type"].value,
                        "purpose": control["purpose"],
                        "navigate": control["navigate"].value
                    }
                    for control in getattr(node, '_controls', [])
                ]

        return items

    @cached_property
    def leafs(self) -> Dict[str, FlatNode]:
        """All leaf nodes (final menu items)."""
        return {n.id: n for n in self._flat_nodes if n.is_leaf and n.id != 'root'}

    @cached_property
    def branches(self) -> Dict[str, FlatNode]:
        """All menu branches (nodes with children)."""
        return {n.id: n for n in self._flat_nodes if n.is_branch and n.id != 'root'}

    @cached_property
    def first(self) -> Optional[FlatNode]:
        """The first menu node (after root)."""
        root_node = next((node for node in self._flat_nodes if node.id == 'root'), None)
        if root_node and root_node.first_child:
            return root_node.first_child
        return None

    @cached_property
    def callback_nodes(self) -> Dict[str, FlatNode]:
        """All nodes with the callback role."""
        return {n.id: n for n in self._flat_nodes if n.role == 'callback' and n.id != 'root'}

    @cached_property
    def required_functions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Functions grouped by category, marking the required ones."""
        required = {}

        for node in self._flat_nodes:
            if node.id == 'root':
                continue

            for control in getattr(node, '_controls', []):
                if control.get("required", False):
                    category = node.category_name
                    if category not in required:
                        required[category] = []

                    function_info = {
                        "node_id": node.id,
                        "control": control["type"].value,
                        "purpose": control["purpose"],
                        "function_name": getattr(node, f"function_{control['type'].value}_name", None)
                    }
                    required[category].append(function_info)

        return required

    @cached_property
    def custom_callbacks(self) -> Dict[str, Dict[str, Any]]:
        """All custom callback functions."""
        callbacks = {}

        for node in self._flat_nodes:
            if node.id == 'root':
                continue

            node_callbacks = node.custom_callbacks_summary
            for cb_type, cb_name in node_callbacks.items():
                if cb_name and cb_type != "auto_draw_value_cb":  # Exclude automatic ones
                    callbacks[cb_name] = {
                        "node_id": node.id,
                        "callback_type": cb_type,
                        "function_name": cb_name,
                        "node": node
                    }

        return callbacks

    @cached_property
    def auto_generated_functions(self) -> Dict[str, Dict[str, Any]]:
        """All automatically generated functions with full information."""
        auto_funcs = {}

        for node in self._flat_nodes:
            if node.id == 'root':
                continue

            # Automatic handler functions
            for func_info in node.all_function_infos:
                auto_funcs[func_info["name"]] = {
                    **func_info,
                    "node_id": node.id,
                    "source": "auto_generated"
                }

            # Automatic draw functions
            if node.callback_manager.auto_draw_value_cb_name and not node.callback_manager.draw_value_cb:
                auto_funcs[node.callback_manager.auto_draw_value_cb_name] = {
                    "name": node.callback_manager.auto_draw_value_cb_name,
                    "category": node.category,
                    "node_id": node.id,
                    "source": "auto_draw",
                    "purpose": "draw_value",
                    "event_type": "draw_value",
                    "navigate": None
                }

        return auto_funcs

    @cached_property
    def functions_by_event_type(self) -> Dict[str, List[Dict[str, Any]]]:
        """Functions grouped by event type."""
        grouped = {}

        for func_name, func_info in self.functions.items():
            event_type = func_info.get("event_type", "unknown")
            if event_type not in grouped:
                grouped[event_type] = []
            grouped[event_type].append(func_info)

        return grouped

    @cached_property
    def functions_by_navigation(self) -> Dict[str, List[Dict[str, Any]]]:
        """Functions grouped by navigation type."""
        grouped = {}

        for func_name, func_info in self.functions.items():
            navigate = func_info.get("navigate", "unknown")
            if navigate not in grouped:
                grouped[navigate] = []
            grouped[navigate].append(func_info)

        return grouped

    @cached_property
    def nodes_with_custom_callbacks(self) -> Dict[str, FlatNode]:
        """All nodes with custom callbacks."""
        return {n.id: n for n in self._flat_nodes if n.has_custom_callbacks and n.id != 'root'}

    def get_callbacks_by_type(self, callback_type: str) -> Dict[str, str]:
        """Get callbacks of a specific type."""
        result = {}
        for node in self._flat_nodes:
            if node.id == 'root':
                continue

            callback_value = getattr(node, callback_type, None)
            if callback_value:
                result[node.id] = callback_value
        return result

    def get_functions_by_category(self, category_name: str) -> List[Dict[str, Any]]:
        """All functions for the given category."""
        return [
            func_info for func_info in self.functions.values()
            if func_info.get("category", {}).get("name") == category_name
        ]

    @cached_property
    def detailed_callback_infos(self) -> Dict[str, List[Dict[str, Any]]]:
        """Detailed information about all callback functions, grouped by type."""
        callback_types = [
            'click_cb', 'position_cb', 'double_click_cb',
            'long_click_cb', 'event_cb', 'draw_value_cb'
        ]

        result = {cb_type: [] for cb_type in callback_types}

        for node in self._flat_nodes:
            if node.id == 'root':
                continue

            for cb_type in callback_types:
                info = node.get_callback_info(cb_type)
                if info:
                    result[cb_type].append(info)

        return result

    @cached_property
    def callback_summary_by_category(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """Callback function summary by category."""
        categories = {}

        for node in self._flat_nodes:
            if node.id == 'root':
                continue

            category = node.category_name
            if category not in categories:
                categories[category] = {}

            # Group callbacks by type for each category
            for cb_type, info in node.defined_callback_infos.items():
                if cb_type not in categories[category]:
                    categories[category][cb_type] = []
                categories[category][cb_type].append(info)

        return categories

    def get_callbacks_by_category(self, category_name: str) -> Dict[str, List[Dict[str, Any]]]:
        """All callback functions for the given category."""
        result = {}

        for node in self._flat_nodes:
            if node.id == 'root' or node.category_name != category_name:
                continue

            for cb_type, info in node.defined_callback_infos.items():
                if cb_type not in result:
                    result[cb_type] = []
                result[cb_type].append(info)

        return result

    @cached_property
    def functions_by_type_role(self) -> Dict[str, List[Dict[str, Any]]]:
        """Functions grouped by the type_role combination."""
        grouped = {}

        for func_name, func_info in self.functions.items():
            type_val = func_info.get("type", "N/A")
            role_val = func_info.get("role", "N/A")
            type_role = f"{type_val}_{role_val}"

            if type_role not in grouped:
                grouped[type_role] = []
            grouped[type_role].append(func_info)

        return grouped

    @cached_property
    def functions_by_type(self) -> Dict[str, List[Dict[str, Any]]]:
        """Functions grouped by data type."""
        grouped = {}

        for func_name, func_info in self.functions.items():
            type_val = func_info.get("type", "unknown")
            if type_val not in grouped:
                grouped[type_val] = []
            grouped[type_val].append(func_info)

        return grouped

    @cached_property
    def functions_by_role(self) -> Dict[str, List[Dict[str, Any]]]:
        """Functions grouped by role."""
        grouped = {}

        for func_name, func_info in self.functions.items():
            role_val = func_info.get("role", "unknown")
            if role_val not in grouped:
                grouped[role_val] = []
            grouped[role_val].append(func_info)

        return grouped
