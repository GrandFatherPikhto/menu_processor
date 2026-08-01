# 🎛️ Генератор C-меню для Embedded LCD1602

## 📖 Общее описание

**Генератор C-меню** - это Python-пакет для автоматической генерации C-кода системы меню на основе JSON-конфигурации. Система предназначена для использования в embedded-проектах с LCD дисплеями 1602 и энкодерами.

### 🚀 Основные возможности:
- **Автоматическая генерация** C-кода из JSON-конфигурации
- **Поддержка различных типов данных**: числа, строки, перечисления
- **Гибкая система callback-функций**: пользовательские и автоматические
- **Циклическая навигация**: закольцованные и линейные меню
- **Валидация конфигурации**: проверка корректности перед генерацией
- **Модульная архитектура**: легко расширяемая система

## 🏗️ Архитектура системы

### 📁 Структура проекта

```
Menu_Processor/
├── 📁 config/                 # Конфигурационные файлы
│   ├── config.json           # Основной конфиг с путями
│   ├── menu_schema.json      # JSON Schema для валидации
│   ├── menu.json            # Дерево меню
│   └── menu_data.json       # Правила типов, ролей, callback'ов
├── 📁 src/                   # Исходный код
│   ├── 🏗️  base_flat_node.py      # Базовый класс узла
│   ├── 🎛️  callback_manager.py    # Менеджер callback-функций  
│   ├── 📊  flat_node.py           # Основной класс узла
│   ├── 🧭  menu_config.py         # Загрузка конфигурации
│   ├── 📋  menu_data.py           # Правила типов и ролей
│   ├── 🔄  menu_flattener.py      # Преобразование дерева в плоский список
│   ├── 🛠️  menu_generator.py      # Генерация C-кода
│   ├── ⚙️  menu_processor.py      # Основной координатор
│   ├── ✅  menu_validator.py      # Валидация JSON
│   ├── 📁  managers/              # Менеджеры
│   │   ├── 📊  node_data_manager.py      # Управление данными
│   │   ├── 🎮  node_control_manager.py   # Управление контролами
│   │   └── 🧭  node_navigation_manager.py # Управление навигацией
│   └── 🔧  common.py              # Вспомогательные функции
├── 📁 templates/             # Jinja2 шаблоны для генерации C-кода
├── 📁 output/                # Сгенерированные файлы
└── 📁 menu/                  # Примеры меню (внешняя папка)
```

### 🔄 Процесс работы

```
JSON конфигурация 
    → MenuConfig (загрузка)
    → MenuValidator (проверка)
    → MenuFlattener (преобразование в плоский список)
    → FlatNode с менеджерами (обработка данных)
    → MenuProcessor (подготовка данных)
    → MenuGenerator (генерация C-кода через шаблоны)
    → C файлы
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install jinja2 jsonschema
```

### 2. Создание конфигурации

**config/config.json:**
```json
{
  "menu_schema": "menu_schema.json",
  "menu_config": "menu_data.json", 
  "menu": "../menu/menu.json",
  "output_flattern": "../output/flatterned.json",
  "generation_files": "files.json"
}
```

**config/files.json:**
```json
{
  "templates": "../templates",
  "files": {
    "menu_context.h.j2": "../output/menu_context.h",
    "menu_context.c.j2": "../output/menu_context.c",
    "menu_type.h.j2": "../output/menu_type.h"
  }
}
```

### 3. Запуск генерации

В ```config/config.json``` указать путь к файлу конфигурации меню. Например:
```json
{
    "menu": "../menu/menu.json",
    "menu_schema": "menu_schema.json",
    "menu_config": "menu_data.json",
    "output_flattern": "../output/flatterned.json",
    "generation_files": "files.json"
}
```
Запускаем генератор:
```bash
python generator.py 
```

## 📝 Создание меню

### 🎯 Базовые свойства узла

```json
{
  "id": "unique_id",           // Уникальный идентификатор
  "title": "Display Name",     // Отображаемое имя
  "type": "ubyte",            // Тип данных
  "role": "simple"            // Роль элемента
}
```

### 📊 Типы данных (type)

| Тип | C-тип | Описание |
|-----|-------|----------|
| `byte` | `int8_t` | Знаковый байт |
| `ubyte` | `uint8_t` | Беззнаковый байт |
| `word` | `int16_t` | Знаковое слово |
| `uword` | `uint16_t` | Беззнаковое слово |
| `dword` | `int32_t` | Знаковое двойное слово |
| `udword` | `uint32_t` | Беззнаковое двойное слово |
| `string` | `char*` | Строка |
| `callback` | `void*` | Функция обратного вызова |

### 🎭 Роли элементов (role)

#### 1. **simple** - Простые числовые значения
```json
{
  "id": "brightness",
  "title": "Brightness", 
  "type": "ubyte",
  "role": "simple",
  "min": 0,
  "max": 100,
  "default": 50,
  "step": 5
}
```

#### 2. **factor** - Значения с множителями
```json
{
  "id": "delay",
  "title": "Delay",
  "type": "udword", 
  "role": "factor",
  "default": 10,
  "min": 10,
  "max": 10000,
  "factors": [1, 10, 100, 1000]
}
```

#### 3. **fixed** - Фиксированные наборы значений
```json
{
  "id": "mode",
  "title": "Mode",
  "type": "string",
  "role": "fixed",
  "values": ["Auto", "Manual", "Test"],
  "default_idx": 0
}
```

#### 4. **callback** - Пользовательские обработчики
```json
{
  "id": "version",
  "title": "Firmware version", 
  "type": "callback",
  "role": "callback"
}
```

### 🎮 Управление контролами (controls)

#### Доступные контролы:
- **`click`** - обработка клика энкодера
- **`position`** - обработка поворота энкодера

#### Примеры конфигурации:
```json
// Использовать только position контроль
{
  "controls": ["position"],
  "navigate": "cyclic"
}

// Использовать оба контроля (по умолчанию)
{
  "controls": ["click", "position"]
}

// Для factor роли всегда оба контроля
{
  "role": "factor"
  // автоматически используются click и position
}
```

### 🧭 Навигация (navigate)

#### Типы навигации:
- **`cyclic`** - циклическое переключение (закольцованное)
- **`limit`** - ограниченное (до первого/последнего элемента)

#### Примеры:
```json
// Циклическое меню
{
  "navigate": "cyclic",
  "items": [
    {"id": "item1", "title": "Item 1", "type": "string", "role": "fixed", "values": ["A", "B"]},
    {"id": "item2", "title": "Item 2", "type": "string", "role": "fixed", "values": ["X", "Y"]}
  ]
}

// Ограниченное меню  
{
  "navigate": "limit",
  "items": [
    // переход только между существующими элементами
  ]
}
```

### 📞 Callback-функции

#### Типы callback-ов:
- **`click_cb`** - обработка клика
- **`position_cb`** - обработка поворота энкодера  
- **`double_click_cb`** - двойной клик
- **`long_click_cb`** - долгий клик
- **`event_cb`** - обработка событий меню
- **`draw_value_cb`** - отрисовка значения

#### Пример пользовательского callback:
```json
{
  "id": "custom_item",
  "title": "Custom",
  "type": "ubyte", 
  "role": "simple",
  "click_cb": "my_custom_click_handler",
  "draw_value_cb": "my_custom_draw_function"
}
```

#### Автоматические функции:
Если callback не указан, генерируется автоматически по шаблону:
- `{type}_{role}_{control}_{navigate}_cb` - для обработки
- `menu_draw_{type}_{role}_value_cb` - для отрисовки

## 📊 Генерируемые файлы

Система генерирует следующие C-файлы:

- **`menu_context.h/c`** - контекст меню и основные структуры
- **`menu_type.h/c`** - типы данных и enum'ы  
- **`menu_data.h/c`** - конфигурация данных меню
- **`menu_tree.h/c`** - дерево меню со связями
- **`menu_value.h/c`** - функции работы со значениями
- **`menu_navigate.h/c`** - функции навигации
- **`menu_engine.h/c`** - движок меню
- **`menu_edit.h/c`** - функции редактирования значений

## 🔧 Расширение системы

### Добавление нового типа данных:

1. Добавить тип в `config/menu_data.json`
2. Обновить схему в `config/menu_schema.json`
3. Создать шаблоны отрисовки и редактирования

### Добавление новой роли:

1. Добавить роль в `config/menu_data.json`
2. Определить правила контролов в `role_rules`
3. Создать функции обработки в шаблонах

## 🐛 Отладка и диагностика

### Просмотр сгенерированных функций:

```bash
python menu_processor.py ./config/config.json
```

Команда покажет:
- Сводку по узлам меню
- Все сгенерированные callback-функции
- Информацию о типах и ролях
- Проверку обязательных функций

### Сохранение промежуточных данных:

```python
# В menu_processor.py
processor.save_flattern_json("./debug/flattened.json")
save_json_data(processor.functions, "./debug/functions.json")
```

## 📈 Статус проекта

- ✅ **Завершено**: Архитектура, валидация, преобразование дерева
- ✅ **Завершено**: Система callback-ов и автоматических функций  
- ✅ **Завершено**: Модульный рефакторинг (менеджеры)
- 🔄 **В процессе**: Генерация полного набора C-функций
- 🔄 **В процессе**: Интеграция с реальными embedded-проектами

## 🎯 Пример полного меню

```json
{
  "config": {
    "default_navigate": "cyclic",
    "default_control": "position",
    "default_branch_navigate": "limit",
    "root_navigate": "limit"
  },
  "menu": [
    {
      "id": "settings",
      "title": "Settings",
      "navigate": "cyclic",
      "items": [
        {
          "id": "brightness",
          "title": "Brightness",
          "type": "ubyte",
          "role": "simple",
          "min": 0,
          "max": 100,
          "default": 50,
          "step": 5
        },
        {
          "id": "contrast",
          "title": "Contrast", 
          "type": "ubyte",
          "role": "factor",
          "default": 10,
          "min": 10,
          "max": 10000,
          "factors": [1, 10, 100, 1000]
        },
        {
          "id": "display_mode",
          "title": "Display Mode",
          "type": "string", 
          "role": "fixed",
          "values": ["Normal", "Inverted", "Test"],
          "default_idx": 0
        }
      ]
    },
    {
      "id": "info",
      "title": "Information",
      "items": [
        {
          "id": "version",
          "title": "Firmware Version",
          "type": "callback",
          "role": "callback"
        }
      ]
    }
  ]
}
```

## 🌍 Интернационализация (i18n / gettext)

Все пользовательские сообщения пакета переведены на систему **gettext (Babel)**.
Основной (исходный) язык сообщений — **английский**.

### Выбор языка

Язык выбирается через переменную окружения `MENU_PROCESSOR_LANG`:

```bash
# Английский (по умолчанию, исходные сообщения)
python -X utf8 generator.py

# Русский (используется каталог locale/ru)
set MENU_PROCESSOR_LANG=ru
python -X utf8 generator.py
```

Если каталог переводов отсутствует, язык не найден или переменная не задана —
используются исходные английские сообщения (fallback).

### Структура каталогов

```
locale/
├── messages.pot                      # Шаблон извлечённых сообщений
└── ru/
    └── LC_MESSAGES/
        ├── messages.po               # Переводы (редактируется вручную)
        └── messages.mo               # Скомпилированный каталог (используется в рантайме)
```

### Рабочий процесс перевода

После изменения сообщений в коде (`_("...")` или `ngettext`) обновите каталоги:

```bash
# 1. Извлечение сообщений в messages.pot
python -m babel.messages.frontend extract -F babel.cfg -k _ -k ngettext:1,2 -o locale/messages.pot .

# 2. Обновление существующего каталога (например, ru)
python -m babel.messages.frontend update -i locale/messages.pot -d locale -l ru

# 3. Компиляция каталогов в .mo
python -m babel.messages.frontend compile -d locale
```

Для нового языка создайте каталог с нуля:

```bash
python -m babel.messages.frontend init -i locale/messages.pot -d locale -l <код_языка>
```

> **Примечание:** в исходном коде внутри `_()` используйте обычные строки с
> `{placeholders}` и `.format(...)`, а не f-строки — Babel корректно извлекает
> только обычные строковые литералы.

