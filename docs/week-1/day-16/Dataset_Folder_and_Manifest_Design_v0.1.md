# Dataset Folder and Manifest Design v0.1

> **Ngày:** 16/07/2026
> **Owner:** B — Data & Automation
> **Trạng thái:** Design specification. Week 1 chưa có raw data; không có inventory, manifest hay candidate result thực tế.
> **Code basis:** `config.py`, `debug_artifacts.py`, `models.py`, `.gitignore`.

## 1. Current repository contract

```text
data/raw/                         raw camera video, local-only
data/inventory/                   reserved; no current CLI output
data/manifests/                   reserved; no current CLI output
data/review_queue/person_detected/ current POC JSON output
outputs/logs/                     local runtime logs
after local setup: models/weights/, models/cache/, .cache/torch/, tools/ffmpeg/
```

All paths above are Git-ignored. Current `candidate-mining run` writes **one** `person-detections.v1` JSON per raw source under `data/review_queue/person_detected/`; raw-relative subfolders are preserved to avoid name collisions. Rerun replaces the same JSON atomically. It does not create inventory JSON, candidate CSV, proxy/review MP4 or batch manifest.

## 2. Current JSON evidence

The JSON holds source filename/path/SHA-256/FPS/frame dimensions; detector sample FPS/image size/confidence/person class; actual detection snapshots; and logical `person_detected` presence segments. Technical `track_id` and `episode_id` are debugging metadata, not identity or final label.

## 3. Planned manifest contract

`models.py` defines a future `CandidateSample` CSV shape: `sample_id`, `source_id`, `source_path`, `camera_id`, `clip_path`, clip/candidate start/end, `categories`, `selection_source`, person/signal scores, `context_status`, `review_status`, anomaly types, tracks/episodes and reconciliation status.

This contract is **not currently generated**. `camera_id`, human review, ROI, rule-engine, alert, ground-truth, eligibility, source-group and dataset-version fields must be added/received in a future controlled contract; they are absent from the current person JSON.

## 4. Planned data controls

- Assign source identity from full-file SHA-256; keep raw source read-only.
- Keep source-group, split eligibility and version/change information outside raw paths.
- Store only references to sensitive video in any tracked documentation.
- Raw video, derived JSON/CSV/MP4 and manifests remain local; commit only non-sensitive code, config, schemas, docs and permitted fixtures.
