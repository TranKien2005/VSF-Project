"""Deterministic random-background selection."""

from __future__ import annotations

import random

from .models import ClipWindow


def _overlaps(left: tuple[float, float], right: tuple[float, float]) -> bool:
    return left[0] < right[1] and right[0] < left[1]


def select_background_windows(
    duration_seconds: float,
    count: int,
    clip_duration_seconds: float,
    exclusion_windows: list[ClipWindow],
    exclusion_seconds: float,
    seed: int,
) -> list[ClipWindow]:
    if duration_seconds < clip_duration_seconds or count == 0:
        return []
    exclusions = [
        (
            max(0.0, window.start_sec - exclusion_seconds),
            min(duration_seconds, window.end_sec + exclusion_seconds),
        )
        for window in exclusion_windows
    ]
    candidates = list(range(0, int(duration_seconds - clip_duration_seconds) + 1))
    random.Random(seed).shuffle(candidates)
    selected: list[ClipWindow] = []
    for start in candidates:
        proposed = (float(start), float(start) + clip_duration_seconds)
        if any(_overlaps(proposed, excluded) for excluded in exclusions):
            continue
        if any(_overlaps(proposed, (item.start_sec, item.end_sec)) for item in selected):
            continue
        selected.append(ClipWindow(*proposed, context_status="sufficient"))
        if len(selected) == count:
            break
    return sorted(selected, key=lambda item: item.start_sec)
