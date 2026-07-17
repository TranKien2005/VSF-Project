# Camera Stream and ROI Evidence Checklist v0.1

> **Ngày:** 16/07/2026
> **Owner:** B — Data & Automation
> **Trạng thái:** Intake checklist for Week 2; not evidence that system access/data already exists.

## 1. Known camera reference

- Vendor/model: HIKVISION `DS-2CD3T46G2-ISU/SL`.
- Firmware: `V5.7.55`.
- Approximate camera spacing: 40 m.
- Relevant business ROI categories: Green, Yellow and Red.

## 2. Evidence to obtain per source

| Group | Required fields | Current POC support |
|---|---|---|
| Source | `source_id`, source path/reference, filename, SHA-256, recording period. | Filename/path/SHA-256 in person JSON; source ID/period planned. |
| Media | FPS, width, height, codec/container, audio, duration. | Person JSON has FPS/dimensions; `inventory.probe_video` can obtain broader media metadata but is not CLI-wired. |
| Time | Source-relative timestamp basis, timezone, NTP/clock status, retention gap. | Not captured. |
| Camera | `camera_id`, physical location/group, stream/channel reference. | Not captured. |
| ROI | `roi_config_id`, version, effective time, snapshot/reference and relevant zone. | Not captured; B does not create/edit ROI. |
| System | Alert/log reference, rule ID/version and severity output when available. | Not captured. |

Missing evidence is recorded as `Unknown`; it must not be inferred from filename, bbox, track ID or a viewer display.

## 3. Review boundary

ROI Green/Yellow/Red is category evidence. Cover ≥30% for ≥120 seconds, strong shake/rotation and interference facts are requirements for later review, not capabilities of the person-only POC. Severity is rule-engine output, never reviewer-selected severity.
