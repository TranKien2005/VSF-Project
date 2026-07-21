"""Command-line entry points for the local technical candidate tool."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Annotated

import typer

from .config import load_config
from .debug_renderer import inspect_raw_video
from .export_dialog import choose_export_path
from .exporter import export_clip, export_clip_with_bboxes, normalize_export_target
from .media_tools import resolve_media_tools
from .processed_store import import_video_files
from .weights import MODELS, download_model

app = typer.Typer(help="Local technical person-detection evidence tool; no final event labels.")


@app.command("download-weights")
def download_weights(
    model: Annotated[str, typer.Option(help="Supported local model artifact")] = "yolo11n",
    config: Annotated[Path | None, typer.Option(help="Path to TOML configuration")] = None,
) -> None:
    """Explicitly download a model artifact; normal processing remains offline."""
    if model not in MODELS:
        raise typer.BadParameter(f"Supported models: {', '.join(MODELS)}")
    app_config = load_config(config)
    target, checksum = download_model(
        model, app_config.providers.rtdetr_l_weights if model == "rtdetr-l" else app_config.providers.yolo11n_weights
    )
    typer.echo(f"Downloaded local weights: {target}\nSHA-256: {checksum}")


@app.command()
def import_video(
    video_path: Annotated[Path, typer.Argument(help="External video to register without copying")],
    config: Annotated[Path | None, typer.Option(help="Path to TOML configuration")] = None,
) -> None:
    """Register an external video as an independent processed source."""
    app_config = load_config(config)
    records, failures = import_video_files(
        [video_path], app_config.paths.processed_dir, resolve_media_tools(app_config.paths.ffmpeg_dir)
    )
    for record in records:
        typer.echo(f"Registered {record.filename}: {record.source_id}")
    for failure in failures:
        typer.echo(f"FAILED {failure}")


@app.command()
def gui() -> None:
    """Launch the optional PySide6 desktop client."""
    from .gui.app import main

    raise typer.Exit(main())


def _span_action(video_path: Path, store, span, app_config) -> None:  # type: ignore[no-untyped-def]
    """View or explicitly export one technical candidate context."""
    while True:
        action = typer.prompt("V view, E clean MP4, A bbox MP4, or B back").strip().casefold()
        if action in {"b", "back"}:
            return
        if action in {"v", "view"}:
            inspect_raw_video(video_path, store, context_start_sec=span.context_start_sec, context_end_sec=span.context_end_sec)
        elif action in {"e", "export", "clean"}:
            _export_span(video_path, store, span, app_config)
        elif action in {"a", "annotated", "bbox"}:
            _export_span(video_path, store, span, app_config, annotated=True)
        else:
            typer.echo("Enter V, E, A, or B.")


def _export_span(video_path: Path, store, span, app_config, *, annotated: bool = False) -> None:  # type: ignore[no-untyped-def]
    """Create an operator-selected export only after overwrite confirmation."""
    target = choose_export_path(video_path, span.span_id, span.context_start_sec, span.context_end_sec, annotated=annotated)
    if target is None:
        typer.echo("Export cancelled; no file written.")
        return
    try:
        target = normalize_export_target(video_path, target)
    except ValueError as error:
        typer.echo(f"Export not started: {error}")
        return
    if target.exists() and not typer.confirm(f"Overwrite existing file? {target}", default=False):
        typer.echo("Export cancelled; existing file left unchanged.")
        return
    try:
        tools = resolve_media_tools(app_config.paths.ffmpeg_dir)
        if annotated:
            export_clip_with_bboxes(video_path, span.context_start_sec, span.context_end_sec, target, store, ffmpeg=tools.ffmpeg)
        else:
            export_clip(video_path, span.context_start_sec, span.context_end_sec, target, ffmpeg=tools.ffmpeg)
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        typer.echo(f"Export failed: {error}")
        return
    typer.echo(f"Exported local {'annotated bbox' if annotated else 'clean'} MP4: {target.resolve()}")


if __name__ == "__main__":
    app()
