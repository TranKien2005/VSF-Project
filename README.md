# VSF Candidate Mining

VSF Candidate Mining is a local Python 3.11 desktop proof of concept for preparing **technical evidence** from external camera video. It does not produce final intrusion, authorization, loitering, severity, ground-truth, KPI, or business-event decisions.

The current technical outputs are ROI-filtered `person_detected` candidates and a secondary generic `camera_anomaly` signal path. A category, bbox, technical track, ROI match, or candidate is evidence for review—not a final label.

## Install and launch

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -e ".[vision,gui,dev]"

# Download explicitly; processing does not download weights.
.\.venv\Scripts\candidate-mining download-weights --model rtdetr-l

# Start the desktop application.
.\.venv\Scripts\candidate-mining-gui
```

The configured person detector is Ultralytics RT-DETR-L pretrained on COCO and filtered to `person`. The default profile in [configs/candidate-mining.toml](configs/candidate-mining.toml) samples at 2 FPS, uses image size 960, batch size 4, and confidence threshold 0.30. The Process tab permits a per-run sampling and batch-size override.

FFmpeg and FFprobe are required for source probing and explicit exports. The application prefers `tools/ffmpeg/` and otherwise resolves them from `PATH`.

## Desktop workflow

1. **Sources:** import independent external videos or a camera folder. Import records metadata and SHA-256 provenance only; it never copies, moves, renames, or modifies source media.
2. **ROI Setup:** draw one freehand divider/closed stroke on a reference frame. The application derives a tracking partition, defaulting to the smaller partition; it may be flipped and saved as a source override or camera shared default.
3. **Process:** processing requires a registered checksum-verified source and effective ROI. It runs full-frame person detection, then filters detections by the bbox bottom-centre footpoint in the tracking ROI. A boundary footpoint is included.
4. **Review:** select technical candidates and view their source-video context. Saved bbox snapshots are held until the next sampled frame; this is not per-frame inference, interpolation, or prediction.
5. **Export:** export is an explicit operator action. Processing itself never creates MP4 files.

ROI precedence is source/video override → camera shared default → no ROI. Full-frame detector input is never cropped by ROI.

## Local artifact layout

```text
data/
  processed/
    videos/<source-id>/source.json
    videos/<source-id>/roi.json
    cameras/<camera-id>/camera.json
    cameras/<camera-id>/roi.json
    cameras/<camera-id>/videos/<source-id>/source.json
    cameras/<camera-id>/videos/<source-id>/roi.json

  results/
    videos/<source-id>/<category>/<candidate-id>/candidate.json
    cameras/<camera-id>/videos/<source-id>/<category>/<candidate-id>/candidate.json
```

`source-id` is the video file's full SHA-256 checksum. `data/processed/` stores imported source/camera metadata and optional ROI configuration only. `candidate.json` uses the `technical-candidate.v2` schema and stores source/camera provenance, category and trigger, candidate/context bounds, saved technical detections, technical track/episode diagnostics, review state, and ROI provenance.

A successful run atomically replaces the complete result set for the processed source. Result categories express technical origin only. The generic `camera_anomaly` signal is not a validated classification of camera cover, rain, glare, shake, or rotation.

All `data/processed/**` and `data/results/**` artifacts are local and Git-ignored. Camera footage and generated evidence can be sensitive; do not commit or push them.

## Optional CLI registration

```powershell
.\.venv\Scripts\candidate-mining import-video "D:\camera-data\front-gate.mp4"
```

## Verification

```powershell
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m pytest
```

See [docs/desktop-roi-workflow.md](docs/desktop-roi-workflow.md) for the current technical workflow. The human-labeling requirements in [docs/huong-dan-gan-nhan.md](docs/huong-dan-gan-nhan.md) and [docs/yeu-cau-va-huong-dan-tool-gan-nhan.md](docs/yeu-cau-va-huong-dan-tool-gan-nhan.md) are specifications for a separate labeling workflow; they are not current Candidate Mining output behavior.
