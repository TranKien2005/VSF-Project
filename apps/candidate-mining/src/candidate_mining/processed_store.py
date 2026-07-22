"""Metadata-only catalog for imported external videos and cameras.

The catalog never copies or changes an imported video. Detection boxes and review
candidates belong in ``data/results`` rather than this module's processed tree.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .inventory import probe_video, sha256_file
from .media_tools import MediaTools
from .video_browser import VIDEO_EXTENSIONS

SOURCE_SCHEMA_VERSION = "processed-source.v2"
CAMERA_SCHEMA_VERSION = "processed-camera.v1"


@dataclass(frozen=True)
class ProcessedSource:
    source_id: str
    raw_absolute_path_at_registration: str
    filename: str
    sha256: str
    size_bytes: int
    duration_seconds: float
    fps: float | None
    frame_width: int | None
    frame_height: int | None
    codec: str | None
    has_audio: bool
    camera_id: str | None = None
    observation_metadata: dict[str, str] = field(
        default_factory=lambda: {"lighting": "Unknown", "weather": "Unknown", "viewpoint_note": ""}
    )

    @property
    def raw_relative_path(self) -> str:
        """Compatibility display value; imported paths are external locators."""
        return self.raw_absolute_path_at_registration

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": SOURCE_SCHEMA_VERSION,
            "source_id": self.source_id,
            "source": {
                "absolute_path_at_registration": self.raw_absolute_path_at_registration,
                "filename": self.filename,
                "sha256": self.sha256,
                "size_bytes": self.size_bytes,
                "duration_seconds": self.duration_seconds,
                "fps": self.fps,
                "frame_width": self.frame_width,
                "frame_height": self.frame_height,
                "codec": self.codec,
                "has_audio": self.has_audio,
            },
            "camera_id": self.camera_id,
            "observation_metadata": self.observation_metadata,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, object]) -> ProcessedSource:
        if raw.get("schema_version") != SOURCE_SCHEMA_VERSION:
            raise ValueError("Unsupported processed source schema")
        source = raw.get("source")
        if not isinstance(source, dict):
            raise ValueError("Processed source must contain source metadata")
        return cls(
            source_id=str(raw["source_id"]),
            raw_absolute_path_at_registration=str(source["absolute_path_at_registration"]),
            filename=str(source["filename"]),
            sha256=str(source["sha256"]),
            size_bytes=int(source["size_bytes"]),
            duration_seconds=float(source["duration_seconds"]),
            fps=float(source["fps"]) if source.get("fps") is not None else None,
            frame_width=int(source["frame_width"]) if source.get("frame_width") is not None else None,
            frame_height=int(source["frame_height"]) if source.get("frame_height") is not None else None,
            codec=str(source["codec"]) if source.get("codec") is not None else None,
            has_audio=bool(source["has_audio"]),
            camera_id=str(raw["camera_id"]) if raw.get("camera_id") else None,
            observation_metadata=dict(raw.get("observation_metadata", {})),
        )


@dataclass(frozen=True)
class CameraRecord:
    camera_id: str
    name: str
    imported_folder_at_registration: str
    description: str = ""

    def to_dict(self) -> dict[str, object]:
        return {"schema_version": CAMERA_SCHEMA_VERSION, **asdict(self)}

    @classmethod
    def from_dict(cls, raw: dict[str, object]) -> CameraRecord:
        if raw.get("schema_version") != CAMERA_SCHEMA_VERSION:
            raise ValueError("Unsupported camera schema")
        return cls(
            camera_id=str(raw["camera_id"]),
            name=str(raw["name"]),
            imported_folder_at_registration=str(raw["imported_folder_at_registration"]),
            description=str(raw.get("description", "")),
        )


def _safe_id(value: str) -> str:
    safe = "".join(character if character.isalnum() or character in "-_" else "-" for character in value.strip())
    return safe.strip("-") or "camera"


def independent_source_directory(processed_dir: Path, source_id: str) -> Path:
    return processed_dir / "videos" / source_id


def camera_directory(processed_dir: Path, camera_id: str) -> Path:
    return processed_dir / "cameras" / _safe_id(camera_id)


def camera_source_directory(processed_dir: Path, camera_id: str, source_id: str) -> Path:
    return camera_directory(processed_dir, camera_id) / "videos" / source_id


def source_directory(processed_dir: Path, record: ProcessedSource) -> Path:
    if record.camera_id:
        return camera_source_directory(processed_dir, record.camera_id, record.source_id)
    return independent_source_directory(processed_dir, record.source_id)


def source_path(processed_dir: Path, source_id: str, *, camera_id: str | None = None) -> Path:
    directory = (
        camera_source_directory(processed_dir, camera_id, source_id)
        if camera_id
        else independent_source_directory(processed_dir, source_id)
    )
    return directory / "source.json"


def camera_path(processed_dir: Path, camera_id: str) -> Path:
    return camera_directory(processed_dir, camera_id) / "camera.json"


def source_roi_path(processed_dir: Path, record: ProcessedSource) -> Path:
    return source_directory(processed_dir, record) / "roi.json"


def camera_roi_path(processed_dir: Path, camera_id: str) -> Path:
    return camera_directory(processed_dir, camera_id) / "roi.json"


def effective_roi_path(processed_dir: Path, record: ProcessedSource) -> tuple[Path | None, str | None]:
    override = source_roi_path(processed_dir, record)
    if override.exists():
        return override, "source"
    if record.camera_id:
        shared = camera_roi_path(processed_dir, record.camera_id)
        if shared.exists():
            return shared, "camera"
    return None, None


def write_source(record: ProcessedSource, processed_dir: Path) -> Path:
    target = source_directory(processed_dir, record) / "source.json"
    _write_json(target, record.to_dict())
    return target


def read_source(path: Path) -> ProcessedSource:
    return ProcessedSource.from_dict(_read_json(path, "Processed source"))


def write_camera(record: CameraRecord, processed_dir: Path) -> Path:
    target = camera_path(processed_dir, record.camera_id)
    _write_json(target, record.to_dict())
    return target


def read_camera(path: Path) -> CameraRecord:
    return CameraRecord.from_dict(_read_json(path, "Camera metadata"))


def list_sources(processed_dir: Path) -> list[ProcessedSource]:
    paths = [*processed_dir.glob("videos/*/source.json"), *processed_dir.glob("cameras/*/videos/*/source.json")]
    return sorted((read_source(path) for path in paths), key=lambda item: (item.camera_id or "", item.filename.casefold()))


def list_cameras(processed_dir: Path) -> list[CameraRecord]:
    return sorted(
        (read_camera(path) for path in processed_dir.glob("cameras/*/camera.json")), key=lambda item: item.name.casefold()
    )


def resolve_source(record: ProcessedSource) -> Path:
    """Resolve an imported external source and reject missing or changed content."""
    candidate = Path(record.raw_absolute_path_at_registration)
    if not candidate.is_file():
        raise FileNotFoundError(f"Imported source is missing: {candidate}")
    if sha256_file(candidate) != record.sha256:
        raise ValueError(f"Imported source checksum no longer matches processed metadata: {candidate}")
    return candidate


def import_video_files(
    paths: list[Path],
    processed_dir: Path,
    tools: MediaTools,
    *,
    camera_id: str | None = None,
    on_progress: object | None = None,
) -> tuple[list[ProcessedSource], list[str]]:
    """Register explicit external files without copying or modifying them."""
    candidates = sorted(
        {path.resolve() for path in paths if path.is_file() and path.suffix.casefold() in VIDEO_EXTENSIONS},
        key=lambda item: str(item).casefold(),
    )
    records: list[ProcessedSource] = []
    failures: list[str] = []
    total = len(candidates)
    for index, video_path in enumerate(candidates, start=1):
        if on_progress:
            on_progress(index, total, video_path.name)
        try:
            inventory = probe_video(video_path, ffprobe=tools.ffprobe)
        except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
            failures.append(f"{video_path}: {error}")
            continue
        record = ProcessedSource(
            source_id=inventory.sha256,
            raw_absolute_path_at_registration=str(video_path),
            filename=video_path.name,
            sha256=inventory.sha256,
            size_bytes=inventory.size_bytes,
            duration_seconds=inventory.duration_seconds,
            fps=inventory.fps,
            frame_width=inventory.width,
            frame_height=inventory.height,
            codec=inventory.codec,
            has_audio=inventory.has_audio,
            camera_id=camera_id,
        )
        write_source(record, processed_dir)
        records.append(record)
    return records, failures


def _is_macos_junk(path: Path) -> bool:
    """Return True for macOS resource fork metadata files and __MACOSX directories."""
    if path.name.startswith("._"):
        return True
    return any(part == "__MACOSX" for part in path.parts)


def import_camera_folder(
    folder: Path,
    processed_dir: Path,
    tools: MediaTools,
    *,
    camera_name: str | None = None,
    on_progress: object | None = None,
) -> tuple[list[CameraRecord], list[ProcessedSource], list[str]]:
    """Register all supported videos in a folder, auto-grouping by immediate camera subfolder."""
    resolved = folder.resolve()
    if not resolved.is_dir():
        raise ValueError(f"Camera folder does not exist: {resolved}")
    videos = [
        path
        for path in resolved.rglob("*")
        if path.is_file() and path.suffix.casefold() in VIDEO_EXTENSIONS and not _is_macos_junk(path)
    ]
    if not videos:
        return [], [], []

    camera_groups: dict[Path, list[Path]] = {}
    for video in videos:
        cam_dir = video.parent
        camera_groups.setdefault(cam_dir, []).append(video)

    cameras: list[CameraRecord] = []
    all_records: list[ProcessedSource] = []
    all_failures: list[str] = []

    for cam_dir, group_videos in camera_groups.items():
        name = camera_name if (len(camera_groups) == 1 and camera_name) else cam_dir.name
        camera_id = _safe_id(name)
        camera = CameraRecord(
            camera_id=camera_id,
            name=name,
            imported_folder_at_registration=str(cam_dir),
        )
        write_camera(camera, processed_dir)
        cameras.append(camera)
        records, failures = import_video_files(
            group_videos, processed_dir, tools, camera_id=camera.camera_id, on_progress=on_progress
        )
        all_records.extend(records)
        all_failures.extend(failures)

    return cameras, all_records, all_failures


def import_paths(paths: list[Path], processed_dir: Path, tools: MediaTools) -> tuple[list[ProcessedSource], list[str]]:
    """Import files as independent videos and each selected directory as camera folders."""
    records, failures = import_video_files(paths, processed_dir, tools)
    for path in paths:
        if path.is_dir():
            _, camera_records, camera_failures = import_camera_folder(path, processed_dir, tools)
            records.extend(camera_records)
            failures.extend(camera_failures)
    return records, failures


def register_sources(raw_dir: Path, processed_dir: Path, tools: MediaTools) -> list[ProcessedSource]:
    """Compatibility import adapter; a directory is now treated as a camera folder."""
    return import_paths([raw_dir], processed_dir, tools)[0]


def _read_json(path: Path, label: str) -> dict[str, object]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise FileNotFoundError(f"{label} is missing: {path}") from error
    if not isinstance(raw, dict):
        raise ValueError(f"Invalid {label.casefold()}: {path}")
    return raw


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
