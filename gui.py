"""Root entry point for the MenuCraft GUI.

Mirrors generate_menu.py: makes the project importable and resolves the
current working directory to the project root, since values inside the
loaded config files (templates_path, output_directory, flatten) are
resolved relative to the CWD, not the config file's own location. gui.py
never routes through generate_menu.cli.main() (where that chdir normally
happens), so it is repeated here explicitly.
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
os.chdir(project_root)

from gui.app import main

if __name__ == "__main__":
    sys.exit(main())
