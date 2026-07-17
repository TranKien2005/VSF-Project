"""Command line interface for the local person-detection viewer POC."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Annotated

import typer

from .config import load_config
from .debug_artifacts import person_detection_path, read_person_detection_store
from .debug_renderer import inspect_raw_video
from .export_dialog import choose_export_path
from .exporter import export_clip, export_clip_with_bboxes, normalize_export_target
from .media_tools import resolve_media_tools
from .pipeline import run_pipeline
from .video_browser import catalog_raw_videos
from .weights import MODELS, download_model

app = typer.Typer(help="Local person-detection viewer POC; no review video or model evaluation.")


def _validate_video(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_file():
        raise typer.BadParameter(f"Video file does not exist: {resolved}")
    return resolved


@app.command("download-weights")
def download_weights(
    model: Annotated[str, typer.Option(help="Supported local model artifact")] = "yolo11n",
    config: Annotated[Path | None, typer.Option(help="Path to TOML configuration")] = None,
) -> None:
    """Explicitly download a model artifact; normal runs never download weights."""
    if model not in MODELS:
        raise typer.BadParameter(f"Supported models: {', '.join(MODELS)}")
    app_config = load_config(config)
    destination = (
        app_config.providers.rtdetr_l_weights if model == "rtdetr-l" else app_config.providers.yolo11n_weights
    )
    target, checksum = download_model(model, destination)
    typer.echo(f"Downloaded local weights: {target}")
    typer.echo(f"SHA-256: {checksum}")


def _run_source(source: Path, app_config) -> bool:
    try:
        target = run_pipeline(source, app_config)
    except Exception as error:
        typer.echo(f"FAILED {source}: {error}")
        return False
    typer.echo(f"OK {source.relative_to(app_config.paths.raw_dir)} -> {target}")
    return True


@app.command()
def run(
    video_path: Annotated[Path | None, typer.Argument(help="Optional raw source video path")] = None,
    config: Annotated[Path | None, typer.Option(help="Path to TOML configuration")] = None,
) -> None:
    """Process one raw video directly, or select one/all raw videos interactively."""
    app_config = load_config(config)
    if video_path is not None:
        _run_source(_validate_video(video_path), app_config)
        return
    entries = catalog_raw_videos(app_config.paths.raw_dir, app_config.paths.review_queue_dir)
    if not entries:
        typer.echo(f"No supported raw videos found under {app_config.paths.raw_dir}")
        return
    typer.echo("#   Raw video (alphabetical)")
    for index, entry in enumerate(entries, start=1):
        typer.echo(f"{index:>2}  {entry.relative_path.as_posix()}")
    selected = typer.prompt("Select number, A for all, or Q to quit").strip().casefold()
    if selected in {"q", "quit"}:
        return
    if selected in {"a", "all"}:
        succeeded = sum(_run_source(entry.video_path, app_config) for entry in entries)
        typer.echo(f"Completed {succeeded}/{len(entries)} raw videos")
        return
    try:
        entry = entries[int(selected) - 1]
    except (ValueError, IndexError):
        raise typer.BadParameter(f"Enter a number from 1 to {len(entries)}, A, or Q") from None
    _run_source(entry.video_path, app_config)


@app.command()
def inspect(
    video_path: Annotated[Path, typer.Argument(help="Raw source video path used by candidate-mining run")],
    config: Annotated[Path | None, typer.Option(help="Path to TOML configuration")] = None,
) -> None:
    """Open raw video with persisted person boxes; writes no artifact."""
    source = _validate_video(video_path)
    app_config = load_config(config)
    store = read_person_detection_store(
        person_detection_path(app_config.paths.review_queue_dir, source, raw_dir=app_config.paths.raw_dir), source
    )
    typer.echo("Controls: Space pause/play; Left/Right step; [/ ] seek 5s; o overlay; q/Esc close")
    inspect_raw_video(source, store)


@app.command()
def browse(
    config: Annotated[Path | None, typer.Option(help="Path to TOML configuration")] = None,
) -> None:
    """List raw videos alphabetically and open one with existing persisted boxes."""
    app_config = load_config(config)
    typer.echo("Scanning raw videos and validating persisted person JSON files...")
    entries = catalog_raw_videos(app_config.paths.raw_dir, app_config.paths.review_queue_dir)
    if not entries:
        typer.echo(f"No supported raw videos found under {app_config.paths.raw_dir}")
        return
    while True:
        typer.echo("\n#   Raw video (alphabetical)                                      JSON      Boxes")
        typer.echo("-" * 88)
        for index, entry in enumerate(entries, start=1):
            boxes = "-" if entry.box_count is None else str(entry.box_count)
            typer.echo(f"{index:>2}  {entry.relative_path.as_posix():<62} {entry.status:<8} {boxes}")
        try:
            selected = typer.prompt("Select number, or q to quit").strip()
        except (EOFError, typer.Abort):
            return
        if selected.casefold() in {"q", "quit"}:
            return
        try:
            entry = entries[int(selected) - 1]
        except (ValueError, IndexError):
            typer.echo(f"Enter a number from 1 to {len(entries)}, or q.")
            continue
        if entry.status not in {"READY", "EMPTY"} or entry.store is None:
            typer.echo(f"{entry.status}: {entry.detail}")
            continue
        spans = [span for span in entry.store.presence_segments if span.category == "person_detected"]
        if not spans:
            typer.echo("person_detected: no logical spans")
            continue
        typer.echo("\n1  person_detected | " + str(len(spans)) + " logical spans")
        category = typer.prompt("Select category number, or b to return").strip().casefold()
        if category in {"b", "back"}:
            continue
        if category != "1":
            typer.echo("Only person_detected is available in this POC.")
            continue
        while True:
            typer.echo("\nID                    detected range       context range        max people  note")
            typer.echo("-" * 94)
            for index, span in enumerate(spans, start=1):
                full_source = span.context_start_sec == 0.0 and span.context_end_sec >= entry.store.detections[-1].timestamp_sec
                note = "full source; context clipped" if full_source else ""
                typer.echo(
                    f"{index:>2}  {span.span_id:<20} {span.candidate_start_sec:>6.1f}-{span.candidate_end_sec:<6.1f} "
                    f"{span.context_start_sec:>6.1f}-{span.context_end_sec:<6.1f} {str(span.person_count_max):>10}  {note}"
                )
            selected_span = typer.prompt("Select span number, or b to return").strip().casefold()
            if selected_span in {"b", "back"}:
                break
            try:
                span = spans[int(selected_span) - 1]
            except (ValueError, IndexError):
                typer.echo(f"Enter a number from 1 to {len(spans)}, or b.")
                continue
            _span_action(entry.video_path, entry.store, span, app_config)


def _span_action(video_path: Path, store, span, app_config) -> None:
    """Let an operator view or explicitly export one bounded source span."""
    while True:
        action = typer.prompt("V view, E clean MP4, A bbox MP4, or B back").strip().casefold()
        if action in {"b", "back"}:
            return
        if action in {"v", "view"}:
            typer.echo("Controls: Space pause/play; Left/Right step; [/ ] seek 5s; o overlay; q/Esc close")
            inspect_raw_video(
                video_path,
                store,
                context_start_sec=span.context_start_sec,
                context_end_sec=span.context_end_sec,
            )
            continue
        if action in {"e", "export", "clean"}:
            _export_span(video_path, store, span, app_config)
            continue
        if action in {"a", "annotated", "bbox"}:
            _export_span(video_path, store, span, app_config, annotated=True)
            continue
        typer.echo("Enter V to view, E for clean MP4, A for bbox MP4, or B to return.")


def _export_span(video_path: Path, store, span, app_config, *, annotated: bool = False) -> None:
    """Save a selected context span only after an explicit destination choice."""
    target = choose_export_path(
        video_path,
        span.span_id,
        span.context_start_sec,
        span.context_end_sec,
        annotated=annotated,
    )
    if target is None:
        typer.echo("Export cancelled; no file written.")
        return
    try:
        target = normalize_export_target(video_path, target)
    except ValueError as error:
        typer.echo(f"Export not started: {error}")
        return
    if target.exists():
        overwrite = typer.confirm(f"Overwrite existing file? {target}", default=False)
        if not overwrite:
            typer.echo("Export cancelled; existing file left unchanged.")
            return
    try:
        tools = resolve_media_tools(app_config.paths.ffmpeg_dir)
        if annotated:
            typer.echo("Rendering stored 5-FPS bbox snapshots; this can take longer than clean export.")
            export_clip_with_bboxes(
                video_path,
                span.context_start_sec,
                span.context_end_sec,
                target,
                store,
                ffmpeg=tools.ffmpeg,
            )
        else:
            export_clip(
                video_path,
                span.context_start_sec,
                span.context_end_sec,
                target,
                ffmpeg=tools.ffmpeg,
            )
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        typer.echo(f"Export failed: {error}")
        return
    export_kind = "annotated bbox" if annotated else "clean"
    typer.echo(f"Exported local {export_kind} MP4: {target.resolve()}")


if __name__ == "__main__":
    app()
