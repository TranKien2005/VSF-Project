"""Qt worker that runs camera/file imports off the GUI thread."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from ..media_tools import MediaTools
from ..processed_store import CameraRecord, import_camera_folder, import_video_files


class ImportWorker(QObject):
    """Run one import operation and emit progress signals."""

    progress = Signal(int, int, str)  # current, total, filename
    succeeded = Signal(list, list, list)  # cameras, records, failures
    finished = Signal()

    def __init__(
        self,
        *,
        paths: list[Path] | None = None,
        folder: Path | None = None,
        processed_dir: Path,
        tools: MediaTools,
    ) -> None:
        super().__init__()
        self._paths = paths
        self._folder = folder
        self._processed_dir = processed_dir
        self._tools = tools

    def _report_progress(self, current: int, total: int, filename: str) -> None:
        self.progress.emit(current, total, filename)

    @Slot()
    def run(self) -> None:
        try:
            if self._folder:
                cameras, records, failures = import_camera_folder(
                    self._folder,
                    self._processed_dir,
                    self._tools,
                    on_progress=self._report_progress,
                )
            elif self._paths:
                cameras: list[CameraRecord] = []
                records, failures = import_video_files(
                    self._paths,
                    self._processed_dir,
                    self._tools,
                    on_progress=self._report_progress,
                )
            else:
                cameras, records, failures = [], [], []
            self.succeeded.emit(cameras, records, failures)
        except Exception as error:
            self.succeeded.emit([], [], [str(error)])
        finally:
            self.finished.emit()
