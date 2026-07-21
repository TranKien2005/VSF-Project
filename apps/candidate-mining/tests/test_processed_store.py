from candidate_mining.media_tools import MediaTools
from candidate_mining.processed_store import (
    camera_path,
    import_camera_folder,
    import_video_files,
    list_sources,
    source_path,
)


class Inventory:
    sha256 = "a" * 64
    size_bytes = 5
    duration_seconds = 12.0
    fps = 30.0
    width = 1920
    height = 1080
    codec = "h264"
    has_audio = True


def test_independent_video_writes_metadata_only(tmp_path, monkeypatch) -> None:
    source = tmp_path / "source.mp4"
    source.write_bytes(b"video")
    processed = tmp_path / "processed"
    monkeypatch.setattr("candidate_mining.processed_store.probe_video", lambda *_args, **_kwargs: Inventory())

    records, failures = import_video_files([source], processed, MediaTools(tmp_path / "ffmpeg", tmp_path / "ffprobe"))

    assert not failures
    assert records[0].camera_id is None
    assert source_path(processed, Inventory.sha256).exists()
    assert list_sources(processed)[0].raw_absolute_path_at_registration == str(source.resolve())


def test_camera_folder_name_owns_all_nested_videos(tmp_path, monkeypatch) -> None:
    camera_root = tmp_path / "Front gate"
    source = camera_root / "nested" / "source.mp4"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"video")
    processed = tmp_path / "processed"
    monkeypatch.setattr("candidate_mining.processed_store.probe_video", lambda *_args, **_kwargs: Inventory())

    camera, records, failures = import_camera_folder(
        camera_root, processed, MediaTools(tmp_path / "ffmpeg", tmp_path / "ffprobe")
    )

    assert not failures
    assert camera.name == "Front gate"
    assert records[0].camera_id == "Front-gate"
    assert camera_path(processed, camera.camera_id).exists()
    assert source_path(processed, Inventory.sha256, camera_id=camera.camera_id).exists()
