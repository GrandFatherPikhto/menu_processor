from menu_generator import MenuGenerator

def main(config_path:str, output_path: str):
    generator = MenuGenerator()
    generator.load_config(config_path)
    generator.save_template(output_path)
    generator.generate()

if __name__ == '__main__':
    main('config/menu.json', 'config/template.json')
