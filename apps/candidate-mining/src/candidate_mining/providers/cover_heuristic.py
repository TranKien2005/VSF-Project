"""Explainable visual signals suggesting a possible camera-cover condition."""

from __future__ import annotations

from dataclasses import dataclass

from ..frame_sampling import SampledFrame
from ..models import Signal


@dataclass(frozen=True)
class CoverSettings:
    analysis_width: int = 640
    dark_pixel_threshold: int = 35
    dark_pixel_ratio_threshold: float = 0.85
    brightness_low_threshold: float = 0.18
    brightness_delta_threshold: float = 0.40
    blur_laplacian_reference: float = 100.0
    blur_score_threshold: float = 0.80
    edge_density_threshold: float = 0.015
    histogram_distance_threshold: float = 0.55
    minimum_consecutive_signals: int = 3


class CoverHeuristicProvider:
    """Emit technical cover candidates; environmental effects can also trigger them."""

    def __init__(self, settings: CoverSettings = CoverSettings()) -> None:
        self.settings = settings
        self._previous_brightness: float | None = None
        self._previous_histogram: object | None = None
        self._consecutive = 0

    def process(self, frame: SampledFrame) -> Signal | None:
        import cv2
        import numpy as np

        image = frame.bgr
        height, width = image.shape[:2]
        if width > self.settings.analysis_width:
            image = cv2.resize(image, (self.settings.analysis_width, round(height * self.settings.analysis_width / width)))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        brightness = float(gray.mean() / 255.0)
        dark_ratio = float((gray <= self.settings.dark_pixel_threshold).mean())
        sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        blur_score = float(np.clip(1.0 - sharpness / self.settings.blur_laplacian_reference, 0.0, 1.0))
        edges = cv2.Canny(gray, 100, 200)
        edge_density = float((edges > 0).mean())
        histogram = cv2.calcHist([gray], [0], None, [32], [0, 256])
        cv2.normalize(histogram, histogram)
        brightness_delta = abs(brightness - self._previous_brightness) if self._previous_brightness is not None else 0.0
        histogram_distance = (
            float(cv2.compareHist(self._previous_histogram, histogram, cv2.HISTCMP_BHATTACHARYYA))
            if self._previous_histogram is not None
            else 0.0
        )
        self._previous_brightness = brightness
        self._previous_histogram = histogram
        suspicious = (
            (dark_ratio >= self.settings.dark_pixel_ratio_threshold and brightness <= self.settings.brightness_low_threshold)
            or (blur_score >= self.settings.blur_score_threshold and edge_density <= self.settings.edge_density_threshold)
            or (
                brightness_delta >= self.settings.brightness_delta_threshold
                and histogram_distance >= self.settings.histogram_distance_threshold
            )
        )
        self._consecutive = self._consecutive + 1 if suspicious else 0
        if self._consecutive < self.settings.minimum_consecutive_signals:
            return None
        return Signal(
            timestamp_sec=frame.timestamp_sec,
            category="camera_cover",
            brightness_score=brightness,
            blur_score=blur_score,
            motion_score=max(brightness_delta, histogram_distance),
        )
