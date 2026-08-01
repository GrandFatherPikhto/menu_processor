# 📐 Архитектурный обзор и рекомендации (Menu Processor)

> Дата: 2026-08-01 · Анализ проведён по состоянию кодовой базы.

## 1. Общее описание системы

Проект — Python-генератор C-кода системы меню для embedded LCD1602.
Конвейер работы:

```
config (JSON)
  → MenuConfig          — загрузка всех конфигурационных файлов
  → MenuValidator       — JSON Schema + кастомная валидация дерева
  → MenuFlattener       — разворачивание дерева в плоский список + связи
  → FlatNode/BaseFlatNode — узел с композицией менеджеров
  → MenuProcessor       — координатор, агрегация данных для шаблонов
  → MenuGenerator       — рендер Jinja2 шаблонов → C-файлы
```

**Положительные стороны архитектуры:**

- ✅ Чистая композиция менеджеров в узле: [`NodeDataManager`](managers/node_data_manager.py:4), [`NodeControlManager`](managers/node_control_manager.py:7), [`NodeNavigationManager`](managers/node_navigation_manager.py:4), [`CallbackManager`](managers/callback_manager.py:4) — хорошее разделение ответственности.
- ✅ Разделение конвейера на загрузка → валидация → флаттенинг → генерация.
- ✅ `FunctionInfo`-dataclass + фабричные методы ([`managers/function_info.py`](managers/function_info.py:6)).
- ✅ Jinja2-шаблоны вынесены из кода.

---

## 2. Проблемы и рекомендации

### 2.1. Критические / архитектурные

#### 🔴 A1. «God-object» в MenuProcessor
[`menu_processor.py`](menu_processor.py:16) содержит **20+ свойств**, каждое из которых заново обходит `_flat_nodes` и собирает агрегированные словари (`functions`, `categories`, `functions_by_event_type`, `functions_by_navigation`, `functions_by_type_role`, `functions_by_type`, `functions_by_role`, `callback_summary_by_category`, `required_functions`, `custom_callbacks`, `auto_generated_functions` …).

Проблемы:
- O(N × M) повторных итераций по узлам;
- много почти идентичного кода (одна и та же «группировка по ключу»);
- класс трудно тестировать.

**Рекомендация:** вынести агрегацию в отдельный класс `MenuDataAggregator` (или серию функций), который один раз обходит узлы и кэширует результат (`functools.cached_property`). Это и упростит [`MenuProcessor`](menu_processor.py:16), и ускорит генерацию.

#### 🔴 A2. Dead code / недостижимый код
В [`managers/node_control_manager.py`](managers/node_control_manager.py:171) в свойстве `all_function_infos` после `return infos` (строка 195) осталось **недостижимое продолжение** (строки 196–225) — мёртвый код, который никогда не выполнится, но путает читателя.

Также:
- [`_apply_parent_navigation_rules`](menu_flattener.py:61) — не вызывается (дубликат `_apply_branch_navigation_rules`);
- [`MenuValidator._validate_data_type`](menu_validator.py:111) — возвращает пустой список (заглушка);
- множество закомментированных `print(f"DEBUG …")` во всех менеджерах.

**Рекомендация:** удалить недостижимые блоки и заглушки; закомментированные отладочные строки вычистить.

#### 🔴 A3. `print()` вместо логирования
Весь код завязан на `print()` с эмодзи (в том числе в production-путях). В [`menu_config.py`](menu_config.py:125) остался случайный отладочный `print(output_directory)`.

**Рекомендация:** перейти на `logging` (модуль `logging`): `logger = logging.getLogger(__name__)`. Вывод останется читаемым, но станет управляемым (уровни, файлы, отключение).

#### 🔴 A4. Конфиг: неконсистентность ключей и опечатки
- `output_flattern` — опечатка (`flatten`), она же в [`save_flattern_json`](menu_processor.py:49).
- Ключ `"menu_config"` в [`config.json`](config/config.json:4) указывает на `menu_data.json` — путаница между «конфигом меню» и «правилами типов/ролей».
- `files.json` использует `templates_path`, а `files_test01.json` — `templates` → при переключении на test01 конфиг сломается.
- В [`menu_config.py`](menu_config.py:22) ключ `"menu"` загружает дерево меню, а `"menu_config"` — правила данных; описания в аргументах перепутаны местами.
- В [`config/menu_schema.json`](config/menu_schema.json:29) в enum типов есть `"float"`, которого нет в [`config/menu_data.json`](config/menu_data.json:2) → расхождение схемы и правил.
- README упоминает `.j2`, а реальные шаблоны — `.jinja`.

**Рекомендация:** унифицировать имена ключей (например `menu_tree`, `data_rules`, `generation_files`, `templates_path`), исправить опечатки, привести схему в соответствие с правилами.

#### 🔴 A5. Пути: абсолютные пути и непереносимость
- [`menu/menu.json`](menu/menu.json:9): `output_directory: /home/yevst/...` — жёстко зашит абсолютный путь чужой машины; именно он используется в [`MenuConfig.generation_files`](menu_config.py:120) для построения выходных путей.
- `config/files_orig.json` и `config/files_test01.json` содержат абсолютные пути `/home/yevst/...`.

**Рекомендация:** `output_directory` вынести из дерева меню в основной конфиг (или задавать через CLI), по умолчанию — `./output/`. Пути в конфиге задавать относительно корня проекта.

#### 🔴 A6. Конструкторы с побочными эффектами
- [`MenuProcessor.__init__`](menu_processor.py:17) выполняет всю загрузку/валидацию/флаттенинг и бросает исключения.
- [`MenuGenerator.__init__`](menu_generator.py:15) сразу вызывает `_generate()`.

**Рекомендация:** конструкторы должны только сохранять зависимости; рабочие методы вызывать явно (`processor.run()`, `generator.generate()`). Это упростит тестирование и повторное использование.

---

### 2.2. Оптимизация и улучшения

#### 🟡 B1. Единая точка входа (CLI)
Сейчас **7** модулей имеют `main()` + блок `if __name__ == "__main__":` с захардкоженным `./config/config.json` (`menu_processor.py`, `menu_config.py`, `menu_data.py`, `menu_validator.py`, `menu_flattener.py`, `menu_generator.py`, `generator.py`).

**Рекомендация:** один `cli.py`/`__main__.py` с `argparse` (`--config`, `--output`, `--flat-only`, `--debug`). Модули-библиотеки оставить без `main()`.

#### 🟡 B2. Нет тестов
В проекте нет ни одного теста (ни `pytest`, ни `unittest`). Отладочные `main()` в каждом модуле — это замена тестам.

**Рекомендация:** добавить `tests/` с `pytest`:
- unit: `MenuData` (правила типов/ролей/контролов);
- unit: `MenuValidator` (валидные/невалидные деревья);
- unit: `MenuFlattener` (связи, циклическая навигация);
- e2e: полная генерация из sample-конфига → проверка, что C-файлы создаются.

#### 🟡 B3. Кэширование агрегаций
Вычисляемые свойства `MenuProcessor` считать один раз. Особенно актуально при больших деревьях меню.

#### 🟡 B4. Убрать дублирование валидации
`MenuValidator._validate_item` дублирует логику из `NodeDataManager.validate_numeric_range/validate_fixed_values`. Единый источник правды — правила из [`config/menu_data.json`](config/menu_data.json:1).

#### 🟡 B5. `pathlib.Path` везде
Смешаны `os.path`, строки и `Path`. Привести всё к `pathlib.Path`.

#### 🟡 B6. Временная связность CallbackManager
[`CallbackManager`](managers/callback_manager.py:28) инициализируется с пустыми `_auto_*`, а заполняется позже через `set_auto_functions()` из `NodeControlManager`. Это хрупко (нужно не забыть вызвать). **Рекомендация:** передавать автоматические функции при конструировании или вычислять их лениво.

#### 🟡 B7. Неконсистентная типизация
Смешаны `Dict`/`dict`, `List`/`list` в аннотациях. Унифицировать (лучше — перейти на современный синтаксис `dict[str, ...]`, Py3.10+).

#### 🟡 B8. Лишние импорты
- [`menu_flattener.py`](menu_flattener.py:5) импортирует `MenuValidator` — не используется.
- [`menu_generator.py`](menu_generator.py:6) импортирует `Environment` дважды.
- `generator.py`/`menu_generator.py` — параметр `config_file` в `main()` не используется.

#### 🟡 B9. Схема для `menu_data.json`
Правила типов/ролей/контролов не валидируются вообще. Добавить схему/валидацию для этого файла.

---

## 3. Миграция конфигурации на YAML (реализовано)

`PyYAML` уже присутствует в [`requirements.txt`](requirements.txt:6), но не использовался.

Что сделано:
1. В [`common.py`](common.py:1) добавлен универсальный загрузчик [`load_config_file()`](common.py:28) — автоматически определяет формат по расширению (`.json` / `.yaml` / `.yml`).
2. [`MenuConfig`](menu_config.py:16) переведён на универсальный загрузчик — поддерживает и JSON, и YAML.
3. Созданы YAML-конфиги:
   - [`config/config.yaml`](config/config.yaml:1)
   - [`config/files.yaml`](config/files.yaml:1)
   - [`config/menu_data.yaml`](config/menu_data.yaml:1)
   - [`config/menu_schema.yaml`](config/menu_schema.yaml:1)
   - [`menu/menu.yaml`](menu/menu.yaml:1)
4. Все точки входа переведены на `./config/config.yaml`.
5. JSON-файлы оставлены как резервные/справочные (могут быть удалены после проверки).

---

## 4. Приоритизированный план изменений

| Приоритет | Задача | Файлы |
|-----------|--------|-------|
| 🔴 P0 | Перевести конфиг на YAML (готово) | `common.py`, `menu_config.py`, `config/*.yaml`, `menu/menu.yaml` |
| 🔴 P0 | Удалить dead code, недостижимые блоки | `node_control_manager.py`, `menu_flattener.py`, `menu_validator.py` |
| 🔴 P1 | `logging` вместо `print()` | все модули |
| 🔴 P1 | Исправить опечатки и ключи конфига | `menu_config.py`, `config/*` |
| 🔴 P1 | Вынести `output_directory` из дерева меню | `menu_config.py`, `config.yaml`, CLI |
| 🟡 P2 | Вынести агрегацию из `MenuProcessor` | новый `aggregator.py` |
| 🟡 P2 | Единый CLI с `argparse` | новый `cli.py` |
| 🟡 P2 | Тесты `pytest` | `tests/` |
| 🟡 P3 | Единая валидация, `pathlib`, типизация | все модули |
