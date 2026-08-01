# 📝 Журнал изменений (Menu Processor)

Все значимые изменения перечислены в обратном хронологическом порядке.
Формат вдохновлён [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### 🏗️ Реструктуризация пакета

- В корне проекта теперь находится **только** точка входа [`generate_menu.py`](../generate_menu.py:1).
- Весь исходный код, конфигурация, шаблоны, locale-каталоги и сгенерированный вывод
  перенесены в Python-пакет [`generate_menu/`](../generate_menu/):
  - добавлены [`__init__.py`](../generate_menu/__init__.py) и [`managers/__init__.py`](../generate_menu/managers/__init__.py);
  - все внутренние импорты переведены на **относительные** (например, `from .i18n import _`,
    `from ..menu_data import MenuData`, `from .callback_manager import CallbackManager`);
  - удалён старый корневой entry point `generator.py`.
- [`generate_menu.py`](../generate_menu.py:1) меняет рабочую директорию на пакет перед
  созданием [`MenuGenerator`](../generate_menu/menu_generator.py:15), т.к. `templates_path`,
  `output_directory` и `output_flattern` зависят от CWD.
- Исправлен путь `output_flattern` в [`config.yaml`](../generate_menu/config/config.yaml:1):
  `../output/flatterned.json` → `output/flatterned.json`.

### 🌐 Комментарии и докстринги переведены на английский

- Все комментарии и докстринги во всех Python-файлах теперь на английском
  (ранее многие были на русском).
- Убраны остатки: удалён случайный отладочный `print()` в `main()`
  ([`menu_config.py`](../generate_menu/menu_config.py:145)), убран дублирующий импорт.

### 📚 Документация

- Добавлены [`docs/architect.md`](./architect.md) (en) и [`docs/architect_ru.md`](./architect_ru.md) (ru)
  — обзор архитектуры, разбор модулей, конфигурация и разрешение путей, известные проблемы
  и приоритизированный план улучшений.
- Добавлены [`docs/changes.md`](./changes.md) (en) и [`docs/changes_ru.md`](./changes_ru.md) (ru) — этот журнал.
- Переписан [`README.md`](../README.md) (en/ru): назначение проекта, примеры конфигурации,
  как это работает, а также ссылки на документацию.

## [2026-08-01] — YAML-конфигурация

- Добавлен универсальный загрузчик [`load_config_file()`](../generate_menu/common.py:25),
  автоматически определяющий формат по расширению (`.json` / `.yaml` / `.yml`).
- [`MenuConfig`](../generate_menu/menu_config.py:17) теперь поддерживает и JSON, и YAML.
- Добавлены YAML-конфиги:
  - [`config/config.yaml`](../generate_menu/config/config.yaml:1)
  - [`config/files.yaml`](../generate_menu/config/files.yaml:1)
  - [`config/menu_data.yaml`](../generate_menu/config/menu_data.yaml:1)
  - [`config/menu_schema.yaml`](../generate_menu/config/menu_schema.yaml:1)
  - [`menu/menu.yaml`](../generate_menu/menu/menu.yaml:1)
- Все точки входа переведены на `./config/config.yaml`.
- JSON-файлы оставлены как резервные/справочные (могут быть удалены после проверки).

## [2026-08-01] — Интернационализация (gettext / Babel)

- Все пользовательские сообщения интернационализированы через **gettext (Babel)**.
- Основной (исходный) язык — **английский**.
- Добавлен [`i18n.py`](../generate_menu/i18n.py) с самокорректирующимся каталогом locale
  (`Path(__file__).resolve().parent / "locale"`).
- Добавлены [`babel.cfg`](../generate_menu/babel.cfg) и структура каталогов
  `locale/messages.pot`, `locale/ru/LC_MESSAGES/messages.{po,mo}`.
- Язык выбирается через переменную окружения `MENU_PROCESSOR_LANG` (например, `ru`);
  при отсутствии или ошибке используется английский (fallback).

## [Раньше] — Первоначальная реализация

- Базовая цепочка: загрузка конфигов, валидация (JSON Schema + кастомная),
  флаттенинг, модель узла на менеджерах, агрегация, генерация C-кода на Jinja2
  для меню LCD1602.
