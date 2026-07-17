# Technical Readiness Checklist v0.1

> **Ngày:** 16/07/2026
> **Owner:** B — Data & Automation
> **Trạng thái:** Week 1 readiness design; each checkbox is verified only when evidence exists.

## 1. Environment checklist

| Check | Current code/config expectation | Evidence/status at execution |
|---|---|---|
| Python | Python ≥3.11; virtual environment. | `Not run` |
| Dependencies | Install `.[vision,dev]`: Typer, NumPy, OpenCV, Ultralytics and test tools. | `Not run` |
| Local model | Explicit `candidate-mining download-weights --model rtdetr-l`; normal run never downloads. | `Not run` |
| Provider profile | RT-DETR-L person-only; 5 FPS, 960, batch 1, confidence .20, device auto. | `Not run` |
| CUDA | `device=auto` selects CUDA when available, otherwise CPU. | `Not run` |
| Media tools | Prefer `tools/ffmpeg/ffmpeg.exe` and `ffprobe.exe`; PATH fallback; required for metadata/manual export. | `Not run` |
| Raw access | Read access to local raw video only from Week 2. | `Blocked until receipt` |
| Storage/PII | Local controlled storage; raw/derived artifacts Git-ignored. | `Required` |

## 2. Valid commands

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[vision,dev]"
.\.venv\Scripts\candidate-mining download-weights --model rtdetr-l
.\.venv\Scripts\candidate-mining run
.\.venv\Scripts\candidate-mining browse
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m pytest
```

`run` writes person JSON only. `browse`/`inspect` do not write artifacts. There is currently **no inventory CLI and no manifest-generation CLI**.

## 3. Failure handling

Missing local weights, unreadable video, missing FFmpeg for export, invalid/stale detection JSON, insufficient local storage or unavailable raw access must be logged as a limitation. Do not substitute a synthetic result, fake dry-run or inferred system metadata.
