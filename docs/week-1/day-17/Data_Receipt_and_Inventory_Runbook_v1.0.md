# Data Receipt and Inventory Runbook v1.0

> **Ngày:** 17/07/2026
> **Owner:** B — Data & Automation
> **Trạng thái:** Runbook for Week 2 data receipt; no inventory has been run in Week 1.

## 1. Intake procedure

1. Record non-sensitive receipt reference, permitted access and local storage location.
2. Keep received raw video read-only; do not commit/copy it into tracked documentation.
3. Assign/record `source_id`, `camera_id` when supplied, recording period and source-time basis.
4. Resolve FFmpeg/ffprobe and probe media metadata.
5. Calculate complete source SHA-256; record unreadable/no-video-stream failures separately.
6. Record exact duplicate candidates from checksum; flag possible near/temporal duplicates for review.
7. Record absent camera, time, ROI, rule-engine or train-provenance metadata as `Unknown`.
8. Only after receipt/inventory checks, decide whether a source can enter technical mining.

## 2. Current code capability

`inventory.probe_video(video_path, ffprobe=...)` can produce source ID, resolved source path, filename, size, SHA-256, duration, FPS, dimensions, codec, container and audio presence. `write_inventory` can write a local inventory JSON.

These are **library functions**, not a `candidate-mining` CLI workflow today. `candidate-mining run` runs person detection and writes person JSON; it is not an inventory command.

## 3. Local result policy

Inventory records, checksums, invalid-file lists and duplicate reports are local generated artifacts. Their existence/result must be reported only after execution. Do not fabricate counts, received video paths, camera metadata or validation outcomes in Week 1 documents.
