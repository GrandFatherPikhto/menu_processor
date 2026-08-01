#ifndef MENU_CONFIG_H
#define MENU_CONFIG_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#include "menu_type.h"

// Макросы для безопасного вызова колбэков
#define MENU_SAFE_CALL_CLICK(ctx, id) \
    ((ctx) && (id) < MENU_ID_COUNT && (ctx)->configs[(id)].click_cb ? \
     (ctx)->configs[(id)].click_cb((ctx), (id)) : (void)0)

#define MENU_SAFE_CALL_POSITION(ctx, id, delta) \
    ((ctx) && (id) < MENU_ID_COUNT && (ctx)->configs[(id)].position_cb ? \
     (ctx)->configs[(id)].position_cb((ctx), (id), (delta)) : (void)0)

#define MENU_SAFE_CALL_EVENT(ctx, id, event) \
    ((ctx) && (id) < MENU_ID_COUNT && (ctx)->configs[(id)].event_cb ? \
     (ctx)->configs[(id)].event_cb((ctx), (id), (event)) : false)

// Базовые структуры (только forward declarations)
typedef struct menu_context menu_context_t;
typedef struct menu_node menu_node_t;
typedef struct menu_node_config menu_node_config_t;
typedef struct menu_callback menu_callback_t;

typedef struct s_stub_config_t {} stub_config_t;

// string_fixed
typedef struct s_string_fixed_t {
    uint8_t count;
    uint8_t default_idx;
    const const char* *values; 
} string_fixed_config_t;

// udword_factor
typedef struct s_udword_factor_t {
    uint32_t max;
    uint32_t min;
    uint32_t step;
    uint32_t default_value;
    uint8_t count;
    uint8_t default_idx;
    const uint32_t *factors;

} udword_factor_config_t;

// ubyte_simple
typedef struct s_ubyte_simple_t {
    uint8_t default_value;
    uint8_t step;
    uint8_t min;
    uint8_t max;

} ubyte_simple_config_t;


// Объявления callback-функций
typedef void (*menu_click_cb_t)(menu_context_t *ctx, menu_id_t id);
typedef void (*menu_position_cb_t)(menu_context_t *ctx, menu_id_t id, int8_t delta);
typedef void (*menu_double_click_cb_t)(menu_context_t *ctx, menu_id_t id);
typedef void (*menu_long_click_cb_t)(menu_context_t *ctx, menu_id_t id);
typedef void (*menu_draw_value_cb_t)(menu_context_t *ctx, menu_id_t id);
typedef void (*menu_handle_event_cb_t)(menu_context_t *ctx, menu_id_t id, menu_event_t event);

typedef struct menu_node_config {
    menu_id_t id;
    menu_category_t category;
    menu_click_cb_t click_cb;
    menu_position_cb_t position_cb;
    menu_double_click_cb_t double_click_cb;
    menu_long_click_cb_t long_click_cb;
    menu_draw_value_cb_t draw_value_cb;
    menu_handle_event_cb_t event_cb;
    union {        
        stub_config_t stub_config;
        string_fixed_config_t string_fixed;
        udword_factor_config_t udword_factor;
        ubyte_simple_config_t ubyte_simple;
    } data;
} menu_node_config_t;

#endif /* MENU_CONFIG_H */