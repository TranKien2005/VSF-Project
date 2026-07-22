"""Persist categorized technical candidate evidence under ``data/results``."""

from __future__ import annotations

import hashlib
import json
import shutil
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path

from .debug_artifacts import PersonDetectionStore, StoredDetection, StoredPresenceSegment
from .models import Signal
from .roi import TrackRoi, roi_contains_detection
from .segments import merge_signals, proxy_window

SCHEMA_VERSION = "technical-candidate.v2"


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


def source_results_path(results_dir: Path, source_id: str, camera_id: str | None) -> Path:
    """Return the sole result container owned by one imported source."""
    if camera_id:
        return results_dir / "cameras" / camera_id / "videos" / source_id
    return results_dir / "videos" / source_id


def candidate_path(results_dir: Path, source_id: str, camera_id: str | None, category: str, candidate_id: str) -> Path:
    return source_results_path(results_dir, source_id, camera_id) / category / candidate_id / "candidate.json"


def _write_candidate_to_source_dir(candidate: TechnicalCandidate, source_dir: Path) -> Path:
    target = source_dir / candidate.category / candidate.candidate_id / "candidate.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(candidate.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(target)
    return target


def write_candidate(candidate: TechnicalCandidate, results_dir: Path) -> Path:
    return _write_candidate_to_source_dir(
        candidate,
        source_results_path(results_dir, candidate.source_id, candidate.camera_id),
    )


def read_candidate(path: Path) -> TechnicalCandidate:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise FileNotFoundError(f"Technical candidate is missing: {path}") from error
    if not isinstance(raw, dict) or raw.get("schema_version") not in {"technical-candidate.v1", SCHEMA_VERSION}:
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
            detections=tuple(_read_detection(item) for item in raw["detections"]),
            review_state=str(raw.get("review_state", "pending_review")),
            roi_provenance=dict(raw["roi_provenance"]) if isinstance(raw.get("roi_provenance"), dict) else None,
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"Invalid technical candidate: {path}") from error


def _read_detection(raw: object) -> StoredDetection:
    if not isinstance(raw, dict):
        raise ValueError("Candidate detection must be an object")
    bbox = tuple(float(value) for value in raw["bbox_xyxy_px"])
    if len(bbox) != 4:
        raise ValueError("Candidate detection bbox must have four coordinates")
    initial_footpoint = raw.get("initial_footpoint_xy_px")
    if initial_footpoint is None:
        initial_footpoint = ((bbox[0] + bbox[2]) / 2, bbox[3])
    footpoint = tuple(float(value) for value in initial_footpoint)
    if len(footpoint) != 2:
        raise ValueError("Candidate detection initial footpoint must have two coordinates")
    return StoredDetection(
        source_frame_index=int(raw["source_frame_index"]),
        timestamp_sec=float(raw["timestamp_sec"]),
        bbox_xyxy_px=bbox,
        confidence=float(raw["confidence"]),
        track_id=int(raw["track_id"]),
        episode_id=str(raw["episode_id"]),
        initial_footpoint_xy_px=footpoint,
        initial_bbox_height_px=float(raw.get("initial_bbox_height_px", bbox[3] - bbox[1])),
        motion_confirmed=bool(raw.get("motion_confirmed", True)),
    )


def list_candidates(results_dir: Path, source_id: str, camera_id: str | None) -> list[TechnicalCandidate]:
    source_dir = source_results_path(results_dir, source_id, camera_id)
    if not source_dir.exists():
        return []
    return sorted(
        (read_candidate(path) for path in source_dir.glob("*/**/candidate.json")),
        key=lambda item: (item.category, item.context_start_sec, item.candidate_id),
    )


def replace_source_results(
    results_dir: Path,
    *,
    source_id: str,
    camera_id: str | None,
    candidates: list[TechnicalCandidate],
) -> list[Path]:
    """Atomically replace one source's complete technical result set after a successful run."""
    target = source_results_path(results_dir, source_id, camera_id)
    run_id = uuid.uuid4().hex[:12]
    staging = target.parent / f".staging-{run_id}"
    backup = target.parent / f".backup-{run_id}"
    staging.mkdir(parents=True, exist_ok=False)
    try:
        paths = [_write_candidate_to_source_dir(candidate, staging) for candidate in candidates]
        if target.exists():
            target.replace(backup)
        try:
            staging.replace(target)
        except Exception:
            if backup.exists():
                backup.replace(target)
            raise
        shutil.rmtree(backup, ignore_errors=True)
        return [target / path.relative_to(staging) for path in paths]
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def remove_legacy_source_results(results_dir: Path, source_id: str) -> None:
    """Drop old flat-layout candidates belonging to a source after its first successful replacement."""
    for path in results_dir.glob("*/*/candidate.json"):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(raw, dict) and raw.get("source_id") == source_id:
            shutil.rmtree(path.parent, ignore_errors=True)
            parent = path.parent.parent
            if parent.exists() and not any(parent.iterdir()):
                parent.rmdir()


def _candidate_source(path: Path, source_id: str) -> bool:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return isinstance(raw, dict) and raw.get("source_id") == source_id


def has_source_results(results_dir: Path, source_id: str, camera_id: str | None) -> bool:
    """Return True if results exist for a given source."""
    source_dir = source_results_path(results_dir, source_id, camera_id)
    return source_dir.exists() and any(source_dir.glob("*/**/candidate.json"))


def clear_source_results(results_dir: Path, source_id: str, camera_id: str | None) -> None:
    """Delete stored technical candidates for one source."""
    target = source_results_path(results_dir, source_id, camera_id)
    if target.exists():
        shutil.rmtree(target, ignore_errors=True)
    remove_legacy_source_results(results_dir, source_id)


def clear_camera_results(results_dir: Path, camera_id: str) -> None:
    """Delete stored technical candidates for all videos under a camera."""
    cam_dir = results_dir / "cameras" / camera_id
    if cam_dir.exists():
        shutil.rmtree(cam_dir, ignore_errors=True)


def clear_all_results(results_dir: Path) -> None:
    """Delete all stored technical candidates across all sources and cameras."""
    if results_dir.exists():
        for sub in ("videos", "cameras"):
            target = results_dir / sub
            if target.exists():
                shutil.rmtree(target, ignore_errors=True)


def write_person_candidates(
    store: PersonDetectionStore, results_dir: Path, *, source_id: str, camera_id: str | None
) -> list[Path]:
    return [write_candidate(_from_presence(store, span, source_id, camera_id), results_dir) for span in store.presence_segments]


def build_roi_filtered_person_candidates(
    store: PersonDetectionStore,
    *,
    source_id: str,
    camera_id: str | None,
    roi: TrackRoi,
    merge_gap_seconds: float,
    duration_seconds: float,
    pre_roll_seconds: float,
    post_roll_seconds: float,
    roi_scope: str,
) -> list[TechnicalCandidate]:
    observations = [
        item
        for item in store.detections
        if item.motion_confirmed and roi_contains_detection(roi, item.bbox_xyxy_px, store.frame_width, store.frame_height)
    ]
    candidates: list[TechnicalCandidate] = []
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
        candidates.append(candidate)
    return candidates


def build_camera_anomaly_candidates(
    signals: list[Signal],
    *,
    store: PersonDetectionStore,
    source_id: str,
    camera_id: str | None,
    merge_gap_seconds: float,
    duration_seconds: float,
    pre_roll_seconds: float,
    post_roll_seconds: float,
) -> list[TechnicalCandidate]:
    anomaly_signals = [s for s in signals if s.category == "camera_anomaly"]
    if not anomaly_signals:
        return []
    segments = merge_signals(anomaly_signals, merge_gap_seconds)
    candidates: list[TechnicalCandidate] = []
    for index, seg in enumerate(segments, start=1):
        cat = next(iter(seg.categories)) if seg.categories else "camera_anomaly"
        start, end = seg.start_sec, seg.end_sec
        window = proxy_window(start, end, duration_seconds, pre_roll_seconds, post_roll_seconds)
        candidate = TechnicalCandidate(
            candidate_id=_candidate_id(store.source_sha256, cat, index, start, end),
            category=cat,
            source_id=source_id,
            source_sha256=store.source_sha256,
            source_filename=store.source_filename,
            camera_id=camera_id,
            trigger_reason=f"camera_anomaly_detected (score: {seg.motion_score or 0.0:.2f})",
            candidate_start_sec=start,
            candidate_end_sec=end,
            context_start_sec=window.start_sec,
            context_end_sec=window.end_sec,
            context_status=window.context_status,
            track_ids=(),
            episode_ids=(),
            detections=(),
        )
        candidates.append(candidate)
    return candidates


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
    signals: list[Signal] | None = None,
) -> list[Path]:
    person_candidates = build_roi_filtered_person_candidates(
        store,
        source_id=source_id,
        camera_id=camera_id,
        roi=roi,
        merge_gap_seconds=merge_gap_seconds,
        duration_seconds=duration_seconds,
        pre_roll_seconds=pre_roll_seconds,
        post_roll_seconds=post_roll_seconds,
        roi_scope=roi_scope,
    )
    anomaly_candidates = (
        build_camera_anomaly_candidates(
            signals,
            store=store,
            source_id=source_id,
            camera_id=camera_id,
            merge_gap_seconds=merge_gap_seconds,
            duration_seconds=duration_seconds,
            pre_roll_seconds=pre_roll_seconds,
            post_roll_seconds=post_roll_seconds,
        )
        if signals
        else []
    )
    candidates = person_candidates + anomaly_candidates
    paths = replace_source_results(
        results_dir,
        source_id=source_id,
        camera_id=camera_id,
        candidates=candidates,
    )
    remove_legacy_source_results(results_dir, source_id)
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
