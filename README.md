# Генератор меню
## Общие представления
1. Шаблоны template/menu_renc.c.j2 template/menu_renc.h.j2 -- внешние. Не в файле python!
2. Создаётся два файла (по умолчанию output/menu_renc.c, output/menu_renc.h, renc -- rotary encoder)
3. При помощи config/menu_config.json программой menu_generator.py с использованием библиотеки [JINJA2](https://jinja.palletsprojects.com/en/stable/). 
   Объекты меню описываются, как вложенные. Т.е., мы не указываем вручную parent, child, next, prev, e.t.c.
4. В настройках генератора можно указать путь и имя *.h файла меню и путь и имя *.c файла меню,
   но есть пути и имена по умолчанию (имена не из командной строки!). 
5. Лучше указывать все настройки проекта расположить в menu_config.json
6. Генератор на python сделан в виде класса или классов
7. В скрипт встроена проверка на синтаксические ошибки с указанием номера строки, где ошибка и
    проверка связности элементов меню (если какие-то меню ни с кем не связаны сообщаем об этом)
    если цепочка связности нарушена, сообщаем об этом

## Событийная модель
Пока приспособлен только для генерации меню для rotary encoder
Всего 4 cобытия:
1. PUSH_BUTTON -- Если текущее меню -- submenu, переход на уровень ниже (first_child) Если текущее меню EDITABLE, переход в состояние MENU_STATE_EDIT
2. LONG_PUSH_BUTTON -- выход на один уровень вверх если меню submenu, переход в состояние MENU_STATE_NAVIGATION
3. DOUBLE_CLICK_BUTTON -- сброс текущего меню (если оно редактируемое) к состоянию по умолчанию, если текущее меню -- submenu -- сброс на первый child от root
4. CHANGE_POSITION -- если меню в состоянии редактирования MENU_STATE_EDIT, изменяет управляемое значение. Если меню в состоянии MENU_STATE_NAVIGATION, переход вперёд/назад (sibling)
5. Все изменения CHANGE_POSITION обрабатываются функцией void handle_change_position(int8_t delta) в зависимости от типа меню и его состояния (MENU_STATE_NAVIGATION/MENU_STATE_EDIT)
6. Все вызовы PUSH_BUTTON обрабатываются void handle_push_button(void)
7. Все вызовы LONG_PUSH_BUTTON обрабатываются void handle_long_push_button(void)
8. Все вызовы DOUBLE_CLICK_PUSH_BUTTON обрабатываются void handle_long_push_button(void)

## Структура сгенерированного проекта
1. Все данные, относящиеся к навигации, factor, min, max мы будем хранить в отдельном массиве static const menu_data_t s_menu_data
2. Все данные которые изменяются в процессе работы меню хранятся в структуре
static menu_values_t s_menu_values.
Сюда попадают значения factor_idx, value, относящееся к данному меню.
Данные можно получать виду void * по MENU_ID
2. Все изменяемые данные, такие, как factor_idx, value, e.t.c. -- в другом массиве static
2. Формируется таблица enum с ID всех редактируемых элементов меню, по которым можно назначать callback, получать указатель на хранимые данные (void *ptr)
3. Все числовые элементы имеют min, max, default
4. Все элементы с _factor хранят таблицу множителей и тоже min, max, default, default_factor_idx и factor_idx (индекс текущего множителя)
5. Все редактируемые элементы (action_...) имеют возможность назначения callback на изменение значения
6. Может быть элемент action_callback. Без изменения по умолчинию. В callback передаётся ACTION_CHANGE со знаком изменения
7. В сгенерированном файле должна формироваться структура menu_data_t, в которую складываются все данные, которые изменяются и 
    7.1. Создаётся статическая переменная `static menu_data_t s_data = {...};
    7.2. сделать возврат `menu_data_t *menu_get_data(void)`
    7.3. для типов action_int_factor еще хранится factor_id (номер множителя из таблицы множителей)
    7.4. Каждый элемент привязан к элементу меню void *data_ptr, чтобы можно было привязать ко внешнему значению
    7.5. Соответственно, для меню со значениями (action...) есть get_data_ptr(menu_id_t id);

## Всего два состояния:
1. MENU_STATE_NAVIGATION -- переход между соседними элементами меню по CHANGE_POSITION и переход вверх, если есть куда (в root не переходим) по LONG_PUSH_BUTTON, и переходим к first_child, если он есть по PUSH_BUTTON
2. MENU_STATE_EDIT (может быть только у редактируемых типов меню -- action_bool, action_int, action_int_factor)

## Стандартная навигация (submenu)
1. PUSH_BUTTON -- переход к first_child, если он есть. Если нет, ничего не происходит
2. LONG_PUSH_BUTTON -- переход к родителю, если есть куда (в root не переходим, это невидимая нода!)
3. DOUBLE_CLICK_BUTTON -- переход к first_child root
4. CHANGE_POSITION -- перемещаемся в горизонтальном направлении next/prev в зависимости от знака delta = current_position - next_position. Перемещения в горизонтальном меню закольцованы. Если достигнут next == null, переходим к first

## Типы меню:
1. root (возможно, оно должно быть скрыто)
2. submenu (просто отображается в верхней строке). Стандартная навигация. 
3. action_bool (по нажатию PUSH_BUTTON ON/OFF переключаются)
4. action_int (по нажати PUSH_BUTTON ничего не происходит), по CHANGE_POSITION значение изменяется на +-step
5. action_int_factor (по нажатию PUSH_BUTTON выбирается следующий factor из таблицы в колцевом режиме), по CHANGE_POSITION значение изменяется на +-factors[factor_idx];
6. action_float (по нажатию PUSH_BUTTON ничего не происходит), по CHANGE_POSITION значение меняется на +-step
7. action_int_step (по нажатию PUSH_BUTTON ничего не происходит), по CHANGE_POSITION выбирается +-step_idx из таблицы values
8. action_float_step (по нажатию PUSH_BUTTON ничего не происходит), по CHANGE_POSITION выбирается +-step_idx из таблицы values
9. action_callback (по нажатию PUSH_BUTTON ничего не происходит), по CHANGE_POSITION вызывается callback со знаком изменения

## Типы возвращаемых функций `action_callback`
1. ```void change_cb(int8_t delta)``` -- возвращает изменение позиции rotary encoder'а
2. ```void click_cb(void)``` -- отрабатывает коллбэк одиночного нажатия кнопки rotary encoder'а
3. ```void enter_cb(void)``` -- событие входа в меню
4. ```void exit_cb(void)``` -- событие выхода из меню
5. ```const char *display_cb(void)``` -- ОБЯЗАТЕЛЬНЫЙ коллбэк. Возвращает строку, которая будет отображаться во второй строке LCD1602

## Структура конфигурационного файла
### Раздел конфигурации
```javascript
  "config" : {
    "templates" : {
      "menu_source" : "templates/menu.c.j2", // Путь к JINJA2 шаблону файла menu.c. ОБЯЗАТЕЛЬНОЕ поле
      "menu_header" : "templates/menu.h.j2", // Путь к JINJA2 шаблона файла menu.h. ОБЯЗАТЕЛЬНОЕ поле
      "callback_header": "templates/callback.h.j2" // Путь к JINJA2 шаблона файла menu.h. необязательное поле. Создаётся, только если указан этот путь и путь к генерируемому файлу
    },
    "output" : {
      "menu_source" : "../src/rotenc_menu.c", // Путь к генерируемому файлу исходного кода меню. ОБЯЗАТЕЛЬНОЕ поле
      "menu_header" : "../src/rotenc_menu.h", // Путь к генерируемому файлу заголовка меню. ОБЯЗАТЕЛЬНОЕ поле
      "callback_header": "../src/rotenc_callback.h" // Путь к генерируемому файлу заголовков функций обратного вызова. Создаётся если указан путь к шаблону и callback_header. Необязательное поле
    },
    "includes" : [ // #includes, которые будут включены в сгенерированный файл исходного кода меню. Необязательное поле
      "lcd1602.h", 
      "rotenc_callback.h"
    ]
```

### Меню:
```javascript
    "menu" : [

    ] // обязательное поле конфигурационного файла, содержащего пункты меню
```

Для всех вложенных элементов меню ОБЯЗАТЕЛЬНЫ следующие поля:
1. "id" -- без пробелов указывается уникальный идентификатор пункта меню. Будет переведён в верхний регистр и добавлен в ```c enum``` c ID пунктов меню
2. "title" -- Заголовок меню. Не более 14 символов
3. "type" -- может принимать значения:
    a. "action_menu" -- просто пункт меню. Например, "options"
    b. "action_bool" -- пункт меню принимающий значения "On/Off"
    c. "action_int" -- целое число, которое можно изменять от "min" до "max" на "step" при помощи вращающегося переключателя (rotary encoder)
    d. "action_int_factor" -- целое число, которое можно изменять с каждым шагом энкодера от "min" до "max" на текущий множитель (обязательна таблица множителей) умноженный на дельту энкодера (смещение) при помощи вращающегося переключателя (rotary encoder)
    e. "action_float" -- число с плавающей запятой, которое можно изменять на количество шагов энкодера умноженное на step от min до max
    f. "action_float_factor"  -- число с плавающей запятой, которое можно изменять на количество шагов энкодера умноженное на текущий множитель из таблицы множителей от min до max
    g. "action_callback" -- тип меню с функциями обратного вызова. ОБЯЗАТЕЛЬНО задать "display_cb", которая возвращает строку представленную как значение меню (2я строка LCD1602)
4. "children" -- массив подменю. Типы могут быть теми же.

#### `action_menu`
1. "id" -- обязательное поле. Латинские буквы и подчёркивания. Например, "id_main"
2. "type" : "action_menu" -- обязательное поле. В данном случае, "action_menu"
3. "title" : "Main" -- обязательное поле. Заголовок, который отображается в верхней строке меню LCD1602

### `action_int`
Управляет целым числом типа `int32_t`. 
1. "id" -- обязательное поле. Латинские буквы и подчёркивания. Например, "id_speed"
2. "type" : "action_int" -- обязательное поле. В данном случае, "action_int"
3. "title" : "Engine speed" -- обязательное поле. Заголовок, который отображается в верхней строке меню LCD1602
4. "default" : 3000 -- обязательное поле. Значение по умолчанию для этого поля
5. "step" : 100 -- шаг изменения значения value вращающимся переключателем
6. "min" : 300 -- минимальное значение value
7. "max" : 6000 -- максимальное значение value

### `action_int_factor`
Управляет целым числом типа `int32_t`. Есть таблица множителей
1. "id" -- обязательное поле. Латинские буквы и подчёркивания. Например, "id_speed"
2. "type" : "action_int" -- обязательное поле. В данном случае, "action_int"
3. "title" : "Engine speed" -- обязательное поле. Заголовок, который отображается в верхней строке меню LCD1602
4. "default" : 3000 -- обязательное поле. Значение по умолчанию для этого поля
5. "min" : 300 -- минимальное значение value
6. "max" : 6000 -- максимальное значение value
7. "factors" : [1, 10, 100, 1000] -- набор множителей на которые умножается количество шагов вращающегося переключателя. Если delta отрицательная, то полученное значение вычитается из текущего, если delta положительная, прибавляется
8. "default_factor_idx" -- индекс множителя по умолчанию

### `action_float_factor`
Управляет числом с плавающей запятой типа `float`. Есть таблица множителей
1. "id" -- обязательное поле. Латинские буквы и подчёркивания. Например, "id_speed"
2. "type" : "action_int" -- обязательное поле. В данном случае, "action_int"
3. "title" : "Engine speed" -- обязательное поле. Заголовок, который отображается в верхней строке меню LCD1602
4. "default" : 3000 -- обязательное поле. Значение по умолчанию для этого поля
5. "min" : 300 -- минимальное значение value
6. "max" : 6000 -- максимальное значение value
7. "factors" : [1, 10, 100, 1000] -- набор множителей на которые умножается количество шагов вращающегося переключателя. Если delta отрицательная, то полученное значение вычитается из текущего, если delta положительная, прибавляется
8. "default_factor_idx" -- индекс множителя по умолчанию

### `action_callback`
Обработка значений и создание строки вывода возлагается на разработчика. Содержит набор указателей на функции обратного вызова (коллбеки)
Управляет целым числом типа `int32_t`. Есть таблица множителей
Если в разделе `config` в подразделах `templates` и `output` указаны поля `callback_header`, будет автоматически создан заголовочный файл с функциями обратного вызова 

1. "id" -- обязательное поле. Латинские буквы и подчёркивания. Например, "id_speed".
2. "type" : "action_int" -- обязательное поле. В данном случае, "action_int"
3. "title" : "Engine speed" -- обязательное поле. Заголовок, который отображается в верхней строке меню LCD1602
4. "change_cb" : "callback_engine_speed_change". Прототип этой функции `void (*change_cb)(int8_t delta);`
5. "click_cb" : "callback_engine_click". Прототип такой функции `void (*click_cb)(void);`
6. "enter_cb" : "callback_engine_enter". Прототип этой функции `void (*enter_cb)(void);`
7. "exit_cb" : "callback_engine_exit". Прототип этой функции `void (*exit_cb)(void);`

## Добавление нового типа в процессор
1. Файл [menu_validator.py](menu_validator.py)
  a. Добавить в `VALID_TYPES` новый тип `action_new_type`
```python
    VALID_TYPES = {'action_menu', 'action_int', 'action_int_factor', 
                  'action_callback', 'action_bool', 
                  'action_fixed_ints', 'action_fixed_floats', 'action_fixed_strings', 
                  'action_new_type'}
```  
  b. Добавить в `action_new_type` в `type_validators`:
```python
    def _validate_type_specific_fields(self, node: Dict, path: List[str]) -> None:
        """Валидация полей, специфичных для типа"""
        if 'type' not in node:
            return
        
        type_validators = {
            'action_int': self._validate_action_int,
            'action_int_factor': self._validate_action_int_factor,
            'action_callback': self._validate_action_callback,
            'action_bool': self._validate_action_bool,
            'action_fixed_ints': self._validate_action_fixed_ints,
            'action_fixed_floats': self._validate_action_fixed_floats,
            'action_fixed_strings': self._validate_action_fixed_strings,
            'action_new_type': self._validate_action_new_type
        }
```
  c. Создать метод `_validate_action_new_type` и в нём обработку необходимых полей
```python  
    def _validate_action_new_type(self, node: Dict, path: List[str]) -> None:
        """Валидация action_callback"""
        required_fields = ["field01", "field02"]
        for field in required_fields:
            if field not in node:
                self.errors.append(MenuError(
                    f"Для action_callback обязательно поле '{field}'",
                    path
                ))
```
2. В файле [menu_flattener.py](menu_flattener.py)
  a. В метод `_add_type_specific_fields` дописываем лямбду обработки нужных полей
     Если поле необязательное, как `field03` в примере, используем оператор "распаковки словаря"
```python
    def _add_type_specific_fields(self, item: Dict, node: Dict) -> None:
        """Добавление полей, специфичных для типа"""
        type_processors = {
            'action_int': lambda: item.update({
                'min': node['min'],
                'max': node['max'],
                'default': node['default'],
                'step': node.get('step', 1)
            }),
            'action_int_factor': lambda: item.update({
                'min': node['min'],
                'max': node['max'],
                'default': node['default'],
                'factors': node['factors'],
                'factors_count': (len(node.get('factors', []))),
                'default_factor_idx': node['default_factor_idx']
            }),
            'action_float': lambda: item.update({
                'min': node['min'],
                'max': node['max'],
                'default': node['default'],
                'step': node.get('step', 1)
            }),
            'action_float_factor': lambda: item.update({
                'min': node['min'],
                'max': node['max'],
                'default': node['default'],
                'factors': node['factors'],
                'factors_count': (len(node.get('factors', []))),
                'default_factor_idx': node['default_factor_idx']
            }),
            'action_bool': lambda: item.update({
                'default': node['default']
            }),
            'action_new_type': lambda: item.update({
                'filed01': node[field01].upper()
                **({} if node.get('field03') is None else {'field03': len(node['filed03']) })
            })
```  
3. В файл [menu_generator.py](menu_generator.py) добавить нужный тип:
```python
class MenuType(Enum):
    ROOT = "root"
    SUBMENU = "action_menu" 
    ACTION_BOOL = "action_bool"
    ACTION_INT = "action_int"
    ACTION_INT_FACTOR = "action_int_factor"
    ACTION_CALLBACK = "action_callback"
    ACTION_FLOAT = "action_float"
    ACTION_FLOAT_FACTOR = "action_float_factor"
    ACTION_FIXED_INTS = "action_fixed_ints"
    ACTION_FIXED_FLOATS = "action_fixed_floats"
    ACTION_FIXED_STRINGS = "action_fixed_strings"
    ACTION_NEW_TYPE = "action_new_type"
```
и не забыть добавить в типы меню:
```python
            'menu_types': {
                'ROOT': 'root',
                'ACTION_MENU': 'action_menu',
                'ACTION_BOOL': 'action_bool',
                'ACTION_INT': 'action_int',
                'ACTION_INT_FACTOR': 'action_int_factor',
                'ACTION_FLOAT': 'action_float',
                'ACTION_FLOAT_FACTOR': 'action_float_factor',
                'ACTION_FIXED_INTS': 'action_fixed_ints',
                'ACTION_FIXED_FLOATS': 'action_fixed_floats',
                'ACTION_FIXED_STRINGS': 'action_fixed_strings',
                'ACTION_CALLBACK': 'action_callback',
                'ACTION_NEW_TYPE': 'action_new_type
            },
```
4. Осталось внести добавления в генерацию из шаблонов
  a. В `menu.c.j2`
```jinja2  
  static const menu_item_t s_menu_config[MENU_ID_COUNT] = {
    ...
  {% elif item.type == 'action_fixed_ints '%}
    .action_new_type = {
      .field01 = {{ item.field01 }},
      ...
    }
  {% endif %}