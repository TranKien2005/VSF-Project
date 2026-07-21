from candidate_mining.processed_store import (
    ProcessedSource,
    camera_roi_path,
    effective_roi_path,
    source_roi_path,
)
from candidate_mining.roi import TrackRoi, write_roi


def _record(camera_id: str | None) -> ProcessedSource:
    return ProcessedSource(
        source_id="a" * 64,
        raw_absolute_path_at_registration="C:/external/source.mp4",
        filename="source.mp4",
        sha256="a" * 64,
        size_bytes=1,
        duration_seconds=1.0,
        fps=30.0,
        frame_width=100,
        frame_height=100,
        codec="h264",
        has_audio=True,
        camera_id=camera_id,
    )


def _roi() -> TrackRoi:
    return TrackRoi.create(
        revision=1,
        reference_source_sha256="a" * 64,
        reference_timestamp_sec=0.0,
        reference_frame_size_px=(100, 100),
        stroke_points_normalized=((0.0, 0.2), (0.5, 0.25), (1.0, 0.2)),
    )


def test_source_roi_override_wins_camera_default(tmp_path) -> None:
    record = _record("camera-a")
    write_roi(_roi(), camera_roi_path(tmp_path, "camera-a"))
    assert effective_roi_path(tmp_path, record)[1] == "camera"

    write_roi(_roi(), source_roi_path(tmp_path, record))
    assert effective_roi_path(tmp_path, record)[1] == "source"


def test_independent_source_has_no_inherited_roi(tmp_path) -> None:
    assert effective_roi_path(tmp_path, _record(None)) == (None, None)
