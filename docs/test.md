# 🧩 Integration Tests (`test/`)

> This document covers the **end-to-end integration tests** located in the
> [`test/integration`](../test/integration) directory. For the unit & smoke tests
> see [tests.md](./tests.md).

---

## 1. Overview

The integration tests run the **real generator pipeline** and verify that the
produced C sources and JSON artifacts actually appear on disk. They live in
[`test/integration/`](../test/integration) and consist of two modules:

- [`test_entrypoint.py`](../test/integration/test_entrypoint.py) — runs the root
  `generate_menu.py` script in a **subprocess**, exactly as a user would, and checks
  the exit code, the generated artifacts and i18n localization;
- [`test_generation.py`](../test/integration/test_generation.py) — runs the full
  pipeline **in-process** (`MenuGenerator` / `MenuCraft`) and verifies the
  generated C files and JSON dumps.

Both suites reuse the shared fixtures from [`conftest.py`](../conftest.py).

## 2. `test_entrypoint.py` — subprocess end-to-end

These tests execute `python generate_menu.py` in the project root and assert:

| Test | Verifies |
|------|----------|
| `test_entrypoint_runs_successfully` | The root script runs end-to-end and exits with code 0; the output mentions "Configuration". |
| `test_entrypoint_generates_output_files` | The run produces `output/menu.c`, `output/include/menu.h`, `output/flatterned.json` and `output/functions.json`. |
| `test_entrypoint_writes_output_at_project_root` | Generation writes into the root `output/` and leaves **no stray** `generate_menu/output` directory. |
| `test_russian_entrypoint_output` | With `MENU_PROCESSOR_LANG=ru` the console output is localized ("Конфигурация", "успешно загружена"). |

The subprocess forces `PYTHONIOENCODING=utf-8` so the emoji in the program output is
not corrupted on Windows (default console encoding is cp1251).

## 3. `test_generation.py` — in-process pipeline

These tests change into the project root (via `monkeypatch.chdir`) and construct the
real generator/processor:

| Test | Verifies |
|------|----------|
| `test_generator_creates_c_files` | The generator writes every expected file (11 `.c` sources + headers, listed in `EXPECTED_FILES`), non-empty. |
| `test_processor_exposes_flat_menu` | `processor.menu` contains 17 nodes (18 flat nodes minus the virtual root). |
| `test_processor_saves_flat_and_functions_json` | `save_flattern_json()` / `save_json_data()` write valid `flatterned.json` (17 nodes) and `functions.json`. |
| `test_generated_data_file_contains_node_titles` | The generated `menu_data_config.c` embeds real node data (`s_values_str_start`, `"Start"`). |

## 4. Running the integration suite

From the project root:

```bash
# integration tests only
python -m pytest test -q

# the whole project suite (unit + integration)
python -m pytest -q
```

## 5. Notes

- The integration tests **overwrite** the files in `output/` (they run the real
  generator). `output/` is git-ignored, so this is harmless.
- `test_entrypoint_writes_output_at_project_root` guards against a regression where
  generation would recreate an `output/` folder inside the `generate_menu` package.
- The two test directories share the same root [`conftest.py`](../conftest.py), so
  `pytest.ini` (testpaths) and the fixtures apply to both `tests/` and `test/`.
