"""Pure signal merge, multi-category consolidation, and proxy-window logic."""

from __future__ import annotations

from itertools import groupby

from .models import TOOL_CATEGORIES, ClipWindow, Segment, Signal


def _maximum(current: int | float | None, value: int | float | None) -> int | float | None:
    if value is None:
        return current
    return value if current is None else max(current, value)


def _add_signal(segment: Segment, signal: Signal) -> None:
    segment.end_sec = max(segment.end_sec, signal.timestamp_sec)
    segment.person_count_max = _maximum(segment.person_count_max, signal.person_count)  # type: ignore[assignment]
    segment.motion_score = _maximum(segment.motion_score, signal.motion_score)  # type: ignore[assignment]
    segment.brightness_score = _maximum(segment.brightness_score, signal.brightness_score)  # type: ignore[assignment]
    segment.blur_score = _maximum(segment.blur_score, signal.blur_score)  # type: ignore[assignment]
    segment.camera_shift_score = _maximum(segment.camera_shift_score, signal.camera_shift_score)  # type: ignore[assignment]
    segment.anomaly_types.update(signal.anomaly_types)
    segment.track_ids.update(signal.track_ids)
    segment.episode_ids.update(signal.episode_ids)
    if signal.track_reconciliation_status:
        segment.track_reconciliation_statuses.add(signal.track_reconciliation_status)


def merge_signals(signals: list[Signal], merge_gap_seconds: float) -> list[Segment]:
    """Merge same-category technical signals within the configured gap."""
    merged: list[Segment] = []
    ordered = sorted(signals, key=lambda item: (item.category, item.timestamp_sec))
    for category, items in groupby(ordered, key=lambda item: item.category):
        current: Segment | None = None
        for signal in items:
            if current is None or signal.timestamp_sec - current.end_sec > merge_gap_seconds:
                current = Segment(signal.timestamp_sec, signal.timestamp_sec, {category})
                merged.append(current)
            _add_signal(current, signal)
    return merged


def merge_person_presence_signals(signals: list[Signal], presence_gap_seconds: float) -> list[Segment]:
    """Merge timestamps with one-or-more persons into source-level presence spans."""
    person_signals = sorted(
        (signal for signal in signals if signal.category == "person_detected"),
        key=lambda item: item.timestamp_sec,
    )
    merged: list[Segment] = []
    current: Segment | None = None
    for timestamp, items in groupby(person_signals, key=lambda item: item.timestamp_sec):
        signals_at_timestamp = list(items)
        if current is None or timestamp - current.end_sec > presence_gap_seconds:
            current = Segment(timestamp, timestamp, {"person_detected"})
            merged.append(current)
        for signal in signals_at_timestamp:
            _add_signal(current, signal)
        current.person_count_max = _maximum(current.person_count_max, len(signals_at_timestamp))  # type: ignore[assignment]
    return merged


def merge_non_person_signals(signals: list[Signal], merge_gap_seconds: float) -> list[Segment]:
    return merge_signals(
        [signal for signal in signals if signal.category != "person_detected"], merge_gap_seconds
    )


def _merge_segments(left: Segment, right: Segment) -> Segment:
    combined = Segment(
        start_sec=min(left.start_sec, right.start_sec),
        end_sec=max(left.end_sec, right.end_sec),
        categories=left.categories | right.categories,
        person_count_max=_maximum(left.person_count_max, right.person_count_max),
        motion_score=_maximum(left.motion_score, right.motion_score),
        brightness_score=_maximum(left.brightness_score, right.brightness_score),
        blur_score=_maximum(left.blur_score, right.blur_score),
        camera_shift_score=_maximum(left.camera_shift_score, right.camera_shift_score),
        anomaly_types=left.anomaly_types | right.anomaly_types,
        track_ids=left.track_ids | right.track_ids,
        episode_ids=left.episode_ids | right.episode_ids,
        track_reconciliation_statuses=(
            left.track_reconciliation_statuses | right.track_reconciliation_statuses
        ),
    )
    return combined


def consolidate_segments(segments: list[Segment]) -> list[Segment]:
    """Union overlapping category segments into one logical sample."""
    result: list[Segment] = []
    for segment in sorted(segments, key=lambda item: (item.start_sec, item.end_sec)):
        overlaps_previous = result and segment.start_sec <= result[-1].end_sec
        if overlaps_previous:
            result[-1] = _merge_segments(result[-1], segment)
        else:
            result.append(segment)
    return result


def ordered_categories(categories: set[str]) -> tuple[str, ...]:
    return tuple(category for category in TOOL_CATEGORIES if category in categories)


def proxy_window(
    start_sec: float,
    end_sec: float,
    duration_seconds: float,
    pre_roll_seconds: float,
    post_roll_seconds: float,
) -> ClipWindow:
    clip_start = max(0.0, start_sec - pre_roll_seconds)
    clip_end = min(duration_seconds, end_sec + post_roll_seconds)
    at_start = clip_start == 0.0 and start_sec < pre_roll_seconds
    at_end = clip_end == duration_seconds and end_sec + post_roll_seconds > duration_seconds
    if at_start and at_end:
        status = "clipped_at_video_start_and_end"
    elif at_start:
        status = "clipped_at_video_start"
    elif at_end:
        status = "clipped_at_video_end"
    else:
        status = "sufficient"
    return ClipWindow(clip_start, clip_end, status)
