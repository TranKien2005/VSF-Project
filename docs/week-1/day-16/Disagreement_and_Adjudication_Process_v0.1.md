# Disagreement and Adjudication Process v0.1

> **Ngày:** 16/07/2026
> **Owner:** C — Annotation & Data Quality
> **Trạng thái:** Future process; no disagreement or adjudication result exists.

## 1. Lifecycle

```text
independent review -> compare -> needs_second_review
-> adjudication or business-rule escalation
-> resolved record OR ambiguous/invalid/unresolved exclusion
```

Preserve each reviewer decision, raw-source interval, timestamp, evidence and rationale. No reviewer silently overwrites another review.

## 2. Disagreement classes

- event label or positive/negative decision;
- `event_start_sec` / `event_end_sec` boundary;
- ROI evidence interpretation;
- cover area/duration or movement evidence;
- severity/system-output interpretation;
- evidence quality, `ambiguous` or `invalid` status.

Severity disagreements cannot be solved by reviewer-assigned Cấp 1–4. Escalate missing rule-engine/system evidence as limitation.

## 3. Resolution rules

Second review is independent where possible. Adjudication records the final status, rationale and reference; unresolved rule/evidence cases remain `needs_second_review`, `ambiguous` or `invalid` and are excluded from ground truth/KPI as applicable.

```text
Agreement acceptance threshold: TBD_STAKEHOLDER_APPROVAL
```

No numerical threshold is defined in this document.
