"""Global-motion signals suggesting possible camera displacement or shake."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..frame_sampling import SampledFrame
from ..models import Signal


@dataclass(frozen=True)
class MovementSettings:
    analysis_width: int = 640
    max_corners: int = 300
    quality_level: float = 0.01
    min_distance_px: int = 8
    min_tracked_points: int = 30
    min_inlier_ratio: float = 0.60
    translation_threshold_px: float = 12.0
    rotation_threshold_deg: float = 1.5
    scale_delta_threshold: float = 0.03
    shift_score_threshold: float = 0.65
    scene_change_histogram_threshold: float = 0.70
    minimum_consecutive_signals: int = 2


class CameraMovementProvider:
    """Use robust global feature displacement; this is not a confirmed tamper label."""

    def __init__(self, settings: MovementSettings = MovementSettings()) -> None:
        self.settings = settings
        self._previous_gray: object | None = None
        self._previous_histogram: object | None = None
        self._consecutive = 0

    def process(self, frame: SampledFrame) -> Signal | None:
        import cv2

        image = frame.bgr
        height, width = image.shape[:2]
        if width > self.settings.analysis_width:
            image = cv2.resize(image, (self.settings.analysis_width, round(height * self.settings.analysis_width / width)))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        histogram = cv2.calcHist([gray], [0], None, [32], [0, 256])
        cv2.normalize(histogram, histogram)
        if self._previous_gray is None:
            self._previous_gray, self._previous_histogram = gray, histogram
            return None
        scene_change = float(cv2.compareHist(self._previous_histogram, histogram, cv2.HISTCMP_BHATTACHARYYA))
        previous_gray = self._previous_gray
        self._previous_gray, self._previous_histogram = gray, histogram
        if scene_change >= self.settings.scene_change_histogram_threshold:
            self._consecutive = 0
            return None
        points = cv2.goodFeaturesToTrack(
            previous_gray,
            maxCorners=self.settings.max_corners,
            qualityLevel=self.settings.quality_level,
            minDistance=self.settings.min_distance_px,
        )
        if points is None or len(points) < self.settings.min_tracked_points:
            self._consecutive = 0
            return None
        tracked, status, _ = cv2.calcOpticalFlowPyrLK(previous_gray, gray, points, None)
        if tracked is None or status is None:
            self._consecutive = 0
            return None
        source = points[status.ravel() == 1]
        target = tracked[status.ravel() == 1]
        if len(source) < self.settings.min_tracked_points:
            self._consecutive = 0
            return None
        matrix, inliers = cv2.estimateAffinePartial2D(source, target, method=cv2.RANSAC)
        if matrix is None or inliers is None:
            self._consecutive = 0
            return None
        inlier_ratio = float(inliers.mean())
        if inlier_ratio < self.settings.min_inlier_ratio:
            self._consecutive = 0
            return None
        translation = math.hypot(float(matrix[0, 2]), float(matrix[1, 2]))
        rotation = abs(math.degrees(math.atan2(float(matrix[1, 0]), float(matrix[0, 0]))))
        scale = math.hypot(float(matrix[0, 0]), float(matrix[1, 0]))
        scale_delta = abs(scale - 1.0)
        score = max(
            min(1.0, translation / self.settings.translation_threshold_px),
            min(1.0, rotation / self.settings.rotation_threshold_deg),
            min(1.0, scale_delta / self.settings.scale_delta_threshold),
        )
        suspicious = score >= self.settings.shift_score_threshold
        self._consecutive = self._consecutive + 1 if suspicious else 0
        if self._consecutive < self.settings.minimum_consecutive_signals:
            return None
        return Signal(
            timestamp_sec=frame.timestamp_sec,
            category="camera_movement",
            motion_score=score,
            camera_shift_score=score,
        )
