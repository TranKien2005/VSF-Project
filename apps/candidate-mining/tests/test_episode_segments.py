from candidate_mining.models import Signal
from candidate_mining.segments import merge_person_presence_signals, proxy_window


def test_overlapping_person_episodes_merge_into_one_source_presence_span() -> None:
    signals = [
        Signal(0.0, "person_detected", person_count=1, episode_ids=("episode_001",), track_ids=(1,)),
        Signal(0.2, "person_detected", person_count=2, episode_ids=("episode_002",), track_ids=(2,)),
        Signal(1.0, "person_detected", person_count=1, episode_ids=("episode_001",), track_ids=(1,)),
    ]

    segments = merge_person_presence_signals(signals, presence_gap_seconds=2.0)

    assert len(segments) == 1
    assert (segments[0].start_sec, segments[0].end_sec) == (0.0, 1.0)
    assert segments[0].person_count_max == 2
    assert segments[0].episode_ids == {"episode_001", "episode_002"}
    assert segments[0].track_ids == {1, 2}


def test_person_presence_splits_only_after_gap_exceeds_threshold() -> None:
    signals = [
        Signal(0.0, "person_detected", person_count=1),
        Signal(2.0, "person_detected", person_count=1),
        Signal(4.001, "person_detected", person_count=1),
    ]

    segments = merge_person_presence_signals(signals, presence_gap_seconds=2.0)

    assert [(segment.start_sec, segment.end_sec) for segment in segments] == [(0.0, 2.0), (4.001, 4.001)]


def test_presence_span_uses_full_duration_with_five_second_outer_context() -> None:
    segment = merge_person_presence_signals(
        [Signal(10.0, "person_detected", person_count=1), Signal(20.0, "person_detected", person_count=1)],
        presence_gap_seconds=15.0,
    )[0]

    window = proxy_window(segment.start_sec, segment.end_sec, 30.0, pre_roll_seconds=5.0, post_roll_seconds=5.0)

    assert (window.start_sec, window.end_sec) == (5.0, 25.0)
