# Desktop technical-evidence workflow

## Scope

The desktop application prepares technical evidence for later human review. It does not automatically decide intrusion, authorization, loitering, severity, a final label, ground truth, or KPI.

The configured person lane uses full-frame RT-DETR-L inference filtered to COCO `person`. The current default sampling rate is **2 FPS**; the Process tab can override sampling and batch size for one run. The UI holds the most recent saved bbox snapshot until the next sample. This is a display policy, not inference on every source frame and not motion interpolation.

## Import and durable source metadata

Use **Sources** to import either independent external video files or a camera folder. Import never copies or changes source media. It probes the source, computes its full SHA-256 checksum as `source-id`, and keeps the external absolute path as a locator.

Before processing or export, the selected source must exist and its checksum must still match the registered metadata. Imported metadata and results are source-scoped:

```text
data/processed/
  videos/<source-id>/source.json
  videos/<source-id>/roi.json
  cameras/<camera-id>/camera.json
  cameras/<camera-id>/roi.json
  cameras/<camera-id>/videos/<source-id>/source.json
  cameras/<camera-id>/videos/<source-id>/roi.json

data/results/
  videos/<source-id>/<category>/<candidate-id>/candidate.json
  cameras/<camera-id>/videos/<source-id>/<category>/<candidate-id>/candidate.json
```

`data/processed/` contains source/camera metadata and optional ROI configuration only. It must not contain detections, candidate boxes, technical categories, final labels, or review state.

## Freehand track ROI

ROI Setup has one freehand-stroke interaction:

1. Load a source reference frame.
2. Draw one simple stroke inside the frame.
3. A near-closed stroke can form its own closed region. Otherwise, endpoint tangents extend to the frame boundary and close the stroke with frame edges.
4. The smaller derived partition is selected by default; the operator may flip to the opposite partition.
5. Save either a source override or, for a camera-owned source, a camera shared default.

Effective ROI precedence is source override → camera shared ROI → none. A detection belongs to the tracking ROI only if its bbox bottom-centre footpoint lies in the selected region; boundary points are included. The detector always analyzes the complete frame.

## Processing, review, and export

Processing requires a registered, checksum-verified source and effective saved ROI. The application samples the source, performs detection and technical tracking, and atomically publishes source-scoped `technical-candidate.v2` records.

- `person_detected` records are ROI-filtered technical person evidence. Track/episode IDs are diagnostics, not identity or final labels.
- `camera_anomaly` may be emitted as a generic secondary technical signal. It is not a complete classification of cover, rain, glare, shake, or rotation.
- Each candidate stores source/camera checksum provenance, category, trigger reason, candidate/context time bounds, saved technical detections, diagnostics, review state, and ROI provenance.

The Review tab loads candidate context from the source video and marks the context start/end on the timeline. Technical boxes and ROI overlays are review aids only.

No MP4 is generated during processing. Export is a later explicit operator action: clean export uses FFmpeg, and annotated export uses persisted evidence rather than rerunning the detector.

## Launch and checks

```powershell
.\.venv\Scripts\python -m pip install -e ".[vision,gui,dev]"
.\.venv\Scripts\candidate-mining-gui
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m ruff check .
```
