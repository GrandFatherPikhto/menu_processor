#ifndef MENU_H
#define MENU_H

#include <stdint.h>
#include <stdbool.h>

typedef enum {
    MENU_STATE_NAVIGATION = 0,
    MENU_STATE_EDIT = 1
} menu_state_t;

typedef enum {
    MENU_EVENT_NONE = 0,
    MENU_EVENT_CHANGE = 1,
    MENU_EVENT_CHANGE_VALUE = 2,
    MENU_EVENT_FOCUSED = 3,
    MENU_EVENT_UNFOCUSED = 4,
    MENU_EVENT_START_EDIT = 5,
    MENU_EVENT_STOP_EDIT = 6,
    MENU_EVENT_CHANGE_VALUE = 7
} menu_event_t;

typedef struct menu_context {
    menu_id_t current;
    menu_id_t previous;
    menu_state_t state;
    menu_event_t event;
    bool dirty;
    menu_value_t *values;
    const menu_config_t *config;
    const menu_node_t *tree;
} menu_context_t;

void menu_update();
menu_id_t menu_get_current(void);
menu_id_t menu_get_prev(void);
void menu_get_sibling(menu_id_t id, int8_t delta);
void menu_go_to(menu_id_t id);

#endif // MENU_H