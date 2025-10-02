#include "menu.h"
#include "menu_data_context.h"
#include "menu_context.h"
#include "menu_navigate.h"
#include "menu_draw.h"

// Инициализация
void menu_init(void) {
    static menu_context_t context = { 0 };
    menu_context_init(&context);
}

// Публичное API для внешнего мира
void menu_position(int8_t delta) {
    menu_context_t *ctx = menu_data_get_context();
    menu_navigate_handle_position(ctx, ctx->current, delta);
}

void menu_enter(void) {
    menu_context_t *ctx = menu_data_get_context();
    menu_navigate_handle_enter(ctx, ctx->current);
}

void menu_back(void) {
    menu_context_t *ctx = menu_data_get_context();
    menu_navigate_handle_back(ctx, ctx->current);
}

void menu_reset(void) {
    // Пока не реализовано. Сброс к начальным значениям
    menu_context_t *ctx = menu_data_get_context();
}

void menu_update(void) {
    menu_context_t *ctx = menu_data_get_context();
    if (menu_context_get_dirty(ctx)) {
        menu_draw_update(ctx, menu_context_get_current_id(ctx));
    }
}

// Для отрисовки (можно вынести в отдельный menu_display.h)
char* menu_title_buf(void) {
    menu_context_t *ctx = menu_data_get_context();
    return menu_context_get_title_str(ctx);
}

char* menu_value_buf(void) {
    menu_context_t *ctx = menu_data_get_context();
    return menu_context_get_value_str(ctx);
}

bool menu_needs_redraw(void) {
    menu_context_t *ctx = menu_data_get_context();
    return menu_context_get_update(ctx);
}

bool menu_ack_redraw(void) {
    menu_context_t *ctx = menu_data_get_context();
    bool ack_redraw = menu_context_get_update(ctx);
    menu_context_reset_update(ctx);
    return ack_redraw;
}

void menu_set_dirty(void) {
    menu_context_t *ctx = menu_data_get_context();
    menu_context_set_dirty(ctx);
}

menu_state_t menu_state(void) {
    menu_context_t *ctx = menu_data_get_context();
    return menu_context_get_state(ctx);
}