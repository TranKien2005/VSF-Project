"""Qt worker that keeps source processing off the GUI thread."""

from __future__ import annotations

from threading import Event

from PySide6.QtCore import QObject, Signal, Slot

from ..automatic_signals import ProcessingCancelled
from ..pipeline import run_pipeline


class ProcessingWorker(QObject):
    """Run one immutable source request and emit data-only progress signals."""

    progress = Signal(object)
    succeeded = Signal(object)
    failed = Signal(str)
    cancelled = Signal()
    finished = Signal()

    def __init__(self, source, config, batch_size: int) -> None:  # type: ignore[no-untyped-def]
        super().__init__()
        if batch_size <= 0:
            raise ValueError("Inference batch size must be positive")
        self.source = source
        self.config = config
        self.batch_size = batch_size
        self._cancel = Event()

    def request_cancel(self) -> None:
        self._cancel.set()

    @Slot()
    def run(self) -> None:
        try:
            targets = run_pipeline(
                self.source,
                self.config,
                on_progress=self.progress.emit,
                is_cancelled=self._cancel.is_set,
                batch_size_override=self.batch_size,
            )
        except ProcessingCancelled:
            self.cancelled.emit()
        except Exception as error:
            self.failed.emit(str(error))
        else:
            self.succeeded.emit(targets)
        finally:
            self.finished.emit()
