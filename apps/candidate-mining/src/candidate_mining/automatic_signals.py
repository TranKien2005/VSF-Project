"""Run enabled candidate providers over one sampled frame stream."""

from __future__ import annotations

import os
import time
from collections.abc import Callable
from dataclasses import fields
from pathlib import Path

from .config import AppConfig
from .frame_sampling import sample_video_frames
from .models import Signal
from .processing_progress import ProcessingProgress, estimate_eta, estimated_sample_count
from .providers.camera_anomaly import CameraAnomalyProvider
from .providers.person_rtdetr import PersonRtdetrSettings, RtdetrPersonProvider
from .providers.person_yolo import PersonYoloSettings, YoloPersonProvider
from .tracking import PersonEpisodeTracker, TrackObservation


class ProcessingCancelled(Exception):
    """Raised cooperatively before a pipeline run publishes result artifacts."""


def _settings(settings_type: type, values: dict[str, object]):
    permitted = {field.name for field in fields(settings_type)}
    return settings_type(**{key: value for key, value in values.items() if key in permitted})


def runtime_summary(config: AppConfig, person: object | None) -> str:
    provider_name, settings = _person_provider_config(config)
    device = person.selected_device if person else "disabled"
    return (
        f"sample_fps={config.pipeline.sample_fps}; person_provider={provider_name}; device={device}; "
        f"imgsz={settings['image_size']}; batch={settings['batch_size']}"
    )


def _person_provider_config(config: AppConfig) -> tuple[str, dict[str, object]]:
    enabled = [("yolo11n", config.providers.person_yolo), ("rtdetr-l", config.providers.person_rtdetr)]
    active = [(name, settings) for name, settings in enabled if settings["enabled"]]
    if len(active) != 1:
        raise ValueError("Exactly one person provider must be enabled")
    return active[0]


def _expected_samples(video_path: Path, sample_fps: float) -> int | None:
    import cv2

    capture = cv2.VideoCapture(str(video_path))
    try:
        if not capture.isOpened():
            return None
        return estimated_sample_count(
            capture.get(cv2.CAP_PROP_FRAME_COUNT),
            capture.get(cv2.CAP_PROP_FPS),
            sample_fps,
        )
    finally:
        capture.release()


def _resolve_device_name(person: object | None) -> str:
    try:
        import torch

        if torch.cuda.is_available():
            return f"GPU 0 ({torch.cuda.get_device_name(0)})"
    except (ImportError, RuntimeError):
        pass
    if person and getattr(person, "selected_device", None):
        return str(person.selected_device)
    return "CPU"


def generate_automatic_signals(
    video_path: Path,
    config: AppConfig,
    *,
    on_progress: Callable[[ProcessingProgress], None] | None = None,
    is_cancelled: Callable[[], bool] | None = None,
    batch_size_override: int | None = None,
    sample_fps_override: float | None = None,
) -> tuple[list[Signal], list[TrackObservation], tuple[int, int] | None]:
    """Generate signals while reporting only frames that completed processing."""
    os.environ.setdefault("TORCH_HOME", str(config.paths.torch_cache_dir))
    effective_sample_fps = (
        sample_fps_override if sample_fps_override is not None and sample_fps_override > 0 else config.pipeline.sample_fps
    )
    person_name, person_raw = _person_provider_config(config)
    configured_batch_size = int(person_raw.get("batch_size", 1))
    batch_size = batch_size_override if batch_size_override is not None else configured_batch_size
    if not isinstance(batch_size, int) or batch_size <= 0:
        raise ValueError("Person provider batch size must be a positive integer")
    total_samples = _expected_samples(video_path, effective_sample_fps)
    started_at = time.monotonic()
    completed = 0
    latest_timestamp: float | None = None
    person: YoloPersonProvider | RtdetrPersonProvider | None = None

    def cancelled() -> bool:
        return bool(is_cancelled and is_cancelled())

    def report(phase: str, message: str) -> None:
        if not on_progress:
            return
        elapsed = time.monotonic() - started_at
        on_progress(
            ProcessingProgress(
                phase=phase,
                processed_samples=completed,
                total_samples=total_samples,
                source_timestamp_sec=latest_timestamp,
                elapsed_seconds=elapsed,
                eta_seconds=estimate_eta(elapsed, completed, total_samples),
                configured_batch_size=batch_size,
                effective_batch_size=batch_size,
                device=_resolve_device_name(person),
                message=message,
            )
        )

    report("preparing", "Preparing source and providers")
    camera_anomaly_provider = CameraAnomalyProvider()
    person_optional = bool(person_raw.get("optional", False))
    try:
        if person_name == "rtdetr-l":
            person = RtdetrPersonProvider(config.providers.rtdetr_l_weights, _settings(PersonRtdetrSettings, person_raw))
        else:
            person = YoloPersonProvider(config.providers.yolo11n_weights, _settings(PersonYoloSettings, person_raw))
        report("loading_model", "Loading person detector")
        person._load_model()
    except (FileNotFoundError, ImportError, ModuleNotFoundError) as error:
        if not person_optional:
            raise RuntimeError(f"Person provider could not start: {error}") from error
        person = None

    signals: list[Signal] = []
    observations: list[TrackObservation] = []
    frame_size: tuple[int, int] | None = None
    pending_person_frames = []
    tracker = PersonEpisodeTracker(
        gap_seconds=float(person_raw.get("person_episode_gap_seconds", 8.0)),
        movement_threshold_ratio=float(person_raw.get("movement_threshold_ratio", 0.5)),
    )

    def process_person_batch() -> None:
        nonlocal completed, frame_size, latest_timestamp, pending_person_frames
        if not person or not pending_person_frames:
            return
        if cancelled():
            raise ProcessingCancelled("Processing cancelled before inference batch")
        frames = pending_person_frames
        detections_by_frame = person.detect_batch(frames)
        for frame, detections in zip(frames, detections_by_frame, strict=True):
            if cancelled():
                raise ProcessingCancelled("Processing cancelled during batch evaluation")

            height, width = frame.bgr.shape[:2]
            frame_size = (width, height)
            diagonal = (height**2 + width**2) ** 0.5
            frame_observations = tracker.update(frame.timestamp_sec, detections, diagonal)
            observations.extend(frame_observations)
            for observation in frame_observations:
                if observation.motion_confirmed:
                    signals.append(
                        Signal(
                            timestamp_sec=observation.timestamp_sec,
                            category="person_detected",
                            person_count=1,
                            track_ids=(observation.track_id,),
                            episode_ids=(observation.episode_id,),
                            track_reconciliation_status=observation.reconciliation_status,
                        )
                    )
            completed += 1
            latest_timestamp = frame.timestamp_sec
        pending_person_frames = []
        report("detecting", "Detecting and tracking person evidence")

    for frame in sample_video_frames(video_path, effective_sample_fps):
        if cancelled():
            raise ProcessingCancelled("Processing cancelled during source decoding")
        if camera_anomaly_provider:
            sig = camera_anomaly_provider.process(frame)
            if sig:
                signals.append(sig)
        if person:
            pending_person_frames.append(frame)
            if len(pending_person_frames) >= batch_size:
                process_person_batch()
        else:
            completed += 1
            latest_timestamp = frame.timestamp_sec
            report("detecting", "Sampling technical signals")
    if person and pending_person_frames:
        process_person_batch()
    return signals, observations, frame_size
