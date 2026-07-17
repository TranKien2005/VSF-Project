"""Typed records shared by the candidate-mining pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

TOOL_CATEGORIES = (
    "person_detected",
    "camera_cover",
    "camera_movement",
    "anomaly_unknown",
)
ALL_CATEGORIES = (*TOOL_CATEGORIES, "random_background")
ANOMALY_TYPES = (
    "motion_without_person",
    "image_quality_change",
    "frozen_video",
    "black_screen",
    "signal_loss_candidate",
    "unexplained_scene_change",
    "uncertain_person",
    "fragmented_person_track",
)
MANIFEST_FIELDS = (
    "sample_id",
    "source_id",
    "source_path",
    "camera_id",
    "clip_path",
    "clip_start_sec",
    "clip_end_sec",
    "categories",
    "candidate_start_sec",
    "candidate_end_sec",
    "selection_source",
    "person_count_max",
    "motion_score",
    "brightness_score",
    "blur_score",
    "camera_shift_score",
    "context_status",
    "review_status",
    "anomaly_types",
    "person_track_ids",
    "person_episode_ids",
    "track_reconciliation_status",
)


@dataclass(frozen=True)
class VideoInventory:
    source_id: str
    source_path: str
    filename: str
    size_bytes: int
    sha256: str
    duration_seconds: float
    fps: float | None
    width: int | None
    height: int | None
    codec: str | None
    container: str | None
    has_audio: bool


@dataclass(frozen=True)
class Signal:
    timestamp_sec: float
    category: Literal["person_detected", "camera_cover", "camera_movement", "anomaly_unknown"]
    person_count: int | None = None
    motion_score: float | None = None
    brightness_score: float | None = None
    blur_score: float | None = None
    camera_shift_score: float | None = None
    anomaly_types: tuple[str, ...] = ()
    track_ids: tuple[int, ...] = ()
    episode_ids: tuple[str, ...] = ()
    track_reconciliation_status: str | None = None


@dataclass
class Segment:
    start_sec: float
    end_sec: float
    categories: set[str] = field(default_factory=set)
    person_count_max: int | None = None
    motion_score: float | None = None
    brightness_score: float | None = None
    blur_score: float | None = None
    camera_shift_score: float | None = None
    anomaly_types: set[str] = field(default_factory=set)
    track_ids: set[int] = field(default_factory=set)
    episode_ids: set[str] = field(default_factory=set)
    track_reconciliation_statuses: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class ClipWindow:
    start_sec: float
    end_sec: float
    context_status: str


@dataclass(frozen=True)
class CandidateSample:
    sample_id: str
    source_id: str
    source_path: str
    camera_id: str
    clip_path: str
    clip_start_sec: float
    clip_end_sec: float
    categories: tuple[str, ...]
    candidate_start_sec: float | None
    candidate_end_sec: float | None
    selection_source: str
    person_count_max: int | None = None
    motion_score: float | None = None
    brightness_score: float | None = None
    blur_score: float | None = None
    camera_shift_score: float | None = None
    context_status: str = "sufficient"
    review_status: str = "pending_review"
    anomaly_types: tuple[str, ...] = ()
    person_track_ids: tuple[int, ...] = ()
    person_episode_ids: tuple[str, ...] = ()
    track_reconciliation_status: tuple[str, ...] = ()

    def to_manifest_row(self) -> dict[str, str | int | float]:
        def value(item: object | None) -> object:
            return "" if item is None else item

        return {
            "sample_id": self.sample_id,
            "source_id": self.source_id,
            "source_path": self.source_path,
            "camera_id": self.camera_id,
            "clip_path": self.clip_path,
            "clip_start_sec": self.clip_start_sec,
            "clip_end_sec": self.clip_end_sec,
            "categories": "|".join(self.categories),
            "candidate_start_sec": value(self.candidate_start_sec),
            "candidate_end_sec": value(self.candidate_end_sec),
            "selection_source": self.selection_source,
            "person_count_max": value(self.person_count_max),
            "motion_score": value(self.motion_score),
            "brightness_score": value(self.brightness_score),
            "blur_score": value(self.blur_score),
            "camera_shift_score": value(self.camera_shift_score),
            "context_status": self.context_status,
            "review_status": self.review_status,
            "anomaly_types": "|".join(self.anomaly_types),
            "person_track_ids": "|".join(map(str, self.person_track_ids)),
            "person_episode_ids": "|".join(self.person_episode_ids),
            "track_reconciliation_status": "|".join(self.track_reconciliation_status),
        }
