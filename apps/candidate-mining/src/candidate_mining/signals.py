"""Development signal input seam; automatic detection is intentionally deferred."""

from __future__ import annotations

import json
from pathlib import Path

from .models import TOOL_CATEGORIES, Signal


def load_signals(path: Path | None) -> list[Signal]:
    if path is None:
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    entries = raw["signals"] if isinstance(raw, dict) else raw
    if not isinstance(entries, list):
        raise ValueError("Signals JSON must be a list or an object with a 'signals' list")
    signals: list[Signal] = []
    for index, item in enumerate(entries):
        if not isinstance(item, dict):
            raise ValueError(f"Signal {index} must be an object")
        category = item.get("category")
        if category not in TOOL_CATEGORIES:
            raise ValueError(f"Signal {index} has unsupported category: {category!r}")
        timestamp = float(item["timestamp_sec"])
        if timestamp < 0:
            raise ValueError(f"Signal {index} has a negative timestamp")
        signals.append(
            Signal(
                timestamp_sec=timestamp,
                category=category,
                person_count=item.get("person_count"),
                motion_score=item.get("motion_score"),
                brightness_score=item.get("brightness_score"),
                blur_score=item.get("blur_score"),
                camera_shift_score=item.get("camera_shift_score"),
                anomaly_types=tuple(item.get("anomaly_types", [])),
                track_ids=tuple(item.get("track_ids", [])),
                episode_ids=tuple(item.get("episode_ids", [])),
                track_reconciliation_status=item.get("track_reconciliation_status"),
            )
        )
    return signals
