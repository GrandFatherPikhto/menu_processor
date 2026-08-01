#!/usr/bin/env python3
"""
Menu Processor — command-line entry point.

Runs the menu generator that produces C source files for an embedded
LCD1602 menu system from a YAML/JSON menu definition.

The script first changes the current working directory into the
``generate_menu`` package directory because configuration paths
(templates, output directory and the flattened menu file) are resolved
relative to the current working directory.
"""
import os
import sys
from pathlib import Path

#: Configuration file path, resolved relative to the package directory.
CONFIG_PATH = "./config/config.yaml"


def main() -> int:
    """Runs the menu generator and returns the process exit code."""
    project_root = Path(__file__).resolve().parent
    package_dir = project_root / "generate_menu"

    if not package_dir.is_dir():
        print(f"Package directory not found: {package_dir}")
        return 1

    # Make the package importable even when the script is invoked from
    # a different working directory.
    root_dir = str(project_root)
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    # Configuration paths (templates, output directory, flattened menu)
    # are resolved relative to the current working directory, so change
    # into the package directory to keep them stable.
    os.chdir(package_dir)

    from generate_menu.menu_generator import MenuGenerator

    MenuGenerator(CONFIG_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
