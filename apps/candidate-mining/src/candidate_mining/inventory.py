"""Video inventory using ffprobe and a complete source checksum."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from .models import VideoInventory


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _frame_rate(value: str | None) -> float | None:
    if not value or value == "0/0":
        return None
    numerator, denominator = value.split("/", maxsplit=1)
    return float(numerator) / float(denominator)


def probe_video(video_path: Path, *, ffprobe: Path) -> VideoInventory:
    command = [
        str(ffprobe),
        "-v",
        "error",
        "-show_entries",
        "format=format_name,duration:stream=codec_type,codec_name,width,height,avg_frame_rate",
        "-of",
        "json",
        str(video_path),
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    probe = json.loads(result.stdout)
    streams = probe.get("streams", [])
    video = next((stream for stream in streams if stream.get("codec_type") == "video"), None)
    if video is None:
        raise ValueError(f"No video stream found in {video_path}")
    checksum = sha256_file(video_path)
    format_info = probe.get("format", {})
    return VideoInventory(
        source_id=f"video_{checksum[:16]}",
        source_path=str(video_path.resolve()),
        filename=video_path.name,
        size_bytes=video_path.stat().st_size,
        sha256=checksum,
        duration_seconds=float(format_info["duration"]),
        fps=_frame_rate(video.get("avg_frame_rate")),
        width=video.get("width"),
        height=video.get("height"),
        codec=video.get("codec_name"),
        container=format_info.get("format_name"),
        has_audio=any(stream.get("codec_type") == "audio" for stream in streams),
    )


def _source_basename(filename: str) -> str:
    stem = Path(filename).stem.strip()
    if not stem:
        raise ValueError("Video filename must have a non-empty stem")
    return "".join(character if character.isalnum() or character in "-_" else "_" for character in stem)


def write_inventory(record: VideoInventory, directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"{_source_basename(record.filename)}.inventory.json"
    temporary = target.with_suffix(".json.tmp")
    content = json.dumps(record.__dict__, ensure_ascii=False, indent=2)
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(target)
    return target
