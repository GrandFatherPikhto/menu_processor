from menu_generator import MenuGenerator

def main(config_file:str):
    generator = MenuGenerator(config_file)

if __name__ == '__main__':
    main('./config/config.json')
