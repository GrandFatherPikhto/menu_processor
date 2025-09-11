# Генератор меню
## Общие представления
1. Шаблоны template/menu_renc.c.j2 template/menu_renc.h.j2 -- внешние. Не в файле python!
2. Создаётся два файла (по умолчанию output/menu_renc.c, output/menu_renc.h, renc -- rotary encoder)
3. При помощи config/menu_config.json программой menu_generator.py с использованием библиотеки jinja2. 
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
1. Структура сгенерированного меню статическая. 
    Т.е., есть некая структура которая описывает содержимое меню и хранится в статическом массиве, где разные типы меню представлены при помощи union (накладываются друг на друга)
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
