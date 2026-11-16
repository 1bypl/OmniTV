"""Wątek pobierający i parsujący EPG (program TV) dla kanału."""

from PySide6.QtCore import QThread, Signal

from omnity.core.epg import fetch_xmltv, find_programmes


class EpgWorker(QThread):
    ready = Signal(str, list)
    failed = Signal(str, str)

    def __init__(self, channel_id: str, channel_name: str, sources: list[str], parent=None):
        super().__init__(parent)
        self._channel_id = channel_id
        self._channel_name = channel_name
        self._sources = sources

    def run(self):
        for url in self._sources:
            if self.isInterruptionRequested():
                return
            try:
                data = fetch_xmltv(url)
                if self.isInterruptionRequested():
                    return
                programmes = find_programmes(data, self._channel_name)
            except Exception:
                continue
            if programmes:
                if not self.isInterruptionRequested():
                    self.ready.emit(self._channel_id, programmes)
                return
        if not self.isInterruptionRequested():
            self.failed.emit(self._channel_id, "Brak danych EPG")
