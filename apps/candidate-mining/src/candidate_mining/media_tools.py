"""Resolve portable or PATH-based FFmpeg executables without mutating PATH."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MediaTools:
    ffmpeg: Path
    ffprobe: Path


def _resolve_one(name: str, portable_dir: Path) -> Path | None:
    executable = f"{name}.exe" if name in {"ffmpeg", "ffprobe"} else name
    bundled = portable_dir / executable
    if bundled.is_file():
        return bundled.resolve()
    on_path = shutil.which(name)
    return Path(on_path).resolve() if on_path else None


def resolve_media_tools(portable_dir: Path) -> MediaTools:
    """Prefer repository-local tools, then fall back to executables on PATH."""
    ffmpeg = _resolve_one("ffmpeg", portable_dir)
    ffprobe = _resolve_one("ffprobe", portable_dir)
    missing = [name for name, value in (("ffmpeg", ffmpeg), ("ffprobe", ffprobe)) if value is None]
    if missing:
        names = ", ".join(missing)
        raise RuntimeError(
            f"Missing media tool(s): {names}. Expected portable files in {portable_dir} "
            "or both tools on PATH. See docs/ffmpeg-portable-windows.md."
        )
    return MediaTools(ffmpeg=ffmpeg, ffprobe=ffprobe)
