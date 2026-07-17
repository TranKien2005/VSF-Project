"""Decode a source video once and yield frames at a fixed source-relative cadence."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SampledFrame:
    timestamp_sec: float
    bgr: object
    source_frame_index: int = 0


def sample_video_frames(video_path: Path, sample_fps: float) -> Iterator[SampledFrame]:
    """Yield BGR frames at a fixed cadence; requires the optional vision extra."""
    if sample_fps <= 0:
        raise ValueError("sample_fps must be positive")
    import cv2

    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise RuntimeError(f"OpenCV could not open video: {video_path}")
    try:
        source_fps = capture.get(cv2.CAP_PROP_FPS)
        if source_fps <= 0:
            source_fps = sample_fps
        frame_interval = max(1, round(source_fps / sample_fps))
        index = 0
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            if index % frame_interval == 0:
                timestamp = capture.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                yield SampledFrame(timestamp_sec=timestamp, bgr=frame, source_frame_index=index)
            index += 1
    finally:
        capture.release()
