from menu_generator import MenuGenerator
from common import load_json_data

def main():
    config = load_json_data('config/config.json')

    generator = MenuGenerator(config=config)
    generator.load_menu()
    generator.save_flatterned_menu()
    generator.generate()

if __name__ == '__main__':
    main()
