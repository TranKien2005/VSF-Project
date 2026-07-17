# Ground Truth Release Criteria v1.0

> **Ngày:** 17/07/2026
> **Owner:** C — Annotation & Data Quality
> **Trạng thái:** Future release criteria; no ground-truth release exists in Week 1.

## 1. Required release evidence

A record can be ground-truth eligible only when it has valid source/SHA-256 and `person-detections.v1` anchor, stable `span_id` or explicit source anchor, source-relative final interval, taxonomy label/status, required reviewer audit, evidence reference, eligibility state, ROI evidence when applicable, and completed second-review/adjudication when required.

Candidate presence alone is insufficient. A technical detector span does not make an event ground truth.

## 2. Release classifications

| Classification | Condition |
|---|---|
| Ground-truth eligible | Human reviewed, QC-valid and no blocking unresolved item. |
| Golden-set eligible | Ground-truth eligible; no `ambiguous`, `invalid`, unresolved or missing traceability. |
| Diagnostic-only | Useful review evidence but incomplete for release/KPI. |
| Excluded | Invalid source, insufficient required evidence or eligibility limitation. |
| `ambiguous` / `invalid` / unresolved | Retain audit evidence; exclude from official ground truth/KPI/golden set. |

Agreement evidence is a release dependency, but its acceptance threshold is `TBD_STAKEHOLDER_APPROVAL`. Rule-engine severity is included only when supplied with rule reference.
