"""Full-frame person detection routed into ROI-filtered person_detected candidates."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from .automatic_signals import generate_automatic_signals
from .config import AppConfig
from .debug_artifacts import PersonDetectionStore
from .processed_store import effective_roi_path, list_sources, resolve_source
from .processing_progress import ProcessingProgress
from .result_store import write_roi_filtered_person_candidates
from .roi import read_roi
from .segments import merge_person_presence_signals


def person_presence_segments(signals, config: AppConfig):  # type: ignore[no-untyped-def]
    """Build source-level any-person spans for technical candidate handoff."""
    return merge_person_presence_signals(signals, config.pipeline.person_presence_merge_gap_seconds)


def run_pipeline(
    video_path: Path,
    config: AppConfig,
    *,
    on_progress: Callable[[ProcessingProgress], None] | None = None,
    is_cancelled: Callable[[], bool] | None = None,
    batch_size_override: int | None = None,
) -> list[Path]:
    """Detect full-frame people, then publish only ROI-filtered person_detected candidates."""
    record = _registered_source(video_path, config)
    source = resolve_source(record)
    roi_path, roi_scope = effective_roi_path(config.paths.processed_dir, record)
    if not roi_path or not roi_scope:
        raise ValueError("Draw and save one valid track ROI before processing this source.")
    roi = read_roi(roi_path)
    signals, observations, frame_size = generate_automatic_signals(
        source,
        config,
        on_progress=on_progress,
        is_cancelled=is_cancelled,
        batch_size_override=batch_size_override,
    )
    if frame_size is None:
        raise RuntimeError(f"No readable frames were found in source video: {source}")
    width, height = frame_size
    import cv2

    capture = cv2.VideoCapture(str(source))
    try:
        source_fps = capture.get(cv2.CAP_PROP_FPS)
        frame_count = capture.get(cv2.CAP_PROP_FRAME_COUNT)
    finally:
        capture.release()
    if source_fps <= 0:
        source_fps = config.pipeline.sample_fps
    duration_seconds = frame_count / source_fps if frame_count > 0 else record.duration_seconds
    settings = config.providers.person_rtdetr if config.providers.person_rtdetr["enabled"] else config.providers.person_yolo
    store = PersonDetectionStore.from_observations(
        source,
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
    return write_roi_filtered_person_candidates(
        store,
        config.paths.results_dir,
        source_id=record.source_id,
        camera_id=record.camera_id,
        roi=roi,
        merge_gap_seconds=config.pipeline.person_presence_merge_gap_seconds,
        duration_seconds=duration_seconds,
        pre_roll_seconds=config.pipeline.pre_roll_seconds,
        post_roll_seconds=config.pipeline.post_roll_seconds,
        roi_scope=roi_scope,
    )


def _registered_source(video_path: Path, config: AppConfig):  # type: ignore[no-untyped-def]
    resolved = video_path.resolve()
    for record in list_sources(config.paths.processed_dir):
        if Path(record.raw_absolute_path_at_registration) == resolved:
            return record
    raise ValueError("Import this video in Sources before processing it.")
