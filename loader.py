"""Wątek pobierający bazę kanałów bez blokowania interfejsu."""

from PySide6.QtCore import QThread, Signal

from omnity.core.catalog import Catalog, CatalogError


class CatalogLoader(QThread):
    progress = Signal(str)
    loaded = Signal(object)
    failed = Signal(str)

    def __init__(self, force: bool = False, parent=None):
        super().__init__(parent)
        self._force = force

    def _should_stop(self) -> bool:
        return self.isInterruptionRequested()

    def run(self):
        try:
            catalog = Catalog()
            catalog.load(
                force=self._force,
                progress=self.progress.emit,
                should_stop=self._should_stop,
            )
        except CatalogError as exc:
            if not self.isInterruptionRequested():
                self.failed.emit(str(exc))
            return
        except Exception as exc:  # noqa: BLE001
            if not self.isInterruptionRequested():
                self.failed.emit(str(exc))
            return

        if self.isInterruptionRequested():
            return
        self.loaded.emit(catalog)
