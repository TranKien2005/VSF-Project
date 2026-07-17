# Annotation QC Protocol v1.0

> **Ngày:** 17/07/2026
> **Owner:** C — Annotation & Data Quality
> **Trạng thái:** Planned QC protocol; no validation/release result exists in Week 1.

## 1. Blocking checks

- source exists; source filename/SHA-256 matches valid `person-detections.v1`;
- `span_id` exists; candidate/context values remain unchanged;
- `event_start_sec < event_end_sec`, both within raw duration and source-relative;
- `event_label` and `ground_truth_status` are valid taxonomy values;
- reviewer, review timestamp, annotation ID/version and evidence reference exist;
- ROI-dependent label has ROI reference or explicit `Unknown`/exclusion;
- no duplicate annotation ID; no unresolved required second review;
- no use of technical track/episode as identity; no candidate-to-ground-truth shortcut.

## 2. Warning and business-rule checks

Flag clipped context, missing alert/rule-engine fields, missing eligibility/source-group data, unclear cover area/duration, uncertain movement and missing comments. These block KPI/release only where the intended conclusion depends on them.

## 3. Release restrictions

`ambiguous`, `invalid`, unresolved and leakage-ineligible records cannot enter golden set or official KPI. All raw/JSON/export annotation evidence remains local/Git-ignored. Current internal UI/schema extension is not implemented, so this protocol is future execution guidance.
