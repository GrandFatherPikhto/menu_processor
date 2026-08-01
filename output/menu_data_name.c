#include "menu_data_name.h"
#include "menu_name.h"

static const menu_node_name_t s_menu_id_names[] = {
    [MENU_ID_ROOT] = {MENU_ID_ROOT, "MENU_ID_ROOT"},
    [MENU_ID_START] = {
            .id = MENU_ID_START,
            .name = "MENU_ID_START",
    },
    [MENU_ID_REGIMES] = {
            .id = MENU_ID_REGIMES,
            .name = "MENU_ID_REGIMES",
    },
    [MENU_ID_VERSION] = {
            .id = MENU_ID_VERSION,
            .name = "MENU_ID_VERSION",
    },
    [MENU_ID_SETTINGS] = {
            .id = MENU_ID_SETTINGS,
            .name = "MENU_ID_SETTINGS",
    },
    [MENU_ID_PWM_FREQUENCY] = {
            .id = MENU_ID_PWM_FREQUENCY,
            .name = "MENU_ID_PWM_FREQUENCY",
    },
    [MENU_ID_HI_CHANNEL] = {
            .id = MENU_ID_HI_CHANNEL,
            .name = "MENU_ID_HI_CHANNEL",
    },
    [MENU_ID_HI_ON] = {
            .id = MENU_ID_HI_ON,
            .name = "MENU_ID_HI_ON",
    },
    [MENU_ID_HI_DELAY] = {
            .id = MENU_ID_HI_DELAY,
            .name = "MENU_ID_HI_DELAY",
    },
    [MENU_ID_HI_DURATION] = {
            .id = MENU_ID_HI_DURATION,
            .name = "MENU_ID_HI_DURATION",
    },
    [MENU_ID_HI_PWM_ON] = {
            .id = MENU_ID_HI_PWM_ON,
            .name = "MENU_ID_HI_PWM_ON",
    },
    [MENU_ID_HI_DUTY] = {
            .id = MENU_ID_HI_DUTY,
            .name = "MENU_ID_HI_DUTY",
    },
    [MENU_ID_LO_CHANNEL] = {
            .id = MENU_ID_LO_CHANNEL,
            .name = "MENU_ID_LO_CHANNEL",
    },
    [MENU_ID_LO_ON] = {
            .id = MENU_ID_LO_ON,
            .name = "MENU_ID_LO_ON",
    },
    [MENU_ID_LO_DELAY] = {
            .id = MENU_ID_LO_DELAY,
            .name = "MENU_ID_LO_DELAY",
    },
    [MENU_ID_LO_DURATION] = {
            .id = MENU_ID_LO_DURATION,
            .name = "MENU_ID_LO_DURATION",
    },
    [MENU_ID_LO_PWM_ON] = {
            .id = MENU_ID_LO_PWM_ON,
            .name = "MENU_ID_LO_PWM_ON",
    },
    [MENU_ID_LO_DUTY] = {
            .id = MENU_ID_LO_DUTY,
            .name = "MENU_ID_LO_DUTY",
    },
    
};

const menu_node_name_t *menu_data_get_node_names(void) {
    return s_menu_id_names;
}

