# Annotation Queue Entry Template v0.1

> **Ngày:** 16/07/2026
> **Owner:** C — Annotation & Data Quality
> **Trạng thái:** Empty template for future internal UI; no queue records exist in Week 1.

## Queue entry

```text
annotation_id:
source_path:
source_sha256:
person_detection_json_path:
span_id:
category: person_detected
candidate_start_sec:
candidate_end_sec:
context_start_sec:
context_end_sec:

final event_start_sec (raw-source seconds):
final event_end_sec (raw-source seconds):
event_label:
ground_truth_status:
roi_config_id / roi_version / snapshot reference:
cover_area_percent / cover_duration_seconds:
motion_type / lighting / distance / occlusion:
rule_engine_rule_id / version / severity output (if supplied):
test_eligibility:
reviewer / review_timestamp / review_round:
evidence_reference:
comment / uncertainty_reason:
second_review_status / adjudication_reference:
```

## Entry validation checklist

- [ ] `source_sha256` matches selected raw source; JSON is not `MISSING`, `STALE` or `INVALID`.
- [ ] `span_id` exists and candidate/context values are retained unchanged.
- [ ] `event_start_sec < event_end_sec` and both are raw-source seconds within source duration.
- [ ] Candidate output was not copied directly into final ground truth.
- [ ] ROI/system evidence is recorded or explicitly `Unknown` where relevant.
- [ ] `ambiguous`/`invalid` are not marked golden/KPI eligible.
- [ ] Raw video, JSON and manual export remain local/Git-ignored.
