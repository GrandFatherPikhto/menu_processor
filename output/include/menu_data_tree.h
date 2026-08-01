#ifndef MENU_DATA_TREE_H
#define MENU_DATA_TREE_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#include "menu_type.h"

const menu_node_t *menu_data_get_tree(void);
menu_id_t menu_data_get_first_id(void);

#endif /* MENU_DATA_TREE_H */