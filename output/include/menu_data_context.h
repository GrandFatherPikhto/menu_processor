#ifndef MENU_DATA_CONTEXT_H
#define MENU_DATA_CONTEXT_H

#include <stdint.h>
#include <stdbool.h>

#include "menu_type.h"

menu_context_t *menu_data_get_context(void);
void menu_data_set_context(menu_context_t *ctx);

#endif /* MENU_DATA_CONTEXT_H */