from candidate_mining.tracking import PersonDetection, PersonEpisodeTracker


def detection(timestamp: float, box: tuple[float, float, float, float]) -> PersonDetection:
    return PersonDetection(timestamp, box, 0.9, round(timestamp * 30))


def test_same_person_keeps_one_episode_after_short_gap() -> None:
    tracker = PersonEpisodeTracker(gap_seconds=8.0)

    first = tracker.update(0.0, [detection(0.0, (10, 10, 30, 50))], 100.0)[0]
    second = tracker.update(4.0, [detection(4.0, (12, 10, 32, 50))], 100.0)[0]

    assert first.episode_id == second.episode_id
    assert second.track_id == first.track_id


def test_far_person_creates_a_separate_episode() -> None:
    tracker = PersonEpisodeTracker(gap_seconds=8.0, center_distance_ratio=0.1)

    first = tracker.update(0.0, [detection(0.0, (10, 10, 30, 50))], 100.0)[0]
    second = tracker.update(2.0, [detection(2.0, (70, 70, 90, 95))], 100.0)[0]

    assert first.episode_id != second.episode_id


def test_long_absence_creates_a_new_episode() -> None:
    tracker = PersonEpisodeTracker(gap_seconds=5.0)

    first = tracker.update(0.0, [detection(0.0, (10, 10, 30, 50))], 100.0)[0]
    second = tracker.update(6.0, [detection(6.0, (10, 10, 30, 50))], 100.0)[0]

    assert first.episode_id != second.episode_id
