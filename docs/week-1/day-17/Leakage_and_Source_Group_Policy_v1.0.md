# Leakage and Source Group Policy v1.0

> **Ngày:** 17/07/2026
> **Owner:** B — Data & Automation
> **Trạng thái:** Policy for Week 2/3 execution; no split or leakage result exists yet.

## 1. Source-group rule

Keep records in the same source group when they share a raw source, camera/channel, recording period/date, continuous or overlapping time range, exact SHA-256, or a reviewed near-duplicate relationship. A source group must not be split across nominally independent evaluation partitions.

## 2. Eligibility states

| State | Meaning |
|---|---|
| `Test eligible` | Provenance supports the intended test use and no known train overlap. |
| `Train overlap` | Source/group is known to overlap training/reference data. |
| `Suspected overlap` | Evidence suggests overlap but is not conclusive. |
| `Unknown` | Train manifest/source list or sufficient provenance is absent. |

If train provenance is absent, set `Unknown`; never claim test independence. Current person JSON has per-source SHA-256 but does not implement source groups, split assignment or eligibility status.

## 3. Checks at execution

- Use full SHA-256 for exact duplicate detection.
- Review camera/source identity and time overlap for near duplicates.
- Keep raw-derived clips/spans from the same source group together.
- Record eligibility and exclusion rationale in a future local manifest/report.
- Exclude or label limitations before KPI conclusions; do not solve imbalance or leakage by duplicating data.
