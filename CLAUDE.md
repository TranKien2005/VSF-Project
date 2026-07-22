# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Scope and evidence boundary

VSF Candidate Mining is a local Python 3.11 desktop proof of concept that prepares **technical person-detection evidence** from external camera video. Persisted detections, boxes, technical tracks, ROI candidates, and result categories are never final event labels, intrusion/authorization decisions, severity, ground truth, or KPI conclusions.

The supported processing lane is one enabled person detector (normally Ultralytics RT-DETR-L pretrained on COCO and filtered to `person`). Do not describe cover, camera movement, anomaly, annotation, or KPI helpers/documents as implemented output lanes unless they are wired end-to-end through configuration, processing, persistence, and UI.

## Environment and commands

Use Python 3.11. The editable install includes optional runtime and development dependencies:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -e ".[vision,gui,dev]"
```

```powershell
# Entire test suite and lint
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m ruff check .

# One test module or one test
.\.venv\Scripts\python -m pytest apps/candidate-mining/tests/test_roi.py
.\.venv\Scripts\python -m pytest apps/candidate-mining/tests/test_roi.py::test_name

# Desktop application
.\.venv\Scripts\candidate-mining-gui
# Equivalent CLI entry point
.\.venv\Scripts\candidate-mining gui

# Explicit model download. Normal processing must use local artifacts only.
.\.venv\Scripts\candidate-mining download-weights --model rtdetr-l

# Register an external video without copying it
.\.venv\Scripts\candidate-mining import-video "D:\camera-data\front-gate.mp4"
```

FFmpeg and FFprobe are required for source probing and exports. Resolution prefers `tools/ffmpeg/*.exe`, then `PATH`.

Project configuration is [configs/candidate-mining.toml](configs/candidate-mining.toml). [config.py](apps/candidate-mining/src/candidate_mining/config.py) resolves all configured paths under the repository root and validates pipeline settings. The current default sampling rate is configured there; do not assume a sampling rate from older docs.

## Architecture

The installable package is [apps/candidate-mining/src/candidate_mining/](apps/candidate-mining/src/candidate_mining/). The `candidate-mining` Typer CLI is [cli.py](apps/candidate-mining/src/candidate_mining/cli.py); `candidate-mining-gui` launches the PySide6 desktop application via [gui/app.py](apps/candidate-mining/src/candidate_mining/gui/app.py).

### Import catalog and ROI

[processed_store.py](apps/candidate-mining/src/candidate_mining/processed_store.py) owns **metadata only** for imported external media and cameras. It probes a video, computes its full SHA-256 as `source-id`, and stores the original absolute path only as a locator. Resolving a source re-verifies the checksum, so copying local metadata/results to another machine and re-importing an unchanged file reconnects it without depending on its former path.

- An individual import creates an independent source.
- A camera-folder import uses the selected outer folder's name as the camera and assigns every recursively discovered video to it; intermediate folders are not cameras.
- `data/processed/` must never own detections, candidate boxes, review state, or final labels.

Metadata is stored under:

```text
data/processed/
  videos/<source-id>/source.json
  videos/<source-id>/roi.json
  cameras/<camera-id>/camera.json
  cameras/<camera-id>/roi.json
  cameras/<camera-id>/videos/<source-id>/source.json
  cameras/<camera-id>/videos/<source-id>/roi.json
```

[roi.py](apps/candidate-mining/src/candidate_mining/roi.py) implements exactly one `track-roi-line.v1` ROI. It derives a divider from an operator stroke, extends/clips the divider to the frame, and selects the smaller closed partition. A detection is in the ROI when its bbox bottom-centre footpoint is inside that polygon; the boundary is included. Detector input remains full-frame. Effective ROI precedence is source override → camera shared default → none.

### Processing and technical results

[gui/processed_window.py](apps/candidate-mining/src/candidate_mining/gui/processed_window.py) is the desktop shell: one shared source hierarchy drives the Sources, ROI Setup, Process, Review, and Export tabs. UI workers in [gui/import_worker.py](apps/candidate-mining/src/candidate_mining/gui/import_worker.py) and [gui/processing_worker.py](apps/candidate-mining/src/candidate_mining/gui/processing_worker.py) keep long import/processing work off the Qt UI thread.

[pipeline.py](apps/candidate-mining/src/candidate_mining/pipeline.py) is the orchestration boundary: it requires a registered, checksum-verified source and an effective ROI; invokes [automatic_signals.py](apps/candidate-mining/src/candidate_mining/automatic_signals.py) for sampling, person detection, and technical tracking; then publishes candidates. Detection providers live under [providers/](apps/candidate-mining/src/candidate_mining/providers/). [debug_artifacts.py](apps/candidate-mining/src/candidate_mining/debug_artifacts.py) retains persisted detection snapshots, and [debug_renderer.py](apps/candidate-mining/src/candidate_mining/debug_renderer.py) renders the held-snapshot review overlay.

[result_store.py](apps/candidate-mining/src/candidate_mining/result_store.py) owns `technical-candidate.v2` persistence. A successful run atomically replaces one source's complete result set using a staging directory. Candidate directories are grouped by source, then technical category:

```text
data/results/
  videos/<source-id>/<category>/<candidate-id>/candidate.json
  cameras/<camera-id>/videos/<source-id>/<category>/<candidate-id>/candidate.json
```

A candidate records source/camera provenance, technical category and trigger, source-relative and context bounds, stored detections, non-identity track/episode diagnostics, review state, and ROI provenance. Category directories identify technical origin only. Processing does not create MP4s; [exporter.py](apps/candidate-mining/src/candidate_mining/exporter.py) creates exports only as an explicit operator action.

## Local artifacts and planning documents

`data/processed/**`, `data/results/**`, logs, model weights/caches, Torch cache, and portable FFmpeg are local Git-ignored artifacts. Raw media and generated evidence can be sensitive; do not commit or push them.

The Week 1/plan documents under [docs/](docs/) are contracts and planning artifacts unless behavior is visibly implemented in code. Preserve the distinction between planned annotation/KPI workflows and the current technical-evidence workflow.
