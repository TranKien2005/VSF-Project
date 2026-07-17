"""Catalog raw videos and their persisted person-detection JSON status."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .debug_artifacts import PersonDetectionStore, person_detection_path, read_person_detection_store

VIDEO_EXTENSIONS = frozenset({".mp4", ".avi", ".mov", ".mkv", ".m4v", ".webm"})


@dataclass(frozen=True)
class VideoEntry:
    video_path: Path
    relative_path: Path
    status: str
    box_count: int | None
    detail: str
    store: PersonDetectionStore | None = None


def discover_raw_videos(raw_dir: Path) -> list[tuple[Path, Path]]:
    if not raw_dir.is_dir():
        raise FileNotFoundError(f"Raw video directory does not exist: {raw_dir}")
    found = [
        (path, path.relative_to(raw_dir))
        for path in raw_dir.rglob("*")
        if path.is_file() and path.suffix.casefold() in VIDEO_EXTENSIONS
    ]
    return sorted(found, key=lambda item: (item[1].as_posix().casefold(), item[1].as_posix()))


def catalog_raw_videos(raw_dir: Path, review_queue_dir: Path) -> list[VideoEntry]:
    return [
        catalog_video(video_path, relative_path, raw_dir, review_queue_dir)
        for video_path, relative_path in discover_raw_videos(raw_dir)
    ]


def catalog_video(video_path: Path, relative_path: Path, raw_dir: Path, review_queue_dir: Path) -> VideoEntry:
    target = person_detection_path(review_queue_dir, video_path, raw_dir=raw_dir)
    if not target.exists():
        return VideoEntry(video_path, relative_path, "MISSING", None, "Run candidate-mining run for this video")
    try:
        store = read_person_detection_store(target, video_path)
    except ValueError as error:
        status = "STALE" if "does not match" in str(error) else "INVALID"
        return VideoEntry(video_path, relative_path, status, None, str(error))
    count = len(store.detections)
    return VideoEntry(video_path, relative_path, "READY" if count else "EMPTY", count, "", store)
