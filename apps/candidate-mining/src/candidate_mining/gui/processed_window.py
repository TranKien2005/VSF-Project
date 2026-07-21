"""Desktop shell with shared imported-source selection."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import replace
from pathlib import Path

from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QTabBar,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from ..config import load_config
from ..frame_access import FrameAccess
from ..media_tools import resolve_media_tools
from ..processed_store import (
    ProcessedSource,
    camera_roi_path,
    effective_roi_path,
    import_camera_folder,
    import_video_files,
    list_cameras,
    list_sources,
    resolve_source,
    source_roi_path,
)
from ..processing_progress import cuda_diagnostics
from ..result_store import list_candidates
from ..roi import read_roi, write_roi
from .app import RoiReferenceCanvas, VideoWorkspace


class ProcessedMainWindow(QMainWindow):
    """Global source selection, native preview, ROI configuration, and review."""

    def __init__(self) -> None:
        super().__init__()
        self.config = load_config()
        self.selected_record: ProcessedSource | None = None
        self.selected_candidate = None
        self._selected_source_path: Path | None = None
        self._selected_roi = None
        self._viewer_positions: dict[str, int] = {}
        self._processing_thread: QThread | None = None
        self._processing_worker = None
        self._processing_source_id: str | None = None
        self.setWindowTitle("VSF Candidate Mining")
        self.resize(1480, 920)
        root = QWidget()
        shell = QVBoxLayout(root)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.addWidget(self._header())
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._tree_panel())
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 14, 20, 20)
        self.tabs = QTabBar()
        for name in ("Sources", "ROI Setup", "Process", "Review", "Export"):
            self.tabs.addTab(name)
        self.tabs.currentChanged.connect(self._select_page)
        body_layout.addWidget(self.tabs)
        self.pages = QStackedWidget()
        self.source_preview = VideoWorkspace(editable=False)
        self.source_preview.show_boxes.setChecked(False)
        self.roi_workspace = RoiReferenceCanvas()
        self.roi_workspace.roi_rejected.connect(self._show_roi_rejection)
        self.review_workspace = VideoWorkspace(editable=False)
        for page in (self._sources_page(), self._roi_page(), self._process_page(), self._review_page(), self._export_page()):
            self.pages.addWidget(page)
        body_layout.addWidget(self.pages, 1)
        splitter.addWidget(body)
        splitter.setSizes([320, 1160])
        shell.addWidget(splitter, 1)
        self.setCentralWidget(root)
        self.statusBar().showMessage("Import a source. Technical detections are not final labels.")
        self.refresh_catalog()

    def _header(self) -> QWidget:
        header = QFrame(objectName="navRail")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.addWidget(QLabel("VSF Candidate Mining", objectName="pageTitle"))
        layout.addStretch()
        self.selection_label = QLabel("No imported source selected", objectName="subtitle")
        layout.addWidget(self.selection_label)
        return header

    def _tree_panel(self) -> QWidget:
        panel = QFrame(objectName="sidePanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 14, 12, 12)
        layout.addWidget(QLabel("Source library", objectName="pageTitle"))
        layout.addWidget(QLabel("Unique videos and cameras", objectName="subtitle"))
        self.tree = QTreeView()
        self.tree.setHeaderHidden(True)
        self.tree.clicked.connect(self._select_source)
        layout.addWidget(self.tree, 1)
        refresh = QPushButton("Refresh catalog")
        refresh.clicked.connect(self.refresh_catalog)
        layout.addWidget(refresh)
        return panel

    def _sources_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Sources", objectName="pageTitle"))
        text = "Import unique videos or one outer camera folder. Source files are never copied or changed."
        layout.addWidget(QLabel(text, objectName="notice"))
        actions = QHBoxLayout()
        files = QPushButton("Import unique videos", objectName="primary")
        files.clicked.connect(self.import_files)
        camera = QPushButton("Import camera folder")
        camera.clicked.connect(self.import_camera)
        actions.addWidget(files)
        actions.addWidget(camera)
        actions.addStretch()
        layout.addLayout(actions)
        self.source_detail = QLabel("Select a source from the shared tree to preview it.", objectName="notice")
        self.source_detail.setWordWrap(True)
        layout.addWidget(self.source_detail)
        layout.addWidget(self.source_preview, 1)
        return page

    def _roi_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("ROI Setup", objectName="pageTitle"))
        self.roi_notice = QLabel(
            "Draw one freehand stroke. Endpoint tangents extend to the frame; the smaller closed partition is the track ROI.",
            objectName="notice",
        )
        self.roi_notice.setWordWrap(True)
        layout.addWidget(self.roi_notice)
        controls = QHBoxLayout()
        self.roi_scope = QComboBox()
        self.roi_scope.addItem("Source override", "source")
        self.roi_scope.addItem("Camera shared default", "camera")
        controls.addWidget(QLabel("Save scope"))
        controls.addWidget(self.roi_scope)
        self.roi_draw = QPushButton("Draw freehand ROI", objectName="primary")
        self.roi_draw.setCheckable(True)
        self.roi_draw.toggled.connect(self.roi_workspace.set_drawing)
        self.roi_workspace.drawing_changed.connect(self._set_roi_draw_checked)
        clear = QPushButton("Clear ROI")
        clear.clicked.connect(self.roi_workspace.clear_roi)
        save = QPushButton("Save track ROI", objectName="primary")
        save.clicked.connect(self.save_roi)
        controls.addWidget(self.roi_draw)
        controls.addWidget(clear)
        controls.addWidget(save)
        controls.addStretch()
        layout.addLayout(controls)
        layout.addWidget(self.roi_workspace, 1)
        return page

    def _configured_batch_size(self) -> int:
        provider = (
            self.config.providers.person_rtdetr
            if self.config.providers.person_rtdetr["enabled"]
            else self.config.providers.person_yolo
        )
        return int(provider["batch_size"])

    def _process_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Process", objectName="pageTitle"))
        text = "A saved track ROI is required. Only in-ROI footpoints produce person_detected candidates."
        layout.addWidget(QLabel(text, objectName="notice"))
        self.process_state = QLabel("Select an imported source.", objectName="subtitle")
        self.process_state.setWordWrap(True)
        layout.addWidget(self.process_state)
        self.process_progress = QProgressBar()
        self.process_progress.setRange(0, 100)
        layout.addWidget(self.process_progress)
        self.process_diagnostics = QLabel(
            f"RT-DETR-L · image 960 · configured batch {self._configured_batch_size()} · {cuda_diagnostics()}",
            objectName="subtitle",
        )
        self.process_diagnostics.setWordWrap(True)
        layout.addWidget(self.process_diagnostics)
        batch_controls = QHBoxLayout()
        batch_controls.addWidget(QLabel("Inference batch"))
        self.batch_size = QSpinBox()
        self.batch_size.setRange(1, 64)
        self.batch_size.setValue(self._configured_batch_size())
        self.batch_size.setToolTip("Frames inferred together for this run only. Lower it if CUDA runs out of memory.")
        batch_controls.addWidget(self.batch_size)
        batch_controls.addWidget(QLabel("Per-run only; does not change configuration.", objectName="subtitle"))
        batch_controls.addStretch()
        layout.addLayout(batch_controls)
        controls = QHBoxLayout()
        self.process_run = QPushButton("Run detection", objectName="primary")
        self.process_run.clicked.connect(self.run_selected_source)
        self.process_cancel = QPushButton("Cancel")
        self.process_cancel.clicked.connect(self.cancel_processing)
        self.process_cancel.setEnabled(False)
        controls.addWidget(self.process_run)
        controls.addWidget(self.process_cancel)
        controls.addStretch()
        layout.addLayout(controls)
        layout.addStretch()
        return page

    def _review_page(self) -> QWidget:
        page = QWidget()
        layout = QHBoxLayout(page)
        browser = QFrame(objectName="inspector")
        browser_layout = QVBoxLayout(browser)
        browser_layout.addWidget(QLabel("Person-detected candidates", objectName="pageTitle"))
        self.candidate_tree = QTreeView()
        self.candidate_tree.setHeaderHidden(True)
        self.candidate_tree.clicked.connect(self.select_candidate)
        browser_layout.addWidget(self.candidate_tree, 1)
        layout.addWidget(browser)
        content = QVBoxLayout()
        content.addWidget(QLabel("Review", objectName="pageTitle"))
        self.review_notice = QLabel("Select an in-ROI person_detected candidate.", objectName="notice")
        content.addWidget(self.review_notice)
        content.addWidget(self.review_workspace, 1)
        layout.addLayout(content, 1)
        return page

    def _export_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Export", objectName="pageTitle"))
        self.export_notice = QLabel("Select a candidate in Review. Export remains explicit.", objectName="notice")
        layout.addWidget(self.export_notice)
        layout.addStretch()
        return page

    def _select_page(self, index: int) -> None:
        self._close_inactive_viewers(index)
        self.pages.setCurrentIndex(index)
        self._load_viewer_for_page(index)
        if index == 3:
            self.refresh_candidates()

    def import_files(self) -> None:
        values, _ = QFileDialog.getOpenFileNames(
            self, "Import unique videos", "", "Videos (*.mp4 *.avi *.mov *.mkv *.m4v *.webm)"
        )
        if not values:
            return
        records, failures = import_video_files(
            [Path(value) for value in values], self.config.paths.processed_dir, resolve_media_tools(self.config.paths.ffmpeg_dir)
        )
        self._report_import(f"Imported or reused {len(records)} unique videos.", failures)

    def import_camera(self) -> None:
        value = QFileDialog.getExistingDirectory(self, "Import outer camera folder")
        if not value:
            return
        camera, records, failures = import_camera_folder(
            Path(value), self.config.paths.processed_dir, resolve_media_tools(self.config.paths.ffmpeg_dir)
        )
        self._report_import(f"Imported or reused {len(records)} videos for camera {camera.name}.", failures)

    def _report_import(self, message: str, failures: list[str]) -> None:
        self.refresh_catalog()
        self.statusBar().showMessage(message if not failures else f"{message} {len(failures)} failed.")

    def refresh_catalog(self) -> None:
        model = QStandardItemModel(self.tree)
        unique, cameras = QStandardItem("Unique videos"), QStandardItem("Cameras")
        grouped: dict[str, list[ProcessedSource]] = defaultdict(list)
        for record in list_sources(self.config.paths.processed_dir):
            if record.camera_id:
                grouped[record.camera_id].append(record)
            else:
                unique.appendRow(self._source_item(record))
        for camera in list_cameras(self.config.paths.processed_dir):
            item = QStandardItem(camera.name)
            item.appendRow(QStandardItem("Camera metadata / shared ROI"))
            for record in grouped.pop(camera.camera_id, []):
                item.appendRow(self._source_item(record))
            cameras.appendRow(item)
        model.appendRow(unique)
        model.appendRow(cameras)
        self.tree.setModel(model)
        self.tree.expandAll()

    @staticmethod
    def _source_item(record: ProcessedSource) -> QStandardItem:
        item = QStandardItem(record.filename)
        item.setData(record.source_id, Qt.UserRole)
        return item

    def _select_source(self, index) -> None:  # type: ignore[no-untyped-def]
        source_id = index.data(Qt.UserRole)
        record = {item.source_id: item for item in list_sources(self.config.paths.processed_dir)}.get(str(source_id))
        if not record:
            return
        try:
            source = resolve_source(record)
        except (FileNotFoundError, ValueError) as error:
            self.statusBar().showMessage(str(error))
            return
        self._close_all_viewers()
        self.selected_record, self._selected_source_path = record, source
        self._viewer_positions.clear()
        roi_path, scope = effective_roi_path(self.config.paths.processed_dir, record)
        try:
            self._selected_roi = read_roi(roi_path) if roi_path else None
        except ValueError:
            self._selected_roi = None
        self.selection_label.setText(f"{record.filename} · {record.duration_seconds:.1f}s")
        self.source_detail.setText(f"{record.filename}\n{source}\nSHA-256: {record.sha256}")
        self.roi_notice.setText(
            "No ROI saved. Draw and save one freehand track ROI before processing."
            if not self._selected_roi
            else f"Effective {scope} freehand ROI revision {self._selected_roi.revision}."
        )
        self.process_state.setText(f"Selected source: {record.filename}")
        self._load_viewer_for_page(self.tabs.currentIndex())
        self.refresh_candidates()

    def _viewer_for_page(self, page_index: int) -> tuple[str, VideoWorkspace] | None:
        return {0: ("source", self.source_preview), 3: ("review", self.review_workspace)}.get(page_index)

    def _load_viewer_for_page(self, page_index: int) -> None:
        if page_index == 1:
            self._load_roi_reference()
            return
        entry = self._viewer_for_page(page_index)
        if entry and self._selected_source_path:
            key, viewer = entry
            if not viewer.is_loaded:
                viewer.open_source(
                    self._selected_source_path, roi=self._selected_roi, initial_frame_index=self._viewer_positions.get(key)
                )

    def _load_roi_reference(self) -> None:
        if not self._selected_source_path or self.roi_workspace.is_loaded:
            return
        try:
            access = FrameAccess(self._selected_source_path)
            try:
                frame = access.read_at_time(0.0)
            finally:
                access.close()
        except (RuntimeError, EOFError, ValueError) as error:
            self.roi_notice.setText(f"Could not load ROI reference frame: {error}")
            self.statusBar().showMessage(self.roi_notice.text())
            return
        self.roi_workspace.load_reference(self._selected_source_path, frame, self._selected_roi)
        self.roi_notice.setText(
            "Draw one freehand stroke on this reference image. Endpoint tangents extend to the frame; "
            "the smaller closed partition is the track ROI."
        )

    def _close_inactive_viewers(self, active_page: int) -> None:
        active = self._viewer_for_page(active_page)
        active_key = active[0] if active else None
        for key, viewer in (("source", self.source_preview), ("review", self.review_workspace)):
            if key != active_key:
                position = viewer.close_source()
                if position is not None:
                    self._viewer_positions[key] = position

    def _close_all_viewers(self) -> None:
        for key, viewer in (("source", self.source_preview), ("review", self.review_workspace)):
            position = viewer.close_source()
            if position is not None:
                self._viewer_positions[key] = position
        self.roi_workspace.clear_reference()
        self.roi_draw.setChecked(False)

    def save_roi(self) -> None:
        if not self.selected_record or not self.roi_workspace.roi:
            QMessageBox.warning(self, "Track ROI required", "Select a source and draw one valid freehand stroke first.")
            return
        scope = str(self.roi_scope.currentData())
        if scope == "camera" and not self.selected_record.camera_id:
            QMessageBox.warning(self, "Camera required", "An independent video cannot save a camera-shared ROI.")
            return
        roi = replace(self.roi_workspace.roi, reference_source_sha256=self.selected_record.sha256)
        target = (
            camera_roi_path(self.config.paths.processed_dir, self.selected_record.camera_id)
            if scope == "camera"
            else source_roi_path(self.config.paths.processed_dir, self.selected_record)
        )
        write_roi(roi, target)
        self._selected_roi = roi
        for viewer in (self.source_preview, self.roi_workspace, self.review_workspace):
            viewer.set_roi(roi)
        self.statusBar().showMessage(f"Saved {scope} freehand track ROI.")

    def _set_roi_draw_checked(self, active: bool) -> None:
        self.roi_draw.blockSignals(True)
        self.roi_draw.setChecked(active)
        self.roi_draw.blockSignals(False)

    def _show_roi_rejection(self, message: str) -> None:
        self.roi_notice.setText(message)
        self.statusBar().showMessage(message)

    def run_selected_source(self) -> None:
        if not self.selected_record or self._processing_thread:
            return
        if not self._selected_roi:
            self.process_state.setText("Process blocked: draw and save a valid freehand track ROI first.")
            return
        try:
            source = resolve_source(self.selected_record)
        except (FileNotFoundError, ValueError) as error:
            self.process_state.setText(f"Processing unavailable: {error}")
            return
        from .processing_worker import ProcessingWorker

        selected_batch = self.batch_size.value()
        self._processing_source_id = self.selected_record.source_id
        self._processing_thread = QThread(self)
        self._processing_worker = ProcessingWorker(source, self.config, selected_batch)
        self._processing_worker.moveToThread(self._processing_thread)
        self._processing_thread.started.connect(self._processing_worker.run)
        self._processing_worker.progress.connect(self._update_processing_progress)
        self._processing_worker.succeeded.connect(self._processing_succeeded)
        self._processing_worker.failed.connect(self._processing_failed)
        self._processing_worker.cancelled.connect(self._processing_cancelled)
        self._processing_worker.finished.connect(self._processing_thread.quit)
        self._processing_worker.finished.connect(self._processing_worker.deleteLater)
        self._processing_thread.finished.connect(self._processing_finished)
        self._processing_thread.finished.connect(self._processing_thread.deleteLater)
        self.process_run.setEnabled(False)
        self.batch_size.setEnabled(False)
        self.process_cancel.setEnabled(True)
        self.tree.setEnabled(False)
        self.process_progress.setRange(0, 0)
        self.process_state.setText(f"Preparing processing run with batch {selected_batch}…")
        self._processing_thread.start()

    def cancel_processing(self) -> None:
        if self._processing_worker:
            self._processing_worker.request_cancel()
            self.process_cancel.setEnabled(False)
            self.process_state.setText("Cancelling after the current safe processing step…")

    def _update_processing_progress(self, progress) -> None:  # type: ignore[no-untyped-def]
        percent = progress.percent
        self.process_progress.setRange(0, 0 if percent is None else 100)
        if percent is not None:
            self.process_progress.setValue(percent)
        eta = "ETA calculating…" if progress.eta_seconds is None else f"ETA {progress.eta_seconds:.0f}s"
        self.process_state.setText(f"{progress.phase}: {percent if percent is not None else '…'}% · {eta} · {progress.message}")
        self.process_diagnostics.setText(
            f"Device: {progress.device} · batch {progress.effective_batch_size}/{progress.configured_batch_size}"
        )

    def _processing_succeeded(self, targets) -> None:  # type: ignore[no-untyped-def]
        self.process_progress.setRange(0, 100)
        self.process_progress.setValue(100)
        self.process_state.setText(f"Processing complete: {len(targets)} person_detected candidates written.")
        self.refresh_candidates()

    def _processing_failed(self, message: str) -> None:
        self.process_state.setText(f"Processing failed: {message}")
        QMessageBox.warning(self, "Processing failed", message)

    def _processing_cancelled(self) -> None:
        self.process_state.setText("Processing cancelled; no new results published.")

    def _processing_finished(self) -> None:
        self.process_run.setEnabled(True)
        self.batch_size.setEnabled(True)
        self.process_cancel.setEnabled(False)
        self.tree.setEnabled(True)
        self._processing_worker = None
        self._processing_thread = None
        self._processing_source_id = None

    def refresh_candidates(self) -> None:
        candidates = (
            list_candidates(self.config.paths.results_dir, self.selected_record.source_id) if self.selected_record else []
        )
        candidates = [candidate for candidate in candidates if candidate.category == "person_detected"]
        model = QStandardItemModel(self.candidate_tree)
        for candidate in candidates:
            item = QStandardItem(f"person_detected · {candidate.context_start_sec:.1f}–{candidate.context_end_sec:.1f}s")
            item.setData(candidate, Qt.UserRole)
            model.appendRow(item)
        self.candidate_tree.setModel(model)
        self.review_notice.setText(
            f"{len(candidates)} in-ROI person_detected candidate(s)." if self.selected_record else "Select a source first."
        )

    def select_candidate(self, index) -> None:  # type: ignore[no-untyped-def]
        candidate = index.data(Qt.UserRole)
        if not candidate:
            return
        if not self.selected_record:
            return
        self.tabs.setCurrentIndex(3)
        self._load_viewer_for_page(3)
        self.selected_candidate = candidate
        self.review_workspace.set_review_context(
            detections=candidate.detections,
            source_fps=self.selected_record.fps,
            frame_width=self.selected_record.frame_width,
            frame_height=self.selected_record.frame_height,
            start_sec=candidate.context_start_sec,
            end_sec=candidate.context_end_sec,
        )
        self.review_notice.setText(
            f"Technical evidence context: {candidate.context_start_sec:.1f}–{candidate.context_end_sec:.1f}s. "
            "ROI and boxes are not final labels."
        )
        self.export_notice.setText(
            f"Selected person_detected context: {candidate.context_start_sec:.1f}–{candidate.context_end_sec:.1f}s."
        )

    def closeEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        if self._processing_worker:
            self._processing_worker.request_cancel()
        self._close_all_viewers()
        event.accept()
