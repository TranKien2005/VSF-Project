"""One stable person-detection JSON auxiliary file for each raw source."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .inventory import sha256_file
from .models import Segment
from .tracking import TrackObservation

SCHEMA_VERSION = "person-detections.v2"


def source_basename(video_path: Path) -> str:
    stem = video_path.stem.strip()
    if not stem:
        raise ValueError("Raw video filename must have a non-empty stem")
    return "".join(character if character.isalnum() or character in "-_" else "_" for character in stem)


def person_detection_path(directory: Path, video_path: Path, *, raw_dir: Path | None = None) -> Path:
    if raw_dir:
        try:
            relative = video_path.resolve().relative_to(raw_dir.resolve())
        except ValueError:
            relative = None
        if relative:
            parent = [source_basename(Path(part)) for part in relative.parent.parts if part not in (".", "")]
            return directory / "person_detected" / Path(*parent) / f"{source_basename(relative)}.detections.json"
    path_hash = hashlib.sha256(str(video_path.resolve()).encode("utf-8")).hexdigest()[:10]
    return directory / "person_detected" / f"{source_basename(video_path)}-{path_hash}.detections.json"


@dataclass(frozen=True)
class StoredDetection:
    source_frame_index: int
    timestamp_sec: float
    bbox_xyxy_px: tuple[float, float, float, float]
    confidence: float
    track_id: int
    episode_id: str
    initial_footpoint_xy_px: tuple[float, float]
    initial_bbox_height_px: float
    motion_confirmed: bool


@dataclass(frozen=True)
class StoredPresenceSegment:
    span_id: str
    category: str
    review_status: str
    candidate_start_sec: float
    candidate_end_sec: float
    context_start_sec: float
    context_end_sec: float
    person_count_max: int | None
    track_ids: tuple[int, ...]
    episode_ids: tuple[str, ...]


@dataclass(frozen=True)
class PersonDetectionStore:
    source_filename: str
    source_path: str
    source_sha256: str
    source_fps: float
    frame_width: int
    frame_height: int
    sample_fps: float
    image_size: int
    confidence_threshold: float
    detections: tuple[StoredDetection, ...]
    presence_segments: tuple[StoredPresenceSegment, ...] = ()

    @classmethod
    def from_observations(
        cls,
        video_path: Path,
        observations: list[TrackObservation],
        *,
        source_fps: float,
        frame_width: int,
        frame_height: int,
        sample_fps: float,
        image_size: int,
        confidence_threshold: float,
        person_presence_segments: list[Segment] | None = None,
        duration_seconds: float = 0.0,
        pre_roll_seconds: float = 5.0,
        post_roll_seconds: float = 5.0,
    ) -> PersonDetectionStore:
        ordered = sorted(person_presence_segments or [], key=lambda item: (item.start_sec, item.end_sec))
        spans = tuple(
            StoredPresenceSegment(
                span_id=f"person_detected-{index:04d}",
                category="person_detected",
                review_status="pending_review",
                candidate_start_sec=segment.start_sec,
                candidate_end_sec=segment.end_sec,
                context_start_sec=max(0.0, segment.start_sec - pre_roll_seconds),
                context_end_sec=min(duration_seconds, segment.end_sec + post_roll_seconds),
                person_count_max=segment.person_count_max,
                track_ids=tuple(sorted(segment.track_ids)),
                episode_ids=tuple(sorted(segment.episode_ids)),
            )
            for index, segment in enumerate(ordered, start=1)
        )
        confirmed_episodes = {obs.episode_id for obs in observations if obs.motion_confirmed}
        return cls(
            source_filename=video_path.name,
            source_path=str(video_path.resolve()),
            source_sha256=sha256_file(video_path),
            source_fps=source_fps,
            frame_width=frame_width,
            frame_height=frame_height,
            sample_fps=sample_fps,
            image_size=image_size,
            confidence_threshold=confidence_threshold,
            detections=tuple(
                StoredDetection(
                    item.detection.source_frame_index,
                    item.timestamp_sec,
                    item.detection.bbox_xyxy,
                    item.detection.confidence,
                    item.track_id,
                    item.episode_id,
                    item.initial_footpoint_xy,
                    item.initial_bbox_height_px,
                    item.motion_confirmed or (item.episode_id in confirmed_episodes),
                )
                for item in observations
            ),
            presence_segments=spans,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": SCHEMA_VERSION,
            "source": {
                "filename": self.source_filename,
                "path": self.source_path,
                "sha256": self.source_sha256,
                "fps": self.source_fps,
                "frame_width": self.frame_width,
                "frame_height": self.frame_height,
            },
            "detector": {
                "sample_fps": self.sample_fps,
                "image_size": self.image_size,
                "confidence_threshold": self.confidence_threshold,
                "class_filter": ["person"],
                "viewer_box_policy": "hold_last_5fps_snapshot_until_next_sample",
            },
            "presence_segments": [asdict(item) for item in self.presence_segments],
            "detections": [asdict(item) for item in self.detections],
        }


def write_person_detection_store(
    store: PersonDetectionStore, directory: Path, video_path: Path, *, raw_dir: Path | None = None
) -> Path:
    target = person_detection_path(directory, video_path, raw_dir=raw_dir)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(store.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(target)
    return target


def _read_stored_detection(raw: object) -> StoredDetection:
    if not isinstance(raw, dict):
        raise ValueError("Detection must be an object")
    bbox = tuple(float(value) for value in raw["bbox_xyxy_px"])
    if len(bbox) != 4:
        raise ValueError("Detection bbox must have four coordinates")
    initial_footpoint = raw.get("initial_footpoint_xy_px")
    if initial_footpoint is None:
        initial_footpoint = ((bbox[0] + bbox[2]) / 2, bbox[3])
    footpoint = tuple(float(value) for value in initial_footpoint)
    if len(footpoint) != 2:
        raise ValueError("Detection initial footpoint must have two coordinates")
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


def read_person_detection_store(path: Path, video_path: Path) -> PersonDetectionStore:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise FileNotFoundError(f"Person detection JSON is missing: {path}. Run candidate-mining first.") from error
    if raw.get("schema_version") not in {"person-detections.v1", SCHEMA_VERSION}:
        raise ValueError(f"Unsupported person detection JSON schema: {path}")
    try:
        source = raw["source"]
        if source["filename"] != video_path.name or source["sha256"] != sha256_file(video_path):
            raise ValueError("Person detection JSON does not match the selected raw video; rerun candidate-mining.")
        detections = tuple(_read_stored_detection(item) for item in raw["detections"])
        spans = tuple(
            StoredPresenceSegment(
                span_id=str(item.get("span_id", f"person_detected-{index:04d}")),
                category=str(item.get("category", "person_detected")),
                review_status=str(item.get("review_status", "pending_review")),
                candidate_start_sec=float(item["candidate_start_sec"]),
                candidate_end_sec=float(item["candidate_end_sec"]),
                context_start_sec=float(item["context_start_sec"]),
                context_end_sec=float(item["context_end_sec"]),
                person_count_max=(int(item["person_count_max"]) if item["person_count_max"] is not None else None),
                track_ids=tuple(int(value) for value in item["track_ids"]),
                episode_ids=tuple(str(value) for value in item["episode_ids"]),
            )
            for index, item in enumerate(raw.get("presence_segments", []), start=1)
        )
        detector = raw["detector"]
        return PersonDetectionStore(
            str(source["filename"]),
            str(source["path"]),
            str(source["sha256"]),
            float(source["fps"]),
            int(source["frame_width"]),
            int(source["frame_height"]),
            float(detector["sample_fps"]),
            int(detector["image_size"]),
            float(detector["confidence_threshold"]),
            detections,
            spans,
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"Invalid person detection JSON: {path}") from error
