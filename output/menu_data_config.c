#include "menu_data_config.h"
#include "menu_config.h"
#include "menu_edit.h"
#include "menu_draw.h"

#include "pulse_config.h"

static const uint32_t s_factors_hi_delay[] = { 1, 10, 100, 1000 };
static const uint32_t s_factors_hi_duration[] = { 1, 10, 100, 1000 };
static const uint32_t s_factors_lo_delay[] = { 1, 10, 100, 1000 };
static const uint32_t s_factors_lo_duration[] = { 1, 10, 100, 1000 };

static const char *s_values_str_start[] = { "Start", "Started" };
static const char *s_values_str_regimes[] = { "Simple", "Strong", "Quality" };
static const char *s_values_str_hi_on[] = { "Off", "On" };
static const char *s_values_str_hi_pwm_on[] = { "Off", "On" };
static const char *s_values_str_lo_on[] = { "Off", "On" };
static const char *s_values_str_lo_pwm_on[] = { "Off", "On" };

static const menu_node_config_t s_menu_config[] = {
    [MENU_ID_START] = {        
        .id = MENU_ID_START,
        .category = MENU_CATEGORY_STRING_FIXED,
        .click_cb = string_fixed_click_cyclic_cb,
        .position_cb = string_fixed_position_cyclic_cb,
        .double_click_cb = NULL,
        .long_click_cb = NULL,
        .draw_value_cb = menu_draw_string_fixed_value_cb,
        .event_cb = NULL,
        .data.string_fixed = {
            .default_idx = 0,
            .count = 2,
            .values = s_values_str_start
        }
    },
    [MENU_ID_REGIMES] = {        
        .id = MENU_ID_REGIMES,
        .category = MENU_CATEGORY_STRING_FIXED,
        .click_cb = NULL,
        .position_cb = string_fixed_position_cyclic_cb,
        .double_click_cb = NULL,
        .long_click_cb = NULL,
        .draw_value_cb = menu_draw_string_fixed_value_cb,
        .event_cb = NULL,
        .data.string_fixed = {
            .default_idx = 2,
            .count = 3,
            .values = s_values_str_regimes
        }
    },
    [MENU_ID_VERSION] = {        
        .id = MENU_ID_VERSION,
        .category = MENU_CATEGORY_CALLBACK_CALLBACK,
        .click_cb = NULL,
        .position_cb = NULL,
        .double_click_cb = NULL,
        .long_click_cb = NULL,
        .draw_value_cb = draw_version_cb,
        .event_cb = NULL,
        .data.stub_config = {}
    },
    [MENU_ID_PWM_FREQUENCY] = {        
        .id = MENU_ID_PWM_FREQUENCY,
        .category = MENU_CATEGORY_CALLBACK_CALLBACK,
        .click_cb = NULL,
        .position_cb = pwm_frequency_change_cb,
        .double_click_cb = NULL,
        .long_click_cb = NULL,
        .draw_value_cb = pwm_frequency_display_cb,
        .event_cb = NULL,
        .data.stub_config = {}
    },
    [MENU_ID_HI_ON] = {        
        .id = MENU_ID_HI_ON,
        .category = MENU_CATEGORY_STRING_FIXED,
        .click_cb = string_fixed_click_cyclic_cb,
        .position_cb = string_fixed_position_cyclic_cb,
        .double_click_cb = NULL,
        .long_click_cb = NULL,
        .draw_value_cb = menu_draw_string_fixed_value_cb,
        .event_cb = my_event_cb,
        .data.string_fixed = {
            .default_idx = 1,
            .count = 2,
            .values = s_values_str_hi_on
        }
    },
    [MENU_ID_HI_DELAY] = {        
        .id = MENU_ID_HI_DELAY,
        .category = MENU_CATEGORY_UDWORD_FACTOR,
        .click_cb = udword_factor_click_cyclic_factor_cb,
        .position_cb = udword_factor_position_limit_cb,
        .double_click_cb = NULL,
        .long_click_cb = NULL,
        .draw_value_cb = menu_draw_udword_factor_value_cb,
        .event_cb = NULL,
        .data.udword_factor = {
            .default_value = 10,
            .min = 10,
            .max = 10000,
            .step = 1,
            .default_idx = 0,
            .count = 4,
            .factors = s_factors_hi_delay
        }
    },
    [MENU_ID_HI_DURATION] = {        
        .id = MENU_ID_HI_DURATION,
        .category = MENU_CATEGORY_UDWORD_FACTOR,
        .click_cb = udword_factor_click_cyclic_factor_cb,
        .position_cb = udword_factor_position_limit_cb,
        .double_click_cb = NULL,
        .long_click_cb = NULL,
        .draw_value_cb = menu_draw_udword_factor_value_cb,
        .event_cb = NULL,
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
    [MENU_ID_HI_PWM_ON] = {        
        .id = MENU_ID_HI_PWM_ON,
        .category = MENU_CATEGORY_STRING_FIXED,
        .click_cb = string_fixed_click_cyclic_cb,
        .position_cb = string_fixed_position_cyclic_cb,
        .double_click_cb = NULL,
        .long_click_cb = NULL,
        .draw_value_cb = menu_draw_string_fixed_value_cb,
        .event_cb = my_event_cb,
        .data.string_fixed = {
            .default_idx = 0,
            .count = 2,
            .values = s_values_str_hi_pwm_on
        }
    },
    [MENU_ID_HI_DUTY] = {        
        .id = MENU_ID_HI_DUTY,
        .category = MENU_CATEGORY_UBYTE_SIMPLE,
        .click_cb = NULL,
        .position_cb = ubyte_simple_position_limit_cb,
        .double_click_cb = NULL,
        .long_click_cb = NULL,
        .draw_value_cb = menu_draw_ubyte_simple_value_cb,
        .event_cb = NULL,
        .data.ubyte_simple = {
            .default_value = 30,
            .step = 1,
            .min = 0,
            .max = 95
        }
    },
    [MENU_ID_LO_ON] = {        
        .id = MENU_ID_LO_ON,
        .category = MENU_CATEGORY_STRING_FIXED,
        .click_cb = string_fixed_click_cyclic_cb,
        .position_cb = string_fixed_position_cyclic_cb,
        .double_click_cb = NULL,
        .long_click_cb = NULL,
        .draw_value_cb = menu_draw_string_fixed_value_cb,
        .event_cb = my_event_cb,
        .data.string_fixed = {
            .default_idx = 1,
            .count = 2,
            .values = s_values_str_lo_on
        }
    },
    [MENU_ID_LO_DELAY] = {        
        .id = MENU_ID_LO_DELAY,
        .category = MENU_CATEGORY_UDWORD_FACTOR,
        .click_cb = udword_factor_click_cyclic_factor_cb,
        .position_cb = udword_factor_position_limit_cb,
        .double_click_cb = NULL,
        .long_click_cb = NULL,
        .draw_value_cb = menu_draw_udword_factor_value_cb,
        .event_cb = NULL,
        .data.udword_factor = {
            .default_value = 10,
            .min = 10,
            .max = 10000,
            .step = 1,
            .default_idx = 0,
            .count = 4,
            .factors = s_factors_lo_delay
        }
    },
    [MENU_ID_LO_DURATION] = {        
        .id = MENU_ID_LO_DURATION,
        .category = MENU_CATEGORY_UDWORD_FACTOR,
        .click_cb = udword_factor_click_cyclic_factor_cb,
        .position_cb = udword_factor_position_limit_cb,
        .double_click_cb = NULL,
        .long_click_cb = NULL,
        .draw_value_cb = menu_draw_udword_factor_value_cb,
        .event_cb = NULL,
        .data.udword_factor = {
            .default_value = 10,
            .min = 10,
            .max = 10000,
            .step = 1,
            .default_idx = 0,
            .count = 4,
            .factors = s_factors_lo_duration
        }
    },
    [MENU_ID_LO_PWM_ON] = {        
        .id = MENU_ID_LO_PWM_ON,
        .category = MENU_CATEGORY_STRING_FIXED,
        .click_cb = string_fixed_click_cyclic_cb,
        .position_cb = string_fixed_position_cyclic_cb,
        .double_click_cb = NULL,
        .long_click_cb = NULL,
        .draw_value_cb = menu_draw_string_fixed_value_cb,
        .event_cb = my_event_cb,
        .data.string_fixed = {
            .default_idx = 0,
            .count = 2,
            .values = s_values_str_lo_pwm_on
        }
    },
    [MENU_ID_LO_DUTY] = {        
        .id = MENU_ID_LO_DUTY,
        .category = MENU_CATEGORY_UBYTE_SIMPLE,
        .click_cb = NULL,
        .position_cb = ubyte_simple_position_limit_cb,
        .double_click_cb = NULL,
        .long_click_cb = NULL,
        .draw_value_cb = menu_draw_ubyte_simple_value_cb,
        .event_cb = NULL,
        .data.ubyte_simple = {
            .default_value = 30,
            .step = 1,
            .min = 0,
            .max = 95
        }
    },
};


const menu_node_config_t *menu_data_get_config(void) {
    return s_menu_config;
}
