"""Raw-source discovery and local camera grouping conventions."""

from __future__ import annotations

from pathlib import Path


def camera_id_for_source(video_path: Path, raw_dir: Path) -> str:
    """Return the local camera grouping from the first raw-relative folder."""
    try:
        relative = video_path.resolve().relative_to(raw_dir.resolve())
    except ValueError as error:
        raise ValueError(f"Source is outside configured raw directory: {video_path}") from error
    return relative.parts[0] if len(relative.parts) > 1 else "unassigned"
