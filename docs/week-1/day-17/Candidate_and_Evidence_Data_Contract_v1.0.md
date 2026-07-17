# Candidate and Evidence Data Contract v1.0

> **Ngày:** 17/07/2026
> **Owner:** B — Data & Automation
> **Trạng thái:** Current JSON contract plus planned handoff contracts. No candidate manifest or human-review record is currently generated.

## 1. Implemented person JSON contract

Schema: `person-detections.v1`.

| Area | Persisted fields |
|---|---|
| Source | `filename`, `path`, `sha256`, `fps`, `frame_width`, `frame_height` |
| Detector | `sample_fps`, `image_size`, `confidence_threshold`, `class_filter=[person]`, viewer box policy |
| Detection | `source_frame_index`, `timestamp_sec`, `bbox_xyxy_px`, `confidence`, `track_id`, `episode_id` |
| Presence span | `span_id`, `category=person_detected`, `review_status=pending_review`, candidate/context bounds, person count max, track/episode IDs |

Reader validation rejects mismatched source filename/SHA-256. A track/episode is technical debug metadata only: it is not identity, authorization, ROI state, event label or ground truth.

## 2. Planned candidate manifest — NOT IMPLEMENTED

Future candidate rows use `CandidateSample` fields: sample/source/camera IDs; source/clip paths; clip and candidate bounds; categories; selection source; person/motion/brightness/blur/camera-shift scores; context/review status; anomaly types; technical tracks/episodes and reconciliation status.

The current POC does not generate this CSV, proxy clips, random/risk sample rows or persisted cover/movement/anomaly categories.

## 3. Planned review/system evidence contract

Human/system layers must add: source-relative final event boundaries, review category/status, `roi_config_id`, ROI version/snapshot/effective time, cover area/duration, movement evidence, reviewer/adjudication, alert ID/category/timestamp, rule ID/version, `rule_engine_severity_output`, eligibility, evidence reference and dataset/run version.

ROI category Green/Yellow/Red is evidence; reviewer does not assign severity. Cover ≥30%/≥120s and movement strong shake/rotation are review rules, not fields inferred from current person JSON.
