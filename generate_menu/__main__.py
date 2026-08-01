"""Enables running the CLI with ``python -m generate_menu``."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
