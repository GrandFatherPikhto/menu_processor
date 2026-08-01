#include "menu_data_tree.h"
#include "menu_tree.h"

static const menu_node_t s_menu_tree[] = {
    [MENU_ID_ROOT] = {
        .id = MENU_ID_ROOT,
        .title = "root",
        .parent = MENU_ID_COUNT,
        .child = MENU_ID_START,
        .prev = MENU_ID_COUNT,
        .next = MENU_ID_COUNT,
        .type = MENU_TREE_TYPE_BRANCH
    },
    [MENU_ID_START] = {
        .id = MENU_ID_START,
        .title = "Start",
        .parent = MENU_ID_ROOT,
        .child = MENU_ID_COUNT,
        .prev = MENU_ID_SETTINGS,
        .next = MENU_ID_REGIMES,
        .type = MENU_TREE_TYPE_LEAF
    },
    [MENU_ID_REGIMES] = {
        .id = MENU_ID_REGIMES,
        .title = "Regimes",
        .parent = MENU_ID_ROOT,
        .child = MENU_ID_COUNT,
        .prev = MENU_ID_START,
        .next = MENU_ID_VERSION,
        .type = MENU_TREE_TYPE_LEAF
    },
    [MENU_ID_VERSION] = {
        .id = MENU_ID_VERSION,
        .title = "Firmware version",
        .parent = MENU_ID_ROOT,
        .child = MENU_ID_COUNT,
        .prev = MENU_ID_REGIMES,
        .next = MENU_ID_SETTINGS,
        .type = MENU_TREE_TYPE_LEAF
    },
    [MENU_ID_SETTINGS] = {
        .id = MENU_ID_SETTINGS,
        .title = "Settings",
        .parent = MENU_ID_ROOT,
        .child = MENU_ID_PWM_FREQUENCY,
        .prev = MENU_ID_VERSION,
        .next = MENU_ID_START,
        .type = MENU_TREE_TYPE_BRANCH
    },
    [MENU_ID_PWM_FREQUENCY] = {
        .id = MENU_ID_PWM_FREQUENCY,
        .title = "PWM Frequency",
        .parent = MENU_ID_SETTINGS,
        .child = MENU_ID_COUNT,
        .prev = MENU_ID_COUNT,
        .next = MENU_ID_HI_CHANNEL,
        .type = MENU_TREE_TYPE_LEAF
    },
    [MENU_ID_HI_CHANNEL] = {
        .id = MENU_ID_HI_CHANNEL,
        .title = "Hi Channel",
        .parent = MENU_ID_SETTINGS,
        .child = MENU_ID_HI_ON,
        .prev = MENU_ID_PWM_FREQUENCY,
        .next = MENU_ID_LO_CHANNEL,
        .type = MENU_TREE_TYPE_BRANCH
    },
    [MENU_ID_HI_ON] = {
        .id = MENU_ID_HI_ON,
        .title = "Hi On/Off",
        .parent = MENU_ID_HI_CHANNEL,
        .child = MENU_ID_COUNT,
        .prev = MENU_ID_HI_DUTY,
        .next = MENU_ID_HI_DELAY,
        .type = MENU_TREE_TYPE_LEAF
    },
    [MENU_ID_HI_DELAY] = {
        .id = MENU_ID_HI_DELAY,
        .title = "Delay",
        .parent = MENU_ID_HI_CHANNEL,
        .child = MENU_ID_COUNT,
        .prev = MENU_ID_HI_ON,
        .next = MENU_ID_HI_DURATION,
        .type = MENU_TREE_TYPE_LEAF
    },
    [MENU_ID_HI_DURATION] = {
        .id = MENU_ID_HI_DURATION,
        .title = "Duration",
        .parent = MENU_ID_HI_CHANNEL,
        .child = MENU_ID_COUNT,
        .prev = MENU_ID_HI_DELAY,
        .next = MENU_ID_HI_PWM_ON,
        .type = MENU_TREE_TYPE_LEAF
    },
    [MENU_ID_HI_PWM_ON] = {
        .id = MENU_ID_HI_PWM_ON,
        .title = "PWM On/Off",
        .parent = MENU_ID_HI_CHANNEL,
        .child = MENU_ID_COUNT,
        .prev = MENU_ID_HI_DURATION,
        .next = MENU_ID_HI_DUTY,
        .type = MENU_TREE_TYPE_LEAF
    },
    [MENU_ID_HI_DUTY] = {
        .id = MENU_ID_HI_DUTY,
        .title = "PWM Duty",
        .parent = MENU_ID_HI_CHANNEL,
        .child = MENU_ID_COUNT,
        .prev = MENU_ID_HI_PWM_ON,
        .next = MENU_ID_HI_ON,
        .type = MENU_TREE_TYPE_LEAF
    },
    [MENU_ID_LO_CHANNEL] = {
        .id = MENU_ID_LO_CHANNEL,
        .title = "Lo Channel",
        .parent = MENU_ID_SETTINGS,
        .child = MENU_ID_LO_ON,
        .prev = MENU_ID_HI_CHANNEL,
        .next = MENU_ID_COUNT,
        .type = MENU_TREE_TYPE_BRANCH
    },
    [MENU_ID_LO_ON] = {
        .id = MENU_ID_LO_ON,
        .title = "Lo On/Off",
        .parent = MENU_ID_LO_CHANNEL,
        .child = MENU_ID_COUNT,
        .prev = MENU_ID_LO_DUTY,
        .next = MENU_ID_LO_DELAY,
        .type = MENU_TREE_TYPE_LEAF
    },
    [MENU_ID_LO_DELAY] = {
        .id = MENU_ID_LO_DELAY,
        .title = "Delay",
        .parent = MENU_ID_LO_CHANNEL,
        .child = MENU_ID_COUNT,
        .prev = MENU_ID_LO_ON,
        .next = MENU_ID_LO_DURATION,
        .type = MENU_TREE_TYPE_LEAF
    },
    [MENU_ID_LO_DURATION] = {
        .id = MENU_ID_LO_DURATION,
        .title = "Duration",
        .parent = MENU_ID_LO_CHANNEL,
        .child = MENU_ID_COUNT,
        .prev = MENU_ID_LO_DELAY,
        .next = MENU_ID_LO_PWM_ON,
        .type = MENU_TREE_TYPE_LEAF
    },
    [MENU_ID_LO_PWM_ON] = {
        .id = MENU_ID_LO_PWM_ON,
        .title = "PWM On/Off",
        .parent = MENU_ID_LO_CHANNEL,
        .child = MENU_ID_COUNT,
        .prev = MENU_ID_LO_DURATION,
        .next = MENU_ID_LO_DUTY,
        .type = MENU_TREE_TYPE_LEAF
    },
    [MENU_ID_LO_DUTY] = {
        .id = MENU_ID_LO_DUTY,
        .title = "PWM Duty",
        .parent = MENU_ID_LO_CHANNEL,
        .child = MENU_ID_COUNT,
        .prev = MENU_ID_LO_PWM_ON,
        .next = MENU_ID_LO_ON,
        .type = MENU_TREE_TYPE_LEAF
    },
    
};

const menu_node_t *menu_data_get_tree(void) {
    return s_menu_tree;
}

menu_id_t menu_data_get_first_id(void) {
    return MENU_ID_START;
}
