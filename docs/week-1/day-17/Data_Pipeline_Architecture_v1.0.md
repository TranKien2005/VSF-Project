# Data Pipeline Architecture v1.0

> **Ngày:** 17/07/2026
> **Owner:** B — Data & Automation
> **Trạng thái:** Architecture plan. `v1.0` does not mean the target pipeline has been implemented or executed.

## 1. Implemented POC lane

```text
local raw video
  -> frame sampling at 5 FPS
  -> local RT-DETR-L person detection + technical tracking
  -> any-person presence merge (gap <=2 s)
  -> bounded +/-5 s context
  -> one source-owned person-detections.v1 JSON
  -> browse/view or optional manual clean/bbox Save As export
```

This is the only end-to-end implemented lane. It supports person technical evidence; it does not label intrusion, ROI, cover, movement, severity, ground truth or KPI.

## 2. Planned execution lane — NOT IMPLEMENTED

```text
receipt -> inventory/checksum -> validity/duplicate checks
 -> source-group/leakage eligibility -> technical candidate mining
 -> candidate manifest + controlled sampling -> human review
 -> ground truth/QC -> alert/rule-engine matching -> KPI -> handover
```

`inventory.py`, `CandidateSample`/`manifest.py`, generic signal consolidation and non-person signal providers are reusable design/code pieces, but are not wired into current CLI `run` output. Proxy batch generation, manifest generation, annotation integration, alert ingestion and KPI calculation are planned capabilities.

## 3. Architecture boundaries

- Current JSON persists person observations/spans only, despite configured cover/movement/anomaly providers.
- ROI Green/Yellow/Red, cover area/duration, movement evidence and rule-engine severity belong to system/human-review contracts, not POC conclusions.
- Raw video and derived evidence stay local/Git-ignored; tracked docs contain schemas, rules and references only.
- Human review owns final labels and ground truth; severity is only a system rule-engine output when available.
