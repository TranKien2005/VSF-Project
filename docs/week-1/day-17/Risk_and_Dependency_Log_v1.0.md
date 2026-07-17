# Risk and Dependency Log v1.0

> **Ngày:** 17/07/2026
> **Owner:** A — QA Lead / Test Design
> **Trạng thái:** Planning risk log — no raw-data execution result is recorded.
> **Nguồn:** [Kế hoạch ba tuần](../../ke-hoach-3-tuan-kiem-thu-ai-camera.md), Mục 6, 9, 11 và 12.

## 1. Facts no longer treated as open blockers

| Fact | Use in execution |
|---|---|
| Cover positive = coverage ≥30% and duration ≥120 seconds. | Capture area/duration evidence; test boundary cases without inventing a result. |
| Strong shake or rotation/changed orientation = movement positive. | Use as review category; no numeric movement threshold is inferred. |
| Heavy rain, vehicle glare, scene motion not caused by camera = interference/negative. | Include as hard-negative/interference evidence. |
| Severity belongs to rule engine. | Keep reviewer category/ROI separate from `rule_engine_severity_output`. |

## 2. Active risks and dependencies

| ID | Risk/dependency | Impact | Handling | Status |
|---|---|---|---|---|
| R-001 | No raw video before Week 2. | No inventory, candidate result, review, ground truth, coverage or KPI result. | Keep Week 1 outputs to plan/spec/template/base preparation only. | Expected dependency. |
| R-002 | Missing ROI config/version/snapshot/effective-time evidence. | ROI-dependent case cannot be verified reliably. | Record limitation; exclude affected case from ROI-dependent conclusion. | Open until system/data access. |
| R-003 | No train manifest/source list. | Cannot claim test-set independence. | Use eligibility `Unknown`; report limitation. | Open until provenance is supplied. |
| R-004 | Missing alert/log or rule-engine output. | Cannot verify E2E category/severity or calculate affected KPI. | Separate review category from system output; state `Chưa kết luận`. | Open until system access. |
| R-005 | No event matching, cooldown/dedup or re-entry rule. | TP/FP/FN/duplicate treatment may be inconsistent. | Report duplicate/misclassification separately; do not publish dependent KPI conclusion. | Open until rule reference is supplied. |
| R-006 | No detection-window/latency origin. | Latency cannot be measured correctly. | Do not set or report a latency result. | Open until rule reference is supplied. |
| R-007 | Freeze/black-screen/video-loss system behavior unclear. | Camera-health case may be misgrouped as cover. | Keep separate from cover until a system rule is available. | Open. |
| R-008 | Insufficient/imbalanced real samples after receipt. | Coverage/KPI may be unreliable. | Record gap; use controlled sampling; do not fabricate data or claim achieved coverage. | Pending Week 2 inventory. |
| R-009 | Automation bias or candidate misses. | Ground truth/data distribution could be biased. | Use random background and risk-based sampling; blind/second review. | Pending Week 2–3 execution. |
| R-010 | PII/sensitive camera artifacts. | Privacy/access risk. | Local controlled storage and Git-ignore; no raw/JSON/export/log commit. | Ongoing control. |

## 3. Week 1 gate

Week 1 is complete when A/B/C planning and preparation documents are coherent and contain no false raw-data, review, ground-truth, coverage, KPI, approval or meeting claims. It does **not** require external approvals, raw video, system alert access or a dry run.

The Week 2 execution gate is limited by R-001 through R-010 as applicable. Each missing dependency must be recorded as a limitation rather than being replaced with an invented owner, deadline, threshold or result.
