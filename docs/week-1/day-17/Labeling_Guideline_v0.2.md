# Labeling Guideline v0.2

> **Ngày:** 17/07/2026
> **Owner:** C — Annotation & Data Quality
> **Trạng thái:** Operational draft updating `Labeling_Guideline_v0.1`; future internal UI is selected but not implemented.

## 1. Fixed working decisions

- Review in a future internal UI, using B’s existing per-source `person-detections.v1` JSON.
- Add annotation data as an extension of that JSON; do not introduce a standalone annotation file.
- Final `event_start_sec`/`event_end_sec` always use original raw-source seconds.
- Candidate/context span is a review aid, not final event, ground truth or severity.

## 2. Examples

| Situation | Review action |
|---|---|
| Full-source person span | Review raw context; final event can still be shorter or no confirmed event. |
| Context clipped at source start/end | Preserve clip status; do not treat missing context as proof. Use `ambiguous` if it prevents decision. |
| Final event inside a logical span | Keep candidate bounds and record narrower source-relative final bounds. |
| No confirmed event in span | Set `confirmed_negative`, `ambiguous` or `invalid` based on evidence; do not delete technical evidence. |
| Multiple spans in one source | Review each `span_id` independently; tracks/episodes do not establish identity. |

## 3. Rule and escalation discipline

Apply taxonomy v0.1 and preserve ROI/cover/movement evidence. `rule_engine_severity_output` is optional system data, never a reviewer choice. Missing ROI reference, event matching rule, system output or other business rule is recorded as `Unknown`, `needs_second_review` or limitation—not inferred.
