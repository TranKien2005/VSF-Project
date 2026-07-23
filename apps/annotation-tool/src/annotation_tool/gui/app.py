"""VSF Annotation Tool — desktop labeling application.

Mirrors Candidate Mining GUI's layout and workflow:
- Header bar with active source status and export action
- Hierarchical Source Library tree (Unique videos & Cameras)
- Candidate Subvideo Suggestions inspector
- Native PySide6 Multimedia video workspace with ROI and bounding box overlays
- Saved Output Labels inspector & conditional Label Form
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

from candidate_mining.config import load_config
from candidate_mining.gui.app import VideoWorkspace, _silence_ffmpeg_logs
from candidate_mining.gui.theme import APP_STYLESHEET
from candidate_mining.processed_store import (
    ProcessedSource,
    effective_roi_path,
    list_cameras,
    list_sources,
    resolve_source,
)
from candidate_mining.result_store import TechnicalCandidate, list_candidates
from candidate_mining.roi import TrackRoi, read_roi
from PySide6.QtCore import QItemSelectionModel, QModelIndex, Qt, QTimer
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QSplitter,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from ..label_store import (
    DISTANCE_VALUES,
    LIGHTING_VALUES,
    PERSON_LABELS,
    LabelCategory,
    OutputLabel,
    compute_subvideo_bounds,
    delete_label,
    generate_label_id,
    label_directory,
    label_group_for,
    list_labels,
    save_label,
    validate_label,
)

# ---------------------------------------------------------------------------
# Role constants for QStandardItem.data(Qt.UserRole + N)
# ---------------------------------------------------------------------------
ROLE_ID = Qt.UserRole  # source_id, camera_id, or label_id
ROLE_TYPE = Qt.UserRole + 1  # "camera", "video", "candidate", "label", "heading"
ROLE_OBJECT = Qt.UserRole + 2  # full Python object (ProcessedSource, TechnicalCandidate, OutputLabel)


class LabelFormWidget(QWidget):
    """Sidebar form for creating / editing an output label."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._video_duration = 0.0
        self._camera_name = ""
        self._video_name = ""
        self._source_id = ""
        self._editing_label: OutputLabel | None = None
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # --- Info readouts ---
        self.camera_label = QLabel("Camera: —", objectName="subtitle")
        self.video_label = QLabel("Video: —", objectName="subtitle")
        layout.addWidget(self.camera_label)
        layout.addWidget(self.video_label)

        # --- Event start ---
        layout.addWidget(QLabel("Event Start (s):"))
        row_start = QHBoxLayout()
        self.event_start = QDoubleSpinBox()
        self.event_start.setRange(0, 999999)
        self.event_start.setDecimals(1)
        self.event_start.setSingleStep(0.5)
        self.btn_set_start = QPushButton("◄ Set")
        self.btn_set_start.setFixedWidth(52)
        self.btn_set_start.setToolTip("Set from current player position")
        row_start.addWidget(self.event_start, 1)
        row_start.addWidget(self.btn_set_start)
        layout.addLayout(row_start)

        # --- Event end ---
        layout.addWidget(QLabel("Event End (s):"))
        row_end = QHBoxLayout()
        self.event_end = QDoubleSpinBox()
        self.event_end.setRange(0, 999999)
        self.event_end.setDecimals(1)
        self.event_end.setSingleStep(0.5)
        self.btn_set_end = QPushButton("◄ Set")
        self.btn_set_end.setFixedWidth(52)
        self.btn_set_end.setToolTip("Set from current player position")
        row_end.addWidget(self.event_end, 1)
        row_end.addWidget(self.btn_set_end)
        layout.addLayout(row_end)

        # --- Label selector ---
        layout.addWidget(QLabel("Label:"))
        self.label_combo = QComboBox()
        self.label_combo.addItem("— chọn nhãn —", "")
        for cat in LabelCategory:
            self.label_combo.addItem(cat.value, cat.value)
        self.label_combo.currentIndexChanged.connect(self._on_label_changed)
        layout.addWidget(self.label_combo)

        # --- Conditional metadata: distance ---
        self.distance_label = QLabel("Distance to camera:")
        self.distance_combo = QComboBox()
        self.distance_combo.addItem("— chọn —", "")
        for d in DISTANCE_VALUES:
            self.distance_combo.addItem(d, d)
        layout.addWidget(self.distance_label)
        layout.addWidget(self.distance_combo)

        # --- Conditional metadata: lighting ---
        self.lighting_label = QLabel("Lighting condition:")
        self.lighting_combo = QComboBox()
        self.lighting_combo.addItem("— chọn —", "")
        for lit in LIGHTING_VALUES:
            self.lighting_combo.addItem(lit, lit)
        layout.addWidget(self.lighting_label)
        layout.addWidget(self.lighting_combo)

        # --- Buttons ---
        btn_row = QHBoxLayout()
        self.btn_save = QPushButton("Save", objectName="primary")
        self.btn_delete = QPushButton("Delete", objectName="danger")
        self.btn_delete.setVisible(False)
        self.btn_new = QPushButton("New")
        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_delete)
        btn_row.addWidget(self.btn_new)
        layout.addLayout(btn_row)

        self.status_label = QLabel("", objectName="subtitle")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        layout.addStretch()
        self._on_label_changed()

    def _on_label_changed(self) -> None:
        """Show/hide distance and lighting fields based on selected label."""
        selected = self.label_combo.currentData()
        is_person = selected in PERSON_LABELS
        self.distance_label.setVisible(is_person)
        self.distance_combo.setVisible(is_person)
        self.lighting_label.setVisible(is_person)
        self.lighting_combo.setVisible(is_person)

    def set_source_context(self, camera_name: str, video_name: str, source_id: str, duration: float) -> None:
        """Update the form context when a video is selected."""
        self._camera_name = camera_name
        self._video_name = video_name
        self._source_id = source_id
        self._video_duration = duration
        self.camera_label.setText(f"Camera: {camera_name or '(standalone)'}")
        self.video_label.setText(f"Video: {video_name}")

    def set_player_time(self, seconds: float, target: str) -> None:
        """Called by 'Set' buttons to inject current player position."""
        if target == "start":
            self.event_start.setValue(round(seconds, 1))
        else:
            self.event_end.setValue(round(seconds, 1))

    def populate_from_label(self, label: OutputLabel) -> None:
        """Fill the form from an existing saved label for editing."""
        self._editing_label = label
        self._camera_name = label.camera_name
        self._video_name = label.video_name
        self._source_id = label.source_id
        self.camera_label.setText(f"Camera: {label.camera_name or '(standalone)'}")
        self.video_label.setText(f"Video: {label.video_name}")
        self.event_start.setValue(label.event_start_time)
        self.event_end.setValue(label.event_end_time)

        idx = self.label_combo.findData(label.label)
        if idx >= 0:
            self.label_combo.setCurrentIndex(idx)

        if label.distance_to_camera:
            idx_d = self.distance_combo.findData(label.distance_to_camera)
            if idx_d >= 0:
                self.distance_combo.setCurrentIndex(idx_d)
        else:
            self.distance_combo.setCurrentIndex(0)

        if label.lighting_condition:
            idx_l = self.lighting_combo.findData(label.lighting_condition)
            if idx_l >= 0:
                self.lighting_combo.setCurrentIndex(idx_l)
        else:
            self.lighting_combo.setCurrentIndex(0)

        self.btn_delete.setVisible(True)
        self.status_label.setText(f"Editing: {label.label_id}")

    def clear_form(self) -> None:
        """Reset form to create-new mode."""
        self._editing_label = None
        self.event_start.setValue(0)
        self.event_end.setValue(0)
        self.label_combo.setCurrentIndex(0)
        self.distance_combo.setCurrentIndex(0)
        self.lighting_combo.setCurrentIndex(0)
        self.btn_delete.setVisible(False)
        self.status_label.setText("")

    def build_label(self) -> OutputLabel | None:
        """Collect form data, validate, and return an OutputLabel or None on error."""
        selected_label = self.label_combo.currentData()
        if not selected_label:
            self.status_label.setText("⚠ Chưa chọn nhãn.")
            return None

        event_start = self.event_start.value()
        event_end = self.event_end.value()
        sub_start, sub_end = compute_subvideo_bounds(event_start, event_end, self._video_duration)

        distance = self.distance_combo.currentData() or None
        lighting = self.lighting_combo.currentData() or None

        now = datetime.now(UTC).isoformat()
        label_id = self._editing_label.label_id if self._editing_label else generate_label_id()
        created = self._editing_label.created_at if self._editing_label else now

        label = OutputLabel(
            label_id=label_id,
            camera_name=self._camera_name,
            video_name=self._video_name,
            source_id=self._source_id,
            label=selected_label,
            label_group=label_group_for(selected_label),
            event_start_time=event_start,
            event_end_time=event_end,
            subvideo_start_time=sub_start,
            subvideo_end_time=sub_end,
            distance_to_camera=distance,
            lighting_condition=lighting,
            created_at=created,
            updated_at=now,
        )

        errors = validate_label(label)
        if errors:
            self.status_label.setText("⚠ " + "; ".join(errors))
            return None

        return label


class LabelerWindow(QMainWindow):
    """Main window for the VSF Annotation Tool matching Candidate Mining architecture."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("VSF Annotation Tool")
        self.resize(1540, 920)
        self._config = load_config()
        self._labels_dir = self._config.root / "data" / "labels"
        self._labels_dir.mkdir(parents=True, exist_ok=True)

        self.selected_record: ProcessedSource | None = None
        self.selected_candidate: TechnicalCandidate | None = None
        self._selected_source_path: Path | None = None
        self._selected_roi: TrackRoi | None = None

        self._build_ui()
        QTimer.singleShot(0, self.refresh_catalog)

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QWidget()
        shell = QVBoxLayout(root)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)

        # Header
        shell.addWidget(self._header())

        # Main horizontal splitter (4 panels)
        splitter = QSplitter(Qt.Horizontal)

        # Panel 1: Source Library Tree
        splitter.addWidget(self._library_panel())

        # Panel 2: Subvideo Candidates Inspector
        splitter.addWidget(self._candidate_panel())

        # Panel 3: Video Workspace
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(4, 8, 4, 8)
        self.workspace = VideoWorkspace(editable=False)
        center_layout.addWidget(self.workspace, 1)

        marker_row = QHBoxLayout()
        btn_mark_start = QPushButton("◄ Set Event Start")
        btn_mark_start.clicked.connect(lambda: self._set_time_from_player("start"))
        btn_mark_end = QPushButton("Set Event End ►")
        btn_mark_end.clicked.connect(lambda: self._set_time_from_player("end"))
        marker_row.addStretch()
        marker_row.addWidget(btn_mark_start)
        marker_row.addWidget(btn_mark_end)
        marker_row.addStretch()
        center_layout.addLayout(marker_row)
        splitter.addWidget(center_widget)

        # Panel 4: Output Labels Tree & Form
        splitter.addWidget(self._label_panel())

        # Proportions: Library (240px), Candidates (240px), Video Workspace (700px), Labels (360px)
        splitter.setSizes([240, 240, 700, 360])
        shell.addWidget(splitter, 1)

        self.setCentralWidget(root)
        self.statusBar().showMessage("Select a source to review and create output labels.")

    def _header(self) -> QWidget:
        header = QFrame(objectName="navRail")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.addWidget(QLabel("📌 VSF Annotation Tool", objectName="pageTitle"))
        layout.addStretch()
        self.selection_label = QLabel("No imported source selected", objectName="subtitle")
        layout.addWidget(self.selection_label)

        self.btn_export = QPushButton("Export All", objectName="primary")
        self.btn_export.clicked.connect(self._do_export_all)
        layout.addWidget(self.btn_export)
        return header

    def _library_panel(self) -> QWidget:
        panel = QFrame(objectName="sidePanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 14, 12, 12)
        layout.addWidget(QLabel("Source library", objectName="pageTitle"))
        layout.addWidget(QLabel("Unique videos and cameras", objectName="subtitle"))

        self.library_tree = QTreeView()
        self.library_tree.setHeaderHidden(True)
        self.library_tree.setRootIsDecorated(True)
        self.library_tree.clicked.connect(self._on_library_tree_clicked)
        layout.addWidget(self.library_tree, 1)

        refresh = QPushButton("Refresh catalog")
        refresh.clicked.connect(self.refresh_catalog)
        layout.addWidget(refresh)
        return panel

    def _candidate_panel(self) -> QWidget:
        panel = QFrame(objectName="sidePanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 14, 12, 12)
        layout.addWidget(QLabel("Gợi ý Subvideo", objectName="pageTitle"))
        layout.addWidget(QLabel("Technical candidates", objectName="subtitle"))

        self.candidate_tree = QTreeView()
        self.candidate_tree.setHeaderHidden(True)
        self.candidate_model = QStandardItemModel()
        self.candidate_tree.setModel(self.candidate_model)
        self.candidate_tree.clicked.connect(self._on_candidate_clicked)
        layout.addWidget(self.candidate_tree, 1)
        return panel

    def _label_panel(self) -> QWidget:
        panel = QFrame(objectName="inspector")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 14, 12, 12)
        layout.addWidget(QLabel("Output Labels", objectName="pageTitle"))
        layout.addWidget(QLabel("Dữ liệu gán nhãn đã lưu", objectName="subtitle"))

        self.output_tree = QTreeView()
        self.output_tree.setHeaderHidden(True)
        self.output_model = QStandardItemModel()
        self.output_tree.setModel(self.output_model)
        self.output_tree.clicked.connect(self._on_output_label_clicked)
        layout.addWidget(self.output_tree, 1)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        layout.addWidget(QLabel("📝 Label Form", objectName="eyebrow"))
        self.form = LabelFormWidget()
        self.form.btn_save.clicked.connect(self._on_save_label)
        self.form.btn_delete.clicked.connect(self._on_delete_label)
        self.form.btn_new.clicked.connect(self._on_new_label)
        self.form.btn_set_start.clicked.connect(lambda: self._set_time_from_player("start"))
        self.form.btn_set_end.clicked.connect(lambda: self._set_time_from_player("end"))
        layout.addWidget(self.form)
        return panel

    # ------------------------------------------------------------------
    # Source Catalog & Tree Operations
    # ------------------------------------------------------------------

    def refresh_catalog(self, select_source_id: str | None = None) -> None:
        target_id = select_source_id or (self.selected_record.source_id if self.selected_record else None)
        model = QStandardItemModel(self.library_tree)
        unique = QStandardItem("Unique videos")
        cameras = QStandardItem("Cameras")
        unique.setData("heading", ROLE_TYPE)
        cameras.setData("heading", ROLE_TYPE)

        from collections import defaultdict

        grouped: dict[str, list[ProcessedSource]] = defaultdict(list)
        for record in list_sources(self._config.paths.processed_dir):
            if record.camera_id:
                grouped[record.camera_id].append(record)
            else:
                unique.appendRow(self._source_item(record))

        for camera in list_cameras(self._config.paths.processed_dir):
            item = QStandardItem(camera.name)
            item.setData(camera.camera_id, ROLE_ID)
            item.setData("camera", ROLE_TYPE)
            for record in grouped.pop(camera.camera_id, []):
                item.appendRow(self._source_item(record))
            cameras.appendRow(item)

        model.appendRow(unique)
        model.appendRow(cameras)
        self.library_tree.setModel(model)
        self.library_tree.expandAll()

        if self.library_tree.selectionModel():
            self.library_tree.selectionModel().selectionChanged.connect(self._on_tree_selection_changed)

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

        if target_index and self.library_tree.selectionModel():
            self.library_tree.selectionModel().select(
                target_index, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
            )
            self._select_source(target_index)

    def _source_item(self, record: ProcessedSource) -> QStandardItem:
        item = QStandardItem(f"🎬 {record.filename}")
        item.setEditable(False)
        item.setData(record.source_id, ROLE_ID)
        item.setData("video", ROLE_TYPE)
        item.setData(record, ROLE_OBJECT)
        return item

    def _on_tree_selection_changed(self, selected, deselected) -> None:  # type: ignore[no-untyped-def]
        indexes = selected.indexes()
        if indexes:
            self._select_source(indexes[0])

    def _find_source_index(self, parent_item: QStandardItem, source_id: str) -> QModelIndex | None:
        for r in range(parent_item.rowCount()):
            child = parent_item.child(r)
            if child:
                if child.data(ROLE_TYPE) == "video" and child.data(ROLE_ID) == source_id:
                    return child.index()
                found = self._find_source_index(child, source_id)
                if found:
                    return found
        return None

    def _find_first_source_index(self, parent_item: QStandardItem) -> QModelIndex | None:
        for r in range(parent_item.rowCount()):
            child = parent_item.child(r)
            if child:
                if child.data(ROLE_TYPE) == "video":
                    return child.index()
                found = self._find_first_source_index(child)
                if found:
                    return found
        return None

    def _on_library_tree_clicked(self, index: QModelIndex) -> None:
        self._select_source(index)

    def _select_source(self, index: QModelIndex) -> None:
        item = self.library_tree.model().itemFromIndex(index)
        if not item:
            return
        item_type = item.data(ROLE_TYPE)
        if item_type != "video":
            return

        record: ProcessedSource = item.data(ROLE_OBJECT)
        if not record:
            return

        try:
            source_path = resolve_source(record)
        except (FileNotFoundError, ValueError) as error:
            self.statusBar().showMessage(str(error))
            return

        self.selected_record = record
        self._selected_source_path = source_path

        # Read effective ROI for this source
        roi_path, scope = effective_roi_path(self._config.paths.processed_dir, record)
        try:
            self._selected_roi = read_roi(roi_path) if roi_path else None
        except ValueError:
            self._selected_roi = None

        self.selection_label.setText(f"{record.filename} · {record.duration_seconds:.1f}s")

        store = type("SourceMeta", (), {
            "source_fps": record.fps or 25.0,
            "frame_width": record.frame_width or 1920,
            "frame_height": record.frame_height or 1080,
            "detections": [],
        })()

        self.workspace.open_source(source_path, store=store, roi=self._selected_roi)
        self.workspace.clear_review_context()

        cam_name = record.camera_id or ""
        self.form.set_source_context(cam_name, record.filename, record.source_id, record.duration_seconds)
        self.form.clear_form()

        self.refresh_candidates()
        self.refresh_output_labels()

    # ------------------------------------------------------------------
    # Candidates Inspector (Middle-Left)
    # ------------------------------------------------------------------

    def refresh_candidates(self) -> None:
        self.candidate_model.clear()
        if not self.selected_record:
            return

        results_dir = self._config.paths.results_dir
        candidates = list_candidates(results_dir, self.selected_record.source_id, self.selected_record.camera_id)
        root = self.candidate_model.invisibleRootItem()

        for cand in candidates:
            icon = "🟢" if cand.category == "person_detected" else "🚨"
            duration = cand.context_end_sec - cand.context_start_sec
            dets_count = len(cand.detections)
            dets_str = f" · {dets_count} dets" if dets_count else ""
            text = (
                f"{icon} [{cand.category}] {cand.context_start_sec:.1f}s–"
                f"{cand.context_end_sec:.1f}s ({duration:.1f}s){dets_str}"
            )
            item = QStandardItem(text)
            item.setEditable(False)
            item.setData(cand.candidate_id, ROLE_ID)
            item.setData("candidate", ROLE_TYPE)
            item.setData(cand, ROLE_OBJECT)
            root.appendRow(item)

    def _on_candidate_clicked(self, index: QModelIndex) -> None:
        item = self.candidate_model.itemFromIndex(index)
        if not item:
            return
        cand: TechnicalCandidate = item.data(ROLE_OBJECT)
        if not cand or not self.selected_record or not self._selected_source_path:
            return

        self.selected_candidate = cand
        store = type("SourceMeta", (), {
            "source_fps": self.selected_record.fps or 25.0,
            "frame_width": self.selected_record.frame_width or 1920,
            "frame_height": self.selected_record.frame_height or 1080,
            "detections": list(cand.detections),
        })()

        self.workspace.open_source(self._selected_source_path, store=store, roi=self._selected_roi)
        self.workspace.set_review_context(
            detections=list(cand.detections),
            source_fps=self.selected_record.fps or 25.0,
            frame_width=self.selected_record.frame_width or 1920,
            frame_height=self.selected_record.frame_height or 1080,
            start_sec=cand.context_start_sec,
            end_sec=cand.context_end_sec,
            autoplay=True,
        )

    # ------------------------------------------------------------------
    # Output Labels Inspector & Form (Right Panel)
    # ------------------------------------------------------------------

    def refresh_output_labels(self) -> None:
        self.output_model.clear()
        if not self.selected_record:
            return

        all_labels = list_labels(self._labels_dir)
        video_labels = [lbl for lbl in all_labels if lbl.source_id == self.selected_record.source_id]
        root = self.output_model.invisibleRootItem()

        for lbl in video_labels:
            duration = lbl.event_end_time - lbl.event_start_time
            meta_str = ""
            if lbl.distance_to_camera:
                meta_str += f" · {lbl.distance_to_camera}"
            if lbl.lighting_condition:
                meta_str += f" · {lbl.lighting_condition}"
            text = f"🏷️ {lbl.label} {lbl.event_start_time:.1f}s–{lbl.event_end_time:.1f}s ({duration:.1f}s){meta_str}"
            item = QStandardItem(text)
            item.setEditable(False)
            item.setData(lbl.label_id, ROLE_ID)
            item.setData("label", ROLE_TYPE)
            item.setData(lbl, ROLE_OBJECT)
            root.appendRow(item)

    def _on_output_label_clicked(self, index: QModelIndex) -> None:
        item = self.output_model.itemFromIndex(index)
        if not item:
            return
        lbl: OutputLabel = item.data(ROLE_OBJECT)
        if not lbl or not self.selected_record or not self._selected_source_path:
            return

        store = type("SourceMeta", (), {
            "source_fps": self.selected_record.fps or 25.0,
            "frame_width": self.selected_record.frame_width or 1920,
            "frame_height": self.selected_record.frame_height or 1080,
            "detections": [],
        })()

        self.workspace.open_source(self._selected_source_path, store=store, roi=self._selected_roi)
        self.workspace.set_review_context(
            detections=[],
            source_fps=self.selected_record.fps or 25.0,
            frame_width=self.selected_record.frame_width or 1920,
            frame_height=self.selected_record.frame_height or 1080,
            start_sec=lbl.subvideo_start_time,
            end_sec=lbl.subvideo_end_time,
            autoplay=True,
        )

        self.form.populate_from_label(lbl)

    # ------------------------------------------------------------------
    # Helper & Form Actions
    # ------------------------------------------------------------------

    def _set_time_from_player(self, target: str) -> None:
        if not self.workspace.is_loaded:
            return
        current_sec = self.workspace.player.position() / 1000.0
        self.form.set_player_time(current_sec, target)

    def _on_save_label(self) -> None:
        if not self.selected_record:
            QMessageBox.warning(self, "Error", "Chưa chọn video nguồn.")
            return

        label = self.form.build_label()
        if label is None:
            return

        try:
            save_label(self._labels_dir, label)
            self.form.status_label.setText(f"✅ Đã lưu: {label.label_id}")
            self.form._editing_label = label
            self.form.btn_delete.setVisible(True)
            self.refresh_output_labels()
        except Exception as exc:
            QMessageBox.critical(self, "Save Error", str(exc))

    def _on_delete_label(self) -> None:
        label = self.form._editing_label
        if not label:
            return
        reply = QMessageBox.question(
            self,
            "Xóa label",
            f"Xóa label '{label.label_id}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        try:
            lbl_dir = label_directory(self._labels_dir, label)
            delete_label(lbl_dir)
            self.form.clear_form()
            self.form.status_label.setText("🗑️ Đã xóa.")
            self.refresh_output_labels()
        except Exception as exc:
            QMessageBox.critical(self, "Delete Error", str(exc))

    def _on_new_label(self) -> None:
        self.form.clear_form()

    # ------------------------------------------------------------------
    # Export All
    # ------------------------------------------------------------------

    def _do_export_all(self) -> None:
        labels = list_labels(self._labels_dir)
        if not labels:
            QMessageBox.information(self, "Export", "Không có label nào để export.")
            return

        export_dir = QFileDialog.getExistingDirectory(self, "Chọn thư mục export")
        if not export_dir:
            return

        from ..label_exporter import export_all

        progress = QProgressDialog("Exporting labels...", "Cancel", 0, len(labels), self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)

        def on_progress(current: int, total: int) -> None:
            progress.setValue(current)
            QApplication.processEvents()

        try:
            ffmpeg_dir = self._config.paths.ffmpeg_dir
            ffmpeg = ffmpeg_dir / "ffmpeg.exe" if (ffmpeg_dir / "ffmpeg.exe").exists() else Path("ffmpeg")

            success, errors = export_all(
                labels_dir=self._labels_dir,
                processed_dir=self._config.paths.processed_dir,
                export_dir=Path(export_dir),
                ffmpeg=ffmpeg,
                on_progress=on_progress,
            )
            progress.close()

            msg = f"Export hoàn tất: {success}/{len(labels)} labels."
            if errors:
                msg += "\n\nLỗi:\n" + "\n".join(errors[:10])
            QMessageBox.information(self, "Export", msg)
        except Exception as exc:
            progress.close()
            QMessageBox.critical(self, "Export Error", str(exc))


def main() -> int:
    _silence_ffmpeg_logs()
    app = QApplication(sys.argv)
    app.setApplicationName("VSF Annotation Tool")
    app.setStyleSheet(APP_STYLESHEET)
    window = LabelerWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
