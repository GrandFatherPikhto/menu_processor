"""Enables ``python -m gui``.

This invocation path never goes through the root ``gui.py`` script, so it
repeats the same sys.path/chdir bootstrap independently.
"""

import os
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
os.chdir(_project_root)

from gui.app import main

if __name__ == "__main__":
    sys.exit(main())
