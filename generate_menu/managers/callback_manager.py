import logging
from typing import Dict, List, Optional, Any

from ..menu_data import MenuData, ControlType
from ..i18n import _

logger = logging.getLogger(__name__)

class CallbackManager:
    """Manager for handling callback functions of a menu node."""
    
    ALL_CALLBACK_TYPES = [
        'click_cb', 'position_cb', 'double_click_cb', 
        'long_click_cb', 'event_cb', 'draw_value_cb'
    ]

    def __init__(self, original_node: Dict[str, Any], node_type: str, node_role: str, 
                 node_category: Dict[str, Any], menu_data: MenuData):
        self._original_node = original_node
        self._node_type = node_type
        self._node_role = node_role
        self._node_category = node_category
        self._menu_data = menu_data

        # Custom callback functions from JSON
        self.click_cb = original_node.get("click_cb")
        self.position_cb = original_node.get("position_cb")
        self.double_click_cb = original_node.get("double_click_cb")
        self.long_click_cb = original_node.get("long_click_cb")
        self.event_cb = original_node.get("event_cb")
        self.draw_value_cb = original_node.get("draw_value_cb")

        # Automatically generated functions (will be set later)
        self._auto_click_function = None
        self._auto_position_function = None
        self._auto_click_info = None
        self._auto_position_info = None

    def set_auto_functions(self, click_info: Optional[Dict] = None, 
                          position_info: Optional[Dict] = None):
        """Sets the automatically generated functions with additional information."""
        self._auto_click_info = click_info
        self._auto_position_info = position_info
        
        # Set function names for backward compatibility
        self._auto_click_function = click_info["name"] if click_info and "name" in click_info else None
        self._auto_position_function = position_info["name"] if position_info and "name" in position_info else None

    def get_callback_info(self, callback_type: str) -> Optional[Dict[str, Any]]:
        """
        Returns detailed information about ANY callback function.
        """
        # For click_cb and position_cb check both custom and automatic
        if callback_type in ['click_cb', 'position_cb']:
            # Custom callback
            callback_value = getattr(self, callback_type, None)
            is_custom = callback_value is not None
            
            # If no custom callback is set, check the automatic one
            if not is_custom:
                if callback_type == 'click_cb':
                    callback_value = self._auto_click_function
                    auto_info = self._auto_click_info
                else:  # position_cb
                    callback_value = self._auto_position_function
                    auto_info = self._auto_position_info
                is_custom = False
            else:
                auto_info = None
        else:
            # For the other callback types
            callback_value = getattr(self, callback_type, None)
            is_custom = callback_value is not None
            
            # draw_value_cb may have an automatic function
            if callback_type == 'draw_value_cb' and not is_custom:
                callback_value = self.auto_draw_value_cb_name
                is_custom = False
                auto_info = None
            else:
                auto_info = None
        
        if not callback_value:
            return None
        
        # Basic information
        info = {
            "name": callback_value,
            "type": self._node_type,
            "role": self._node_role,
            "c_type": self._node_category.get("c_type") if self._node_category else None,
            "category": self._node_category.get("name") if self._node_category else None,
            "custom": is_custom,
            "callback_type": callback_type,
            "node_id": self._original_node.get("id"),
            "event_type": callback_type.replace('_cb', '')  # click_cb -> click
        }
        
        # Add navigation information for automatic functions
        if not is_custom and auto_info:
            info["navigate"] = auto_info.get("navigate")
            info["purpose"] = auto_info.get("purpose")
        
        return info

    # Add a property for getting information about all automatic functions
    @property
    def auto_functions_info(self) -> List[Dict[str, Any]]:
        """Information about all automatically generated functions."""
        auto_funcs = []
        
        if self._auto_click_function and self._auto_click_info:
            auto_funcs.append({
                "name": self._auto_click_function,
                "event_type": "click",
                "navigate": self._auto_click_info.get("navigate"),
                "purpose": self._auto_click_info.get("purpose"),
                "node_id": self._original_node.get("id"),
                "category": self._node_category.get("name") if self._node_category else None
            })
        
        if self._auto_position_function and self._auto_position_info:
            auto_funcs.append({
                "name": self._auto_position_function,
                "event_type": "position", 
                "navigate": self._auto_position_info.get("navigate"),
                "purpose": self._auto_position_info.get("purpose"),
                "node_id": self._original_node.get("id"),
                "category": self._node_category.get("name") if self._node_category else None
            })
        
        # Automatic draw function
        if self.auto_draw_value_cb_name and not self.draw_value_cb:
            auto_funcs.append({
                "name": self.auto_draw_value_cb_name,
                "event_type": "draw_value",
                "navigate": None,  # Navigation does not apply to drawing
                "purpose": "draw_value",
                "node_id": self._original_node.get("id"),
                "category": self._node_category.get("name") if self._node_category else None
            })
        
        return auto_funcs
    
    @property
    def auto_draw_value_cb_name(self) -> Optional[str]:
        """Automatically generated draw function name with a _cb suffix."""
        if self._node_category and self._node_category.get("name"):
            return f"menu_draw_{self._node_category['name']}_value_cb"  # Already contains _cb
        return None

    @property
    def effective_draw_value_cb(self) -> Optional[str]:
        """Effective draw function name (custom or automatic)."""
        return self.draw_value_cb or self.auto_draw_value_cb_name

    @property
    def has_custom_callbacks(self) -> bool:
        """Whether the node has custom callbacks."""
        return any([
            self.click_cb, self.position_cb, self.double_click_cb,
            self.long_click_cb, self.event_cb, self.draw_value_cb
        ])

    # Specialized convenience methods
    def get_draw_value_info(self) -> Optional[Dict[str, Any]]:
        return self.get_callback_info('draw_value_cb')

    def get_double_click_info(self) -> Optional[Dict[str, Any]]:
        return self.get_callback_info('double_click_cb')

    def get_long_click_info(self) -> Optional[Dict[str, Any]]:
        return self.get_callback_info('long_click_cb')

    def get_event_info(self) -> Optional[Dict[str, Any]]:
        return self.get_callback_info('event_cb')

    def get_click_info(self) -> Optional[Dict[str, Any]]:
        return self.get_callback_info('click_cb')

    def get_position_info(self) -> Optional[Dict[str, Any]]:
        return self.get_callback_info('position_cb')

    @property
    def all_callback_infos(self) -> Dict[str, Optional[Dict[str, Any]]]:
        """ALL callback functions of the node with detailed information."""
        return {
            cb_type: self.get_callback_info(cb_type)
            for cb_type in self.ALL_CALLBACK_TYPES
        }

    @property
    def defined_callback_infos(self) -> Dict[str, Dict[str, Any]]:
        """Only defined callback functions (excluding None)."""
        return {
            cb_type: info for cb_type, info in self.all_callback_infos.items()
            if info is not None
        }

    @property
    def auto_generated_callbacks(self) -> Dict[str, Dict[str, Any]]:
        """Only automatically generated callback functions."""
        return {
            cb_type: info for cb_type, info in self.defined_callback_infos.items()
            if not info["custom"]
        }

    @property
    def custom_callbacks(self) -> Dict[str, Dict[str, Any]]:
        """Only custom callback functions."""
        return {
            cb_type: info for cb_type, info in self.defined_callback_infos.items()
            if info["custom"]
        }

    @property
    def custom_callbacks_summary(self) -> Dict[str, Optional[str]]:
        """Custom callback summary."""
        return {
            "click_cb": self.click_cb,
            "position_cb": self.position_cb,
            "double_click_cb": self.double_click_cb,
            "long_click_cb": self.long_click_cb,
            "event_cb": self.event_cb,
            "draw_value_cb": self.draw_value_cb,
            "auto_draw_value_cb": self.auto_draw_value_cb_name if not self.draw_value_cb else None
        }

    def get_callbacks_by_auto_status(self, auto: bool = True) -> Dict[str, Dict[str, Any]]:
        """Get callback functions by status (automatic or custom)."""
        return {
            cb_type: info for cb_type, info in self.defined_callback_infos.items()
            if info["custom"] != auto
        }

    def print_detailed_callback_info(self, node_id: str):
        """Prints detailed information about ALL callback functions of the node."""
        logger.debug("📋 " + _("Detailed callback info for {node_id} ({type}_{role}):").format(
            node_id=node_id, type=self._node_type, role=self._node_role))
        
        for cb_type, info in self.all_callback_infos.items():
            if info:
                custom_flag = "🎛️ CUSTOM" if info["custom"] else "⚙️ AUTO"
                logger.debug("  " + _("{cb_type}:").format(cb_type=cb_type))
                logger.debug("    " + _("Name: {name} ({flag})").format(name=info['name'], flag=custom_flag))
                logger.debug("    " + _("Type: {type}").format(type=info['type']))
                logger.debug("    " + _("Role: {role}").format(role=info['role']))
                logger.debug("    " + _("C Type: {c_type}").format(c_type=info['c_type']))
                logger.debug("    " + _("Category: {category}").format(category=info['category']))
            else:
                logger.debug("  " + _("{cb_type}: None").format(cb_type=cb_type))

    def print_control_info(self, node_id: str, node_role: str, controls_config: List[str] = None):
        """Prints control information for debugging."""
        logger.debug(_("Control info for {id} (role: {role}):").format(id=node_id, role=node_role))
        if controls_config:
            logger.debug("  " + _("Config from JSON: {config}").format(config=controls_config))
        
        # Show custom callbacks
        if self.has_custom_callbacks:
            logger.debug("  " + _("Custom callbacks:"))
            for cb_name, cb_value in self.custom_callbacks_summary.items():
                if cb_value and cb_name != "auto_draw_value_cb":
                    logger.debug("    " + _("- {cb_name}: {cb_value}").format(cb_name=cb_name, cb_value=cb_value))
        
        # Show automatic functions
        if self._auto_click_function:
            logger.debug("  " + _("Auto click function: {name}").format(name=self._auto_click_function))
        if self._auto_position_function:
            logger.debug("  " + _("Auto position function: {name}").format(name=self._auto_position_function))
        
        # Show the draw function
        if self.effective_draw_value_cb:
            source = "custom" if self.draw_value_cb else "auto"
            logger.debug("  " + _("Draw value function: {name} ({source})").format(
                name=self.effective_draw_value_cb, source=source))