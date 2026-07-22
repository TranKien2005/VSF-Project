from candidate_mining.models import Signal
from candidate_mining.segments import consolidate_segments, merge_signals, proxy_window


def test_merges_same_category_within_gap_and_keeps_metrics() -> None:
    signals = [
        Signal(13.0, "person_detected", person_count=2),
        Signal(10.0, "person_detected", person_count=1),
        Signal(20.1, "person_detected", person_count=1),
    ]

    segments = merge_signals(signals, merge_gap_seconds=5.0)

    boundaries = [(segment.start_sec, segment.end_sec) for segment in segments]
    assert boundaries == [(10.0, 13.0), (20.1, 20.1)]
    assert segments[0].person_count_max == 2


def test_consolidates_overlapping_categories_into_one_sample() -> None:
    signals = [
        Signal(10.0, "person_detected", person_count=1),
        Signal(14.0, "person_detected", person_count=2),
        Signal(13.0, "camera_anomaly", brightness_score=0.8),
    ]

    merged = merge_signals(signals, merge_gap_seconds=5.0)
    consolidated = consolidate_segments(merged)

    assert len(consolidated) == 1
    assert consolidated[0].categories == {"person_detected", "camera_anomaly"}
    assert consolidated[0].start_sec == 10.0
    assert consolidated[0].end_sec == 14.0
    assert consolidated[0].person_count_max == 2
    assert consolidated[0].brightness_score == 0.8


def test_proxy_window_reports_both_boundaries() -> None:
    window = proxy_window(
        5.0,
        15.0,
        duration_seconds=20.0,
        pre_roll_seconds=30.0,
        post_roll_seconds=30.0,
    )

    assert window.start_sec == 0.0
    assert window.end_sec == 20.0
    assert window.context_status == "clipped_at_video_start_and_end"
