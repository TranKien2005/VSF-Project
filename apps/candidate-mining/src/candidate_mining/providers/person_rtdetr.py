"""Local-only RT-DETR COCO person provider for visual POC evidence."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..frame_sampling import SampledFrame
from ..tracking import PersonDetection
from ..weights import verify_weights
from .person_yolo import PersonYoloSettings


@dataclass(frozen=True)
class PersonRtdetrSettings(PersonYoloSettings):
    batch_size: int = 1


class RtdetrPersonProvider:
    """Load only an explicit verified local RT-DETR checkpoint."""

    def __init__(self, weights_path: Path, settings: PersonRtdetrSettings = PersonRtdetrSettings()) -> None:
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
        from ultralytics import RTDETR

        self._device = self._resolve_device()
        self._model = RTDETR(str(self.weights_path.resolve()))

    def detect_batch(self, frames: list[SampledFrame]) -> list[list[PersonDetection]]:
        if not frames:
            return []
        self._load_model()
        results = self._model.predict(
            [frame.bgr for frame in frames],
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
