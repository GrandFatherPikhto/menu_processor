#include "menu_tree.h"
#include "menu_edit.h"
#include "menu_config.h"
#include "menu_value.h"
#include "menu_context.h"

/** @brief Функция для фиксированных наборов значений
  * Последующее или предыдущее значение берётся из массива values
  * Если control == click, то navigation _только_ cycle.
  * @param id Идентификтор меню Определён, в enum в menu_struct.h
  * @param delta Количество "щелчков" энкодера. Передаётся только если control==position
  */
void string_fixed_click_cyclic_cb(menu_context_t *ctx, menu_id_t id) {
    uint8_t *idx  = &(ctx->values[id].data.string_fixed.idx);
    uint8_t old_idx = *idx;
    uint8_t count = ctx->configs[id].data.string_fixed.count;
    if (count == 0) {
       return; // Или установите idx в 0
    }

    if (count - 1 > *idx) {
        *idx = *idx + 1;
    } else {
        *idx = 0;
    }

    if (*idx != old_idx) {
        ctx->dirty = true;
    }
}

void string_fixed_position_cyclic_cb(menu_context_t *ctx, menu_id_t id, int8_t delta) {
    uint8_t *idx  = &(ctx->values[id].data.string_fixed.idx);
    uint8_t old_idx = *idx;
    uint8_t count = ctx->configs[id].data.string_fixed.count;
    if (count == 0) {
       return; // Или установите idx в 0
    }
    if (delta > 0) {
        if (delta + *idx < count) {
            *idx = *idx + delta;
        } else {
            *idx = 0;
        }
    }

    if (delta < 0) {
        if (*idx >= -delta) {
            *idx = *idx + delta;
        } else {
            *idx = count - 1;
        }
    }
    if (*idx != old_idx) {
        ctx->dirty = true;
    }
}

/** @brief Функция для изменения простого числового типа при помощи множителя.
  * Здесь обрабатывается клик.
  * Изменение значение изменяется пропорционально выбранному значению factor
  * Если control == click, то navigation _только_ cycle. И для factor клик меняет
  * индекс factor (множителя) из массива factors
  * @param id Идентификтор меню Определён, в enum в menu_struct.h
  * @param delta Количество "щелчков" энкодера. Передаётся только если control==position
  * click
  */
void udword_factor_click_cyclic_factor_cb(menu_context_t *ctx, menu_id_t id) {
    uint8_t *idx  = &(ctx->values[id].data.udword_factor.idx);
    uint8_t count = ctx->configs[id].data.udword_factor.count;
    uint8_t old_idx = *idx;

    if ((*idx + 1) >= count) {
        *idx = 0;
    } else {
        *idx = *idx + 1;
    }

    if (*idx != old_idx) {
        ctx->dirty = true;
    }
}


/** @brief Функция для изменения простого числового типа при помощи множителя.
  * Здесь обрабатывается позиция энкодера. 
  * Изменение значение изменяется пропорционально выбранному значению factor
  * Значение value может изменяться по кругу, т.е., достигнув максимального значения max становится min
  * Достигнув минимального значения min становится max
  * @param id Идентификтор меню Определён, в enum в menu_struct.h
  * @param delta Количество "щелчков" энкодера. Передаётся только если control==position
  * position
  */
void udword_factor_position_limit_cb(menu_context_t *ctx, menu_id_t id, int8_t delta) {
    uint8_t *idx  = &(ctx->values[id].data.udword_factor.idx);
    uint32_t *value  = &(ctx->values[id].data.udword_factor.value);
    uint32_t  min    = ctx->configs[id].data.udword_factor.min;
    uint32_t  max    = ctx->configs[id].data.udword_factor.max;
    uint32_t  factor = ctx->configs[id].data.udword_factor.factors[*idx];
    uint32_t  old_value = *value;
    if (delta > 0) {
        // Увеличение с проверкой переполнения
        if (*value <= max - (uint32_t)(delta * factor)) {
            *value += delta * factor;
        } else {
            *value = max;
        }
    } else {
        // Уменьшение с проверкой underflow
        if (*value >= min + (uint32_t)(-delta * factor)) {
            *value += delta * factor;  // delta отрицательный
        } else {
            *value = min;
        }
    }
    if (*value != old_value) {
        ctx->dirty = true;
    }
}

/** @brief Функция для простейших численных типов.
  * Если control == click, то navigation _только_ cycle.
  * Значения не зациклены. Достигнув max значение остаётся max, 
  * достигнув min значение останется min, пока не поменяем направление вращения энкодера
  * @param id Идентификтор меню Определён, в enum в menu_struct.h
  * @param delta Количество "щелчков" энкодера. Передаётся только если control==position
  */
void ubyte_simple_position_limit_cb(menu_context_t *ctx, menu_id_t id, int8_t delta) {
    uint8_t *value  = &(ctx->values[id].data.ubyte_simple.value);
    uint8_t  step = ctx->configs[id].data.ubyte_simple.step;
    uint8_t   min = ctx->configs[id].data.ubyte_simple.min;
    uint8_t   max = ctx->configs[id].data.ubyte_simple.max;
    uint8_t old_value = *value;  
    if (delta > 0) {
      if ((*value + step * delta) > max) {
        *value = max;
      } else {
        *value = *value + step * delta;
      }
    }

    if (delta < 0) {
      if ((*value + step * delta) < min) {
        *value = min;
      } else {
        *value = *value + step * delta;
      }
    }
    if (*value != old_value) {
        ctx->dirty = true;
    }
}


