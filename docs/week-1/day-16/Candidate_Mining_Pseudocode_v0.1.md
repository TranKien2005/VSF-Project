# Candidate Mining Pseudocode v0.1

> **Ngày:** 16/07/2026
> **Owner:** B — Data & Automation
> **Trạng thái:** Current POC plus clearly separated target design; no Week 1 raw-data execution.
> **Code basis:** `pipeline.py`, `automatic_signals.py`, `frame_sampling.py`, `segments.py`, `debug_artifacts.py`.

## 1. Implemented POC

```text
for selected raw video:
    sample decoded source frames at configured sample_fps (currently 5)
    run enabled providers; require one person provider
    run local RT-DETR-L person detection and technical tracking
    retain accepted person observations
    merge source-level any-person samples when gap <= 2 seconds
    set context = candidate range +/- 5 seconds, bounded by source duration
    write/replace one person-detections.v1 JSON for this source

browse:
    read raw + matching JSON
    list person_detected logical spans
    view raw bbox context or manually Save As clean/bbox MP4
```

Current RT-DETR profile is person class only, confidence `0.20`, image size `960`, batch `1`, device `auto`. Bbox snapshots are held until the next 5-FPS sample for display; this is not interpolation or new inference.

## 2. Current limitations

Although automatic-signal code can instantiate cover, movement and anomaly providers, the current pipeline persists only person observations/segments. It does not persist cover/movement/anomaly candidate evidence, conclude event type/ROI/severity, create candidate CSV/proxy batches, inventory sources, select random/risk samples, or create human review queues.

## 3. Planned target flow — NOT IMPLEMENTED

```text
raw receipt -> inventory/checksum -> source grouping/eligibility
 -> sampled technical signals -> merge candidates -> candidate manifest
 -> controlled tool/random/risk sampling -> human review
 -> annotation/ground truth -> alert matching -> KPI report
```

Any implementation of this target must preserve source-relative time, keep candidate evidence distinct from labels, and treat ROI Green/Yellow/Red, cover area/duration, movement evidence and rule-engine severity as review/system fields—not POC conclusions.
