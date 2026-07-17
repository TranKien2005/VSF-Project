# KPI Calculation Sheet Template v0.1

> **Ngày:** 16/07/2026
> **Owner:** B — Data & Automation
> **Trạng thái:** Empty Week 1 template. The current runtime has no alert ingestion, matching engine or KPI calculator.

## 1. Event-level worksheet columns

```text
run_id, event_id, sample_id, source_id, camera_id,
roi_config_id, roi_version, review_category,
event_start_sec, event_end_sec, ground_truth_status,
alert_id, alert_category, alert_timestamp, rule_engine_rule_id,
rule_engine_rule_version, rule_engine_severity_output,
match_outcome, exclusion_reason, duplicate_of_event_id,
misclassification_note, reviewer, evidence_reference, notes
```

Allowed `match_outcome`: `TP`, `FP`, `FN`, `TN`, `duplicate_alert`, `misclassification`, `excluded`, `unresolved`.

## 2. Calculation cells

```text
Precision = TP / (TP + FP)
Recall    = TP / (TP + FN)
FP ratio  = FP / (TP + FP)
```

`FP/(TP+FP) = 1 − Precision`; it is not statistical false-positive rate `FP/(FP+TN)`. Calculate separately for intrusion, camera cover and camera movement only after event matching is defined.

## 3. Eligibility and conclusion

Exclude `ambiguous`, `invalid`, unresolved, unreadable, missing-context or missing-required-evidence records. Use `Chưa kết luận` if no reviewed ground truth, system alert/log, matching/dedup rule, eligible source provenance or enough samples exists.

Technical candidate JSON status `pending_review` is not a verdict. Severity is copied only from a system rule-engine output; reviewer category/ROI must remain separate.
