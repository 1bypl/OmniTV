"""Własna belka tytułu, żeby dopasować ją kolorystycznie do motywu."""

from __future__ import annotations

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton

from omnity.i18n import tr


class TitleBar(QFrame):
    def __init__(self, window):
        super().__init__(window)
        self._window = window
        self._drag_offset: QPoint | None = None
        self.setObjectName("titleBar")
        self.setFixedHeight(36)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(2)

        self._title = QLabel(window.windowTitle(), self)
        self._title.setObjectName("titleText")
        self._title.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        layout.addWidget(self._title)
        layout.addStretch(1)

        self._minimize = self._button("—", "titleButton")
        self._minimize.clicked.connect(self._window.showMinimized)
        layout.addWidget(self._minimize)

        self._maximize = self._button("□", "titleButton")
        self._maximize.clicked.connect(self._toggle_maximize)
        layout.addWidget(self._maximize)

        self._close = self._button("✕", "closeButton")
        self._close.clicked.connect(self._window.close)
        layout.addWidget(self._close)

        self.retranslate()
        self.update_state()

    def _button(self, text: str, object_name: str) -> QPushButton:
        button = QPushButton(text, self)
        button.setObjectName(object_name)
        button.setFixedSize(46, 36)
        button.setFocusPolicy(Qt.NoFocus)
        return button

    def set_title(self, title: str):
        self._title.setText(title)

    def retranslate(self):
        self.set_title(tr("app_title"))
        self._minimize.setToolTip(tr("minimize"))
        self._maximize.setToolTip(
            tr("restore") if self._window.isMaximized() else tr("maximize")
        )
        self._close.setToolTip(tr("close"))
        self.update_state()

    def update_state(self):
        maximized = self._window.isMaximized()
        self._maximize.setText("❐" if maximized else "□")
        self._maximize.setToolTip(
            tr("restore") if maximized else tr("maximize")
        )

    def _toggle_maximize(self):
        if self._window.isMaximized():
            self._window.showNormal()
        else:
            self._window.showMaximized()
        self.update_state()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_offset = (
                event.globalPosition().toPoint()
                - self._window.frameGeometry().topLeft()
            )
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            self._drag_offset is not None
            and event.buttons() & Qt.LeftButton
            and not self._window.isMaximized()
            and not self._window.isFullScreen()
        ):
            self._window.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_offset = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._toggle_maximize()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)
