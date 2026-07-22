# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Scope and evidence boundary

VSF Candidate Mining is a local Python 3.11 desktop proof of concept that prepares **technical evidence** from external camera video. Persisted detections, boxes, technical tracks, ROI candidates, and result categories are never final event labels, intrusion/authorization decisions, severity, ground truth, or KPI conclusions.

The configured person lane normally uses Ultralytics RT-DETR-L pretrained on COCO and filters to `person`. A generic `camera_anomaly` technical candidate path is wired through processing and results, but it is not a validated or complete classification of cover, camera movement, rain, glare, or other business events. Annotation, final labels, and KPI workflows remain separate specifications unless implemented end-to-end.

## Environment and commands

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -e ".[vision,gui,dev]"

.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m pytest apps/candidate-mining/tests/test_roi.py
.\.venv\Scripts\python -m pytest apps/candidate-mining/tests/test_roi.py::test_name

.\.venv\Scripts\candidate-mining-gui
.\.venv\Scripts\candidate-mining gui
.\.venv\Scripts\candidate-mining download-weights --model rtdetr-l
.\.venv\Scripts\candidate-mining import-video "D:\camera-data\front-gate.mp4"
```

FFmpeg and FFprobe are required for source probing and exports. Resolution prefers `tools/ffmpeg/*.exe`, then `PATH`.

Project configuration is [configs/candidate-mining.toml](configs/candidate-mining.toml). [config.py](apps/candidate-mining/src/candidate_mining/config.py) resolves configured paths under the repository root. The default sampling rate is currently 2 FPS; the GUI permits a per-run sample-rate and batch-size override.

## Architecture

The installable package is [apps/candidate-mining/src/candidate_mining/](apps/candidate-mining/src/candidate_mining/). The `candidate-mining` Typer CLI is [cli.py](apps/candidate-mining/src/candidate_mining/cli.py); `candidate-mining-gui` launches the PySide6 desktop application via [gui/app.py](apps/candidate-mining/src/candidate_mining/gui/app.py).

### Import catalog and ROI

[processed_store.py](apps/candidate-mining/src/candidate_mining/processed_store.py) owns metadata for imported external media and cameras. It probes a video, computes its full SHA-256 as `source-id`, and records the original absolute path as a locator. Source resolution verifies existence and checksum before processing/export.

`data/processed/` contains source/camera metadata and optional ROI configuration only:

```text
data/processed/
  videos/<source-id>/source.json
  videos/<source-id>/roi.json
  cameras/<camera-id>/camera.json
  cameras/<camera-id>/roi.json
  cameras/<camera-id>/videos/<source-id>/source.json
  cameras/<camera-id>/videos/<source-id>/roi.json
```

[roi.py](apps/candidate-mining/src/candidate_mining/roi.py) implements `track-roi-stroke.v1`: an operator-drawn freehand stroke forms a closed region or is extended to the frame boundary by endpoint tangents. The smaller partition is selected by default and can be flipped. A detection is in the ROI when its bbox bottom-centre footpoint is in the selected polygon; the boundary is included. Detector input remains full-frame. Effective ROI precedence is source override → camera shared default → none.

### Processing and technical results

[gui/processed_window.py](apps/candidate-mining/src/candidate_mining/gui/processed_window.py) is the desktop shell: one source hierarchy drives Sources, ROI Setup, Process, Review, and Export. [gui/import_worker.py](apps/candidate-mining/src/candidate_mining/gui/import_worker.py) and [gui/processing_worker.py](apps/candidate-mining/src/candidate_mining/gui/processing_worker.py) keep long operations off the Qt UI thread.

[pipeline.py](apps/candidate-mining/src/candidate_mining/pipeline.py) requires a registered checksum-verified source and effective ROI. It calls [automatic_signals.py](apps/candidate-mining/src/candidate_mining/automatic_signals.py) for sampling, configured person inference, technical tracking, and generic camera-anomaly signals, then atomically publishes source-scoped candidates. [debug_artifacts.py](apps/candidate-mining/src/candidate_mining/debug_artifacts.py) defines persisted detection snapshots and [debug_renderer.py](apps/candidate-mining/src/candidate_mining/debug_renderer.py) provides held-snapshot review overlays.

[result_store.py](apps/candidate-mining/src/candidate_mining/result_store.py) owns `technical-candidate.v2` persistence:

```text
data/results/
  videos/<source-id>/<category>/<candidate-id>/candidate.json
  cameras/<camera-id>/videos/<source-id>/<category>/<candidate-id>/candidate.json
```

A candidate stores provenance, category/trigger, source-relative and context bounds, embedded technical detections, track/episode diagnostics, review state, and ROI provenance. Categories describe technical origin only. Processing does not create MP4s; [exporter.py](apps/candidate-mining/src/candidate_mining/exporter.py) is invoked only for explicit exports.

## Local artifacts and separate labeling specifications

`data/processed/**`, `data/results/**`, logs, model weights/caches, Torch cache, and portable FFmpeg are local Git-ignored artifacts. Raw media and generated evidence can be sensitive; do not commit or push them.

[docs/huong-dan-gan-nhan.md](docs/huong-dan-gan-nhan.md) and [docs/yeu-cau-va-huong-dan-tool-gan-nhan.md](docs/yeu-cau-va-huong-dan-tool-gan-nhan.md) define a future human-labeling workflow. They do not describe current Candidate Mining output behavior.
