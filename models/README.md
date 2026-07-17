# Local model artifacts

`models/weights/` stores explicitly downloaded model-weight files. `models/cache/` stores framework/model caches. Both locations are intentionally ignored by Git.

Before adding a model artifact locally, record its model name, exact version, source URL, license, SHA-256 checksum, download date, and intended pipeline use in this file or a linked non-sensitive document.

## Candidate-mining person provider

### Active quality POC: RT-DETR-L COCO

- Artifact: `models/weights/rtdetr-l.pt`
- Model: Ultralytics RT-DETR Large, pretrained on COCO; pipeline filters COCO class `person` only.
- Source: `https://github.com/ultralytics/assets/releases/download/v8.3.0/rtdetr-l.pt`
- License: Ultralytics AGPL-3.0; review before any closed-source distribution.
- Use: visual person-detection POC only. It is COCO pretrained, not a surveillance/perimeter-specific model, and it does not determine intrusion, ROI state, identity, ground truth, or KPI.

Run `candidate-mining download-weights --model rtdetr-l` to explicitly download the artifact. Normal execution only loads the verified existing local file.

Temporary RTX 4060 Laptop 8GB profile: `sample_fps=5`, `image_size=960`, `batch_size=1`, `confidence_threshold=0.20`, CUDA auto-selection and FP16 where supported.

| Downloaded artifact | SHA-256 | Download date |
|---|---|---|
| `rtdetr-l.pt` | `6de60b10d4bc566f00cda0f5b4d64afe4b66d48dc9695d2171effb7859d8e73f` | 2026-07-17 |


### Previous baseline: YOLO11n COCO

The original YOLO11n entry remains available only as a later comparison profile.


- Artifact: `models/weights/yolo11n.pt`
- Model: Ultralytics YOLO11 nano, COCO class `person` only
- Source: `https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt`
- License: Ultralytics AGPL-3.0; review this license before any closed-source distribution.
- Use: technical `person_detected` candidate signals only; it does not determine intrusion, ROI status, climbing, loitering, ground truth, or a KPI.

Run `candidate-mining download-weights --model yolo11n` to explicitly download the local artifact.

| Downloaded artifact | SHA-256 | Download date |
|---|---|---|
| `yolo11n.pt` | `0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1` | 2026-07-17 |

The runtime loads only the existing local file; it does not fetch a model during normal candidate-mining execution.

Normal installation and candidate-mining execution must not silently download weights. The runtime loads only an existing local file under `models/weights/`.
