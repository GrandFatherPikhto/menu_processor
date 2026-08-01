from typing import Dict, List, Set, Optional, Any
import json

from flat_node import FlatNode
from menu_validator import MenuValidator
from menu_config import MenuConfig, ConfigError
from menu_flattener import MenuFlattener, FlattenerError
from menu_data import ControlType
from common import save_json_data
from i18n import _

class ProcessorError(Exception):
    """Исключение для ошибок конфигурации"""
    def __init__(self, message: str):
        super().__init__(message)

class MenuProcessor:
    def __init__(self, config_name: str):
        self._config_name = config_name
        self._config = MenuConfig(self._config_name)
        print("✅ " + _("Configuration {path} loaded successfully").format(path=self._config_name))
        self._validator = MenuValidator(config=self._config)
        errors = self._validator.validate()
        if errors:
            print("❌ " + _("Configuration contains errors:"))
            for id, items in errors.items():
                print("❌ " + _("{id}:").format(id=id))
                for item in items:
                    print("\t➤ " + str(item))
            raise ProcessorError("❌ " + _("Configuration error"))
        else:
            print("✅ " + _("and validated"))
            self._flattener = MenuFlattener(self._config)
            self._flat_nodes = self._flattener.flatten()
            
            # Отладочная информация о контролах
            self._print_control_summary()
    
    def _print_control_summary(self):
        """Печатает сводку по контролам для отладки"""
        print("\n📊 " + _("Control summary:"))
        for node in self._flat_nodes:
            if node.id == 'root':
                continue
            print("- " + str(node))
            if hasattr(node, 'print_control_info'):
                node.print_control_info()
        print()

    def save_flattern_json(self, file_name: str | None = None):
        """Сохраняет плоское представление меню в JSON (опционально)"""
        if file_name is None and self._config.output_flattern:
            file_name = self._config.output_flattern
        
        if file_name:
            flat_data = {
                "nodes": [
                    {
                        "id": node.id,
                        "name": node.name,
                        "type": node.type,
                        "role": node.role,
                        "parent": node.parent.id if node.parent else None,
                        "prev_sibling": node.prev_sibling.id if node.prev_sibling else None,
                        "next_sibling": node.next_sibling.id if node.next_sibling else None,
                        "children": [child.id for child in node.children],
                        "is_leaf": node.is_leaf,
                        "is_branch": node.is_branch,
                        "controls": [
                            {
                                "type": control["type"].value,
                                "purpose": control["purpose"],
                                "navigate": control["navigate"].value,
                                "required": control["required"]
                            }
                            for control in getattr(node, '_controls', [])
                        ]
                    }
                    for node in self._flat_nodes if node.id != 'root'
                ]
            }
            
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(flat_data, f, indent=2, ensure_ascii=False)
                print("✅ " + _("Flat menu saved to {path}").format(path=file_name))
            except Exception as e:
                print("❌ " + _("Error saving flat menu: {error}").format(error=e))

    @property
    def config(self) -> MenuConfig:
        return self._config

    @property
    def menu(self) -> Dict[str, FlatNode]:
        """Все узлы меню (исключая root)"""
        return {n.id: n for n in self._flat_nodes if n.id != 'root'}

    @property
    def functions(self) -> Dict[str, Dict[str, Any]]:
        """Все функции обработки, сгруппированные по имени с полной информацией"""
        items = {}
        
        for node in self._flat_nodes:
            if node.id == 'root':
                continue
                
            # Добавляем все доступные функции узла с полной информацией
            for function_info in node.all_function_infos:
                items[function_info["name"]] = function_info
            
            # Для callback роли - добавляем информацию о внешних callback'ах
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

    @property
    def categories(self) -> Dict[str, Dict[str, Any]]:
        """Все категории меню (тип + роль)"""
        items = {}
        for node in self._flat_nodes:
            if node.id == 'root':
                continue
                
            category = node.category
            if category is not None:
                items[category["name"]] = category
                
                # Добавляем информацию о доступных контролах для категории
                items[category["name"]]["available_controls"] = [
                    {
                        "type": control["type"].value,
                        "purpose": control["purpose"],
                        "navigate": control["navigate"].value
                    }
                    for control in getattr(node, '_controls', [])
                ]
        
        return items

    @property
    def leafs(self) -> Dict[str, FlatNode]:
        """Все листовые узлы (конечные пункты меню)"""
        return {n.id: n for n in self._flat_nodes if n.is_leaf and n.id != 'root'}

    @property
    def branches(self) -> Dict[str, FlatNode]:
        """Все ветви меню (узлы с детьми)"""
        return {n.id: n for n in self._flat_nodes if n.is_branch and n.id != 'root'}

    @property
    def first(self) -> Optional[FlatNode]:
        """Первый узел меню (после root)"""
        root_node = next((node for node in self._flat_nodes if node.id == 'root'), None)
        if root_node and root_node.first_child:
            return root_node.first_child
        return None

    @property 
    def callback_nodes(self) -> Dict[str, FlatNode]:
        """Все узлы с ролью callback"""
        return {n.id: n for n in self._flat_nodes if n.role == 'callback' and n.id != 'root'}

    @property
    def required_functions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Функции, сгруппированные по категориям с указанием обязательных"""
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

    @property
    def custom_callbacks(self) -> Dict[str, Dict[str, Any]]:
        """Все пользовательские callback-функции"""
        callbacks = {}
        
        for node in self._flat_nodes:
            if node.id == 'root':
                continue
                
            node_callbacks = node.custom_callbacks_summary
            for cb_type, cb_name in node_callbacks.items():
                if cb_name and cb_type != "auto_draw_value_cb":  # Исключаем автоматические
                    callbacks[cb_name] = {
                        "node_id": node.id,
                        "callback_type": cb_type,
                        "function_name": cb_name,
                        "node": node
                    }
        
        return callbacks

    @property
    def auto_generated_functions(self) -> Dict[str, Dict[str, Any]]:
        """Все автоматически сгенерированные функции с полной информацией"""
        auto_funcs = {}
        
        for node in self._flat_nodes:
            if node.id == 'root':
                continue
                
            # Автоматические функции обработки
            for func_info in node.all_function_infos:
                auto_funcs[func_info["name"]] = {
                    **func_info,
                    "node_id": node.id,
                    "source": "auto_generated"
                }
            
            # Автоматические функции отрисовки
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

    # Добавляем метод для группировки функций по типу события
    @property
    def functions_by_event_type(self) -> Dict[str, List[Dict[str, Any]]]:
        """Функции, сгруппированные по типу события"""
        grouped = {}
        
        for func_name, func_info in self.functions.items():
            event_type = func_info.get("event_type", "unknown")
            if event_type not in grouped:
                grouped[event_type] = []
            grouped[event_type].append(func_info)
        
        return grouped

    # Добавляем метод для получения функций по навигации
    @property
    def functions_by_navigation(self) -> Dict[str, List[Dict[str, Any]]]:
        """Функции, сгруппированные по типу навигации"""
        grouped = {}
        
        for func_name, func_info in self.functions.items():
            navigate = func_info.get("navigate", "unknown")
            if navigate not in grouped:
                grouped[navigate] = []
            grouped[navigate].append(func_info)
        
        return grouped
    
    @property
    def nodes_with_custom_callbacks(self) -> Dict[str, FlatNode]:
        """Все узлы с пользовательскими callback'ами"""
        return {n.id: n for n in self._flat_nodes if n.has_custom_callbacks and n.id != 'root'}

    def get_callbacks_by_type(self, callback_type: str) -> Dict[str, str]:
        """Получить callback'и определенного типа"""
        result = {}
        for node in self._flat_nodes:
            if node.id == 'root':
                continue
                
            callback_value = getattr(node, callback_type, None)
            if callback_value:
                result[node.id] = callback_value
        return result
    
    def print_callback_summary(self):
        """Печатает сводку по callback'ам"""
        print("\n🎛️ " + _("Callback functions summary:"))
        
        custom_callbacks = self.custom_callbacks
        if custom_callbacks:
            print(_("Custom callbacks:"))
            for cb_name, cb_info in custom_callbacks.items():
                print("  - " + _("{name} ({type}) -> {node_id}").format(
                    name=cb_name, type=cb_info['callback_type'], node_id=cb_info['node_id']))
        else:
            print(_("Custom callbacks: none"))
        
        auto_funcs = self.auto_generated_functions
        if auto_funcs:
            print(_("Automatically generated functions:"))
            for func_name, func_info in auto_funcs.items():
                print("  - " + _("{name} ({source}) -> {node_id}").format(
                    name=func_name, source=func_info['source'], node_id=func_info['node_id']))
        
        nodes_with_callbacks = self.nodes_with_custom_callbacks
        if nodes_with_callbacks:
            print(_("Nodes with custom callbacks: {count}").format(count=len(nodes_with_callbacks)))
        else:
            print(_("Nodes with custom callbacks: none"))

    def get_functions_by_category(self, category_name: str) -> List[Dict[str, Any]]:
        """Все функции для указанной категории"""
        return [
            func_info for func_info in self.functions.values()
            if func_info.get("category", {}).get("name") == category_name
        ]

    def validate_required_functions(self) -> bool:
        """Проверяет, что все обязательные функции сгенерированы"""
        missing_functions = []
        
        for node in self._flat_nodes:
            if node.id == 'root':
                continue
                
            for control in getattr(node, '_controls', []):
                if control.get("required", False):
                    function_name = None
                    if control["type"] == ControlType.CLICK:
                        function_name = node.callback_manager._auto_click_function
                    elif control["type"] == ControlType.POSITION:
                        function_name = node.callback_manager._auto_position_function
                    
                    if not function_name:
                        missing_functions.append({
                            "node": node.id,
                            "control": control["type"].value,
                            "purpose": control["purpose"]
                        })
        
        if missing_functions:
            print("❌ " + _("Missing required functions:"))
            for missing in missing_functions:
                print("   - " + _("{node}: {control} ({purpose})").format(
                    node=missing['node'], control=missing['control'], purpose=missing['purpose']))
            return False
        
        print("✅ " + _("All required functions are present"))
        return True

    @property
    def detailed_callback_infos(self) -> Dict[str, List[Dict[str, Any]]]:
        """Детальная информация о всех callback-функциях, сгруппированная по типам"""
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

    @property
    def callback_summary_by_category(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """Сводка callback-функций по категориям"""
        categories = {}
        
        for node in self._flat_nodes:
            if node.id == 'root':
                continue
                
            category = node.category_name
            if category not in categories:
                categories[category] = {}
            
            # Группируем callback'и по типу для каждой категории
            for cb_type, info in node.defined_callback_infos.items():
                if cb_type not in categories[category]:
                    categories[category][cb_type] = []
                categories[category][cb_type].append(info)
        
        return categories

    def get_callbacks_by_category(self, category_name: str) -> Dict[str, List[Dict[str, Any]]]:
        """Все callback-функции для указанной категории"""
        result = {}
        
        for node in self._flat_nodes:
            if node.id == 'root' or node.category_name != category_name:
                continue
                
            for cb_type, info in node.defined_callback_infos.items():
                if cb_type not in result:
                    result[cb_type] = []
                result[cb_type].append(info)
        
        return result


    def print_detailed_callback_summary(self):
        """Печатает детальную сводку по всем callback-функциям"""
        print("\n📋 " + _("Detailed callback functions summary:"))
        
        # Сводка по типам callback'ов
        detailed_infos = self.detailed_callback_infos
        for cb_type, infos in detailed_infos.items():
            if infos:
                custom_count = sum(1 for info in infos if info["custom"])
                auto_count = len(infos) - custom_count
                print("\n" + _("{type}:").format(type=cb_type.upper()))
                print("  " + _("Total: {total} (🎛️ {custom} custom, ⚙️ {auto} automatic)").format(
                    total=len(infos), custom=custom_count, auto=auto_count))
                
                for info in infos[:3]:  # Показываем первые 3 для примера
                    custom_flag = "🎛️" if info["custom"] else "⚙️"
                    print("    - " + _("{name} {flag} -> {node_id} ({category})").format(
                        name=info['name'], flag=custom_flag, node_id=info['node_id'], category=info['category']))
                
                if len(infos) > 3:
                    print("    " + _("... and {count} more").format(count=len(infos) - 3))

        # Сводка по категориям
        print("\n📊 " + _("Categories summary:"))
        category_summary = self.callback_summary_by_category
        for category, callbacks in category_summary.items():
            total = sum(len(cb_list) for cb_list in callbacks.values())
            if total > 0:
                print("\n  " + _("{category}:").format(category=category))
                for cb_type, cb_list in callbacks.items():
                    custom_count = sum(1 for cb in cb_list if cb["custom"])
                    auto_count = len(cb_list) - custom_count
                    print("    " + _("{type}: {count} (🎛️ {custom}, ⚙️ {auto})").format(
                        type=cb_type, count=len(cb_list), custom=custom_count, auto=auto_count))

    def print_detailed_function_summary(self):
        """Печатает детальную сводку по всем функциям с type и role"""
        print("\n📋 " + _("Detailed functions summary:"))
        
        # Сводка по типам событий
        by_event = self.functions_by_event_type
        for event_type, functions in by_event.items():
            print("\n🎯 " + _("{event} functions ({count}):").format(
                event=event_type.upper(), count=len(functions)))
            for func in functions[:3]:  # Показываем первые 3 для примера
                source_flag = "🎛️" if func.get("custom") else "⚙️"
                navigate_info = f" [navigate: {func.get('navigate', 'N/A')}]" if func.get("navigate") else ""
                type_role_info = f" ({func.get('type', 'N/A')}_{func.get('role', 'N/A')})"
                print(f"    - {func['name']} {source_flag}{navigate_info}{type_role_info} -> {func['node_id']}")
            
            if len(functions) > 3:
                print("    " + _("... and {count} more").format(count=len(functions) - 3))

        # Сводка по type и role
        print("\n🏷️ " + _("Types and roles summary:"))
        by_type_role = self.functions_by_type_role
        for type_role, functions in by_type_role.items():
            if type_role and type_role != "N/A_N/A":
                print("  " + _("{type_role}: {count} functions").format(
                    type_role=type_role, count=len(functions)))

    @property
    def functions_by_type_role(self) -> Dict[str, List[Dict[str, Any]]]:
        """Функции, сгруппированные по комбинации type_role"""
        grouped = {}
        
        for func_name, func_info in self.functions.items():
            type_val = func_info.get("type", "N/A")
            role_val = func_info.get("role", "N/A")
            type_role = f"{type_val}_{role_val}"
            
            if type_role not in grouped:
                grouped[type_role] = []
            grouped[type_role].append(func_info)
        
        return grouped

    @property
    def functions_by_type(self) -> Dict[str, List[Dict[str, Any]]]:
        """Функции, сгруппированные по типу данных"""
        grouped = {}
        
        for func_name, func_info in self.functions.items():
            type_val = func_info.get("type", "unknown")
            if type_val not in grouped:
                grouped[type_val] = []
            grouped[type_val].append(func_info)
        
        return grouped

    @property
    def functions_by_role(self) -> Dict[str, List[Dict[str, Any]]]:
        """Функции, сгруппированные по роли"""
        grouped = {}
        
        for func_name, func_info in self.functions.items():
            role_val = func_info.get("role", "unknown")
            if role_val not in grouped:
                grouped[role_val] = []
            grouped[role_val].append(func_info)
        
        return grouped
    
    def print_debug_factor_nodes(self):
        """Отладочная информация о factor узлах и их функциях"""
        print("\n🔍 " + _("DEBUG INFO ABOUT FACTOR NODES:"))
        
        factor_nodes = [n for n in self._flat_nodes if n.role == "factor" and n.id != 'root']
        print(_("Factor nodes: {ids}").format(ids=[n.id for n in factor_nodes]))
        
        for node in factor_nodes:
            print(f"\n--- {node.id} ---")
            print(_("Controls: {value}").format(value=node.controls))
            print(_("Navigate: {value}").format(value=node.navigate))
            
            # Проверяем CallbackManager
            print(_("Auto click function: {name}").format(name=node.callback_manager._auto_click_function))
            print(_("Auto position function: {name}").format(name=node.callback_manager._auto_position_function))
            print(_("Auto click info: {value}").format(value=node.callback_manager._auto_click_info))
            print(_("Auto position info: {value}").format(value=node.callback_manager._auto_position_info))
            
            print(_("Auto functions info: {value}").format(value=node.callback_manager.auto_functions_info))
            print(_("All function infos: {value}").format(value=node.all_function_infos))
            
            # Проверяем обязательные функции
            for control in getattr(node, '_controls', []):
                if control.get("required", False):
                    function_name = None
                    if control["type"] == ControlType.CLICK:
                        function_name = node.callback_manager._auto_click_function
                    elif control["type"] == ControlType.POSITION:
                        function_name = node.callback_manager._auto_position_function
                    print(_("Required {type}: {name} (purpose: {purpose})").format(
                        type=control['type'].value, name=function_name, purpose=control['purpose']))

# Обновляем main для использования улучшенной сводки
def main(config_name: str) -> int:
    try:
        processor = MenuProcessor(config_name)
        
        # ДОБАВИТЬ для отладки factor узлов:
        processor.print_debug_factor_nodes()
        
        print("\n📋 " + _("Data summary for generator:"))
        print("• " + _("Menu nodes: {count}").format(count=len(processor.menu)))
        print("• " + _("Categories: {count}").format(count=len(processor.categories)))
        print("• " + _("Functions: {count}").format(count=len(processor.functions)))
        print("• " + _("Leafs: {count}").format(count=len(processor.leafs)))
        print("• " + _("Branches: {count}").format(count=len(processor.branches)))
        print("• " + _("Callback nodes: {count}").format(count=len(processor.callback_nodes)))
        
        # Проверка обязательных функций
        processor.validate_required_functions()

        # Используем улучшенную сводку с type и role
        processor.print_detailed_function_summary()
        
        # Сохраняем плоское представление
        processor.save_flattern_json("./output/flatterned.json")

        save_json_data(processor.functions, "./output/functions.json")
        
        return 0
    except Exception as e:
        print("❌ " + _("Error: {error}").format(error=e))
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    main("./config/config.yaml")