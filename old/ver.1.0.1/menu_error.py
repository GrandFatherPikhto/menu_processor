from typing import Dict, List, Optional, Any    

class MenuError(Exception):
    """Базовое исключение для ошибок меню"""
    def __init__(self, message: str, node_path: List[str] = None):
        self.message = message
        self.node_path = node_path or []
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        path_str = ' -> '.join(self.node_path) if self.node_path else 'root'
        return f"{path_str}: {self.message}"
