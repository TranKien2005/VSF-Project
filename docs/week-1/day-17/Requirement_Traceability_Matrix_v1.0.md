# Requirement Traceability Matrix v1.0

> **Ngày:** 17/07/2026
> **Owner:** A — QA Lead / Test Design
> **Trạng thái:** Active planning matrix. Coverage below is traceability-design coverage, not achieved test-data coverage.
> **Nguồn:** [Kế hoạch ba tuần](../../ke-hoach-3-tuan-kiem-thu-ai-camera.md), Mục 4, 6, 7, 8 và 9.

| Requirement ID | Requirement | Use-case group | Evidence required | Acceptance | KPI / output boundary | Status |
|---|---|---|---|---|---|---|
| REQ-INT-001 | Review person associated with Green ROI. | Intrusion / Green | Video, source timestamp, ROI reference. | AC-INT-001 | Alert category only when available; no reviewer severity. | Planned execution. |
| REQ-INT-002 | Review person associated with Yellow ROI. | Intrusion / Yellow | Video, source timestamp, ROI reference. | AC-INT-002 | No Cấp 2/Cấp 3 video-label decision. | Planned execution. |
| REQ-INT-003 | Review person associated with Red/restricted ROI. | Intrusion / Red | Video, source timestamp, ROI reference. | AC-INT-003 | Rule-engine severity only when output exists. | Planned execution. |
| REQ-INT-004 | Keep person outside relevant ROI distinct from ROI intrusion. | Intrusion negative | Video, timestamp, ROI reference. | AC-INT-NEG-001 | Negative/hard-negative evidence. | Planned execution. |
| REQ-INT-005 | Do not create loitering candidate rule/label from rule-engine context. | Intrusion boundary | System rule reference if supplied. | AC-INT-001–003 | No POC loitering conclusion. | Planning boundary. |
| REQ-COV-001 | Cover positive requires area ≥30% and duration ≥120 seconds. | Cover positive | Video, cover area %, duration, timestamp. | AC-COV-001 | Cover KPI eligible only after review and matching. | Rule confirmed; execution pending. |
| REQ-COV-002 | Below area/duration threshold is boundary/negative evidence. | Cover boundary | Video, cover area %, duration. | AC-COV-NEG-001 | Do not force positive label. | Rule confirmed; execution pending. |
| REQ-COV-003 | Heavy rain and vehicle glare are interference, not cover positive. | Cover negative | Video, timestamp. | AC-COV-NEG-001 | Hard-negative evidence. | Rule confirmed; execution pending. |
| REQ-COV-004 | Freeze, black screen and video loss are not automatically cover. | Camera-health edge | Video/log when available. | AC-COV-EDGE-001 | Depends on system rule. | System dependency. |
| REQ-MOV-001 | Strong shake is positive camera movement. | Movement positive | Video/before-after evidence, timestamp. | AC-MOV-001 | Category KPI after eligible review. | Rule confirmed; execution pending. |
| REQ-MOV-002 | Rotation/changed orientation is positive camera movement. | Movement positive | Video/before-after evidence, timestamp. | AC-MOV-001 | Category KPI after eligible review. | Rule confirmed; execution pending. |
| REQ-MOV-003 | Environmental vibration is not movement positive. | Movement negative | Video, timestamp. | AC-MOV-NEG-001 | Hard-negative evidence. | Rule confirmed; execution pending. |
| REQ-MOV-004 | Scene motion not caused by camera is not movement positive. | Movement negative | Video, timestamp. | AC-MOV-NEG-001 | Hard-negative evidence. | Rule confirmed; execution pending. |
| REQ-MOV-005 | Do not invent numeric movement threshold. | Movement edge | Video, timestamp. | AC-MOV-NEG-001 | Edge/uncertain if evidence insufficient. | Planning boundary. |
| REQ-DATA-001 | Each record is traceable to source/camera/source-relative time. | Data quality | Local manifest/annotation record. | AC-DATA-001 | Preconditions for KPI. | Planned execution. |
| REQ-DATA-002 | ROI-dependent records include ROI config/version/snapshot reference. | Data quality | ROI evidence. | AC-DATA-001 | Missing ROI evidence prevents relevant conclusion. | System/data dependency. |
| REQ-DATA-003 | Track test eligibility and do not claim independence without provenance. | Leakage | Source/train manifest when supplied. | AC-DATA-001 | `Unknown` if provenance absent. | Data dependency. |
| REQ-DATA-004 | Candidate mining does not become final ground truth. | Ground-truth quality | Human review/annotation record. | AC-DATA-002 | Person POC is evidence only. | Planned execution. |
| REQ-E2E-001 | Alert maps to camera, source time and event category when access exists. | E2E | Alert/log plus source evidence. | AC-E2E-001 | Evaluation only with matching rule. | System-access dependency. |
| REQ-E2E-002 | Rule-engine severity is recorded separately when output/rule reference exists. | E2E | Alert/log, rule ID/version, severity output. | AC-E2E-001 | No reviewer-selected severity. | System-access dependency. |
| REQ-E2E-003 | Duplicate/misclassification handling is explicit before KPI conclusion. | E2E/KPI | Alert/log and matching/dedup rule. | Section 3 Acceptance | `Chưa kết luận` if rule absent. | System-rule dependency. |

## Traceability self-check

This matrix maps planned requirements to use-case group, evidence and acceptance. It does not report raw-data coverage, test execution, KPI performance or ground-truth completion.
