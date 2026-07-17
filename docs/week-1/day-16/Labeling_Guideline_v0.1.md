# Labeling Guideline v0.1

> **Ngày:** 16/07/2026
> **Owner:** C — Annotation & Data Quality
> **Trạng thái:** Initial future-internal-UI guideline; no annotation UI is implemented in this repository.

## 1. Review unit and timing

The review unit is a logical source `span_id` from a per-source `person-detections.v1` JSON. In the planned internal UI, navigate:

```text
raw source -> person_detected -> logical span -> review
```

Use candidate/context bounds for navigation only. Select `event_start_sec` and `event_end_sec` in **raw-source-relative seconds**, not export-clip-relative time. The final human event may occupy only part of a candidate span.

## 2. Labeling rules

- Candidate technical boxes/spans are not labels, intrusion conclusions or ground truth.
- Review ROI Green/Yellow/Red as evidence/category only; do not infer authorization or severity.
- Cover positive requires both area ≥30% and duration ≥120s. Rain/glare are interference. Freeze/black screen/video loss remain `camera_health_unknown` without a system rule.
- Movement positive is strong shake or rotation/changed orientation. Environmental vibration and scene motion not caused by camera are negative/interference. Do not invent numeric threshold.
- Missing context, unclear ROI or unresolved system rule: use `ambiguous` or `needs_second_review`; unusable source/artifact: `invalid`.

## 3. Required review behavior

Preserve candidate and final boundaries separately; record evidence/comment, relevant ROI reference, cover/movement fields and system rule output only when supplied. Multiple people or technical track IDs do not create identity labels. Never force a positive/negative label merely to fill a queue.
