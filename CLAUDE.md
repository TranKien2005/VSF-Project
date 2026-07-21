# CLAUDE.md

## Project scope

VSF Candidate Mining is a local Python 3.11 desktop proof of concept that prepares **technical person-detection evidence** from external camera videos. Persisted detections, boxes, technical tracks, ROI candidates, and result categories are never final event labels, intrusion/authorization decisions, severity, ground truth, or KPI conclusions.

The active detector lane is Ultralytics RT-DETR-L pretrained on COCO, filtered to `person`. Cover, camera movement, anomaly, annotation, and KPI contracts may exist in documents or helpers, but must not be represented as implemented output lanes unless wired end-to-end.

## Setup and checks

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -e ".[vision,gui,dev]"

.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\candidate-mining-gui
```

Download model weights explicitly; regular processing must load local artifacts only:

```powershell
.\.venv\Scripts\candidate-mining download-weights --model rtdetr-l
```

FFmpeg and FFprobe are required for exports and source probing. Resolution prefers `tools/ffmpeg/*.exe`, then `PATH`.

## Current architecture

The installable package is [apps/candidate-mining/src/candidate_mining/](apps/candidate-mining/src/candidate_mining/). `candidate-mining-gui` maps to `candidate_mining.gui.app:main`; the small CLI exposes explicit model download and independent-video registration.

### Imported metadata

[processed_store.py](apps/candidate-mining/src/candidate_mining/processed_store.py) persists metadata only under:

```text
data/processed/
  videos/<source-id>/source.json
  videos/<source-id>/roi.json
  cameras/<camera-id>/camera.json
  cameras/<camera-id>/roi.json
  cameras/<camera-id>/videos/<source-id>/source.json
  cameras/<camera-id>/videos/<source-id>/roi.json
```

- Individual import creates an independent video entry.
- A camera-folder import uses the selected outer folder name as camera name and assigns all recursively discovered videos to that camera; nested directory names are not cameras.
- `source-id` is the full SHA-256 of external source content. External absolute paths are locators only. When local processed/results data is copied to another machine, re-importing the unchanged video restores links through the same checksum.
- `processed` must not own detections, boxes, candidates, review state, or final labels.

### One-line ROI

[roi.py](apps/candidate-mining/src/candidate_mining/roi.py) defines exactly one `track-roi-line.v1` configuration at a source or camera scope. The operator draws a straight divider; the implementation extends/clips the infinite line to the frame edges, derives both closed partitions, and selects the smaller polygon. A bbox belongs to this ROI only when its bottom-centre footpoint lies within that polygon (boundary included). Full-frame detection is never cropped by ROI.

Effective ROI resolution is source override → camera shared default → none.

### Technical results

[result_store.py](apps/candidate-mining/src/candidate_mining/result_store.py) persists one `candidate.json` per technical subvideo/context under:

```text
data/results/person_detected/<candidate-id>/candidate.json
data/results/roi_track/<candidate-id>/candidate.json
```

Each result records source/camera identity, technical category and trigger, source-relative bounds, saved detection boxes in context, technical track/episode IDs, review state, and effective ROI provenance. Folder category is technical origin, not a final human/business label. Processing never creates MP4s; exporters remain explicit operator actions.

[pipeline.py](apps/candidate-mining/src/candidate_mining/pipeline.py) resolves and checksum-verifies the selected imported source, runs full-frame detection, writes `person_detected` candidates, then derives `roi_track` candidates if an effective ROI exists. [debug_renderer.py](apps/candidate-mining/src/candidate_mining/debug_renderer.py)'s held 5-FPS snapshot rendering policy remains applicable.

### Desktop flow

[processed_window.py](apps/candidate-mining/src/candidate_mining/gui/processed_window.py) has a single global source hierarchy at left and top tabs: Sources, ROI Setup, Process, Review, Export. Source selection belongs only to the hierarchy. Review filters category/candidates for the global source; Export uses the selected candidate context.

## Data policy

`data/processed/**`, `data/results/**`, logs, weights, model caches, Torch cache, and portable FFmpeg are local Git-ignored artifacts. Raw camera media and generated evidence can be sensitive. Do not commit or push them; commit only approved code, documentation, configuration, and test fixtures.

Week 1 documents remain planning/contract artifacts unless code visibly implements their behavior. Preserve the distinction between planned annotation/KPI workflow and current technical evidence functionality.
