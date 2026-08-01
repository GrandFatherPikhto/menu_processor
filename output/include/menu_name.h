#ifndef MENU_NAME_H
#define MENU_NAME_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#include "menu_type.h"

typedef struct menu_node_name {
    menu_id_t id;
    const char name[0x20];
} menu_node_name_t;

const char *menu_name_get_by_id(menu_context_t *ctx, menu_id_t id);

#endif /* MENU_NAME_H */