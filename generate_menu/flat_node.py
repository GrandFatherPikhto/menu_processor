from typing import Dict, List, Optional, Set, Any
from .base_flat_node import BaseFlatNode
from .menu_config import MenuConfig
from .menu_data import MenuData

class FlatNode(BaseFlatNode):
    """Final node class - uses the manager composition from BaseFlatNode."""
    
    def __init__(self, original_node: Dict[str, Any], config: MenuConfig, menu_data: MenuData):
        # Use inheritance from BaseFlatNode
        super().__init__(original_node, config, menu_data)
        
        # Initialize the control manager
        self._init_control_manager()

    # Keep only backward-compatible properties for temporary support
    @property
    def effective_click_cb_name(self) -> Optional[str]:
        """Callback function name for click (custom or automatic) with a _cb suffix."""
        info = self.get_click_info()
        if not info:
            return None
        return info["name"]

    @property
    def effective_position_cb_name(self) -> Optional[str]:
        """Callback function name for position (custom or automatic) with a _cb suffix."""
        info = self.get_position_info()
        if not info:
            return None
        return info["name"]

    @property
    def effective_double_click_cb_name(self) -> Optional[str]:
        """Callback function name for double click with a _cb suffix."""
        info = self.get_double_click_info()
        if not info:
            return None
        return info["name"] if info else None

    @property
    def effective_long_click_cb_name(self) -> Optional[str]:
        """Callback function name for long click with a _cb suffix."""
        info = self.get_long_click_info()
        if not info:
            return None
        return info["name"] if info else None

    @property
    def effective_event_cb_name(self) -> Optional[str]:
        """Callback function name for events with a _cb suffix."""
        info = self.get_event_info()
        if not info:
            return None
        return info["name"] if info else None

    @property
    def effective_draw_value_cb_name(self) -> Optional[str]:
        """Callback function name for drawing a value with a _cb suffix."""
        info = self.get_draw_value_info()
        if not info:
            return None
        return info["name"]