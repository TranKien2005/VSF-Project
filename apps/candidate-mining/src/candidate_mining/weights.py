"""Explicit, local-only lifecycle for supported model artifacts."""

from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

from .inventory import sha256_file

MODELS = {
    "yolo11n": {
        "filename": "yolo11n.pt",
        "url": "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt",
    },
    "rtdetr-l": {
        "filename": "rtdetr-l.pt",
        "url": "https://github.com/ultralytics/assets/releases/download/v8.3.0/rtdetr-l.pt",
    },
}


def verify_weights(path: Path, expected_sha256: str | None = None) -> Path:
    if not path.is_file():
        raise FileNotFoundError(f"Local model weights are missing: {path}")
    if expected_sha256 and sha256_file(path).lower() != expected_sha256.lower():
        raise ValueError(f"Model weight SHA-256 mismatch: {path}")
    return path.resolve()


def download_model(model: str, destination: Path) -> tuple[Path, str]:
    """Download a supported asset explicitly; normal pipeline runs never call this."""
    if model not in MODELS:
        raise ValueError(f"Unsupported local model artifact: {model}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".pt.download")
    if destination.exists():
        return verify_weights(destination), sha256_file(destination)
    try:
        with urllib.request.urlopen(MODELS[model]["url"], timeout=60) as response:
            digest = hashlib.sha256()
            with temporary.open("wb") as output:
                while block := response.read(1024 * 1024):
                    digest.update(block)
                    output.write(block)
        checksum = digest.hexdigest()
        temporary.replace(destination)
        return destination.resolve(), checksum
    finally:
        if temporary.exists():
            temporary.unlink()


def download_yolo11n(destination: Path) -> tuple[Path, str]:
    """Compatibility wrapper for the original explicit YOLO command."""
    return download_model("yolo11n", destination)
