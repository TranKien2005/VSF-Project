"""Native Qt Multimedia preview workspace and desktop entry point."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt, QUrl, Signal
from PySide6.QtGui import QColor, QImage, QPainter, QPen
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer, QVideoSink
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from ..debug_renderer import held_detections
from ..roi import TrackRoi, normalized_to_pixel
from .theme import APP_STYLESHEET


class VideoOverlay(QWidget):
    """Draw source-coordinate evidence and capture a freehand ROI stroke."""

    stroke_finished = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.drawing = False
        self.draft_stroke: tuple[tuple[float, float], ...] = ()
        self._active_stroke = False
        self._content_transform: tuple[float, float, float] | None = None
        self.source_width = 0
        self.source_height = 0
        self.frame_index = 0
        self.roi: TrackRoi | None = None
        self.store = None
        self.show_boxes = True
        self.show_roi = True

    def update_state(
        self,
        *,
        source_width: int,
        source_height: int,
        frame_index: int,
        roi: TrackRoi | None,
        store,
        show_boxes: bool,
        show_roi: bool,
    ) -> None:  # type: ignore[no-untyped-def]
        self.source_width, self.source_height = source_width, source_height
        self.frame_index, self.roi, self.store = frame_index, roi, store
        self.show_boxes, self.show_roi = show_boxes, show_roi
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        if not self.source_width or not self.source_height:
            return
        scale = min(self.width() / self.source_width, self.height() / self.source_height)
        offset_x = (self.width() - self.source_width * scale) / 2
        offset_y = (self.height() - self.source_height * scale) / 2
        self._content_transform = (scale, offset_x, offset_y)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.show_roi and self.roi:
            points = [self._map_normalized(point, scale, offset_x, offset_y) for point in self.roi.tracking_region_normalized]
            painter.setPen(QPen(QColor("#ffb000"), 3))
            painter.setBrush(QColor(255, 176, 0, 55))
            painter.drawPolygon(points)
            painter.setBrush(Qt.NoBrush)
            stroke = [self._map_normalized(point, scale, offset_x, offset_y) for point in self.roi.stroke_points_normalized]
            start = self._map_normalized(self.roi.start_extension_normalized, scale, offset_x, offset_y)
            end = self._map_normalized(self.roi.end_extension_normalized, scale, offset_x, offset_y)
            painter.drawLine(start, stroke[0])
            for first, second in zip(stroke, stroke[1:]):
                painter.drawLine(first, second)
            painter.drawLine(stroke[-1], end)
        if self.show_boxes and self.store:
            snapshots: dict[int, list] = {}
            for detection in self.store.detections:
                snapshots.setdefault(detection.source_frame_index, []).append(detection)
            painter.setPen(QPen(QColor("#00dc00"), 2))
            for detection in held_detections(snapshots, sorted(snapshots), self.frame_index):
                x1, y1, x2, y2 = detection.bbox_xyxy_px
                top_left = self._map_pixel(x1, y1, scale, offset_x, offset_y)
                bottom_right = self._map_pixel(x2, y2, scale, offset_x, offset_y)
                painter.drawRect(top_left.x(), top_left.y(), bottom_right.x() - top_left.x(), bottom_right.y() - top_left.y())
                painter.drawText(top_left.x(), max(16, top_left.y() - 4), f"person {detection.confidence:.2f}")
        if self.draft_stroke:
            painter.setPen(QPen(QColor("#3a86ff"), 3, Qt.DashLine))
            points = [self._map_normalized(point, scale, offset_x, offset_y) for point in self.draft_stroke]
            for first, second in zip(points, points[1:]):
                painter.drawLine(first, second)

    def mousePressEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        if not self.drawing or event.button() != Qt.LeftButton:
            return super().mousePressEvent(event)
        point = self._normalized_point(event.position().x(), event.position().y())
        if point is not None:
            self._active_stroke = True
            self.draft_stroke = (point,)
            self.update()

    def mouseMoveEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        if not self.drawing or not self._active_stroke:
            return super().mouseMoveEvent(event)
        point = self._normalized_point(event.position().x(), event.position().y())
        if point is not None and point != self.draft_stroke[-1]:
            self.draft_stroke = (*self.draft_stroke, point)
            self.update()

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        if not self.drawing or not self._active_stroke or event.button() != Qt.LeftButton:
            return super().mouseReleaseEvent(event)
        self._active_stroke = False
        point = self._normalized_point(event.position().x(), event.position().y())
        if point is not None and point != self.draft_stroke[-1]:
            self.draft_stroke = (*self.draft_stroke, point)
        self.stroke_finished.emit(self.draft_stroke)
        self.update()

    def _normalized_point(self, x: float, y: float) -> tuple[float, float] | None:
        if not self._content_transform:
            return None
        scale, offset_x, offset_y = self._content_transform
        source_x, source_y = (x - offset_x) / scale, (y - offset_y) / scale
        if 0 <= source_x <= self.source_width and 0 <= source_y <= self.source_height:
            return source_x / self.source_width, source_y / self.source_height
        return None

    def _map_normalized(self, point: tuple[float, float], scale: float, offset_x: float, offset_y: float):
        return self._map_pixel(*normalized_to_pixel(point, self.source_width, self.source_height), scale, offset_x, offset_y)

    @staticmethod
    def _map_pixel(x: float, y: float, scale: float, offset_x: float, offset_y: float):
        from PySide6.QtCore import QPointF

        return QPointF(offset_x + x * scale, offset_y + y * scale)


class VideoFrameCanvas(QWidget):
    """Paint the decoded video frame and technical overlays together."""

    def __init__(self) -> None:
        super().__init__()
        self._image: QImage | None = None
        self.source_width = 0
        self.source_height = 0
        self.frame_index = 0
        self.roi: TrackRoi | None = None
        self.store = None
        self.show_boxes = True
        self.show_roi = True
        self.setMinimumSize(480, 270)

    def set_video_frame(self, frame) -> None:  # type: ignore[no-untyped-def]
        image = frame.toImage()
        if not image.isNull():
            self._image = image
            self.update()

    def update_state(
        self,
        *,
        source_width: int,
        source_height: int,
        frame_index: int,
        roi: TrackRoi | None,
        store,
        show_boxes: bool,
        show_roi: bool,
    ) -> None:  # type: ignore[no-untyped-def]
        self.source_width, self.source_height = source_width, source_height
        self.frame_index, self.roi, self.store = frame_index, roi, store
        self.show_boxes, self.show_roi = show_boxes, show_roi
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#111827"))
        if not self._image or not self.source_width or not self.source_height:
            return
        scale = min(self.width() / self.source_width, self.height() / self.source_height)
        offset_x = (self.width() - self.source_width * scale) / 2
        offset_y = (self.height() - self.source_height * scale) / 2
        painter.drawImage(QRectF(offset_x, offset_y, self.source_width * scale, self.source_height * scale), self._image)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.show_roi and self.roi:
            points = [self._map_normalized(point, scale, offset_x, offset_y) for point in self.roi.tracking_region_normalized]
            painter.setPen(QPen(QColor("#ffb000"), 3))
            painter.setBrush(QColor(255, 176, 0, 55))
            painter.drawPolygon(points)
            painter.setBrush(Qt.NoBrush)
            stroke = [self._map_normalized(point, scale, offset_x, offset_y) for point in self.roi.stroke_points_normalized]
            painter.drawLine(self._map_normalized(self.roi.start_extension_normalized, scale, offset_x, offset_y), stroke[0])
            for first, second in zip(stroke, stroke[1:]):
                painter.drawLine(first, second)
            painter.drawLine(stroke[-1], self._map_normalized(self.roi.end_extension_normalized, scale, offset_x, offset_y))
        if self.show_boxes and self.store:
            snapshots: dict[int, list] = {}
            for detection in self.store.detections:
                snapshots.setdefault(detection.source_frame_index, []).append(detection)
            painter.setPen(QPen(QColor("#00dc00"), 2))
            for detection in held_detections(snapshots, sorted(snapshots), self.frame_index):
                x1, y1, x2, y2 = detection.bbox_xyxy_px
                top_left = self._map_pixel(x1, y1, scale, offset_x, offset_y)
                bottom_right = self._map_pixel(x2, y2, scale, offset_x, offset_y)
                painter.drawRect(top_left.x(), top_left.y(), bottom_right.x() - top_left.x(), bottom_right.y() - top_left.y())
                painter.drawText(top_left.x(), max(16, top_left.y() - 4), f"person {detection.confidence:.2f}")

    def _map_normalized(self, point: tuple[float, float], scale: float, offset_x: float, offset_y: float) -> QPointF:
        return self._map_pixel(*normalized_to_pixel(point, self.source_width, self.source_height), scale, offset_x, offset_y)

    @staticmethod
    def _map_pixel(x: float, y: float, scale: float, offset_x: float, offset_y: float) -> QPointF:
        return QPointF(offset_x + x * scale, offset_y + y * scale)


class RoiReferenceCanvas(QWidget):
    """Editable static source frame for freehand track-ROI authoring."""

    roi_changed = Signal()
    roi_rejected = Signal(str)
    drawing_changed = Signal(bool)

    def __init__(self) -> None:
        super().__init__()
        self.source: Path | None = None
        self.roi: TrackRoi | None = None
        self._image: QImage | None = None
        self._timestamp_sec = 0.0
        self._frame_size = (0, 0)
        self._draft_stroke: tuple[tuple[float, float], ...] = ()
        self._drawing = False
        self._image_rect: QRectF | None = None
        self.setMinimumSize(480, 270)
        self.setMouseTracking(True)

    @property
    def is_loaded(self) -> bool:
        return self.source is not None and self._image is not None

    def load_reference(self, source: Path, decoded_frame, roi: TrackRoi | None) -> None:  # type: ignore[no-untyped-def]
        """Show one verified decoded frame without creating a media player."""
        bgr = decoded_frame.bgr
        height, width = bgr.shape[:2]
        image = QImage(bgr.data, width, height, bgr.strides[0], QImage.Format_BGR888).copy()
        self.source = source
        self.roi = roi
        self._image = image
        self._timestamp_sec = decoded_frame.timestamp_sec
        self._frame_size = (width, height)
        self._draft_stroke = ()
        self._drawing = False
        self.update()

    def clear_reference(self) -> None:
        self.source = None
        self.roi = None
        self._image = None
        self._frame_size = (0, 0)
        self._image_rect = None
        self.set_drawing(False)
        self.update()

    def set_roi(self, roi: TrackRoi | None) -> None:
        self.roi = roi
        self._draft_stroke = ()
        self.update()

    def clear_roi(self) -> None:
        self.roi = None
        self.set_drawing(False)
        self.roi_changed.emit()
        self.update()

    def set_drawing(self, active: bool) -> None:
        drawing = active and self.is_loaded
        changed = drawing != self._drawing
        self._drawing = drawing
        if not drawing:
            self._draft_stroke = ()
        self.setCursor(Qt.CrossCursor if drawing else Qt.ArrowCursor)
        if changed:
            self.drawing_changed.emit(drawing)
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#111827"))
        if not self._image:
            painter.setPen(QColor("#cbd5e1"))
            painter.drawText(self.rect(), Qt.AlignCenter, "Select a source to load one reference frame.")
            return
        image_rect = self._fit_image_rect()
        self._image_rect = image_rect
        painter.drawImage(image_rect, self._image)
        if self.roi:
            self._draw_roi(painter, self.roi)
        if self._draft_stroke:
            painter.setPen(QPen(QColor("#3a86ff"), 3, Qt.DashLine))
            points = [self._normalized_to_display(point) for point in self._draft_stroke]
            for first, second in zip(points, points[1:]):
                painter.drawLine(first, second)

    def mousePressEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        if not self._drawing or event.button() != Qt.LeftButton:
            return super().mousePressEvent(event)
        point = self._display_to_normalized(event.position())
        if point is not None:
            self._draft_stroke = (point,)
            self.update()
            event.accept()

    def mouseMoveEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        if not self._drawing or not self._draft_stroke:
            return super().mouseMoveEvent(event)
        point = self._display_to_normalized(event.position())
        if point is not None and point != self._draft_stroke[-1]:
            self._draft_stroke = (*self._draft_stroke, point)
            self.update()
            event.accept()

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        if not self._drawing or not self._draft_stroke or event.button() != Qt.LeftButton:
            return super().mouseReleaseEvent(event)
        point = self._display_to_normalized(event.position())
        if point is not None and point != self._draft_stroke[-1]:
            self._draft_stroke = (*self._draft_stroke, point)
        try:
            self.roi = TrackRoi.create(
                revision=(self.roi.revision + 1) if self.roi else 1,
                reference_source_sha256="pending-save",
                reference_timestamp_sec=self._timestamp_sec,
                reference_frame_size_px=self._frame_size,
                stroke_points_normalized=self._draft_stroke,
            )
        except ValueError as error:
            self.roi_rejected.emit(f"Invalid freehand ROI: {error}. Redraw it.")
        else:
            self.roi_changed.emit()
        finally:
            self._draft_stroke = ()
            self.set_drawing(False)
            self.update()
        event.accept()

    def _fit_image_rect(self) -> QRectF:
        if not self._image:
            return QRectF()
        scale = min(self.width() / self._image.width(), self.height() / self._image.height())
        width, height = self._image.width() * scale, self._image.height() * scale
        return QRectF((self.width() - width) / 2, (self.height() - height) / 2, width, height)

    def _display_to_normalized(self, position: QPointF) -> tuple[float, float] | None:
        image_rect = self._image_rect or self._fit_image_rect()
        if image_rect.isEmpty() or not image_rect.contains(position):
            return None
        return (
            min(1.0, max(0.0, (position.x() - image_rect.x()) / image_rect.width())),
            min(1.0, max(0.0, (position.y() - image_rect.y()) / image_rect.height())),
        )

    def _normalized_to_display(self, point: tuple[float, float]) -> QPointF:
        image_rect = self._image_rect or self._fit_image_rect()
        return QPointF(image_rect.x() + point[0] * image_rect.width(), image_rect.y() + point[1] * image_rect.height())

    def _draw_roi(self, painter: QPainter, roi: TrackRoi) -> None:
        region = [self._normalized_to_display(point) for point in roi.tracking_region_normalized]
        painter.setPen(QPen(QColor("#ffb000"), 3))
        painter.setBrush(QColor(255, 176, 0, 55))
        painter.drawPolygon(region)
        painter.setBrush(Qt.NoBrush)
        stroke = [self._normalized_to_display(point) for point in roi.stroke_points_normalized]
        start = self._normalized_to_display(roi.start_extension_normalized)
        end = self._normalized_to_display(roi.end_extension_normalized)
        painter.drawLine(start, stroke[0])
        for first, second in zip(stroke, stroke[1:]):
            painter.drawLine(first, second)
        painter.drawLine(stroke[-1], end)


class VideoWorkspace(QWidget):
    """Native OS media playback with position-driven overlays and freehand ROI authoring."""

    roi_changed = Signal()
    roi_rejected = Signal(str)

    def __init__(self, *, editable: bool) -> None:
        super().__init__()
        self.editable = editable
        self.source: Path | None = None
        self.store = None
        self.roi: TrackRoi | None = None
        self.source_fps = 25.0
        self.source_width = 1920
        self.source_height = 1080
        self._pending_start_ms: int | None = None
        self._context_start_ms: int | None = None
        self._context_end_ms: int | None = None
        self.audio = QAudioOutput(self)
        self.player = QMediaPlayer(self)
        self.player.setAudioOutput(self.audio)
        self.video_sink = QVideoSink(self)
        self.video = VideoFrameCanvas()
        self.video_sink.videoFrameChanged.connect(self.video.set_video_frame)
        self.player.setVideoOutput(self.video_sink)
        self.overlay = VideoOverlay()
        self.overlay.stroke_finished.connect(self._finish_stroke)
        self.player.positionChanged.connect(self._position_changed)
        self.player.durationChanged.connect(self._duration_changed)
        self.player.mediaStatusChanged.connect(self._media_status_changed)
        self.player.playbackStateChanged.connect(self._playback_state_changed)
        self.player.errorOccurred.connect(self._media_error)
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.video, 1)
        controls = QHBoxLayout()
        self.play = QPushButton("Play")
        self.play.clicked.connect(self._toggle_play)
        previous = QPushButton("◀ Frame")
        previous.clicked.connect(lambda: self._step_frame(-1))
        following = QPushButton("Frame ▶")
        following.clicked.connect(lambda: self._step_frame(1))
        back = QPushButton("−5 s")
        back.clicked.connect(lambda: self._seek_relative(-5_000))
        forward = QPushButton("+5 s")
        forward.clicked.connect(lambda: self._seek_relative(5_000))
        self.timeline = QSlider(Qt.Horizontal)
        self.timeline.sliderReleased.connect(lambda: self._set_bounded_position(self.timeline.value()))
        for widget in (self.play, previous, following, back, forward, self.timeline):
            controls.addWidget(widget)
        layout.addLayout(controls)
        self.info = QLabel("No source loaded", objectName="subtitle")
        layout.addWidget(self.info)
        switches = QHBoxLayout()
        self.show_boxes = QCheckBox("Technical boxes")
        self.show_boxes.setChecked(True)
        self.show_roi = QCheckBox("Track ROI")
        self.show_roi.setChecked(True)
        self.show_boxes.stateChanged.connect(self._refresh_overlay)
        self.show_roi.stateChanged.connect(self._refresh_overlay)
        switches.addWidget(self.show_boxes)
        switches.addWidget(self.show_roi)
        if self.editable:
            self.draw = QPushButton("Draw freehand ROI", objectName="primary")
            self.draw.setCheckable(True)
            self.draw.toggled.connect(self._toggle_draw)
            clear = QPushButton("Clear ROI")
            clear.clicked.connect(self.clear_roi)
            switches.addWidget(self.draw)
            switches.addWidget(clear)
        switches.addStretch()
        layout.addLayout(switches)

    def open_source(
        self, source: Path, *, store=None, roi: TrackRoi | None = None, initial_frame_index: int | None = None
    ) -> None:  # type: ignore[no-untyped-def]
        self.close_source()
        self.source, self.store, self.roi = source, store, roi
        self.source_fps = float(getattr(store, "source_fps", 0.0) or 25.0)
        self.source_width = int(getattr(store, "frame_width", 0) or 1920)
        self.source_height = int(getattr(store, "frame_height", 0) or 1080)
        self.clear_review_context()
        self._pending_start_ms = round(initial_frame_index / self.source_fps * 1000) if initial_frame_index else None
        self.player.setSource(QUrl.fromLocalFile(str(source)))
        self.info.setText(f"Loading native media: {source.name}")
        self._refresh_overlay()

    def close_source(self) -> int | None:
        frame_index = round(self.player.position() / 1000 * self.source_fps) if self.source_fps else None
        self.player.stop()
        self.player.setSource(QUrl())
        self.source, self.store = None, None
        self.clear_review_context()
        return frame_index

    @property
    def is_loaded(self) -> bool:
        return self.source is not None

    def set_roi(self, roi: TrackRoi | None) -> None:
        self.roi = roi
        self._refresh_overlay()

    def set_detection_store(self, store) -> None:  # type: ignore[no-untyped-def]
        self.store = store
        self.source_fps = float(getattr(store, "source_fps", self.source_fps) or self.source_fps)
        self.source_width = int(getattr(store, "frame_width", self.source_width) or self.source_width)
        self.source_height = int(getattr(store, "frame_height", self.source_height) or self.source_height)
        self._refresh_overlay()

    def set_review_context(
        self,
        *,
        detections,
        source_fps: float,
        frame_width: int,
        frame_height: int,
        start_sec: float,
        end_sec: float,
    ) -> None:  # type: ignore[no-untyped-def]
        if start_sec < 0 or end_sec < start_sec:
            raise ValueError("Review context bounds are invalid")
        self.set_detection_store(
            type(
                "ReviewEvidence",
                (),
                {
                    "detections": detections,
                    "source_fps": source_fps,
                    "frame_width": frame_width,
                    "frame_height": frame_height,
                },
            )()
        )
        self._context_start_ms = round(start_sec * 1000)
        self._context_end_ms = round(end_sec * 1000)
        self._pending_start_ms = self._context_start_ms
        self._apply_context_bounds()
        self.player.pause()
        if self.player.mediaStatus() in {QMediaPlayer.LoadedMedia, QMediaPlayer.BufferedMedia}:
            self._set_bounded_position(self._context_start_ms)
            self._pending_start_ms = None

    def clear_review_context(self) -> None:
        self._context_start_ms = None
        self._context_end_ms = None
        self.timeline.setRange(0, max(0, self.player.duration()))

    def _context_bounds(self) -> tuple[int, int]:
        start = self._context_start_ms if self._context_start_ms is not None else 0
        end = self._context_end_ms if self._context_end_ms is not None else max(0, self.player.duration())
        if self.player.duration() > 0:
            start, end = min(start, self.player.duration()), min(end, self.player.duration())
        return start, max(start, end)

    def _apply_context_bounds(self) -> None:
        start, end = self._context_bounds()
        self.timeline.setRange(start, end)

    def _set_bounded_position(self, position_ms: int) -> None:
        start, end = self._context_bounds()
        self.player.setPosition(max(start, min(end, position_ms)))

    def clear_roi(self) -> None:
        self.roi = None
        self.overlay.draft_stroke = ()
        self.roi_changed.emit()
        self._refresh_overlay()

    def _toggle_draw(self, active: bool) -> None:
        self.overlay.drawing = active
        self.overlay.setAttribute(Qt.WA_TransparentForMouseEvents, not active)
        if active:
            self.player.pause()
            self.info.setText("Draw one freehand ROI stroke; endpoint tangents will close it to the frame.")

    def _finish_stroke(self, points: tuple[tuple[float, float], ...]) -> None:
        try:
            self.roi = TrackRoi.create(
                revision=(self.roi.revision + 1) if self.roi else 1,
                reference_source_sha256="pending-save",
                reference_timestamp_sec=self.player.position() / 1000,
                reference_frame_size_px=(self.source_width, self.source_height),
                stroke_points_normalized=points,
            )
        except ValueError as error:
            self.overlay.draft_stroke = ()
            self.roi_rejected.emit(f"Invalid freehand ROI: {error}. Redraw it.")
        else:
            self.overlay.draft_stroke = ()
            self.roi_changed.emit()
        self._refresh_overlay()

    def _media_status_changed(self, status) -> None:  # type: ignore[no-untyped-def]
        if status in {QMediaPlayer.LoadedMedia, QMediaPlayer.BufferedMedia} and self._pending_start_ms is not None:
            self._set_bounded_position(self._pending_start_ms)
            self._pending_start_ms = None

    def _duration_changed(self, duration_ms: int) -> None:
        self._apply_context_bounds()

    def _position_changed(self, position_ms: int) -> None:
        start, end = self._context_bounds()
        if self._context_end_ms is not None and position_ms >= end:
            if position_ms != end:
                self.player.setPosition(end)
            self.player.pause()
            position_ms = end
        elif self._context_start_ms is not None and position_ms < start:
            self.player.setPosition(start)
            position_ms = start
        self.timeline.blockSignals(True)
        self.timeline.setValue(position_ms)
        self.timeline.blockSignals(False)
        frame_index = int(position_ms / 1000 * self.source_fps)
        context = "" if self._context_start_ms is None else f" · review {start / 1000:.3f}–{end / 1000:.3f}s"
        self.info.setText(f"{position_ms / 1000:.3f}s · frame {frame_index} · native playback{context}")
        self._refresh_overlay(frame_index)

    def _playback_state_changed(self, state) -> None:  # type: ignore[no-untyped-def]
        self.play.setText("Pause" if state == QMediaPlayer.PlayingState else "Play")

    def _media_error(self, error, message: str) -> None:  # type: ignore[no-untyped-def]
        if error:
            self.info.setText(f"Native playback error: {message}")

    def _toggle_play(self) -> None:
        self.player.pause() if self.player.playbackState() == QMediaPlayer.PlayingState else self.player.play()

    def _seek_relative(self, milliseconds: int) -> None:
        self._set_bounded_position(self.player.position() + milliseconds)

    def _step_frame(self, direction: int) -> None:
        self.player.pause()
        self._seek_relative(direction * round(1000 / self.source_fps))

    def _refresh_overlay(self, frame_index: int | None = None) -> None:
        self.video.update_state(
            source_width=self.source_width,
            source_height=self.source_height,
            frame_index=frame_index if frame_index is not None else int(self.player.position() / 1000 * self.source_fps),
            roi=self.roi,
            store=self.store,
            show_boxes=self.show_boxes.isChecked(),
            show_roi=self.show_roi.isChecked(),
        )


def main() -> int:
    from .processed_window import ProcessedMainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("VSF Candidate Mining")
    app.setStyleSheet(APP_STYLESHEET)
    window = ProcessedMainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
