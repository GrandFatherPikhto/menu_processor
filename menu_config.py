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

        if 'includes' in config_data:
            self.includes = config_data['includes'].copy()
        else:
            self.includes = None
    
    def validate(self) -> List[str]:
        """Валидация конфигурации"""
        errors = []
        
        if 'menu_source' not in self.templates:
            errors.append("Отсутствует шаблон для .c файла меню")
        if 'menu_header' not in self.templates:
            errors.append("Отсутствует шаблон для .h файла меню")
        
        print(self.output_files)

        if 'menu_source' not in self.output_files:
            errors.append("Отсутствует путь для создания .h файла меню")
        if 'menu_header' not in self.output_files:
            errors.append("Отсутствует путь для создания .c файла меню")
        
        return errors
    
    def get_template_path(self, file_type: str) -> Optional[str]:
        """Получить путь к шаблону по типу файла"""
        return self.templates.get(file_type, None)
    
    def get_output_path(self, file_type: str) -> Optional[str]:
        """Получить путь к выходному файлу по типу файла"""
        return self.output_files.get(file_type, None)
    
    def get_templates(self) -> Dict[str, str]:
        """Геттер для всех шаблонов"""
        return self.templates.copy()
    
    def get_output_files(self) -> Dict[str, str]:
        """Геттер для всех выходных файлов"""
        return self.output_files.copy()
    
    def get_includes(self) -> List[str] | None:
        """Геттер для includes"""
        return self.includes
