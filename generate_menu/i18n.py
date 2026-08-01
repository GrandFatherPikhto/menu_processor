# -*- coding: utf-8 -*-
"""Project internationalization (i18n) based on gettext/Babel.

The primary (source) language of all messages is **English**.

The translation language is selected through the environment variable
``MENU_PROCESSOR_LANG`` (for example, ``ru`` for Russian)::

    MENU_PROCESSOR_LANG=ru python generate_menu.py

If the translation catalog is missing, the language is not found or the
variable is not set — the original English messages are used (fallback).

Translation catalogs live in ``locale/<lang>/LC_MESSAGES/messages.mo`` and
are compiled from ``.po`` files with the command::

    pybabel compile -d locale

Updating ``.po`` files after changing the sources::

    pybabel extract -F babel.cfg -k _ -o locale/messages.pot .
    pybabel update -d locale -i locale/messages.pot
"""

from __future__ import annotations

import gettext
import os
from pathlib import Path

#: Translation domain (the name of the .po/.mo files).
DOMAIN = "messages"

#: Directory with translations (locale/<lang>/LC_MESSAGES/<domain>.mo).
LOCALE_DIR = Path(__file__).resolve().parent / "locale"

#: Default language (the source language of the messages).
DEFAULT_LANGUAGE = "en"


def get_language() -> str:
    """Returns the language from the environment variable or the default.

    The value is stripped of surrounding whitespace so that shell quirks
    (for example ``set MENU_PROCESSOR_LANG=ru && ...`` on Windows cmd)
    do not produce ``"ru "`` and silently fall back to English.

    Returns:
        The language code (for example, ``"en"``, ``"ru"``).
    """
    return (os.environ.get("MENU_PROCESSOR_LANG") or "").strip() or DEFAULT_LANGUAGE


_translation = gettext.translation(
    DOMAIN,
    localedir=str(LOCALE_DIR),
    languages=[get_language()],
    fallback=True,
)


def _(message: str) -> str:
    """Translates a message into the selected language.

    Args:
        message: The source message (in English).

    Returns:
        The translated message, or the original if no translation exists.
    """
    return _translation.gettext(message)


def ngettext(singular: str, plural: str, n: int) -> str:
    """Translates a message taking plural forms into account.

    Args:
        singular: The form for a single item.
        plural: The form for several items.
        n: The number of items.

    Returns:
        The translated message in the correct plural form.
    """
    return _translation.ngettext(singular, plural, n)
