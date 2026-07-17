# Metadata Schema v0.1

> **Ngày:** 16/07/2026
> **Owner:** C — Annotation & Data Quality
> **Trạng thái:** Proposed additive extension to existing `person-detections.v1`; not emitted or read by current code.

## 1. Storage decision

Annotations will extend the same per-source `person-detections.v1` JSON produced by B. No standalone annotation format/file is introduced. Existing `source`, `detector`, `detections` and `presence_segments` data must remain unchanged as technical evidence.

Current anchors are `source.path`, `source.sha256`, `span_id`, `candidate_start_sec`, `candidate_end_sec`, `context_start_sec` and `context_end_sec`. Current JSON has no final human event interval, label, reviewer, ROI or ground-truth fields.

## 2. Proposed annotation fields

| Field | Meaning |
|---|---|
| `annotation_id`, `annotation_version` | Stable human-review/audit identifier. |
| `source_path`, `source_sha256`, `span_id` | Source and logical-span anchor. |
| `event_start_sec`, `event_end_sec` | Final human interval in **original raw-source seconds**; `start < end`. |
| `event_label`, `ground_truth_status` | Taxonomy label and review/release state. |
| `roi_config_id`, `roi_version`, `roi_snapshot_reference` | Required for ROI-dependent case when available. |
| `cover_area_percent`, `cover_duration_seconds` | Required for cover assessment. |
| `motion_type`, `lighting`, `distance`, `occlusion` | Review evidence/context fields. |
| `rule_engine_rule_id`, `rule_engine_rule_version`, `rule_engine_severity_output` | Optional system output; never reviewer-selected severity. |
| `reviewer`, `review_timestamp`, `review_round`, `comment`, `uncertainty_reason` | Human review audit. |
| `adjudication_status`, `adjudicator_reference` | Disagreement resolution audit. |
| `test_eligibility`, `evidence_reference` | Leakage/evidence state. |

`track_id`/`episode_id` remain technical debug data, not annotation/person identity.

## 3. Proposed shape — NOT IMPLEMENTED

```json
{
  "annotation_extension": {
    "schema_version": "annotation-extension.v0.1",
    "records": [
      {
        "annotation_id": "planned-example",
        "source_sha256": "<same-as-source>",
        "span_id": "person_detected-0001",
        "event_start_sec": 0.0,
        "event_end_sec": 0.0,
        "event_label": "ambiguous",
        "ground_truth_status": "needs_second_review"
      }
    ]
  }
}
```

The example is documentation only. Current readers validate only existing `person-detections.v1` fields and current UI does not persist this extension.
