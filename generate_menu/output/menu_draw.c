#include "menu_draw.h"
#include "menu_context.h"
#include "menu_tree.h"
#include "menu_config.h"
#include "menu_value.h"

#include <string.h>
#include <stdio.h>

bool menu_draw_update(menu_context_t *ctx, menu_id_t id) {
    
    if (id >= MENU_ID_COUNT || ctx->dirty == false)
        return false;
    
    memset((void *)ctx->title_buf, 0, LCD_STRING_LEN);
    memset((void *)ctx->value_buf, 0, LCD_STRING_LEN);

    strncpy((char *)ctx->title_buf, ctx->nodes[id].title, LCD_STRING_LEN);

    if (ctx->nodes[id].child == MENU_ID_COUNT) {
        if (ctx->configs[id].draw_value_cb) {
            ctx->configs[id].draw_value_cb(ctx, id);
        }
    } else {
        ctx->value_buf[0] = '>';
    }

    ctx->dirty = false;
    ctx->update = true;
}

void menu_draw_string_fixed_value_cb(menu_context_t *ctx, menu_id_t id) {
    uint8_t idx  = ctx->values[id].data.string_fixed.idx;
    const char* value = ctx->configs[id].data.string_fixed.values[idx];
    int len = snprintf(NULL, 0, "%s", value);
    snprintf(ctx->value_buf, LCD_STRING_LEN, "%s%*c",
        value,
        15 - len > 0 ? 15 - len : 0,
        ctx->state == MENU_STATE_EDIT ? '*' : '>'
    );
}


void menu_draw_udword_factor_value_cb(menu_context_t *ctx, menu_id_t id) {
    uint8_t idx = ctx->values[id].data.udword_factor.idx;
    uint32_t value = ctx->values[id].data.udword_factor.value;
    uint32_t max = ctx->configs[id].data.udword_factor.max;
    uint32_t factor = ctx->configs[id].data.udword_factor.factors[idx];

    int len = snprintf(NULL, 0, "%u (x%u)", value, factor);
    snprintf(ctx->value_buf, LCD_STRING_LEN, "%u (x%u)%*c",
        value,
        factor,
        15 - len > 0 ? 15 - len : 0,
        ctx->state == MENU_STATE_EDIT ? '*' : '>'
    );
}
void menu_draw_ubyte_simple_value_cb(menu_context_t *ctx, menu_id_t id) {
    uint8_t min = ctx->configs[id].data.ubyte_simple.min;
    uint8_t max = ctx->configs[id].data.ubyte_simple.max;
    uint8_t value = ctx->values[id].data.ubyte_simple.value;
    int len = snprintf(NULL, 0, "%u/%u", value, max);
    snprintf(ctx->value_buf, LCD_STRING_LEN, "%u/%u%*c",
        value,
        max,
        15 - len > 0 ? 15 - len : 0,
        ctx->state == MENU_STATE_EDIT ? '*' : '>'
    );
}

