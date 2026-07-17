"""Viewer-only person-detection POC pipeline."""

from __future__ import annotations

from pathlib import Path

from .automatic_signals import generate_automatic_signals
from .config import AppConfig
from .debug_artifacts import PersonDetectionStore, write_person_detection_store
from .models import Signal
from .segments import merge_person_presence_signals


def person_presence_segments(signals: list[Signal], config: AppConfig):
    """Build source-level any-person spans for later candidate handoff."""
    return merge_person_presence_signals(signals, config.pipeline.person_presence_merge_gap_seconds)


def run_pipeline(video_path: Path, config: AppConfig) -> Path:
    """Run local person detection and replace one source-owned JSON artifact only."""
    signals, observations, frame_size = generate_automatic_signals(video_path, config)
    if frame_size is None:
        raise RuntimeError(f"No readable frames were found in source video: {video_path}")
    width, height = frame_size
    import cv2

    capture = cv2.VideoCapture(str(video_path))
    try:
        source_fps = capture.get(cv2.CAP_PROP_FPS)
        frame_count = capture.get(cv2.CAP_PROP_FRAME_COUNT)
    finally:
        capture.release()
    if source_fps <= 0:
        source_fps = config.pipeline.sample_fps
    duration_seconds = frame_count / source_fps if frame_count > 0 else 0.0
    settings = config.providers.person_rtdetr if config.providers.person_rtdetr["enabled"] else config.providers.person_yolo
    store = PersonDetectionStore.from_observations(
        video_path,
        observations,
        source_fps=source_fps,
        frame_width=width,
        frame_height=height,
        sample_fps=config.pipeline.sample_fps,
        image_size=int(settings["image_size"]),
        confidence_threshold=float(settings["confidence_threshold"]),
        person_presence_segments=person_presence_segments(signals, config),
        duration_seconds=duration_seconds,
        pre_roll_seconds=config.pipeline.pre_roll_seconds,
        post_roll_seconds=config.pipeline.post_roll_seconds,
    )
    return write_person_detection_store(
        store, config.paths.review_queue_dir, video_path, raw_dir=config.paths.raw_dir
    )
