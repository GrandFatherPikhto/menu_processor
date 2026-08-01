"""Tree view of the menu, backed directly by the in-memory node dicts.

Structural edits (add/delete/move) mutate the underlying nested Python
list structure directly, then the whole ``QTreeWidget`` is rebuilt from
scratch. Tree sizes here are tens of nodes, so a full rebuild per
structural edit is simpler and more robust than incremental Qt item
surgery.
"""

import logging
from typing import List, Optional, Set, Tuple

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger("gui.tree_panel")

#: Keys that only make sense on a leaf; stripped when a node becomes a branch.
LEAF_VALUE_KEYS = (
    "type", "role", "min", "max", "step", "default", "default_idx",
    "factors", "values", "controls", "navigate",
    "click_cb", "position_cb", "double_click_cb", "long_click_cb",
    "event_cb", "draw_value_cb",
)


def is_branch(node: dict) -> bool:
    """Matches the validator's own branch/leaf convention: a branch has no ``type``."""
    return "type" not in node


def find_container(tree: List[dict], node_id: str) -> Optional[Tuple[List[dict], int]]:
    """Recursively finds the list containing ``node_id`` and its index within it."""
    for index, item in enumerate(tree):
        if item.get("id") == node_id:
            return tree, index
        if "items" in item:
            found = find_container(item["items"], node_id)
            if found is not None:
                return found
    return None


def all_ids(tree: List[dict]) -> Set[str]:
    ids: Set[str] = set()
    for item in tree:
        if "id" in item:
            ids.add(item["id"])
        if "items" in item:
            ids.update(all_ids(item["items"]))
    return ids


def unique_id(tree: List[dict], prefix: str = "node") -> str:
    """New-node ids must be unique across the *whole* tree, not just siblings."""
    existing = all_ids(tree)
    n = 1
    while f"{prefix}_{n}" in existing:
        n += 1
    return f"{prefix}_{n}"


def new_leaf(node_id: str, title: str) -> dict:
    """A freshly added node defaults to a schema-valid string/fixed leaf."""
    return {
        "id": node_id,
        "title": title,
        "type": "string",
        "role": "fixed",
        "values": ["Value"],
        "default_idx": 0,
        "navigate": "cyclic",
    }


class TreePanel(QWidget):
    nodeSelected = pyqtSignal(dict)

    def __init__(self, document, parent=None):
        super().__init__(parent)
        self._document = document

        self._widget = QTreeWidget(self)
        self._widget.setHeaderLabels(["Menu"])
        self._widget.itemSelectionChanged.connect(self._on_selection_changed)

        add_child_btn = QPushButton("Add child", self)
        add_child_btn.clicked.connect(self.add_child)
        add_sibling_btn = QPushButton("Add sibling", self)
        add_sibling_btn.clicked.connect(self.add_sibling)
        delete_btn = QPushButton("Delete", self)
        delete_btn.clicked.connect(self.delete_selected)
        up_btn = QPushButton("Move up", self)
        up_btn.clicked.connect(self.move_up)
        down_btn = QPushButton("Move down", self)
        down_btn.clicked.connect(self.move_down)

        buttons = QHBoxLayout()
        for button in (add_child_btn, add_sibling_btn, delete_btn, up_btn, down_btn):
            buttons.addWidget(button)

        layout = QVBoxLayout(self)
        layout.addLayout(buttons)
        layout.addWidget(self._widget)

        self.refresh()

    # -- building -------------------------------------------------------------
    def refresh(self, select_id: Optional[str] = None) -> None:
        self._widget.blockSignals(True)
        self._widget.clear()
        for node in self._document.tree:
            self._widget.addTopLevelItem(self._build_item(node))
        self._widget.expandAll()
        self._widget.blockSignals(False)
        if select_id:
            self._select_by_id(select_id)
        else:
            self._on_selection_changed()

    def _build_item(self, node: dict) -> QTreeWidgetItem:
        item = QTreeWidgetItem([node.get("title") or node.get("id") or "?"])
        item.setData(0, Qt.ItemDataRole.UserRole, node)
        for child in node.get("items", []):
            item.addChild(self._build_item(child))
        return item

    def _select_by_id(self, node_id: str) -> None:
        stack = [self._widget.topLevelItem(i) for i in range(self._widget.topLevelItemCount())]
        while stack:
            item = stack.pop()
            node = item.data(0, Qt.ItemDataRole.UserRole)
            if node.get("id") == node_id:
                self._widget.setCurrentItem(item)
                return
            stack.extend(item.child(i) for i in range(item.childCount()))

    # -- selection --------------------------------------------------------------
    def selected_node(self) -> Optional[dict]:
        item = self._widget.currentItem()
        if item is None:
            return None
        return item.data(0, Qt.ItemDataRole.UserRole)

    def _on_selection_changed(self) -> None:
        node = self.selected_node()
        self.nodeSelected.emit(node or {})

    # -- structural edits ---------------------------------------------------------
    def add_child(self) -> None:
        node = self.selected_node()
        if node is None:
            target_list = self._document.tree
        else:
            if not is_branch(node):
                answer = QMessageBox.question(
                    self, "Convert to branch",
                    f"'{node.get('id')}' is a leaf node. Adding a child will convert "
                    "it into a branch and remove its type/value fields. Continue?",
                )
                if answer != QMessageBox.StandardButton.Yes:
                    return
                for key in LEAF_VALUE_KEYS:
                    node.pop(key, None)
                node["items"] = []
            target_list = node.setdefault("items", [])

        new_id = unique_id(self._document.tree)
        target_list.append(new_leaf(new_id, "New Item"))
        self._document.mark_dirty()
        self.refresh(select_id=new_id)

    def add_sibling(self) -> None:
        node = self.selected_node()
        if node is None:
            self.add_child()
            return
        found = find_container(self._document.tree, node["id"])
        if found is None:
            return
        container, index = found
        new_id = unique_id(self._document.tree)
        container.insert(index + 1, new_leaf(new_id, "New Item"))
        self._document.mark_dirty()
        self.refresh(select_id=new_id)

    def delete_selected(self) -> None:
        node = self.selected_node()
        if node is None:
            return
        answer = QMessageBox.question(
            self, "Delete node", f"Delete '{node.get('id')}' and all its children?"
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        found = find_container(self._document.tree, node["id"])
        if found is None:
            return
        container, index = found
        del container[index]
        self._document.mark_dirty()
        self.refresh()

    def move_up(self) -> None:
        self._move(-1)

    def move_down(self) -> None:
        self._move(1)

    def _move(self, offset: int) -> None:
        node = self.selected_node()
        if node is None:
            return
        found = find_container(self._document.tree, node["id"])
        if found is None:
            return
        container, index = found
        new_index = index + offset
        if 0 <= new_index < len(container):
            container[index], container[new_index] = container[new_index], container[index]
            self._document.mark_dirty()
            self.refresh(select_id=node["id"])
