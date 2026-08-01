# 🧩 Интеграционные тесты (`test/`)

> Этот документ описывает **сквозные (интеграционные) тесты** в директории
> [`test/integration`](../test/integration). Модульные и smoke-тесты описаны в
> [tests_ru.md](./tests_ru.md).

---

## 1. Общее описание

Интеграционные тесты запускают **реальный конвейер генератора** и проверяют, что
сгенерированные C-исходники и JSON-артефакты действительно появляются на диске.
Они лежат в [`test/integration/`](../test/integration) и состоят из двух модулей:

- [`test_entrypoint.py`](../test/integration/test_entrypoint.py) — запускает корневой
  скрипт `generate_menu.py` в **отдельном подпроцессе**, ровно как это делает
  пользователь, и проверяет код возврата, сгенерированные артефакты и локализацию
  i18n;
- [`test_generation.py`](../test/integration/test_generation.py) — запускает полный
  конвейер **в том же процессе** (`MenuGenerator` / `MenuCraft`) и проверяет
  сгенерированные C-файлы и JSON-дампы.

Оба набора используют общие фикстуры из [`conftest.py`](../conftest.py).

## 2. `test_entrypoint.py` — сквозной запуск в подпроцессе

Эти тесты выполняют `python generate_menu.py` в корне проекта и проверяют:

| Тест | Что проверяет |
|------|---------------|
| `test_entrypoint_runs_successfully` | Корневой скрипт работает до конца и завершается кодом 0; в выводе есть "Configuration". |
| `test_entrypoint_generates_output_files` | Запуск создаёт `output/menu.c`, `output/include/menu.h`, `output/flatterned.json` и `output/functions.json`. |
| `test_entrypoint_writes_output_at_project_root` | Генерация пишет в корневой `output/` и **не создаёт** случайную папку `generate_menu/output`. |
| `test_russian_entrypoint_output` | При `MENU_PROCESSOR_LANG=ru` консольный вывод локализован ("Конфигурация", "успешно загружена"). |

В подпроцессе принудительно задаётся `PYTHONIOENCODING=utf-8`, чтобы эмодзи в
выводе программы не искажались на Windows (кодировка консоли по умолчанию —
cp1251).

## 3. `test_generation.py` — конвейер в том же процессе

Эти тесты переходят в корень проекта (через `monkeypatch.chdir`) и создают реальные
генератор/процессор:

| Тест | Что проверяет |
|------|---------------|
| `test_generator_creates_c_files` | Генератор записывает каждый ожидаемый файл (11 `.c`-исходников + заголовки, список `EXPECTED_FILES`), и все непустые. |
| `test_processor_exposes_flat_menu` | `processor.menu` содержит 17 узлов (18 плоских узлов минус виртуальный root). |
| `test_processor_saves_flat_and_functions_json` | `save_flattern_json()` / `save_json_data()` записывают корректные `flatterned.json` (17 узлов) и `functions.json`. |
| `test_generated_data_file_contains_node_titles` | Сгенерированный `menu_data_config.c` содержит реальные данные узлов (`s_values_str_start`, `"Start"`). |

## 4. Запуск интеграционного набора

Из корня проекта:

```bash
# только интеграционные тесты
python -m pytest test -q

# весь набор проекта (модульные + интеграционные)
python -m pytest -q
```

## 5. Примечания

- Интеграционные тесты **перезаписывают** файлы в `output/` (они запускают реальный
  генератор). `output/` в `.gitignore`, так что это безвредно.
- `test_entrypoint_writes_output_at_project_root` защищает от регрессии, при которой
  генерация могла бы заново создать папку `output/` внутри пакета `generate_menu`.
- Обе тестовые директории используют общий корневой [`conftest.py`](../conftest.py),
  поэтому `pytest.ini` (testpaths) и фикстуры применяются и к `tests/`, и к `test/`.
