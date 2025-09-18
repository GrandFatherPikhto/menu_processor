#!/usr/bin/env python3

from menu_processor import MenuProcessor
from menu_generator import MenuGenerator

def main(input_file: str, output_file: str):
    if processor.load_menu_file(input_file):
        print("✅ Файл успешно загружен и валидирован")
        
        # Показываем сводную информацию
        processor.print_summary()
        
        # Показываем корневой элемент
        root = processor.menu_structure.get('root')
        if root:
            print(f"\n🌳 Корневая нода:")
            print(f"   ID: {root['id']}")
            print(f"   Первый ребенок: {root.get('first_child', 'None')}")
        
        # Генерируем выходной файл
        processor.generate_output("output/flattened_menu.json")

        print("\n🎉 Обработка завершена успешно!")

        generator = MenuGenerator(processor=processor)

        generator.generate()
        
    else:
        print("\n💥 Ошибка загрузки файла")    

if __name__ == "__main__":
    processor = MenuProcessor()
    
    input_file = "config/menu_config.json"
    output_file = "output/menu_config_flattened.json"
    main(input_file=input_file, output_file=output_file)    
