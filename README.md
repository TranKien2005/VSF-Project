# VSF Candidate Mining

VSF Candidate Mining is a local Python 3.11 desktop proof of concept for preparing **technical person-detection evidence** from camera video. A saved bounding box, track ID, ROI candidate, or result category is not an intrusion decision, authorization decision, final event label, severity, ground truth, or KPI result.

## Install and launch

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -e ".[vision,gui,dev]"

# Download explicitly; processing never downloads weights.
.\.venv\Scripts\candidate-mining download-weights --model rtdetr-l

# Start the desktop application.
.\.venv\Scripts\candidate-mining-gui
```

The enabled POC model is Ultralytics RT-DETR-L pretrained on COCO, filtered to `person`. Install FFmpeg/FFprobe for manual export; the application prefers `tools/ffmpeg/` and otherwise uses `PATH`.

## Desktop workflow

1. **Sources:** import individual videos or select one outer camera folder. Import stores metadata only; source media stays at its original external location and is never copied, moved, renamed, or modified.
2. **ROI Setup:** draw exactly one straight divider over a reference frame. The application extends/clips the divider to frame edges and automatically selects the smaller resulting frame partition as the sole tracking ROI.
3. **Process:** run full-frame person detection for the globally selected imported source. ROI does not crop detector input.
4. **Review:** select the source, a technical category, and a candidate/subvideo context. Bounding boxes are stored 5-FPS snapshots and held visually until the next sample; no 30-FPS inference or motion interpolation is performed.
5. **Export:** export is always an explicit operator action. Processing does not generate MP4s.

A person produces `roi_track` evidence when the bottom-centre footpoint of a persisted person bbox is inside the derived smaller ROI partition. A footpoint on the boundary is included. Technical track/episode IDs are non-identity diagnostics and do not split a candidate.

## Local artifact layout

```text
data/
  processed/
    videos/<source-id>/source.json
    videos/<source-id>/roi.json                 # optional source ROI
    cameras/<camera-id>/camera.json
    cameras/<camera-id>/roi.json                # optional shared camera ROI
    cameras/<camera-id>/videos/<source-id>/source.json
    cameras/<camera-id>/videos/<source-id>/roi.json  # optional source override

  results/
    person_detected/<candidate-id>/candidate.json
    roi_track/<candidate-id>/candidate.json
```

The selected folder's name is the camera name. Videos at any depth below that folder belong to the same camera; nested folder names do not create separate cameras.

`source-id` is the source file's full SHA-256 checksum. `candidate.json` records the same source ID/checksum, optional camera ID, ranges, technical boxes, track/episode diagnostics, trigger reason, state, and effective ROI provenance. Consequently, copying `data/processed/` and `data/results/` to another machine and re-importing the same unchanged video reconnects source metadata and results through the checksum, even though the external path differs.

ROI precedence is: source/video override → camera shared ROI → no ROI. `processed` never stores detections, candidates, review state, or final labels. Result categories describe technical origin only.

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
