from candidate_mining.debug_artifacts import (
    PersonDetectionStore,
    person_detection_path,
    read_person_detection_store,
    source_basename,
    write_person_detection_store,
)
from candidate_mining.tracking import PersonDetection, TrackObservation


def test_person_detection_path_uses_category_and_raw_filename(tmp_path) -> None:
    source = tmp_path / "source video.mp4"
    source.touch()

    assert source_basename(source) == "source_video"
    external_path = person_detection_path(tmp_path, source)
    assert external_path.parent == tmp_path / "person_detected"
    assert external_path.name.startswith("source_video-")
    assert external_path.name.endswith(".detections.json")
    assert person_detection_path(tmp_path, source, raw_dir=tmp_path) == (
        tmp_path / "person_detected" / "source_video.detections.json"
    )


def test_person_detection_store_round_trip_and_overwrite(tmp_path) -> None:
    source = tmp_path / "source video.mp4"
    source.write_bytes(b"raw video")
    observation = TrackObservation(
        timestamp_sec=2.0,
        track_id=1,
        episode_id="episode_000001",
        reconciliation_status="new_episode",
        detection=PersonDetection(2.0, (10.0, 20.0, 30.0, 50.0), 0.8, 60),
    )
    store = PersonDetectionStore.from_observations(
        source,
        [observation],
        source_fps=30.0,
        frame_width=1280,
        frame_height=720,
        sample_fps=5.0,
        image_size=960,
        confidence_threshold=0.2,
    )

    first = write_person_detection_store(store, tmp_path, source)
    second = write_person_detection_store(store, tmp_path, source)
    loaded = read_person_detection_store(second, source)

    assert first == second
    assert len(list((tmp_path / "person_detected").glob("*.json"))) == 1
    assert loaded.detections[0].source_frame_index == 60
    assert loaded.detections[0].bbox_xyxy_px == (10.0, 20.0, 30.0, 50.0)
