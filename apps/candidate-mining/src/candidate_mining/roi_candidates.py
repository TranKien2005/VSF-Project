"""Derive review-assistance candidates from persisted full-frame detections."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from itertools import groupby
from pathlib import Path

from .debug_artifacts import PersonDetectionStore
from .roi import OperatorRoiConfig, detection_footpoint, normalized_to_pixel, point_in_polygon
from .segments import proxy_window

SCHEMA_VERSION = "operator-roi-candidates.v1"
POLICY_VERSION = "capture-zone-occupancy.v1"


@dataclass(frozen=True)
class RoiCandidate:
    candidate_id: str
    source_sha256: str
    camera_id: str
    roi_config_id: str
    roi_config_revision: int
    roi_config_snapshot_sha256: str
    policy_version: str
    trigger_roi_id: str
    trigger_reason: str
    candidate_start_sec: float
    candidate_end_sec: float
    context_start_sec: float
    context_end_sec: float
    context_status: str
    person_count_max: int
    track_ids: tuple[int, ...]
    episode_ids: tuple[str, ...]
    core_roi_ids: tuple[str, ...]


@dataclass(frozen=True)
class RoiCandidateStore:
    source_sha256: str
    camera_id: str
    candidates: tuple[RoiCandidate, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": SCHEMA_VERSION,
            "source_sha256": self.source_sha256,
            "camera_id": self.camera_id,
            "candidates": [asdict(candidate) for candidate in self.candidates],
        }


def mine_candidates(
    store: PersonDetectionStore,
    config: OperatorRoiConfig,
    *,
    duration_seconds: float,
    merge_gap_seconds: float,
    pre_roll_seconds: float,
    post_roll_seconds: float,
) -> RoiCandidateStore:
    """Create capture-zone candidates without altering full-frame detections."""
    if store.source_sha256 != config.reference_source_sha256:
        # A config may be reused across sources from the camera. Its reference hash is provenance, not source identity.
        pass
    if min(merge_gap_seconds, pre_roll_seconds, post_roll_seconds) < 0:
        raise ValueError("Candidate gap and context durations must be non-negative")
    capture_shapes = [shape for shape in config.shapes if shape.enabled and shape.kind == "polygon" and shape.role == "capture"]
    core_shapes = [shape for shape in config.shapes if shape.enabled and shape.kind == "polygon" and shape.role == "core"]
    snapshot_hash = config.snapshot_hash()
    candidates: list[RoiCandidate] = []
    for shape in capture_shapes:
        width, height = store.frame_width, store.frame_height
        polygon = tuple(normalized_to_pixel(point, width, height) for point in shape.points_normalized)
        observations: list[tuple[float, object]] = [
            (detection.timestamp_sec, detection)
            for detection in store.detections
            if point_in_polygon(detection_footpoint(detection.bbox_xyxy_px), polygon)
        ]
        for index, group in enumerate(_merge_observations(observations, merge_gap_seconds), start=1):
            first_timestamp = group[0][0]
            last_timestamp = group[-1][0]
            window = proxy_window(first_timestamp, last_timestamp, duration_seconds, pre_roll_seconds, post_roll_seconds)
            tracks = tuple(sorted({item.track_id for _, item in group}))
            episodes = tuple(sorted({item.episode_id for _, item in group}))
            core_ids = tuple(core.roi_id for core in core_shapes if _has_core_evidence(group, core, width, height))
            trigger_reason = "present_in_capture_zone_at_source_start" if first_timestamp == 0.0 else "person_in_capture_zone"
            candidate_id = _candidate_id(store.source_sha256, shape.roi_id, index, first_timestamp, last_timestamp)
            candidates.append(
                RoiCandidate(
                    candidate_id=candidate_id,
                    source_sha256=store.source_sha256,
                    camera_id=config.camera_id,
                    roi_config_id=config.roi_config_id,
                    roi_config_revision=config.revision,
                    roi_config_snapshot_sha256=snapshot_hash,
                    policy_version=POLICY_VERSION,
                    trigger_roi_id=shape.roi_id,
                    trigger_reason=trigger_reason,
                    candidate_start_sec=first_timestamp,
                    candidate_end_sec=last_timestamp,
                    context_start_sec=window.start_sec,
                    context_end_sec=window.end_sec,
                    context_status=window.context_status,
                    person_count_max=max(_count_at_timestamp(group, timestamp) for timestamp, _ in group),
                    track_ids=tracks,
                    episode_ids=episodes,
                    core_roi_ids=core_ids,
                )
            )
    return RoiCandidateStore(store.source_sha256, config.camera_id, tuple(candidates))


def candidate_path(directory: Path, source_path: Path, *, raw_dir: Path) -> Path:
    relative = source_path.resolve().relative_to(raw_dir.resolve())
    return directory / "roi_candidates" / relative.parent / f"{relative.stem}.roi-candidates.json"


def write_candidates(candidate_store: RoiCandidateStore, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(candidate_store.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return path


def read_candidates(path: Path, *, source_sha256: str) -> RoiCandidateStore:
    """Read a source-owned candidate artifact and reject stale source evidence."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise FileNotFoundError(f"ROI candidate artifact is missing: {path}") from error
    if raw.get("schema_version") != SCHEMA_VERSION or raw.get("source_sha256") != source_sha256:
        raise ValueError(f"ROI candidate artifact is invalid or stale: {path}")
    try:
        candidates = tuple(RoiCandidate(**item) for item in raw["candidates"])
        return RoiCandidateStore(str(raw["source_sha256"]), str(raw["camera_id"]), candidates)
    except (KeyError, TypeError) as error:
        raise ValueError(f"Invalid ROI candidate artifact: {path}") from error


def candidate_artifact_path(directory: Path, source_path: Path, *, raw_dir: Path) -> Path:
    """Alias clarifying that candidate artifacts are source-owned."""
    return candidate_path(directory, source_path, raw_dir=raw_dir)


def _merge_observations(observations: list[tuple[float, object]], gap_seconds: float) -> list[list[tuple[float, object]]]:
    merged: list[list[tuple[float, object]]] = []
    for _, group in groupby(sorted(observations, key=lambda item: item[0]), key=lambda item: item[0]):
        at_timestamp = list(group)
        if not merged or at_timestamp[0][0] - merged[-1][-1][0] > gap_seconds:
            merged.append(at_timestamp)
        else:
            merged[-1].extend(at_timestamp)
    return merged


def _has_core_evidence(group: list[tuple[float, object]], core: object, width: int, height: int) -> bool:
    polygon = tuple(normalized_to_pixel(point, width, height) for point in core.points_normalized)
    return any(point_in_polygon(detection_footpoint(item.bbox_xyxy_px), polygon) for _, item in group)


def _count_at_timestamp(group: list[tuple[float, object]], timestamp: float) -> int:
    return sum(1 for observed_time, _ in group if observed_time == timestamp)


def _candidate_id(source_sha256: str, roi_id: str, index: int, start: float, end: float) -> str:
    value = f"{source_sha256}|{roi_id}|{index}|{start:.6f}|{end:.6f}".encode()
    return f"roi-{hashlib.sha256(value).hexdigest()[:16]}"
