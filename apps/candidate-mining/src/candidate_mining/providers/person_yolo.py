"""Local-only YOLO person provider for review-candidate signals."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..frame_sampling import SampledFrame
from ..models import Signal
from ..tracking import PersonDetection
from ..weights import verify_weights


@dataclass(frozen=True)
class PersonYoloSettings:
    confidence_threshold: float = 0.35
    iou_threshold: float = 0.45
    image_size: int = 640
    batch_size: int = 8
    device: str = "auto"
    half_precision: bool = True


class YoloPersonProvider:
    """Load verified local weights only; never request a model name from a hub."""

    def __init__(self, weights_path: Path, settings: PersonYoloSettings = PersonYoloSettings()) -> None:
        self.weights_path = weights_path
        self.settings = settings
        self._model: object | None = None
        self._device: str | int | None = None

    @property
    def selected_device(self) -> str | int | None:
        return self._device

    def _resolve_device(self) -> str | int:
        import torch

        if self.settings.device != "auto":
            if str(self.settings.device).startswith("cuda") and not torch.cuda.is_available():
                raise RuntimeError("CUDA was requested but is unavailable in the active PyTorch runtime")
            return self.settings.device
        return 0 if torch.cuda.is_available() else "cpu"

    def _load_model(self) -> None:
        if self._model is not None:
            return
        verify_weights(self.weights_path)
        from ultralytics import YOLO

        self._device = self._resolve_device()
        self._model = YOLO(str(self.weights_path.resolve()))

    def detect_batch(self, frames: list[SampledFrame]) -> list[list[PersonDetection]]:
        if not frames:
            return []
        self._load_model()
        images = [frame.bgr for frame in frames]
        results = self._model.predict(
            images,
            classes=[0],
            conf=self.settings.confidence_threshold,
            iou=self.settings.iou_threshold,
            imgsz=self.settings.image_size,
            device=self._device,
            half=bool(self.settings.half_precision and self._device != "cpu"),
            verbose=False,
        )
        output: list[list[PersonDetection]] = []
        for frame, result in zip(frames, results, strict=True):
            detections: list[PersonDetection] = []
            if result.boxes is not None:
                for xyxy, confidence in zip(result.boxes.xyxy.tolist(), result.boxes.conf.tolist(), strict=True):
                    detections.append(
                        PersonDetection(frame.timestamp_sec, tuple(xyxy), float(confidence), frame.source_frame_index)
                    )
            output.append(detections)
        return output

    def process_batch(self, frames: list[SampledFrame]) -> list[Signal]:
        """Compatibility helper for callers that only need frame-level person signals."""
        detections_by_frame = self.detect_batch(frames)
        signals: list[Signal] = []
        for frame, detections in zip(frames, detections_by_frame, strict=True):
            if detections:
                signals.append(
                    Signal(
                        timestamp_sec=frame.timestamp_sec,
                        category="person_detected",
                        person_count=len(detections),
                    )
                )
        return signals
