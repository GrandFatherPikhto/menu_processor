#!/usr/bin/env python3
"""
Menu Processor — command-line entry point.

Runs the menu generator that produces C source files for an embedded
LCD1602 menu system from a YAML/JSON menu definition.

This script is a thin wrapper around :mod:`generate_menu.cli`, which changes
the current working directory into the project root because configuration
paths (config/, menu/, templates/, output/) are resolved relative to the
current working directory.
"""
import sys
from pathlib import Path


def main() -> int:
    """Runs the menu generator CLI and returns the process exit code."""
    project_root = Path(__file__).resolve().parent

    # Make the package importable even when the script is invoked from
    # a different working directory.
    root_dir = str(project_root)
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    from generate_menu.cli import main as cli_main

    return cli_main()


if __name__ == "__main__":
    sys.exit(main())
