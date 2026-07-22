from candidate_mining.debug_artifacts import (
    PersonDetectionStore,
    StoredDetection,
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
        initial_footpoint_xy=(20.0, 50.0),
        initial_bbox_height_px=30.0,
        motion_confirmed=False,
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
    assert loaded.detections[0].initial_footpoint_xy_px == (20.0, 50.0)
    assert loaded.detections[0].initial_bbox_height_px == 30.0
    assert not loaded.detections[0].motion_confirmed


def test_legacy_detection_store_defaults_existing_detections_to_confirmed(tmp_path) -> None:
    source = tmp_path / "source.mp4"
    source.write_bytes(b"raw video")
    payload = {
        "schema_version": "person-detections.v1",
        "source": {
            "filename": source.name,
            "path": str(source),
            "sha256": "ignored",
            "fps": 30.0,
            "frame_width": 100,
            "frame_height": 100,
        },
        "detector": {"sample_fps": 5.0, "image_size": 960, "confidence_threshold": 0.2},
        "detections": [
            {
                "source_frame_index": 0,
                "timestamp_sec": 0.0,
                "bbox_xyxy_px": [10.0, 20.0, 30.0, 50.0],
                "confidence": 0.8,
                "track_id": 1,
                "episode_id": "episode_000001",
            }
        ],
    }
    payload["source"]["sha256"] = __import__("hashlib").sha256(source.read_bytes()).hexdigest()
    path = tmp_path / "legacy.detections.json"
    path.write_text(__import__("json").dumps(payload), encoding="utf-8")

    loaded = read_person_detection_store(path, source)

    assert loaded.detections == (
        StoredDetection(
            0,
            0.0,
            (10.0, 20.0, 30.0, 50.0),
            0.8,
            1,
            "episode_000001",
            (20.0, 50.0),
            30.0,
            True,
        ),
    )
