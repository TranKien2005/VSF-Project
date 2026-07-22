# Candidate Mining v1 — historical planning note

> **Status: historical.** This document preserves the earlier viewer-first planning context. It does not define the current implementation, commands, artifact layout, sampling profile, or output contract.

The historical plan used `data/raw/`, `data/review_queue/`, 5-FPS sampling, and `run`/`browse`/`inspect` commands. Those are no longer the active Candidate Mining workflow.

## Current implementation reference

For the current behavior, use these documents instead:

- [README.md](../README.md) — installation, launch, current local artifact layout, and verification commands.
- [desktop-roi-workflow.md](desktop-roi-workflow.md) — current import, freehand ROI, processing, review, and export contract.
- [../configs/candidate-mining.toml](../configs/candidate-mining.toml) — active runtime configuration.
- [huong-dan-gan-nhan.md](huong-dan-gan-nhan.md) and [yeu-cau-va-huong-dan-tool-gan-nhan.md](yeu-cau-va-huong-dan-tool-gan-nhan.md) — future human-labeling specifications, not current application output lanes.

Current Candidate Mining is a technical-evidence tool: it requires an imported checksum-verified source and an effective ROI, uses the configured local person detector, and writes source-scoped `technical-candidate.v2` evidence under `data/results/`. It does not create final event labels, intrusion/loitering decisions, ground truth, or KPI output.
