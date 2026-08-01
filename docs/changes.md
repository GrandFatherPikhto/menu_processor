# 📝 Changelog (Menu Processor)

All notable changes are listed in reverse chronological order.
The format is inspired by [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### 🏗️ Package restructure

- The project root now contains **only** the entry point [`generate_menu.py`](../generate_menu.py:1).
- All source code, configuration, templates, locale catalogs and generated output moved
  into the [`generate_menu/`](../generate_menu/) Python package:
  - added [`__init__.py`](../generate_menu/__init__.py) and [`managers/__init__.py`](../generate_menu/managers/__init__.py);
  - all intra-package imports converted to **relative imports** (e.g. `from .i18n import _`,
    `from ..menu_data import MenuData`, `from .callback_manager import CallbackManager`);
  - removed the old top-level `generator.py` entry point.
- [`generate_menu.py`](../generate_menu.py:1) changes the working directory into the package before
  constructing [`MenuGenerator`](../generate_menu/menu_generator.py:15), because
  `templates_path`, `output_directory` and `output_flattern` are CWD-relative.
- Fixed `output_flattern` path in [`config.yaml`](../generate_menu/config/config.yaml:1):
  `../output/flatterned.json` → `output/flatterned.json`.

### 🌐 Comments & docstrings translated to English

- All comments and docstrings in every Python source file are now in English
  (previously many were in Russian).
- Cleaned up leftovers: removed a stray debug `print()` in
  [`menu_config.py`](../generate_menu/menu_config.py:145) `main()`, deduplicated an import.

### 📚 Documentation

- Added [`docs/architect.md`](./architect.md) (en) and [`docs/architect_ru.md`](./architect_ru.md) (ru)
  — architecture overview, module breakdown, configuration & path resolution, known issues
  and a prioritized improvement plan.
- Added [`docs/changes.md`](./changes.md) (en) and [`docs/changes_ru.md`](./changes_ru.md) (ru) — this changelog.
- Rewrote [`README.md`](../README.md) (en/ru): project purpose, examples of configuration,
  how it works, plus links to the docs.

## [2026-08-01] — YAML configuration

- Added a universal loader [`load_config_file()`](../generate_menu/common.py:25) that auto-detects
  the format by extension (`.json` / `.yaml` / `.yml`).
- [`MenuConfig`](../generate_menu/menu_config.py:17) now supports both JSON and YAML.
- Added YAML configs:
  - [`config/config.yaml`](../generate_menu/config/config.yaml:1)
  - [`config/files.yaml`](../generate_menu/config/files.yaml:1)
  - [`config/menu_data.yaml`](../generate_menu/config/menu_data.yaml:1)
  - [`config/menu_schema.yaml`](../generate_menu/config/menu_schema.yaml:1)
  - [`menu/menu.yaml`](../generate_menu/menu/menu.yaml:1)
- All entry points now use `./config/config.yaml`.
- JSON files kept as fallback/reference (can be removed once verified).

## [2026-08-01] — Internationalization (gettext / Babel)

- All user-facing messages internationalized with **gettext (Babel)**.
- Primary (source) language: **English**.
- Added [`i18n.py`](../generate_menu/i18n.py) with a self-adjusting locale directory
  (`Path(__file__).resolve().parent / "locale"`).
- Added [`babel.cfg`](../generate_menu/babel.cfg) and the catalog structure
  `locale/messages.pot`, `locale/ru/LC_MESSAGES/messages.{po,mo}`.
- Language is selected via the `MENU_PROCESSOR_LANG` environment variable (e.g. `ru`);
  falls back to English if unset or missing.

## [Earlier] — Initial implementation

- Base pipeline: config loading, validation (JSON Schema + custom), flattening,
  manager-based node model, aggregation, Jinja2 code generation for the LCD1602 menu.
