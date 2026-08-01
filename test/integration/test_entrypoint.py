"""Integration tests: the command-line entry point end-to-end.

The root ``generate_menu.py`` script is executed in a subprocess exactly as
a user would run it, so the tests verify the real entry point, its exit code,
the generated artifacts and i18n localization.
"""

import os
import subprocess
import sys
from pathlib import Path

# Project root (two levels up from this file).
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _run_entrypoint(env_extra=None):
    """Runs the root generate_menu.py entry point in a subprocess."""
    env = dict(os.environ)
    # Force UTF-8 stdout/stderr in the subprocess: on Windows the console
    # encoding (cp1251) cannot represent the emoji used in the program output.
    env["PYTHONIOENCODING"] = "utf-8"
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, "generate_menu.py"],
        cwd=str(PROJECT_ROOT),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_entrypoint_runs_successfully():
    """The root script runs end-to-end and exits with code 0."""
    result = _run_entrypoint()
    assert result.returncode == 0, result.stderr
    assert "Configuration" in result.stdout


def test_entrypoint_generates_output_files():
    """Running the entry point produces the C sources and JSON artifacts."""
    result = _run_entrypoint()
    assert result.returncode == 0, result.stderr

    output = PROJECT_ROOT / "generate_menu" / "output"
    assert (output / "menu.c").is_file()
    assert (output / "include" / "menu.h").is_file()
    assert (output / "flatterned.json").is_file()
    assert (output / "functions.json").is_file()


def test_entrypoint_creates_no_stray_root_output():
    """
    No stray output directory is created at the project root; generation
    writes exclusively into generate_menu/output/.
    """
    result = _run_entrypoint()
    assert result.returncode == 0, result.stderr
    assert not (PROJECT_ROOT / "output").exists()


def test_russian_entrypoint_output():
    """With MENU_PROCESSOR_LANG=ru the console output is localized."""
    result = _run_entrypoint(env_extra={"MENU_PROCESSOR_LANG": "ru"})
    assert result.returncode == 0, result.stderr
    assert "Конфигурация" in result.stdout
    assert "успешно загружена" in result.stdout
