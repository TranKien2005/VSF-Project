"""FFmpeg-based proxy clip export."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .debug_artifacts import PersonDetectionStore
from .debug_renderer import held_detections, render_detection_frame


def normalize_export_target(source: Path, target: Path) -> Path:
    """Normalize a user-selected MP4 destination and reject unsafe self-export."""
    if target.exists() and target.is_dir():
        raise ValueError(f"Export destination is a directory: {target}")
    normalized = target.with_suffix(".mp4") if target.suffix.casefold() != ".mp4" else target
    if normalized.resolve() == source.resolve():
        raise ValueError("Export destination must not overwrite the raw source video")
    return normalized


def export_clip(
    source: Path,
    start_sec: float,
    end_sec: float,
    target: Path,
    *,
    ffmpeg: Path,
) -> None:
    """Export accurately seeked MP4 to a temporary file before publishing it."""
    if end_sec <= start_sec:
        raise ValueError("Clip end must be after clip start")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f"{target.stem}.tmp{target.suffix}")
    command = [
        str(ffmpeg),
        "-y",
        "-ss",
        f"{start_sec:.3f}",
        "-i",
        str(source),
        "-t",
        f"{end_sec - start_sec:.3f}",
        "-map",
        "0:v:0",
        "-map",
        "0:a?",
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        str(temporary),
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        if not temporary.exists() or temporary.stat().st_size == 0:
            raise RuntimeError("FFmpeg completed without a non-empty output file")
        temporary.replace(target)
    finally:
        if temporary.exists():
            temporary.unlink()


def export_clip_with_bboxes(
    source: Path,
    start_sec: float,
    end_sec: float,
    target: Path,
    store: PersonDetectionStore,
    *,
    ffmpeg: Path,
) -> None:
    """Export a source-context MP4 with persisted technical bbox overlays.

    The detector is never called here. Boxes follow the same held 5-FPS snapshot
    policy as the interactive viewer while video/audio retain source timing.
    """
    if end_sec <= start_sec:
        raise ValueError("Clip end must be after clip start")
    import cv2

    capture = cv2.VideoCapture(str(source))
    if not capture.isOpened():
        raise RuntimeError(f"OpenCV could not open raw video: {source}")
    fps = capture.get(cv2.CAP_PROP_FPS) or store.source_fps
    width = round(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = round(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if fps <= 0 or width <= 0 or height <= 0:
        capture.release()
        raise RuntimeError("Raw video has unusable FPS or frame dimensions")

    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f"{target.stem}.tmp{target.suffix}")
    capture.set(cv2.CAP_PROP_POS_FRAMES, max(0, round(start_sec * fps)))
    snapshots: dict[int, list] = {}
    for detection in store.detections:
        snapshots.setdefault(detection.source_frame_index, []).append(detection)
    frame_indices = sorted(snapshots)
    command = [
        str(ffmpeg),
        "-y",
        "-f",
        "rawvideo",
        "-pixel_format",
        "bgr24",
        "-video_size",
        f"{width}x{height}",
        "-framerate",
        f"{fps:.6f}",
        "-i",
        "pipe:0",
        "-ss",
        f"{start_sec:.3f}",
        "-i",
        str(source),
        "-t",
        f"{end_sec - start_sec:.3f}",
        "-map",
        "0:v:0",
        "-map",
        "1:a?",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-shortest",
        "-movflags",
        "+faststart",
        str(temporary),
    ]
    process = None
    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            frame_index = max(0, int(capture.get(cv2.CAP_PROP_POS_FRAMES)) - 1)
            timestamp_sec = frame_index / fps
            if timestamp_sec > end_sec:
                break
            detections = held_detections(snapshots, frame_indices, frame_index)
            render_detection_frame(
                frame,
                detections,
                store,
                timestamp_sec,
                frame_index,
                annotated_export=True,
            )
            if process.stdin is None:
                raise RuntimeError("FFmpeg did not provide a video input stream")
            process.stdin.write(frame.tobytes())
        if process.stdin is not None:
            process.stdin.close()
        stderr = process.stderr.read() if process.stderr is not None else b""
        if process.wait():
            raise RuntimeError(f"FFmpeg bbox export failed: {stderr.decode(errors='replace').strip()}")
        if not temporary.exists() or temporary.stat().st_size == 0:
            raise RuntimeError("FFmpeg completed without a non-empty bbox output file")
        temporary.replace(target)
    finally:
        capture.release()
        if process is not None and process.poll() is None:
            process.kill()
            process.wait()
        if temporary.exists():
            temporary.unlink()
