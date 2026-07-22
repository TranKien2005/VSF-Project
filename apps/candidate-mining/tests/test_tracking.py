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


def test_track_stays_suspect_until_its_footpoint_moves_relative_to_initial_box_height() -> None:
    tracker = PersonEpisodeTracker(movement_threshold_ratio=0.5)

    first = tracker.update(0.0, [detection(0.0, (10, 10, 30, 50))], 100.0)[0]
    still = tracker.update(0.2, [detection(0.2, (15, 10, 35, 50))], 100.0)[0]
    confirmed = tracker.update(0.4, [detection(0.4, (31, 10, 51, 50))], 100.0)[0]
    after_confirmation = tracker.update(0.6, [detection(0.6, (31, 10, 51, 50))], 100.0)[0]

    assert first.initial_footpoint_xy == (20.0, 50)
    assert first.initial_bbox_height_px == 40
    assert not first.motion_confirmed
    assert not still.motion_confirmed
    assert confirmed.motion_confirmed
    assert after_confirmation.motion_confirmed


def test_new_track_gets_a_new_initial_position_after_long_absence() -> None:
    tracker = PersonEpisodeTracker(gap_seconds=0.1, movement_threshold_ratio=0.5)

    first = tracker.update(0.0, [detection(0.0, (10, 10, 30, 50))], 100.0)[0]
    second = tracker.update(1.0, [detection(1.0, (50, 10, 70, 50))], 100.0)[0]

    assert first.track_id != second.track_id
    assert second.initial_footpoint_xy == (60.0, 50)
    assert not second.motion_confirmed


def test_lower_movement_threshold_confirms_motion_at_20_percent() -> None:
    tracker = PersonEpisodeTracker(movement_threshold_ratio=0.20)

    # Initial box height is 40px, footpoint at (20, 50). 20% of 40px is 8px.
    first = tracker.update(0.0, [detection(0.0, (10, 10, 30, 50))], 100.0)[0]
    # Move footpoint by 9px (from x=20 to x=29)
    moved = tracker.update(0.2, [detection(0.2, (19, 10, 39, 50))], 100.0)[0]

    assert not first.motion_confirmed
    assert moved.motion_confirmed


def test_episode_motion_inheritance_across_track_reassociation() -> None:
    tracker = PersonEpisodeTracker(gap_seconds=8.0, movement_threshold_ratio=0.20)

    # Confirm episode motion
    first = tracker.update(0.0, [detection(0.0, (10, 10, 30, 50))], 100.0)[0]
    moved = tracker.update(0.2, [detection(0.2, (25, 10, 45, 50))], 100.0)[0]
    assert moved.motion_confirmed

    # Episode should stay confirmed when reassociated
    reassociated = tracker.update(1.0, [detection(1.0, (26, 10, 46, 50))], 100.0)[0]
    assert reassociated.motion_confirmed
    assert reassociated.episode_id == first.episode_id

