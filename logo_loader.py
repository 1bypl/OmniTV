"""Asynchroniczne pobieranie logotypów kanałów z cache na dysku."""

from __future__ import annotations

import hashlib
import os

import requests
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Qt, Signal
from PySide6.QtGui import QIcon, QImage, QPixmap

from omnity.core.catalog import cache_dir


def _logo_cache_dir() -> str:
    path = os.path.join(cache_dir(), "logos")
    os.makedirs(path, exist_ok=True)
    return path


class _Signals(QObject):
    done = Signal(str, QImage)
    failed = Signal(str)


class _LogoTask(QRunnable):
    def __init__(self, channel_id: str, url: str, signals: _Signals):
        super().__init__()
        self._channel_id = channel_id
        self._url = url
        self._signals = signals

    def run(self):
        try:
            path = os.path.join(
                _logo_cache_dir(), hashlib.sha1(self._url.encode()).hexdigest() + ".img"
            )
            if os.path.exists(path):
                with open(path, "rb") as handle:
                    data = handle.read()
            else:
                response = requests.get(self._url, timeout=15)
                response.raise_for_status()
                data = response.content
                try:
                    with open(path, "wb") as handle:
                        handle.write(data)
                except OSError:
                    pass

            image = QImage()
            if not image.loadFromData(data) or image.isNull():
                self._signals.failed.emit(self._channel_id)
                return
            image = image.scaled(
                48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self._signals.done.emit(self._channel_id, image)
        except Exception:
            self._signals.failed.emit(self._channel_id)


class LogoLoader(QObject):
    icon_ready = Signal(str, QIcon)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pool = QThreadPool(self)
        self._pool.setMaxThreadCount(8)
        self._signals = _Signals()
        self._signals.done.connect(self._on_done)
        self._signals.failed.connect(lambda _channel_id: None)
        self._requested: set[str] = set()
        self._icons: dict[str, QIcon] = {}

    def request(self, channel_id: str, url: str | None):
        if channel_id in self._icons:
            self.icon_ready.emit(channel_id, self._icons[channel_id])
            return
        if not url or channel_id in self._requested:
            return
        self._requested.add(channel_id)
        self._pool.start(_LogoTask(channel_id, url, self._signals))

    def _on_done(self, channel_id: str, image: QImage):
        icon = QIcon(QPixmap.fromImage(image))
        self._icons[channel_id] = icon
        self.icon_ready.emit(channel_id, icon)

    def reset(self):
        self._requested.clear()
        self._icons.clear()

    def shutdown(self):
        self._pool.clear()
        self._pool.waitForDone(2000)
