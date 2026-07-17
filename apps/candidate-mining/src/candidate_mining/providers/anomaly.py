"""Low-cost anomaly signals retained for human review rather than forced labels."""

from __future__ import annotations

from dataclasses import dataclass

from ..frame_sampling import SampledFrame
from ..models import Signal


@dataclass(frozen=True)
class AnomalySettings:
    motion_score_threshold: float = 0.08
    black_brightness_threshold: float = 0.03
    uniform_variance_threshold: float = 5.0
    freeze_difference_threshold: float = 0.002
    minimum_consecutive_signals: int = 3


class AnomalyProvider:
    """Emit unresolved visual anomaly evidence; it never assigns an event label."""

    def __init__(self, settings: AnomalySettings = AnomalySettings()) -> None:
        self.settings = settings
        self._previous_gray: object | None = None
        self._freeze_count = 0
        self._motion_count = 0

    def process(self, frame: SampledFrame, has_accepted_person: bool) -> list[Signal]:
        import cv2
        import numpy as np

        gray = cv2.cvtColor(frame.bgr, cv2.COLOR_BGR2GRAY)
        brightness = float(gray.mean() / 255.0)
        variance = float(gray.var())
        signals: list[Signal] = []
        if brightness <= self.settings.black_brightness_threshold and variance <= self.settings.uniform_variance_threshold:
            signals.append(
                Signal(
                    frame.timestamp_sec,
                    "anomaly_unknown",
                    brightness_score=brightness,
                    anomaly_types=("black_screen", "signal_loss_candidate"),
                )
            )
        if self._previous_gray is not None:
            difference = float(np.abs(gray.astype("float32") - self._previous_gray.astype("float32")).mean() / 255.0)
            self._freeze_count = self._freeze_count + 1 if difference <= self.settings.freeze_difference_threshold else 0
            self._motion_count = self._motion_count + 1 if difference >= self.settings.motion_score_threshold else 0
            if self._freeze_count >= self.settings.minimum_consecutive_signals:
                signals.append(
                    Signal(frame.timestamp_sec, "anomaly_unknown", motion_score=difference, anomaly_types=("frozen_video",))
                )
            if self._motion_count >= self.settings.minimum_consecutive_signals and not has_accepted_person:
                signals.append(
                    Signal(
                        frame.timestamp_sec,
                        "anomaly_unknown",
                        motion_score=difference,
                        anomaly_types=("motion_without_person",),
                    )
                )
        self._previous_gray = gray
        return signals
