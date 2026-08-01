#include "menu_data_value.h"
#include "menu_value.h"

static menu_node_value_t s_menu_values[] = {
    // start fixed
    [MENU_ID_START] = {
        .id = MENU_ID_START,
        .data.string_fixed = {
            .idx = 0
        }
    },
    // regimes fixed
    [MENU_ID_REGIMES] = {
        .id = MENU_ID_REGIMES,
        .data.string_fixed = {
            .idx = 2
        }
    },
    // version callback
    [MENU_ID_VERSION] = {
        .id = MENU_ID_VERSION,
        .data.callback_callback = {
            .value_ptr = 0
        }
    },
    // pwm_frequency callback
    [MENU_ID_PWM_FREQUENCY] = {
        .id = MENU_ID_PWM_FREQUENCY,
        .data.callback_callback = {
            .value_ptr = 0
        }
    },
    // hi_on fixed
    [MENU_ID_HI_ON] = {
        .id = MENU_ID_HI_ON,
        .data.string_fixed = {
            .idx = 1
        }
    },
    // hi_delay factor
    [MENU_ID_HI_DELAY] = {
        .id = MENU_ID_HI_DELAY,
        .data.udword_factor = {
            .idx = 0,
            .value = 10
        }
    },
    // hi_duration factor
    [MENU_ID_HI_DURATION] = {
        .id = MENU_ID_HI_DURATION,
        .data.udword_factor = {
            .idx = 2,
            .value = 10
        }
    },
    // hi_pwm_on fixed
    [MENU_ID_HI_PWM_ON] = {
        .id = MENU_ID_HI_PWM_ON,
        .data.string_fixed = {
            .idx = 0
        }
    },
    // hi_duty simple
    [MENU_ID_HI_DUTY] = {
        .id = MENU_ID_HI_DUTY,
        .data.ubyte_simple = {
            .value = 30
        }
    },
    // lo_on fixed
    [MENU_ID_LO_ON] = {
        .id = MENU_ID_LO_ON,
        .data.string_fixed = {
            .idx = 1
        }
    },
    // lo_delay factor
    [MENU_ID_LO_DELAY] = {
        .id = MENU_ID_LO_DELAY,
        .data.udword_factor = {
            .idx = 0,
            .value = 10
        }
    },
    // lo_duration factor
    [MENU_ID_LO_DURATION] = {
        .id = MENU_ID_LO_DURATION,
        .data.udword_factor = {
            .idx = 0,
            .value = 10
        }
    },
    // lo_pwm_on fixed
    [MENU_ID_LO_PWM_ON] = {
        .id = MENU_ID_LO_PWM_ON,
        .data.string_fixed = {
            .idx = 0
        }
    },
    // lo_duty simple
    [MENU_ID_LO_DUTY] = {
        .id = MENU_ID_LO_DUTY,
        .data.ubyte_simple = {
            .value = 30
        }
    },
};

menu_node_value_t *menu_data_get_values(void) {
    return s_menu_values;
}