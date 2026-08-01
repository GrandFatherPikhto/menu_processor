"""Bottom log panel: captures root-logger records into a colored, searchable view.

Every ``logger.error/info/debug(...)`` call already made throughout
``generate_menu/*`` propagates to the root logger (nothing there sets
``propagate=False``), so attaching :class:`QtLogHandler` there surfaces the
whole backend's existing logging with no backend changes.
"""

import logging

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor, QTextCursor
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

_LEVEL_COLORS = {
    logging.ERROR: QColor("#e05252"),
    logging.CRITICAL: QColor("#e05252"),
    logging.WARNING: QColor("#d99a3c"),
    logging.DEBUG: QColor("#888888"),
}


class _LogEmitter(QObject):
    """Plain QObject signal carrier.

    Kept separate from the handler on purpose: multiply-inheriting
    ``logging.Handler`` and ``QObject`` directly is a well known source of
    metaclass friction in PyQt; composition avoids it entirely.
    """

    logRecord = pyqtSignal(str, int)


class QtLogHandler(logging.Handler):
    """``logging.Handler`` that forwards records to Qt via a signal (thread-safe)."""

    def __init__(self):
        super().__init__()
        self.emitter = _LogEmitter()
        self.setFormatter(logging.Formatter("%(message)s"))

    def emit(self, record: logging.LogRecord) -> None:
        try:
            message = self.format(record)
        except Exception:
            message = record.getMessage()
        self.emitter.logRecord.emit(message, record.levelno)


class LogPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._text = QTextEdit(self)
        self._text.setReadOnly(True)
        self._text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        font = self._text.font()
        font.setFamily("Consolas")
        self._text.setFont(font)

        self._search_edit = QLineEdit(self)
        self._search_edit.setPlaceholderText("Search log...")
        self._search_edit.returnPressed.connect(self._find_next)

        find_next_btn = QPushButton("Next", self)
        find_next_btn.clicked.connect(self._find_next)
        find_prev_btn = QPushButton("Prev", self)
        find_prev_btn.clicked.connect(self._find_prev)
        copy_btn = QPushButton("Copy All", self)
        copy_btn.clicked.connect(self._copy_all)
        clear_btn = QPushButton("Clear", self)
        clear_btn.clicked.connect(self._text.clear)

        search_row = QHBoxLayout()
        search_row.addWidget(self._search_edit)
        search_row.addWidget(find_next_btn)
        search_row.addWidget(find_prev_btn)
        search_row.addStretch(1)
        search_row.addWidget(copy_btn)
        search_row.addWidget(clear_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(search_row)
        layout.addWidget(self._text)

    def append_record(self, message: str, level: int) -> None:
        color = _LEVEL_COLORS.get(level)
        cursor = self._text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._text.setTextCursor(cursor)
        self._text.setTextColor(color if color is not None else self._text.palette().text().color())
        self._text.append(message)

    def _find_next(self) -> None:
        text = self._search_edit.text()
        if text:
            self._text.find(text)

    def _find_prev(self) -> None:
        text = self._search_edit.text()
        if text:
            self._text.find(text, QTextEdit.FindFlag.FindBackward)

    def _copy_all(self) -> None:
        QApplication.clipboard().setText(self._text.toPlainText())
