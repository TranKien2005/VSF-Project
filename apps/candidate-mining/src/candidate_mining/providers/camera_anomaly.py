"""Universal camera anomaly mining engine; detects structural, temporal, and distribution anomalies."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..frame_sampling import SampledFrame
from ..models import Signal


@dataclass(frozen=True)
class CameraAnomalySettings:
    analysis_width: int = 640
    grid_size: int = 4  # 4x4 grid (16 patches)
    anomaly_threshold: float = 0.35
    minimum_consecutive_signals: int = 2


class CameraAnomalyProvider:
    """Universal anomaly detector for camera cover, mờ, chói, freeze, and camera movement."""

    def __init__(self, settings: CameraAnomalySettings = CameraAnomalySettings()) -> None:
        self.settings = settings
        self._prev_gray: np.ndarray | None = None
        self._prev_hist: np.ndarray | None = None
        self._baseline_info: list[float] | None = None
        self._baseline_gray: np.ndarray | None = None
        self._baseline_hist: np.ndarray | None = None
        self._consecutive = 0

    def process(self, frame: SampledFrame) -> Signal | None:
        import cv2

        image = frame.bgr
        height, width = image.shape[:2]
        if width > self.settings.analysis_width:
            target_h = round(height * self.settings.analysis_width / width)
            image = cv2.resize(image, (self.settings.analysis_width, target_h))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gh, gw = gray.shape

        # 1. Spatial Information Loss Score (S_spatial) - Relative Sudden Drop vs Baseline
        grid_rows, grid_cols = self.settings.grid_size, self.settings.grid_size
        cell_h, cell_w = gh // grid_rows, gw // grid_cols
        current_patch_infos: list[float] = []
        patch_scores: list[float] = []

        sobel_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        grad_mag = cv2.magnitude(sobel_x, sobel_y)

        for r in range(grid_rows):
            for c in range(grid_cols):
                patch_gray = gray[r * cell_h : (r + 1) * cell_h, c * cell_w : (c + 1) * cell_w]
                patch_grad = grad_mag[r * cell_h : (r + 1) * cell_h, c * cell_w : (c + 1) * cell_w]

                # a) Shannon Information Entropy H(P)
                hist_patch = cv2.calcHist([patch_gray], [0], None, [256], [0, 256]).ravel()
                prob = hist_patch / (hist_patch.sum() + 1e-7)
                prob = prob[prob > 0]
                entropy = float(-np.sum(prob * np.log2(prob)))
                norm_entropy = float(np.clip(entropy / 8.0, 0.0, 1.0))

                # b) Gradient Energy Density G(P)
                mean_grad = float(patch_grad.mean())
                norm_grad = float(np.clip(mean_grad / 40.0, 0.0, 1.0))

                # Patch Information Richness
                info_richness = float(np.sqrt(norm_entropy * norm_grad))
                current_patch_infos.append(info_richness)

        if self._baseline_info is None or len(self._baseline_info) != len(current_patch_infos):
            self._baseline_info = list(current_patch_infos)
            s_spatial = 0.0
        else:
            for base_info, curr_info in zip(self._baseline_info, current_patch_infos):
                info_drop = max(0.0, base_info - curr_info)
                rel_drop = float(np.clip(info_drop / (base_info + 1e-4), 0.0, 1.0))
                patch_scores.append(rel_drop)
            s_spatial = max(patch_scores) if patch_scores else 0.0

        # 2. Temporal Disruption Score (S_temporal) - Relative vs Pre-Event Baseline (Large Changes Only)
        s_temporal = 0.0
        if self._baseline_gray is None or self._baseline_gray.shape != gray.shape:
            self._baseline_gray = gray.copy()
        else:
            diff = cv2.absdiff(gray, self._baseline_gray)
            diff_mean = float(diff.mean() / 255.0)
            s_temporal = float(np.clip(diff_mean / 0.43, 0.0, 1.0))

        # 3. Distribution Shift Score (S_distribution) - Relative vs Pre-Event Baseline
        hist = cv2.calcHist([gray], [0], None, [32], [0, 256])
        cv2.normalize(hist, hist)
        s_dist = 0.0
        if self._baseline_hist is None:
            self._baseline_hist = hist.copy()
        else:
            dist = float(cv2.compareHist(self._baseline_hist, hist, cv2.HISTCMP_BHATTACHARYYA))
            s_dist = float(np.clip(dist / 0.43, 0.0, 1.0))

        self._prev_gray = gray
        self._prev_hist = hist

        # Max fusion
        s_anomaly = max(s_spatial, s_temporal, s_dist)
        suspicious = s_anomaly >= self.settings.anomaly_threshold

        # Update baseline only during normal non-anomaly operation (freeze during anomaly)
        if not suspicious:
            if self._baseline_info is not None:
                self._baseline_info = [
                    float(0.95 * b + 0.05 * c) for b, c in zip(self._baseline_info, current_patch_infos)
                ]
            if self._baseline_gray is not None:
                self._baseline_gray = cv2.addWeighted(self._baseline_gray, 0.95, gray, 0.05, 0)
            if self._baseline_hist is not None:
                self._baseline_hist = 0.95 * self._baseline_hist + 0.05 * hist
                cv2.normalize(self._baseline_hist, self._baseline_hist)

        self._consecutive = self._consecutive + 1 if suspicious else 0
        if self._consecutive < self.settings.minimum_consecutive_signals:
            return None

        brightness = float(gray.mean() / 255.0)
        sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        blur_score = float(np.clip(1.0 - sharpness / 100.0, 0.0, 1.0))

        return Signal(
            timestamp_sec=frame.timestamp_sec,
            category="camera_anomaly",
            brightness_score=brightness,
            blur_score=blur_score,
            motion_score=s_anomaly,
        )
