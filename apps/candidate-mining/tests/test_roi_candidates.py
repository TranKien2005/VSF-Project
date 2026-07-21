from candidate_mining.debug_artifacts import PersonDetectionStore
from candidate_mining.result_store import write_roi_filtered_person_candidates
from candidate_mining.roi import TrackRoi
from candidate_mining.tracking import PersonDetection, TrackObservation


def test_roi_filtered_candidates_use_person_detected_category(tmp_path) -> None:
    source = tmp_path / "source.mp4"
    source.write_bytes(b"raw video")
    observations = [
        TrackObservation(0.0, 1, "episode_000001", "new_episode", PersonDetection(0.0, (20.0, 10.0, 40.0, 20.0), 0.9, 0)),
        TrackObservation(0.2, 99, "episode_000002", "new_episode", PersonDetection(0.2, (30.0, 10.0, 50.0, 20.0), 0.9, 6)),
    ]
    store = PersonDetectionStore.from_observations(
        source,
        observations,
        source_fps=30.0,
        frame_width=100,
        frame_height=100,
        sample_fps=5.0,
        image_size=960,
        confidence_threshold=0.2,
    )
    roi = TrackRoi.create(
        revision=1,
        reference_source_sha256=store.source_sha256,
        reference_timestamp_sec=0.0,
        reference_frame_size_px=(100, 100),
        stroke_points_normalized=((0.0, 0.25), (0.5, 0.3), (1.0, 0.25)),
    )

    targets = write_roi_filtered_person_candidates(
        store,
        tmp_path / "results",
        source_id=store.source_sha256,
        camera_id=None,
        roi=roi,
        merge_gap_seconds=2.0,
        duration_seconds=1.0,
        pre_roll_seconds=0.0,
        post_roll_seconds=0.0,
        roi_scope="source",
    )

    assert len(targets) == 1
    assert targets[0].parent.parent.name == "person_detected"
    payload = targets[0].read_text(encoding="utf-8")
    assert '"category": "person_detected"' in payload
    assert "99" in payload
