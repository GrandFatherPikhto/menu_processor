# Техническое задание: Генератор C-меню для LCD1602

## 1. Общее описание

Разработан Python-пакет для автоматической генерации C-кода системы меню на основе JSON-конфигурации. Система предназначена для использования в embedded-проектах с LCD дисплеями 1602 и энкодерами.

## 2. Архитектура системы

### 2.1. Основные компоненты

1. **MenuConfig** - загрузка и управление конфигурационными файлами
2. **MenuData** - централизованное хранение правил для типов данных, ролей и callback-функций
3. **FlatNode** - плоское представление узла меню со связями (родитель, дети, siblings)
4. **CallbackManager** - специализированный менеджер для обработки callback-функций
5. **MenuFlattener** - преобразование дерева в плоский список с циклическими связями
6. **MenuValidator** - валидация JSON-конфигурации
7. **MenuProcessor** - основной координатор, предоставляющий данные для генератора
8. **MenuGenerator** - генерация C-кода через Jinja-шаблоны

### 2.2. Входные данные

- `config.json` - основной конфиг с путями к другим файлам
- `menu_schema.json` - JSON Schema для валидации
- `menu.json` - дерево меню с элементами
- `menu_data.json` - правила для типов, ролей, callback-функций

### 2.3. Выходные данные

- `menu_struct.h` - структуры данных и enum'ы
- `menu_config.h/c` - конфигурация меню и callback-функций
- `menu_edit.c` - функции редактирования значений
- `menu_draw.c` - функции отрисовки значений
- `menu_tree.c` - дерево меню со связями

## 3. JSON-конфигурация

### 3.1. Схема menu.json

```json
{
  "id": "unique_id",
  "title": "Display Name",
  "type": "ubyte|string|callback|...",
  "role": "simple|factor|fixed|callback",
  "controls": ["click", "position"], // опционально
  "navigate": "cyclic|limit", // опционально
  "click_cb": "custom_function", // опционально
  "position_cb": "custom_function", // опционально
  "double_click_cb": "custom_function", // опционально
  "long_click_cb": "custom_function", // опционально
  "event_cb": "custom_function", // опционально
  "draw_value_cb": "custom_function", // опционально
  // ... другие свойства в зависимости от типа
}
```

### 3.2. Система ролей (role)

- **simple** - простые числовые типы
- **factor** - значения с множителями (обязательно оба контроля)
- **fixed** - фиксированные наборы значений
- **callback** - пользовательские обработчики

### 3.3. Управление контролями (controls)

- Если указан `controls` в JSON - используются только указанные
- Если не указан - используются оба контроля (кроме callback)
- Для `factor` роли всегда используются оба контроля

### 3.4. Callback-функции

- **6 типов callback'ов**: click, position, double_click, long_click, event, draw_value
- Приоритет пользовательских функций над автоматическими
- Автогенерация имен для draw_value_cb по шаблону: `menu_draw_{category}_value_cb`

### 3.5. Навигация

- **cyclic** - циклическое переключение между элементами
- **limit** - ограниченное (до первого/последнего элемента)
- Для `click` всегда используется `cyclic` навигация

## 4. Текущее состояние проекта

### 4.1. ✅ Завершено

1. Полная загрузка и валидация JSON-конфигурации
2. Преобразование дерева в плоскую структуру с связями
3. Система ролей и типов данных
4. Callback Manager с поддержкой пользовательских и автоматических функций
5. Генерация имен функций по категориям (type + role)
6. Подготовка данных для шаблонов (MenuProcessor)
7. Создание основных Jinja-шаблонов для генерации C-кода

### 4.2. 🔄 Требует доработки

1. **Генерация функций редактирования** для всех категорий
2. **Генерация функций отрисовки** для всех категорий
3. **Интеграция с существующей C-архитектурой**
4. **Тестирование на реальных проектах**

## 5. Генерация C-кода

### 5.1. Основные структуры данных

```c
typedef struct {
    menu_id_t id;
    menu_category_t category;
    menu_click_cb_t click_cb;
    menu_position_cb_t position_cb;
    menu_double_click_cb_t double_click_cb;
    menu_long_click_cb_t long_click_cb;
    menu_display_value_cb_t display_value_cb;
    menu_handle_event_cb_t handle_event_cb;
    union {
        ubyte_simple_config_t ubyte_simple;
        udword_factor_config_t udword_factor;
        // ... другие типы данных
    } data;
} menu_node_config_t;
```

### 5.2. Пример генерируемого кода

```c
[MENU_ID_HI_DURATION] = {
    .id = MENU_ID_HI_DURATION,
    .category = MENU_CATEGORY_UDWORD_FACTOR,
    .click_cb = udword_factor_click_cyclic_factor_cb,
    .position_cb = udword_factor_position_limit_cb,
    .double_click_cb = NULL,
    .long_click_cb = NULL,
    .display_value_cb = menu_draw_udword_factor_value_cb,
    .handle_event_cb = NULL,
    .data.udword_factor = {
        .default_value = 10,
        .min = 10,
        .max = 10000,
        .step = 1,
        .default_idx = 2,
        .count = 4,
        .factors = s_factors_hi_duration
    }
},
```

## 6. Дальнейшие шаги

### 6.1. Приоритетные задачи

1. **Доработка шаблонов** для полной генерации C-кода
2. **Создание функций редактирования** для всех комбинаций type + role + control + navigate
3. **Создание функций отрисовки** для всех категорий
4. **Тестирование генерации** на различных конфигурациях

### 6.2. Дополнительные возможности

1. **Поддержка новых типов данных** (float, double, etc.)
2. **Расширение системы callback'ов** (добавление новых типов событий)
3. **Оптимизация для различных LCD дисплеев**
4. **Поддержка многоязычности**

## 7. Использование

### 7.1. Установка и запуск

```bash
python generator.py ./config/config.json
```

### 7.2. Структура проекта

```
project/
├── config/
│   ├── config.json
│   ├── menu_schema.json
│   ├── menu.json
│   └── menu_data.json
├── templates/
│   ├── config.h.jinja
│   ├── menu_config.c.jinja
│   └── ...
├── output/
│   ├── menu_config.h
│   ├── menu_config.c
│   └── ...
└── src/
    ├── menu_config.py
    ├── menu_data.py
    ├── flat_node.py
    ├── callback_manager.py
    ├── menu_flattener.py
    ├── menu_validator.py
    ├── menu_processor.py
    └── menu_generator.py
```

## 8. Заключение

Система представляет собой мощный инструмент для автоматической генерации кода меню для embedded-устройств. Она значительно ускоряет разработку и обеспечивает consistency кода. Архитектура системы позволяет легко расширять функциональность и добавлять новые типы данных и callback-функции.

Проект готов к использованию в production-среде после завершения текущих доработок и тестирования.