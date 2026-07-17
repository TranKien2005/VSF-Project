"""Native save dialog for an explicitly requested local MP4 export."""

from __future__ import annotations

from pathlib import Path


def suggested_export_name(
    source: Path,
    span_id: str,
    start_sec: float,
    end_sec: float,
    *,
    annotated: bool = False,
) -> str:
    """Build a deterministic, filesystem-friendly default filename."""
    suffix = "_bbox" if annotated else ""
    return f"{source.stem}_{span_id}_{start_sec:.1f}s-{end_sec:.1f}s{suffix}.mp4"


def choose_export_path(
    source: Path,
    span_id: str,
    start_sec: float,
    end_sec: float,
    *,
    annotated: bool = False,
) -> Path | None:
    """Open Windows Save As and return the chosen path, or None on cancellation."""
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    try:
        selected = filedialog.asksaveasfilename(
            parent=root,
            title=("Export annotated bbox span" if annotated else "Export selected person-detection span"),
            initialfile=suggested_export_name(source, span_id, start_sec, end_sec, annotated=annotated),
            defaultextension=".mp4",
            filetypes=(("MP4 video", "*.mp4"), ("All files", "*.*")),
        )
        return Path(selected) if selected else None
    finally:
        root.destroy()
