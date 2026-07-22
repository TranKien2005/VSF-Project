from candidate_mining.debug_artifacts import StoredDetection
from candidate_mining.debug_renderer import held_detections_by_frame


def detection(frame: int, track_id: int = 1) -> StoredDetection:
    return StoredDetection(
        frame,
        frame / 30.0,
        (10.0, 20.0, 30.0, 50.0),
        0.8,
        track_id,
        f"episode_{track_id}",
        (20.0, 50.0),
        30.0,
        True,
    )


def test_viewer_holds_last_5fps_snapshot_until_next_sample() -> None:
    detections = (detection(60), detection(66, 2))

    assert held_detections_by_frame(detections, 59) == []
    assert held_detections_by_frame(detections, 60) == [detection(60)]
    assert held_detections_by_frame(detections, 65) == [detection(60)]
    assert held_detections_by_frame(detections, 66) == [detection(66, 2)]


def test_viewer_holds_multiple_boxes_from_same_snapshot() -> None:
    detections = (detection(60, 1), detection(60, 2), detection(66, 3))

    assert held_detections_by_frame(detections, 63) == [detection(60, 1), detection(60, 2)]
