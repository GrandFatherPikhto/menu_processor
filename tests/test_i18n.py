"""Tests for the gettext/Babel internationalization module.

The translation is bound at module import time, so environment-variable
changes in the current process have no effect. Russian catalog checks
therefore run in a fresh subprocess.
"""

import os
import subprocess
import sys
from pathlib import Path

# Project root (the parent of the tests/ directory).
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_default_language_is_english():
    """Without an environment variable the language is English."""
    from generate_menu import i18n

    assert i18n.get_language() == "en"


def test_get_language_reads_environment(monkeypatch):
    """get_language() reflects the environment variable."""
    from generate_menu import i18n

    monkeypatch.setenv("MENU_PROCESSOR_LANG", "ru")
    assert i18n.get_language() == "ru"


def test_english_identity_without_translation():
    """English source messages pass through unchanged."""
    from generate_menu import i18n

    assert (
        i18n._("Configuration loaded successfully")
        == "Configuration loaded successfully"
    )
    assert i18n.ngettext("file", "files", 1) == "file"
    assert i18n.ngettext("file", "files", 2) == "files"


def test_russian_translation_in_subprocess():
    """
    The Russian catalog is applied in a fresh subprocess.

    A subprocess simulates a real ``MENU_PROCESSOR_LANG=ru`` run because the
    translation is bound when the module is imported.
    """
    code = (
        "import sys; sys.path.insert(0, {root!r}); "
        "from generate_menu import i18n; "
        "print(i18n._('Configuration loaded successfully'))"
    ).format(root=str(PROJECT_ROOT))

    env = dict(os.environ)
    env["MENU_PROCESSOR_LANG"] = "ru"
    # Force UTF-8 stdout in the subprocess (Windows defaults to cp1251,
    # which would garble the Russian output before it reaches this test).
    env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        cwd=str(PROJECT_ROOT),
    )
    assert result.returncode == 0, result.stderr
    assert "Конфигурация успешно загружена" in result.stdout
