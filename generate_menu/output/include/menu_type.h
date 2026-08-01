#ifndef MENU_TYPE_H
#define MENU_TYPE_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define LCD_STRING_LEN 0x20
#define LCD_NUM_STRINGS 2

typedef enum {
    MENU_TREE_TYPE_NONE = 0,
    MENU_TREE_TYPE_BRANCH = 1,
    MENU_TREE_TYPE_LEAF = 2,
    MENU_TREE_TYPE_COUNT = 3
} menu_tree_type_t;

typedef enum {
    MENU_CATEGORY_NONE = 0,
    MENU_CATEGORY_STRING_FIXED = 1,
    MENU_CATEGORY_CALLBACK_CALLBACK = 2,
    MENU_CATEGORY_UDWORD_FACTOR = 3,
    MENU_CATEGORY_UBYTE_SIMPLE = 4,
    MENU_CATEGORY_COUNT = 5
} menu_category_t;

typedef enum {
    MENU_ID_ROOT = 0,
    
    MENU_ID_START = 1,
    
    MENU_ID_REGIMES = 2,
    
    MENU_ID_VERSION = 3,
    
    MENU_ID_SETTINGS = 4,
    
    MENU_ID_PWM_FREQUENCY = 5,
    
    MENU_ID_HI_CHANNEL = 6,
    
    MENU_ID_HI_ON = 7,
    
    MENU_ID_HI_DELAY = 8,
    
    MENU_ID_HI_DURATION = 9,
    
    MENU_ID_HI_PWM_ON = 10,
    
    MENU_ID_HI_DUTY = 11,
    
    MENU_ID_LO_CHANNEL = 12,
    
    MENU_ID_LO_ON = 13,
    
    MENU_ID_LO_DELAY = 14,
    
    MENU_ID_LO_DURATION = 15,
    
    MENU_ID_LO_PWM_ON = 16,
    
    MENU_ID_LO_DUTY = 17,
    
    MENU_ID_COUNT = 18
} menu_id_t;

typedef enum {
    MENU_EVENT_NONE = 0,
    MENU_EVENT_CHANGE_VALUE = 1,
    MENU_EVENT_FOCUSED = 2,
    MENU_EVENT_UNFOCUSED = 3,
    MENU_EVENT_START_EDIT = 4,
    MENU_EVENT_STOP_EDIT = 5,
    MENU_EVENT_COUNT = 6
} menu_event_t;

typedef enum {
    MENU_STATE_NONE = 0,
    MENU_STATE_NAVIGATION = 1,
    MENU_STATE_EDIT = 2,
    MENU_STATE_COUNT = 3
} menu_state_t;

// Базовые структуры (только forward declarations)
typedef struct menu_context menu_context_t;
typedef struct menu_node menu_node_t;
typedef struct menu_node_config menu_node_config_t;
typedef struct menu_node_value menu_node_value_t;
typedef struct menu_node_name menu_node_name_t;

#endif /* MENU_TYPE_H */