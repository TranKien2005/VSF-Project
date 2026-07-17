# Local Artifact and Git Policy v1.0

> **Ngày:** 17/07/2026
> **Owner:** B — Data & Automation
> **Trạng thái:** Active local-data policy.

## 1. Keep local and Git-ignored

```text
data/raw/
data/inventory/
data/manifests/
data/review_queue/
outputs/logs/
models/cache/
models/weights/
.cache/torch/
tools/ffmpeg/
```

This includes camera video, generated person JSON, inventory/manifest data, runtime logs, model weights/caches, portable FFmpeg, and manually exported clean/bbox MP4. These may expose faces, plates, operational layout, camera metadata or system behavior.

## 2. Tracked boundary

Commit only non-sensitive source code, non-sensitive configuration, schemas/contracts, documentation and permitted test fixtures. Never commit/push raw video, derived camera artifacts, runtime logs, local model/FFmpeg binaries, credentials, access tokens or operationally sensitive evidence.

## 3. Integrity and access

- Use full-file SHA-256 as local source integrity/reference evidence where the workflow runs.
- Keep generated artifacts tied to local source/time/config references.
- Restrict local storage/access according to available organizational controls.
- Retain, export, mask or delete footage only under an approved operational/privacy policy; this repository does not invent one.
- Manual exports are sensitive local artifacts. Save As cancellation produces no artifact; exports must not be shared by default.

No Week 1 document may claim that data was received, retained, deleted, reviewed or transferred.
