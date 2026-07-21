"""Persist categorized technical candidate evidence under ``data/results``."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .debug_artifacts import PersonDetectionStore, StoredDetection, StoredPresenceSegment
from .roi import TrackRoi, roi_contains_detection
from .segments import proxy_window

SCHEMA_VERSION = "technical-candidate.v1"


@dataclass(frozen=True)
class TechnicalCandidate:
    candidate_id: str
    category: str
    source_id: str
    source_sha256: str
    source_filename: str
    camera_id: str | None
    trigger_reason: str
    candidate_start_sec: float
    candidate_end_sec: float
    context_start_sec: float
    context_end_sec: float
    context_status: str
    track_ids: tuple[int, ...]
    episode_ids: tuple[str, ...]
    detections: tuple[StoredDetection, ...]
    review_state: str = "pending_review"
    roi_provenance: dict[str, object] | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": SCHEMA_VERSION,
            **asdict(self),
            "detections": [asdict(item) for item in self.detections],
        }


def candidate_path(results_dir: Path, category: str, candidate_id: str) -> Path:
    return results_dir / category / candidate_id / "candidate.json"


def write_candidate(candidate: TechnicalCandidate, results_dir: Path) -> Path:
    target = candidate_path(results_dir, candidate.category, candidate.candidate_id)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(candidate.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(target)
    return target


def read_candidate(path: Path) -> TechnicalCandidate:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise FileNotFoundError(f"Technical candidate is missing: {path}") from error
    if not isinstance(raw, dict) or raw.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"Invalid technical candidate: {path}")
    try:
        return TechnicalCandidate(
            candidate_id=str(raw["candidate_id"]),
            category=str(raw["category"]),
            source_id=str(raw["source_id"]),
            source_sha256=str(raw["source_sha256"]),
            source_filename=str(raw["source_filename"]),
            camera_id=str(raw["camera_id"]) if raw.get("camera_id") else None,
            trigger_reason=str(raw["trigger_reason"]),
            candidate_start_sec=float(raw["candidate_start_sec"]),
            candidate_end_sec=float(raw["candidate_end_sec"]),
            context_start_sec=float(raw["context_start_sec"]),
            context_end_sec=float(raw["context_end_sec"]),
            context_status=str(raw["context_status"]),
            track_ids=tuple(int(value) for value in raw["track_ids"]),
            episode_ids=tuple(str(value) for value in raw["episode_ids"]),
            detections=tuple(StoredDetection(**item) for item in raw["detections"]),
            review_state=str(raw.get("review_state", "pending_review")),
            roi_provenance=dict(raw["roi_provenance"]) if isinstance(raw.get("roi_provenance"), dict) else None,
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"Invalid technical candidate: {path}") from error


def list_candidates(results_dir: Path, source_id: str) -> list[TechnicalCandidate]:
    return sorted(
        (read_candidate(path) for path in results_dir.glob("*/*/candidate.json") if _candidate_source(path, source_id)),
        key=lambda item: (item.category, item.context_start_sec, item.candidate_id),
    )


def _candidate_source(path: Path, source_id: str) -> bool:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return isinstance(raw, dict) and raw.get("source_id") == source_id


def write_person_candidates(
    store: PersonDetectionStore, results_dir: Path, *, source_id: str, camera_id: str | None
) -> list[Path]:
    return [write_candidate(_from_presence(store, span, source_id, camera_id), results_dir) for span in store.presence_segments]


def write_roi_filtered_person_candidates(
    store: PersonDetectionStore,
    results_dir: Path,
    *,
    source_id: str,
    camera_id: str | None,
    roi: TrackRoi,
    merge_gap_seconds: float,
    duration_seconds: float,
    pre_roll_seconds: float,
    post_roll_seconds: float,
    roi_scope: str,
) -> list[Path]:
    observations = [
        item for item in store.detections if roi_contains_detection(roi, item.bbox_xyxy_px, store.frame_width, store.frame_height)
    ]
    paths: list[Path] = []
    for index, group in enumerate(_merge_detections(observations, merge_gap_seconds), start=1):
        start, end = group[0].timestamp_sec, group[-1].timestamp_sec
        window = proxy_window(start, end, duration_seconds, pre_roll_seconds, post_roll_seconds)
        candidate = TechnicalCandidate(
            candidate_id=_candidate_id(store.source_sha256, "person_detected", index, start, end),
            category="person_detected",
            source_id=source_id,
            source_sha256=store.source_sha256,
            source_filename=store.source_filename,
            camera_id=camera_id,
            trigger_reason="person_footpoint_in_track_roi",
            candidate_start_sec=start,
            candidate_end_sec=end,
            context_start_sec=window.start_sec,
            context_end_sec=window.end_sec,
            context_status=window.context_status,
            track_ids=tuple(sorted({item.track_id for item in group})),
            episode_ids=tuple(sorted({item.episode_id for item in group})),
            detections=_context_detections(store.detections, window.start_sec, window.end_sec),
            roi_provenance={"scope": roi_scope, "revision": roi.revision, "snapshot_sha256": roi.snapshot_hash()},
        )
        paths.append(write_candidate(candidate, results_dir))
    return paths


def _from_presence(
    store: PersonDetectionStore, span: StoredPresenceSegment, source_id: str, camera_id: str | None
) -> TechnicalCandidate:
    return TechnicalCandidate(
        candidate_id=_candidate_id(
            store.source_sha256,
            span.category,
            int(span.span_id.rsplit("-", 1)[-1]),
            span.candidate_start_sec,
            span.candidate_end_sec,
        ),
        category=span.category,
        source_id=source_id,
        source_sha256=store.source_sha256,
        source_filename=store.source_filename,
        camera_id=camera_id,
        trigger_reason="person_detected",
        candidate_start_sec=span.candidate_start_sec,
        candidate_end_sec=span.candidate_end_sec,
        context_start_sec=span.context_start_sec,
        context_end_sec=span.context_end_sec,
        context_status="context_clipped" if span.context_start_sec == 0.0 else "context_available",
        track_ids=span.track_ids,
        episode_ids=span.episode_ids,
        detections=_context_detections(store.detections, span.context_start_sec, span.context_end_sec),
    )


def _context_detections(detections: tuple[StoredDetection, ...], start: float, end: float) -> tuple[StoredDetection, ...]:
    return tuple(item for item in detections if start <= item.timestamp_sec <= end)


def _merge_detections(detections: list[StoredDetection], gap_seconds: float) -> list[list[StoredDetection]]:
    merged: list[list[StoredDetection]] = []
    for detection in sorted(detections, key=lambda item: item.timestamp_sec):
        if not merged or detection.timestamp_sec - merged[-1][-1].timestamp_sec > gap_seconds:
            merged.append([detection])
        else:
            merged[-1].append(detection)
    return merged


def _candidate_id(source_sha256: str, category: str, index: int, start: float, end: float) -> str:
    payload = f"{source_sha256}|{category}|{index}|{start:.6f}|{end:.6f}".encode()
    return f"{category}-{hashlib.sha256(payload).hexdigest()[:16]}"
