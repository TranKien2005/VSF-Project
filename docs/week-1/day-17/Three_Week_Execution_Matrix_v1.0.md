# Three Week Execution Matrix v1.0

> **Ngày:** 17/07/2026  
> **Owner:** A — QA Lead / Test Design  
> **Trạng thái:** Planning matrix. Week 1 has no raw data; Week 2/3 outputs are only created after their execution evidence exists.  
> **Nguồn:** [Kế hoạch ba tuần](../../ke-hoach-3-tuan-kiem-thu-ai-camera.md), Mục 7, 10 và 12.

## 1. Tuần 1 — 16–17/07: plan, specification và base preparation

| Vai trò | Trách nhiệm | Điều kiện hoàn thành |
|---|---|---|
| A | Scope, use case, event-level KPI rule, acceptance, coverage hypothesis, traceability, risk/dependency. | Mentor facts được phản ánh; severity tách khỏi reviewer label; không tuyên bố KPI/coverage/ground truth. |
| B | Local data/pipeline/readiness design và capability boundary. | Không claim POC person-only tạo intrusion/ROI/cover/movement result hoặc raw-data artifacts. |
| C | Taxonomy, schema, labeling/QC/calibration planning. | Không có annotation, calibration hoặc ground truth result khi chưa có data. |

Week 1 does not produce raw inventory, candidate output on real video, review clip batch, annotation, leakage result, coverage result or KPI result.

## 2. Tuần 2 — raw data đến prepared annotation queue

| Stage | A — QA/Test Design | B — Data & Automation | C — Annotation/Data Quality | Exit evidence |
|---|---|---|---|---|
| Receive/inventory | Đối chiếu use case/coverage need. | Inventory, eligibility, source group, access/readability checks. | Quan sát mẫu và readiness feedback. | Traceable local inventory/report; no claim of ground truth. |
| Coarse classification | Map candidate reason to sampling category only. | Run only available technical capability; current POC is person JSON/span evidence. | Review candidate context/capability gaps. | Candidate evidence is not final label. |
| Controlled sampling | Maintain normal/edge/negative/interference coverage hypothesis. | Normalize source/time evidence; manual export only when needed. | Fine category/evidence review; mark ambiguous/invalid. | Queue has usable context and known gaps. |
| Cleaning | Review coverage gaps. | Normalize/dedupe/validate local manifest. | Annotation readiness review. | Candidate traceability, eligibility and gaps documented. |

## 3. Tuần 3 — annotation, ground truth, QC và handover

| Stage | A — QA/Test Design | B — Data & Automation | C — Annotation/Data Quality | Exit evidence |
|---|---|---|---|---|
| Calibration | Adjudicate according to guideline and acceptance. | Ensure source/export/field mapping. | Coordinate independent review and calibration. | Unresolved cases stay excluded. |
| Annotation/QC | Check use-case coverage and KPI eligibility. | Schema/source validation and version references. | Primary annotation, agreement and disagreement handling. | Ground truth only for reviewed eligible records. |
| KPI/handover | Compare eligible event-level KPI to targets or state Chưa kết luận. | Reproducibility/storage references. | Annotation quality/release references. | Coverage, limitations, version and handover are documented. |

## 4. Fixed business-rule boundary

- ROI evidence: Green / Yellow / Red.
- Cover positive: at least 30% coverage for at least 120 seconds.
- Movement positive: strong shake or rotation/changed orientation.
- Heavy rain, vehicle glare and scene motion not caused by camera movement: negative/interference.
- Severity: output of the system rule engine; review labels do not select Cấp 1–4.

## 5. Gate discipline

No step may convert an assumption, local candidate signal or unavailable system evidence into ground truth, a KPI pass, a severity label, an approval or a completed operational result.
