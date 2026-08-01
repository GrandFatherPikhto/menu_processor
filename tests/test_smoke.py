"""Smoke tests: minimal end-to-end sanity checks of the package.

These tests verify that the package imports, the real configuration loads
and validates, and the real menu flattens into the expected structure.
"""


def test_package_imports():
    """All public modules of the package import without errors."""
    from generate_menu.menu_config import ConfigError, MenuConfig
    from generate_menu.menu_data import ControlType, MenuData, NavigationType
    from generate_menu.menu_flattener import FlattenerError, MenuFlattener
    from generate_menu.menu_generator import MenuGenerator
    from generate_menu.menucraft import MenuCraft
    from generate_menu.menu_validator import MenuValidator, ParserError
    from generate_menu.flat_node import FlatNode

    assert all(
        cls is not None
        for cls in (
            ConfigError,
            MenuConfig,
            ControlType,
            MenuData,
            NavigationType,
            FlattenerError,
            MenuFlattener,
            MenuGenerator,
            MenuCraft,
            MenuValidator,
            ParserError,
            FlatNode,
        )
    )


def test_config_loads_from_absolute_path(config_path):
    """The real YAML configuration loads from any working directory."""
    from generate_menu.menu_config import MenuConfig

    config = MenuConfig(str(config_path))
    assert config.menu_schema is not None
    assert config.menu_data is not None
    assert config.data_config is not None
    assert config.menu_tree is not None


def test_config_navigation_defaults(menu_config):
    """Configuration defaults read from menu.yaml."""
    assert menu_config.default_navigate == "limit"
    assert menu_config.default_control == "position"
    assert menu_config.default_branch_navigate == "cyclic"
    assert menu_config.root_navigate == "cyclic"


def test_real_config_validates(menu_validator):
    """The bundled menu passes validation without errors."""
    assert menu_validator.validate() == {}


def test_real_menu_flattens(menu_flattener):
    """The bundled menu flattens into the expected number of nodes."""
    flat = menu_flattener.flatten()
    assert len(flat) == 18
    assert flat[0].id == "root"
