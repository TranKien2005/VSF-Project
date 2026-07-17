# Label Taxonomy v0.1

> **Ngày:** 16/07/2026
> **Owner:** C — Annotation & Data Quality
> **Trạng thái:** Draft annotation taxonomy. No Week 1 review/annotation/ground-truth result exists.

## 1. Boundary with current POC

`person_detected`, `camera_cover`, `camera_movement` and `anomaly_unknown` are technical categories. The current persisted POC output is only `person_detected`; it is not a human event label or ground truth.

Reviewer never assigns Cấp 1–4. Severity is recorded only as system `rule_engine_severity_output` when rule reference/output exists.

## 2. Permitted annotation labels

| Group | Label | Meaning / evidence rule | KPI or golden eligibility |
|---|---|---|---|
| ROI | `roi_green_person` | Person associated with Green ROI; retain ROI reference. | Review-dependent |
| ROI | `roi_yellow_person` | Person associated with Yellow ROI; retain ROI reference. | Review-dependent |
| ROI | `roi_red_person` | Person associated with Red/restricted ROI; retain ROI reference. | Review-dependent |
| ROI | `person_outside_roi` | Person not associated with relevant ROI. | Negative if context/evidence sufficient |
| Cover | `camera_cover` | Cover area ≥30% **and** duration ≥120 seconds. | Review-dependent |
| Cover | `cover_boundary` | Area <30% or duration <120 seconds. | Negative/edge, not forced positive |
| Cover | `rain_heavy`, `headlight_glare` | Interference/hard negative. | Negative if evidence sufficient |
| Cover | `camera_health_unknown` | Freeze, black screen or video loss; not automatically cover. | Exclude from cover until system rule exists |
| Movement | `camera_strong_shake` | Strong shake. | Review-dependent |
| Movement | `camera_rotation` | Rotation/changed orientation. | Review-dependent |
| Movement | `temporary_or_uncertain_shake` | Light/short/unclear shake. | Edge/uncertain |
| Movement | `environmental_vibration`, `scene_motion_not_camera_movement` | Interference/negative. | Negative if evidence sufficient |

No loitering label/candidate threshold is introduced. Identity, authorization and production ROI editing are outside annotation scope.

## 3. Review states

| State | Meaning |
|---|---|
| `confirmed_positive` | Human evidence supports a permitted positive label. |
| `confirmed_negative` | Human evidence supports negative/interference label. |
| `needs_second_review` | Conflict, uncertain boundary or rule/evidence needs independent review. |
| `ambiguous` | Available context cannot support a reliable label. |
| `invalid` | Source/artifact/evidence is unusable for review. |

`ambiguous` and `invalid` are excluded from official KPI and golden-set release.
