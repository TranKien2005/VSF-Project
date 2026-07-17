"""Within-camera technical person tracking and episode grouping."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class PersonDetection:
    timestamp_sec: float
    bbox_xyxy: tuple[float, float, float, float]
    confidence: float
    source_frame_index: int = 0


@dataclass(frozen=True)
class TrackObservation:
    timestamp_sec: float
    track_id: int
    episode_id: str
    reconciliation_status: str
    detection: PersonDetection


@dataclass
class _ActiveTrack:
    track_id: int
    episode_id: str
    last_timestamp_sec: float
    last_bbox_xyxy: tuple[float, float, float, float]


def _iou(left: tuple[float, float, float, float], right: tuple[float, float, float, float]) -> float:
    x1 = max(left[0], right[0])
    y1 = max(left[1], right[1])
    x2 = min(left[2], right[2])
    y2 = min(left[3], right[3])
    overlap = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    if overlap == 0:
        return 0.0
    left_area = (left[2] - left[0]) * (left[3] - left[1])
    right_area = (right[2] - right[0]) * (right[3] - right[1])
    return overlap / max(left_area + right_area - overlap, 1.0)


def _center_distance(left: tuple[float, float, float, float], right: tuple[float, float, float, float]) -> float:
    left_center = ((left[0] + left[2]) / 2, (left[1] + left[3]) / 2)
    right_center = ((right[0] + right[2]) / 2, (right[1] + right[3]) / 2)
    return math.dist(left_center, right_center)


class PersonEpisodeTracker:
    """Track bbox continuity in one source; IDs have no identity/business semantics."""

    def __init__(
        self,
        gap_seconds: float = 8.0,
        iou_threshold: float = 0.15,
        center_distance_ratio: float = 0.20,
    ) -> None:
        self.gap_seconds = gap_seconds
        self.iou_threshold = iou_threshold
        self.center_distance_ratio = center_distance_ratio
        self._active: dict[int, _ActiveTrack] = {}
        self._next_track_id = 1
        self._next_episode_number = 1

    def update(
        self,
        timestamp_sec: float,
        detections: list[PersonDetection],
        frame_diagonal: float,
    ) -> list[TrackObservation]:
        active = {
            track_id: track
            for track_id, track in self._active.items()
            if timestamp_sec - track.last_timestamp_sec <= self.gap_seconds
        }
        unmatched_tracks = set(active)
        observations: list[TrackObservation] = []
        for detection in sorted(detections, key=lambda item: item.confidence, reverse=True):
            candidates: list[tuple[float, int]] = []
            for track_id in unmatched_tracks:
                track = active[track_id]
                iou = _iou(track.last_bbox_xyxy, detection.bbox_xyxy)
                distance = _center_distance(track.last_bbox_xyxy, detection.bbox_xyxy)
                if iou >= self.iou_threshold or distance <= frame_diagonal * self.center_distance_ratio:
                    candidates.append((max(iou, 1 - distance / max(frame_diagonal, 1.0)), track_id))
            if candidates:
                _, track_id = max(candidates)
                track = active[track_id]
                status = "continuous" if timestamp_sec == track.last_timestamp_sec else "reassociated_id_change"
                episode_id = track.episode_id
                unmatched_tracks.remove(track_id)
            else:
                track_id = self._next_track_id
                self._next_track_id += 1
                episode_id = f"episode_{self._next_episode_number:06d}"
                self._next_episode_number += 1
                status = "new_episode"
            self._active[track_id] = _ActiveTrack(
                track_id, episode_id, timestamp_sec, detection.bbox_xyxy
            )
            observations.append(
                TrackObservation(timestamp_sec, track_id, episode_id, status, detection)
            )
        self._active = {
            track_id: track
            for track_id, track in self._active.items()
            if timestamp_sec - track.last_timestamp_sec <= self.gap_seconds
        }
        return observations
