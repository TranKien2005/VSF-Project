"""Interactive local viewer for a source-owned review video and bbox store."""

from __future__ import annotations

from bisect import bisect_right
from pathlib import Path

from .debug_artifacts import PersonDetectionStore, StoredDetection


def held_detections_by_frame(
    detections: tuple[StoredDetection, ...], source_frame_index: int
) -> list[StoredDetection]:
    """Hold the latest real detector snapshot until the next sampled frame."""
    snapshots: dict[int, list[StoredDetection]] = {}
    for item in detections:
        snapshots.setdefault(item.source_frame_index, []).append(item)
    frame_indices = sorted(snapshots)
    position = bisect_right(frame_indices, source_frame_index) - 1
    return [] if position < 0 else snapshots[frame_indices[position]]


def held_detections(
    snapshots: dict[int, list[StoredDetection]], frame_indices: list[int], source_frame_index: int
) -> list[StoredDetection]:
    """Resolve a precomputed detector snapshot for viewer playback."""
    position = bisect_right(frame_indices, source_frame_index) - 1
    return [] if position < 0 else snapshots[frame_indices[position]]


def inspect_raw_video(
    video_path: Path,
    store: PersonDetectionStore,
    context_start_sec: float = 0.0,
    context_end_sec: float | None = None,
) -> None:
    """Open raw video with persisted boxes; it never writes video or image artifacts."""
    import cv2

    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise RuntimeError(f"OpenCV could not open raw video: {video_path}")
    fps = capture.get(cv2.CAP_PROP_FPS) or store.source_fps or 30.0
    capture.set(cv2.CAP_PROP_POS_FRAMES, max(0, round(context_start_sec * fps)))
    by_frame: dict[int, list] = {}
    for detection in store.detections:
        by_frame.setdefault(detection.source_frame_index, []).append(detection)
    frame_indices = sorted(by_frame)
    paused = False
    overlay_enabled = True
    window_name = f"Person inspect: {video_path.stem}"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    try:
        while True:
            if not paused:
                ok, frame = capture.read()
                if not ok:
                    break
            else:
                position = max(0, int(capture.get(cv2.CAP_PROP_POS_FRAMES)) - 1)
                capture.set(cv2.CAP_PROP_POS_FRAMES, position)
                ok, frame = capture.read()
                if not ok:
                    break
            source_frame_index = max(0, int(capture.get(cv2.CAP_PROP_POS_FRAMES)) - 1)
            source_time_sec = source_frame_index / fps
            if context_end_sec is not None and source_time_sec > context_end_sec:
                break
            detections = held_detections(by_frame, frame_indices, source_frame_index) if overlay_enabled else []
            render_detection_frame(
                frame,
                detections,
                store,
                source_time_sec,
                source_frame_index,
                overlay_enabled=overlay_enabled,
            )
            cv2.imshow(window_name, frame)
            key = cv2.waitKey(0 if paused else max(1, round(1000 / fps))) & 0xFF
            if key in (27, ord("q")):
                break
            if key == ord(" "):
                paused = not paused
            elif key == ord("o"):
                overlay_enabled = not overlay_enabled
            elif key in (81, ord("[")):
                _seek(capture, fps, -5.0 if key == ord("[") else -1.0 / fps)
                paused = True
            elif key in (83, ord("]")):
                _seek(capture, fps, 5.0 if key == ord("]") else 1.0 / fps)
                paused = True
    finally:
        capture.release()
        cv2.destroyWindow(window_name)


def render_detection_frame(
    frame: object,
    detections: list[StoredDetection],
    store: PersonDetectionStore,
    source_time_sec: float,
    source_frame_index: int,
    *,
    overlay_enabled: bool = True,
    annotated_export: bool = False,
) -> None:
    """Draw persisted technical detections and a diagnostic header on one BGR frame."""
    if overlay_enabled:
        for detection in detections:
            _draw_detection(frame, detection, store)
    _draw_header(
        frame,
        source_time_sec,
        source_frame_index,
        len(detections) if overlay_enabled else 0,
        overlay_enabled,
        annotated_export=annotated_export,
    )


def _seek(capture: object, fps: float, seconds: float) -> None:
    import cv2

    current = capture.get(cv2.CAP_PROP_POS_FRAMES)
    capture.set(cv2.CAP_PROP_POS_FRAMES, max(0, current + seconds * fps))


def _draw_detection(frame: object, item: object, store: PersonDetectionStore) -> None:
    import cv2

    height, width = frame.shape[:2]
    x_scale = width / max(store.frame_width or width, 1)
    y_scale = height / max(store.frame_height or height, 1)
    x1, y1, x2, y2 = item.bbox_xyxy_px
    left, top = round(x1 * x_scale), round(y1 * y_scale)
    right, bottom = round(x2 * x_scale), round(y2 * y_scale)
    if right <= left or bottom <= top:
        return
    color = (0, 220, 0)
    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
    label = f"person {item.confidence:.2f} t{item.track_id} {item.episode_id}"
    cv2.putText(frame, label, (left, max(18, top - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)


def _draw_header(
    frame: object,
    source_time_sec: float,
    frame_index: int,
    count: int,
    enabled: bool,
    *,
    annotated_export: bool = False,
) -> None:
    import cv2

    prefix = "ANNOTATED BBOX EXPORT | " if annotated_export else ""
    text = (
        f"{prefix}source {source_time_sec:.3f}s | frame {frame_index} | boxes {count} "
        f"(held 5-FPS sample) | overlay {'on' if enabled else 'off'}"
    )
    cv2.rectangle(frame, (0, 0), (min(frame.shape[1], 700), 26), (0, 0, 0), -1)
    cv2.putText(frame, text, (8, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
