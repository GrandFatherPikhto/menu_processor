# -*- coding: utf-8 -*-
"""Интернационализация (i18n) проекта на базе gettext/Babel.

Основной (исходный) язык всех сообщений — **английский**.

Выбор языка перевода осуществляется через переменную окружения
``MENU_PROCESSOR_LANG`` (например, ``ru`` для русского языка)::

    MENU_PROCESSOR_LANG=ru python generator.py

Если каталог переводов отсутствует, язык не найден или переменная
не задана — используются исходные английские сообщения (fallback).

Каталоги переводов располагаются в ``locale/<lang>/LC_MESSAGES/messages.mo``
и собираются из ``.po``-файлов командой::

    pybabel compile -d locale

Обновление ``.po`` после изменения исходников::

    pybabel extract -F babel.cfg -k _ -o locale/messages.pot .
    pybabel update -d locale -i locale/messages.pot
"""

from __future__ import annotations

import gettext
import os
from pathlib import Path

#: Домен переводов (имя .po/.mo файлов).
DOMAIN = "messages"

#: Каталог с переводами (locale/<lang>/LC_MESSAGES/<domain>.mo).
LOCALE_DIR = Path(__file__).resolve().parent / "locale"

#: Язык по умолчанию (основной язык сообщений).
DEFAULT_LANGUAGE = "en"


def get_language() -> str:
    """Возвращает язык из переменной окружения или язык по умолчанию.

    Returns:
        Код языка (например, ``"en"``, ``"ru"``).
    """
    return os.environ.get("MENU_PROCESSOR_LANG") or DEFAULT_LANGUAGE


_translation = gettext.translation(
    DOMAIN,
    localedir=str(LOCALE_DIR),
    languages=[get_language()],
    fallback=True,
)


def _(message: str) -> str:
    """Переводит сообщение на выбранный язык.

    Args:
        message: Исходное сообщение (на английском).

    Returns:
        Переведённое сообщение или исходное, если перевод отсутствует.
    """
    return _translation.gettext(message)


def ngettext(singular: str, plural: str, n: int) -> str:
    """Переводит сообщение с учётом множественного числа.

    Args:
        singular: Форма для одного элемента.
        plural: Форма для нескольких элементов.
        n: Количество элементов.

    Returns:
        Переведённое сообщение в правильной форме числа.
    """
    return _translation.ngettext(singular, plural, n)
