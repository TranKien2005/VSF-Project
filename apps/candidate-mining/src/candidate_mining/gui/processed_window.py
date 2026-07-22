"""Desktop shell with shared imported-source selection."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import replace
from pathlib import Path

from PySide6.QtCore import QItemSelectionModel, QModelIndex, Qt, QThread
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
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
    list_cameras,
    list_sources,
    resolve_source,
    source_roi_path,
)
from ..processing_progress import cuda_diagnostics
from ..result_store import (
    clear_all_results,
    clear_camera_results,
    clear_source_results,
    has_source_results,
    list_candidates,
)
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
        self._import_thread: QThread | None = None
        self._import_worker = None
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
        clear = QPushButton("Clear ROI", objectName="danger")
        clear.clicked.connect(self.roi_workspace.clear_roi)
        save = QPushButton("Save track ROI", objectName="primary")
        save.clicked.connect(self.save_roi)
        flip = QPushButton("Flip ROI region")
        flip.setToolTip("Toggle selection to the opposite side of the freehand stroke")
        flip.clicked.connect(self.flip_current_roi)
        controls.addWidget(self.roi_draw)
        controls.addWidget(flip)
        controls.addWidget(clear)
        controls.addWidget(save)
        controls.addStretch()
        layout.addLayout(controls)
        layout.addWidget(self.roi_workspace, 1)
        return page

    def flip_current_roi(self) -> None:
        if self.roi_workspace.roi:
            self.roi_workspace.flip_roi()
            self._selected_roi = self.roi_workspace.roi
            self.sources_workspace.set_roi(self._selected_roi)
            self.review_workspace.set_roi(self._selected_roi)
            self.roi_notice.setText("Flipped ROI tracking region side.")

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
        self.batch_size.setAccelerated(True)
        self.batch_size.setFixedWidth(90)
        self.batch_size.setToolTip("Frames inferred together for this run. Type, click arrows, or pick a preset.")
        batch_controls.addWidget(self.batch_size)
        batch_controls.addWidget(QLabel("Presets:"))
        self.preset_buttons: list[QPushButton] = []
        for preset_val in (1, 4, 8, 16, 32):
            btn = QPushButton(str(preset_val), objectName="preset")
            btn.setToolTip(f"Set batch size to {preset_val}")
            btn.clicked.connect(lambda _, v=preset_val: self.batch_size.setValue(v))
            batch_controls.addWidget(btn)
            self.preset_buttons.append(btn)
        batch_controls.addWidget(QLabel("Per-run only", objectName="subtitle"))
        batch_controls.addStretch()
        layout.addLayout(batch_controls)

        fps_controls = QHBoxLayout()
        fps_controls.addWidget(QLabel("Sample FPS"))
        self.sample_fps_spin = QDoubleSpinBox()
        self.sample_fps_spin.setRange(0.5, 30.0)
        self.sample_fps_spin.setSingleStep(0.5)
        self.sample_fps_spin.setValue(float(self.config.pipeline.sample_fps))
        self.sample_fps_spin.setFixedWidth(90)
        self.sample_fps_spin.setToolTip("Frame sampling rate per second. Lower FPS (e.g. 2.0) speeds up processing.")
        fps_controls.addWidget(self.sample_fps_spin)
        fps_controls.addWidget(QLabel("FPS Presets:"))
        self.fps_preset_buttons: list[QPushButton] = []
        for fps_val in (1.0, 2.0, 4.0, 6.0, 8.0):
            btn = QPushButton(f"{fps_val:.1f}", objectName="preset")
            btn.setToolTip(f"Set sampling rate to {fps_val:.1f} FPS")
            btn.clicked.connect(lambda _, v=fps_val: self.sample_fps_spin.setValue(v))
            fps_controls.addWidget(btn)
            self.fps_preset_buttons.append(btn)
        fps_controls.addStretch()
        layout.addLayout(fps_controls)
        controls = QHBoxLayout()
        self.process_run = QPushButton("Run selected source", objectName="primary")
        self.process_run.clicked.connect(self.run_selected_source)

        self.process_run_all = QPushButton("Run all sources (Batch)")
        self.process_run_all.setToolTip("Process all imported sources that have a saved Track ROI")
        self.process_run_all.clicked.connect(self.run_all_sources)

        self.clear_selection_btn = QPushButton("Clear selection results")
        self.clear_selection_btn.setToolTip("Clear stored results for the currently selected video or camera")
        self.clear_selection_btn.clicked.connect(self.clear_selected_results)

        self.clear_all_btn = QPushButton("Clear ALL results", objectName="danger")
        self.clear_all_btn.setToolTip("Clear stored detection results across ALL sources and cameras")
        self.clear_all_btn.clicked.connect(self.clear_all_results_confirm)

        self.process_cancel = QPushButton("Cancel", objectName="danger")
        self.process_cancel.clicked.connect(self.cancel_processing)
        self.process_cancel.setEnabled(False)

        controls.addWidget(self.process_run)
        controls.addWidget(self.process_run_all)
        controls.addWidget(self.clear_selection_btn)
        controls.addWidget(self.clear_all_btn)
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

        self.export_card = QLabel("No candidate selected for export.", objectName="subtitle")
        self.export_card.setWordWrap(True)
        layout.addWidget(self.export_card)

        options = QHBoxLayout()
        self.export_overlay_checkbox = QCheckBox("Render technical bounding box overlays in exported MP4")
        self.export_overlay_checkbox.setChecked(True)
        options.addWidget(self.export_overlay_checkbox)
        options.addStretch()
        layout.addLayout(options)

        actions = QHBoxLayout()
        self.export_btn = QPushButton("Export Subvideo MP4", objectName="primary")
        self.export_btn.clicked.connect(self.do_export_candidate)
        self.export_btn.setEnabled(False)
        actions.addWidget(self.export_btn)
        actions.addStretch()
        layout.addLayout(actions)

        self.export_status = QLabel("", objectName="subtitle")
        self.export_status.setWordWrap(True)
        layout.addWidget(self.export_status)

        layout.addStretch()
        return page

    def do_export_candidate(self) -> None:
        if not self.selected_candidate or not self.selected_record:
            QMessageBox.warning(self, "Export unavailable", "Please select a candidate in the Review tab first.")
            return
        try:
            source = resolve_source(self.selected_record)
        except (FileNotFoundError, ValueError) as error:
            QMessageBox.warning(self, "Export unavailable", str(error))
            return
        default_name = f"{self.selected_candidate.candidate_id}.mp4"
        default_path = str(self.config.paths.results_dir / default_name)
        target_path, _ = QFileDialog.getSaveFileName(
            self, "Save Candidate Subvideo MP4", default_path, "MP4 Video (*.mp4)"
        )
        if not target_path:
            return
        dest = Path(target_path)
        from .exporter import export_clip, export_clip_with_bboxes
        from .media_tools import resolve_media_tools

        media = resolve_media_tools(self.config.paths.ffmpeg_dir)
        self.export_status.setText(f"Exporting subvideo clip to {dest.name}…")
        self.export_btn.setEnabled(False)
        QApplication.processEvents()
        try:
            if self.export_overlay_checkbox.isChecked():
                from .result_store import person_detection_store_for_source
                store = person_detection_store_for_source(self.config.paths.results_dir, self.selected_record.source_id)
                if store:
                    export_clip_with_bboxes(
                        source,
                        self.selected_candidate.context_start_sec,
                        self.selected_candidate.context_end_sec,
                        dest,
                        store,
                        ffmpeg=media.ffmpeg,
                    )
                else:
                    export_clip(
                        source,
                        self.selected_candidate.context_start_sec,
                        self.selected_candidate.context_end_sec,
                        dest,
                        ffmpeg=media.ffmpeg,
                    )
            else:
                export_clip(
                    source,
                    self.selected_candidate.context_start_sec,
                    self.selected_candidate.context_end_sec,
                    dest,
                    ffmpeg=media.ffmpeg,
                )
            self.export_status.setText(f"Successfully exported candidate subvideo clip to:\n{dest}")
            QMessageBox.information(self, "Export Complete", f"Subvideo MP4 saved successfully:\n{dest}")
        except Exception as error:
            self.export_status.setText(f"Export failed: {error}")
            QMessageBox.critical(self, "Export Failed", f"Could not export candidate clip:\n{error}")
        finally:
            self.export_btn.setEnabled(True)

    def _select_page(self, index: int) -> None:
        self._close_inactive_viewers(index)
        self.pages.setCurrentIndex(index)
        self._load_viewer_for_page(index)

    def import_files(self) -> None:
        values, _ = QFileDialog.getOpenFileNames(
            self, "Import unique videos", "", "Videos (*.mp4 *.avi *.mov *.mkv *.m4v *.webm)"
        )
        if not values:
            return
        self._start_import(paths=[Path(v) for v in values])

    def import_camera(self) -> None:
        value = QFileDialog.getExistingDirectory(self, "Import outer camera folder")
        if not value:
            return
        self._start_import(folder=Path(value))

    def _start_import(self, *, paths: list[Path] | None = None, folder: Path | None = None) -> None:
        from .import_worker import ImportWorker

        tools = resolve_media_tools(self.config.paths.ffmpeg_dir)
        self._import_thread = QThread(self)
        self._import_worker = ImportWorker(
            paths=paths, folder=folder, processed_dir=self.config.paths.processed_dir, tools=tools
        )
        self._import_worker.moveToThread(self._import_thread)
        self._import_thread.started.connect(self._import_worker.run)
        self._import_worker.progress.connect(self._update_import_progress)
        self._import_worker.succeeded.connect(self._import_completed)
        self._import_worker.finished.connect(self._import_thread.quit)
        self._import_worker.finished.connect(self._import_worker.deleteLater)
        self._import_thread.finished.connect(self._import_thread.deleteLater)
        self._import_thread.finished.connect(self._import_cleanup)
        self.tree.setEnabled(False)
        self.statusBar().showMessage("Importing…")
        self._import_thread.start()

    def _update_import_progress(self, current: int, total: int, filename: str) -> None:
        self.statusBar().showMessage(f"Importing [{current}/{total}]: {filename}")

    def _import_completed(self, cameras, records, failures) -> None:  # type: ignore[no-untyped-def]
        sel_id = records[0].source_id if records else None
        label = f"camera(s) {', '.join(c.name for c in cameras)}" if cameras else "unique videos"
        self._report_import(f"Imported or reused {len(records)} videos as {label}.", failures, select_source_id=sel_id)

    def _import_cleanup(self) -> None:
        self.tree.setEnabled(True)
        self._import_worker = None
        self._import_thread = None

    def _report_import(self, message: str, failures: list[str], select_source_id: str | None = None) -> None:
        self.refresh_catalog(select_source_id=select_source_id)
        self.statusBar().showMessage(message if not failures else f"{message} {len(failures)} failed.")

    def refresh_catalog(self, select_source_id: str | None = None) -> None:
        target_id = select_source_id or (self.selected_record.source_id if self.selected_record else None)
        model = QStandardItemModel(self.tree)
        unique, cameras = QStandardItem("Unique videos"), QStandardItem("Cameras")
        unique.setData("heading", Qt.UserRole + 1)
        cameras.setData("heading", Qt.UserRole + 1)
        grouped: dict[str, list[ProcessedSource]] = defaultdict(list)
        for record in list_sources(self.config.paths.processed_dir):
            if record.camera_id:
                grouped[record.camera_id].append(record)
            else:
                unique.appendRow(self._source_item(record))
        for camera in list_cameras(self.config.paths.processed_dir):
            item = QStandardItem(camera.name)
            item.setData(camera.camera_id, Qt.UserRole)
            item.setData("camera", Qt.UserRole + 1)

            for record in grouped.pop(camera.camera_id, []):
                item.appendRow(self._source_item(record))
            cameras.appendRow(item)
        model.appendRow(unique)
        model.appendRow(cameras)
        self.tree.setModel(model)
        self.tree.expandAll()

        # Connect selection model to load source on selection change
        if self.tree.selectionModel():
            self.tree.selectionModel().selectionChanged.connect(self._on_tree_selection_changed)

        # Auto-select target source or first available source
        target_index: QModelIndex | None = None
        if target_id:
            for r in range(model.rowCount()):
                found = self._find_source_index(model.item(r), target_id)
                if found:
                    target_index = found
                    break
        if not target_index:
            for r in range(model.rowCount()):
                found = self._find_first_source_index(model.item(r))
                if found:
                    target_index = found
                    break

        if target_index and self.tree.selectionModel():
            self.tree.selectionModel().select(target_index, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
            self._select_source(target_index)

    def _on_tree_selection_changed(self, selected, deselected) -> None:  # type: ignore[no-untyped-def]
        indexes = selected.indexes()
        if indexes:
            self._select_source(indexes[0])

    def _find_source_index(self, parent_item: QStandardItem, source_id: str) -> QModelIndex | None:
        for r in range(parent_item.rowCount()):
            child = parent_item.child(r)
            if child:
                if child.data(Qt.UserRole + 1) == "video" and child.data(Qt.UserRole) == source_id:
                    return child.index()
                found = self._find_source_index(child, source_id)
                if found:
                    return found
        return None

    def _find_first_source_index(self, parent_item: QStandardItem) -> QModelIndex | None:
        for r in range(parent_item.rowCount()):
            child = parent_item.child(r)
            if child:
                if child.data(Qt.UserRole + 1) == "video":
                    return child.index()
                found = self._find_first_source_index(child)
                if found:
                    return found
        return None

    @staticmethod
    def _source_item(record: ProcessedSource) -> QStandardItem:
        item = QStandardItem(record.filename)
        item.setData(record.source_id, Qt.UserRole)
        item.setData("video", Qt.UserRole + 1)
        return item

    def _select_source(self, index) -> None:  # type: ignore[no-untyped-def]
        role_type = index.data(Qt.UserRole + 1)
        user_data = index.data(Qt.UserRole)

        if role_type in {"camera", "camera_meta"}:
            camera_id = str(user_data)
            self._close_all_viewers()
            self.selected_camera_id = camera_id
            self._viewer_positions.clear()

            camera_records = [
                record for record in list_sources(self.config.paths.processed_dir) if record.camera_id == camera_id
            ]
            if camera_records:
                self.selected_record = camera_records[0]
                try:
                    self._selected_source_path = resolve_source(self.selected_record)
                except (FileNotFoundError, ValueError):
                    self._selected_source_path = None
            else:
                self.selected_record = None
                self._selected_source_path = None

            roi_path = camera_roi_path(self.config.paths.processed_dir, camera_id)
            try:
                self._selected_roi = read_roi(roi_path) if roi_path.exists() else None
            except ValueError:
                self._selected_roi = None

            self.roi_scope.setCurrentIndex(1)

            self.selection_label.setText(f"Camera: {camera_id} · Shared ROI")
            self.source_detail.setText(
                f"Camera ID: {camera_id}\nScope: Shared default ROI for all videos in this camera."
            )
            self.roi_notice.setText(
                "No shared camera ROI saved."
                if not self._selected_roi
                else f"Shared camera freehand ROI revision {self._selected_roi.revision}."
            )
            self.process_state.setText(f"Selected camera: {camera_id}")
            self._load_viewer_for_page(self.tabs.currentIndex())
            self.refresh_candidates()
            return

        if role_type != "video":
            self._close_all_viewers()
            self.selected_record = None
            self.selected_camera_id = None
            self._selected_source_path = None
            self.selection_label.setText("No imported source selected")
            self.source_detail.setText("Select a source from the shared tree to preview it.")
            self.process_state.setText("Select an imported source.")
            self.refresh_candidates()
            return

        record = {item.source_id: item for item in list_sources(self.config.paths.processed_dir)}.get(str(user_data))
        if not record:
            return
        try:
            source = resolve_source(record)
        except (FileNotFoundError, ValueError) as error:
            self.statusBar().showMessage(str(error))
            return
        self._close_all_viewers()
        self.selected_record, self._selected_source_path = record, source
        self.selected_camera_id = record.camera_id
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
        if not self.roi_workspace.roi:
            QMessageBox.warning(self, "Track ROI required", "Draw one valid freehand stroke first.")
            return
        scope = str(self.roi_scope.currentData())
        camera_id = getattr(self, "selected_camera_id", None) or (
            self.selected_record.camera_id if self.selected_record else None
        )
        if scope == "camera" and not camera_id:
            QMessageBox.warning(self, "Camera required", "An independent video cannot save a camera-shared ROI.")
            return
        if scope == "source" and not self.selected_record:
            QMessageBox.warning(self, "Source required", "Select a specific video to save a source override ROI.")
            return
        sha = self.selected_record.sha256 if self.selected_record else ""
        roi = replace(self.roi_workspace.roi, reference_source_sha256=sha)
        target = (
            camera_roi_path(self.config.paths.processed_dir, camera_id)
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
        if not self.selected_record:
            self.process_state.setText("Process blocked: select a registered source.")
            return
        effective_roi, _ = effective_roi_path(self.config.paths.processed_dir, self.selected_record)
        if not effective_roi:
            self.process_state.setText("Process blocked: draw and save a valid freehand track ROI first.")
            return
        try:
            source = resolve_source(self.selected_record)
        except (FileNotFoundError, ValueError) as error:
            self.process_state.setText(f"Processing unavailable: {error}")
            return

        if has_source_results(
            self.config.paths.results_dir, self.selected_record.source_id, self.selected_record.camera_id
        ):
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Existing Results Found")
            msg_box.setText(f"Source '{self.selected_record.filename}' already has saved detection results.")
            msg_box.setInformativeText("Do you want to Resume (skip) or Re-run (overwrite)?")
            resume_btn = msg_box.addButton("Resume (Skip)", QMessageBox.AcceptRole)
            msg_box.addButton("Re-run All", QMessageBox.DestructiveRole)
            cancel_btn = msg_box.addButton("Cancel", QMessageBox.RejectRole)
            msg_box.exec()
            clicked = msg_box.clickedButton()
            if clicked == cancel_btn:
                return
            if clicked == resume_btn:
                self.process_state.setText("Source already processed; skipped.")
                return
            clear_source_results(
                self.config.paths.results_dir, self.selected_record.source_id, self.selected_record.camera_id
            )

        self._batch_queue = [(self.selected_record, source)]
        self._total_batch_count = 1
        self._completed_batch_count = 0
        self._start_next_in_batch()

    def run_all_sources(self) -> None:
        all_records = list_sources(self.config.paths.processed_dir)
        ready_sources: list[tuple[ProcessedSource, Path]] = []
        for rec in all_records:
            roi_path, _ = effective_roi_path(self.config.paths.processed_dir, rec)
            if roi_path:
                try:
                    src_path = resolve_source(rec)
                    ready_sources.append((rec, src_path))
                except (FileNotFoundError, ValueError):
                    continue
        if not ready_sources:
            QMessageBox.warning(self, "No sources ready", "No imported sources have a valid saved Track ROI.")
            return

        sources_with_results = [
            (rec, path)
            for rec, path in ready_sources
            if has_source_results(self.config.paths.results_dir, rec.source_id, rec.camera_id)
        ]

        queue = list(ready_sources)
        if sources_with_results:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Existing Results Found")
            msg_box.setText(
                f"{len(sources_with_results)} of {len(ready_sources)} source(s) already have saved detection results."
            )
            msg_box.setInformativeText(
                "• Resume (Skip): Only process sources that have NOT been run yet.\n"
                "• Re-run All: Overwrite existing results and re-process all sources."
            )
            resume_btn = msg_box.addButton("Resume (Skip processed)", QMessageBox.AcceptRole)
            rerun_btn = msg_box.addButton("Re-run All", QMessageBox.DestructiveRole)
            cancel_btn = msg_box.addButton("Cancel", QMessageBox.RejectRole)
            msg_box.exec()
            clicked = msg_box.clickedButton()
            if clicked == cancel_btn:
                return
            if clicked == resume_btn:
                queue = [item for item in ready_sources if item not in sources_with_results]
                if not queue:
                    QMessageBox.information(
                        self, "All Processed", "All sources already have results. Nothing new to run."
                    )
                    return
            elif clicked == rerun_btn:
                for rec, _ in sources_with_results:
                    clear_source_results(self.config.paths.results_dir, rec.source_id, rec.camera_id)

        self._batch_queue = queue
        self._total_batch_count = len(queue)
        self._completed_batch_count = 0
        self._start_next_in_batch()

    def _start_next_in_batch(self) -> None:
        if not getattr(self, "_batch_queue", None):
            return
        rec, source = self._batch_queue.pop(0)
        from .processing_worker import ProcessingWorker

        selected_batch = self.batch_size.value()
        selected_fps = self.sample_fps_spin.value()
        self._processing_source_id = rec.source_id
        self.selected_record = rec
        self._processing_thread = QThread(self)
        self._processing_worker = ProcessingWorker(source, self.config, selected_batch, selected_fps)
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
        self.process_run_all.setEnabled(False)
        self.clear_selection_btn.setEnabled(False)
        self.clear_all_btn.setEnabled(False)
        self.batch_size.setEnabled(False)
        self.sample_fps_spin.setEnabled(False)
        for btn in getattr(self, "preset_buttons", []):
            btn.setEnabled(False)
        for btn in getattr(self, "fps_preset_buttons", []):
            btn.setEnabled(False)
        self.process_cancel.setEnabled(True)
        self.tree.setEnabled(False)
        self.process_progress.setRange(0, 0)
        total_cnt = getattr(self, "_total_batch_count", 1)
        curr_cnt = getattr(self, "_completed_batch_count", 0) + 1
        count_str = f"[{curr_cnt}/{total_cnt}] " if total_cnt > 1 else ""
        self.process_state.setText(f"{count_str}Processing '{rec.filename}' ({selected_fps:.1f} FPS, batch {selected_batch})…")
        self._processing_thread.start()

    def cancel_processing(self) -> None:
        if self._processing_worker:
            self._batch_queue = []
            self._processing_worker.request_cancel()
            self.process_cancel.setEnabled(False)
            self.process_state.setText("Cancelling after the current safe processing step…")

    def _update_processing_progress(self, progress) -> None:  # type: ignore[no-untyped-def]
        percent = progress.percent
        self.process_progress.setRange(0, 0 if percent is None else 100)
        if percent is not None:
            self.process_progress.setValue(percent)
        total_cnt = getattr(self, "_total_batch_count", 1)
        curr_cnt = getattr(self, "_completed_batch_count", 0) + 1
        batch_prefix = f"[{curr_cnt}/{total_cnt}] " if total_cnt > 1 else ""
        eta = "ETA calculating…" if progress.eta_seconds is None else f"ETA {progress.eta_seconds:.0f}s"
        pct_str = f"{percent}%" if percent is not None else "…"
        self.process_state.setText(f"{batch_prefix}{progress.phase}: {pct_str} · {eta} · {progress.message}")
        self.process_diagnostics.setText(
            f"Device: {progress.device} · batch {progress.effective_batch_size}/{progress.configured_batch_size}"
        )

    def _processing_succeeded(self, targets) -> None:  # type: ignore[no-untyped-def]
        self.process_progress.setRange(0, 100)
        self.process_progress.setValue(100)
        self.process_state.setText(f"Processing complete: {len(targets)} candidate(s) written.")
        self.refresh_candidates()

    def _processing_failed(self, message: str) -> None:
        self.process_state.setText(f"Processing failed: {message}")
        QMessageBox.warning(self, "Processing failed", message)

    def _processing_cancelled(self) -> None:
        if self._processing_source_id and self.selected_record:
            clear_source_results(
                self.config.paths.results_dir,
                self._processing_source_id,
                self.selected_record.camera_id,
            )
        self.process_state.setText("Processing cancelled; no new results published.")

    def _processing_finished(self) -> None:
        if getattr(self, "_completed_batch_count", None) is not None:
            self._completed_batch_count += 1
        if getattr(self, "_batch_queue", None):
            self._start_next_in_batch()
            return
        self.process_run.setEnabled(True)
        self.process_run_all.setEnabled(True)
        self.clear_selection_btn.setEnabled(True)
        self.clear_all_btn.setEnabled(True)
        self.batch_size.setEnabled(True)
        self.sample_fps_spin.setEnabled(True)
        for btn in getattr(self, "preset_buttons", []):
            btn.setEnabled(True)
        for btn in getattr(self, "fps_preset_buttons", []):
            btn.setEnabled(True)
        self.process_cancel.setEnabled(False)
        self.tree.setEnabled(True)
        self._processing_worker = None
        self._processing_thread = None
        self._processing_source_id = None

    def clear_selected_results(self) -> None:
        if self.selected_record:
            filename = self.selected_record.filename
            msg = f"Are you sure you want to clear stored results for video '{filename}'?\n\n(Source files are NOT deleted.)"
            if QMessageBox.question(self, "Clear Video Results", msg, QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                clear_source_results(
                    self.config.paths.results_dir,
                    self.selected_record.source_id,
                    self.selected_record.camera_id,
                )
                self._reload_after_clearing(f"Cleared results for video '{filename}'.")
        elif getattr(self, "selected_camera_id", None):
            cam_id = self.selected_camera_id
            msg = f"Are you sure you want to clear ALL results for camera '{cam_id}'?\n\n(Source files are NOT deleted.)"
            if QMessageBox.question(self, "Clear Camera Results", msg, QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                clear_camera_results(self.config.paths.results_dir, cam_id)
                self._reload_after_clearing(f"Cleared results for camera '{cam_id}'.")
        else:
            QMessageBox.warning(self, "No Selection", "Please select a video or camera from the source tree first.")

    def clear_all_results_confirm(self) -> None:
        msg = "Are you sure you want to clear ALL stored results across ALL sources?\n\n(Source files are NOT deleted.)"
        if QMessageBox.question(self, "Clear ALL Results", msg, QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            clear_all_results(self.config.paths.results_dir)
            self._reload_after_clearing("Cleared ALL stored detection results across all sources.")

    def _reload_after_clearing(self, message: str) -> None:
        self.selected_candidate = None
        self.review_workspace.clear_review_context()
        self.export_btn.setEnabled(False)
        self.export_card.setText("No candidate selected for export.")
        self.export_notice.setText("Select a candidate in Review. Export remains explicit.")

        self.refresh_candidates()
        self._load_viewer_for_page(self.tabs.currentIndex())
        self.statusBar().showMessage(message)

    def refresh_candidates(self) -> None:
        from ..result_store import read_candidate

        if self.selected_record:
            candidates = list_candidates(
                self.config.paths.results_dir,
                self.selected_record.source_id,
                self.selected_record.camera_id,
            )
        elif getattr(self, "selected_camera_id", None):
            cam_dir = self.config.paths.results_dir / "cameras" / self.selected_camera_id
            candidates = (
                sorted(
                    [read_candidate(p) for p in cam_dir.glob("*/**/candidate.json")],
                    key=lambda item: (item.category, item.context_start_sec, item.candidate_id),
                )
                if cam_dir.exists()
                else []
            )
        else:
            candidates = []

        candidates = [
            candidate
            for candidate in candidates
            if candidate.category in {"person_detected", "camera_anomaly"}
        ]
        model = QStandardItemModel(self.candidate_tree)
        for candidate in candidates:
            dur = candidate.context_end_sec - candidate.context_start_sec
            det_count = len(candidate.detections)
            start_s, end_s = candidate.context_start_sec, candidate.context_end_sec
            if candidate.category == "camera_anomaly":
                label_str = f"🚨 [camera_anomaly] {start_s:.1f}s – {end_s:.1f}s ({dur:.1f}s)"
            else:
                label_str = f"🟢 [{candidate.category}] {start_s:.1f}s – {end_s:.1f}s ({dur:.1f}s) · {det_count} dets"
            item = QStandardItem(label_str)
            item.setData(candidate, Qt.UserRole)
            model.appendRow(item)
        self.candidate_tree.setModel(model)

        if self.selected_record:
            notice_str = f"{len(candidates)} candidate(s) loaded for video '{self.selected_record.filename}'."
        elif getattr(self, "selected_camera_id", None):
            notice_str = f"{len(candidates)} candidate(s) loaded for camera '{self.selected_camera_id}'."
        else:
            notice_str = "Select a source or camera first."

        self.review_notice.setText(notice_str)

    def select_candidate(self, index) -> None:  # type: ignore[no-untyped-def]
        if getattr(self, "_is_selecting_candidate", False):
            return
        candidate = index.data(Qt.UserRole)
        if not candidate:
            return
        all_sources = {r.source_id: r for r in list_sources(self.config.paths.processed_dir)}
        record = all_sources.get(candidate.source_id) or self.selected_record
        if not record:
            return
        self._is_selecting_candidate = True
        try:
            try:
                src_path = resolve_source(record)
            except (FileNotFoundError, ValueError) as error:
                self.statusBar().showMessage(str(error))
                return

            self.selected_record = record
            self._selected_source_path = src_path
            roi_path, _ = effective_roi_path(self.config.paths.processed_dir, record)
            try:
                self._selected_roi = read_roi(roi_path) if roi_path else None
            except ValueError:
                self._selected_roi = None

            self.tabs.setCurrentIndex(3)
            if self.review_workspace.is_loaded:
                self.review_workspace.close_source()
            self._load_viewer_for_page(3)
            self.selected_candidate = candidate
            self.review_workspace.set_review_context(
                detections=candidate.detections,
                source_fps=record.fps,
                frame_width=record.frame_width,
                frame_height=record.frame_height,
                start_sec=candidate.context_start_sec,
                end_sec=candidate.context_end_sec,
            )
            self.review_notice.setText(
                f"Technical evidence context: {candidate.context_start_sec:.1f}–{candidate.context_end_sec:.1f}s. "
                "ROI and boxes are not final labels."
            )
            dur = candidate.context_end_sec - candidate.context_start_sec
            start_s, end_s = candidate.context_start_sec, candidate.context_end_sec
            self.export_card.setText(
                f"<b>Candidate ID:</b> <code>{candidate.candidate_id}</code><br/>"
                f"<b>Category:</b> {candidate.category} | <b>Subvideo Bounds:</b> {start_s:.1f}s – {end_s:.1f}s ({dur:.1f}s)<br/>"
                f"<b>Source Video:</b> {record.filename}"
            )
            self.export_btn.setEnabled(True)
            self.export_notice.setText(
                f"Selected candidate context: {candidate.context_start_sec:.1f}–{candidate.context_end_sec:.1f}s."
            )
        finally:
            self._is_selecting_candidate = False

    def closeEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        if self._processing_worker:
            self._processing_worker.request_cancel()
        self._close_all_viewers()
        event.accept()
