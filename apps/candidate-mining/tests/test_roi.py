import pytest
from candidate_mining.roi import TrackRoi, derive_track_region, point_in_polygon, roi_contains_detection


def test_freehand_stroke_uses_endpoint_tangents_and_smaller_partition() -> None:
    region = derive_track_region(((0.0, 0.2), (0.4, 0.25), (1.0, 0.2)))

    assert region.start_extension == ((0.0, 0.2),)
    assert region.end_extension == ((1.0, 0.2),)
    assert point_in_polygon((0.5, 0.1), region.tracking_region)
    assert not point_in_polygon((0.5, 0.6), region.tracking_region)


def test_curved_stroke_round_trip_and_footpoint_membership() -> None:
    roi = TrackRoi.create(
        revision=1,
        reference_source_sha256="a" * 64,
        reference_timestamp_sec=1.0,
        reference_frame_size_px=(100, 100),
        stroke_points_normalized=((0.0, 0.25), (0.4, 0.3), (1.0, 0.25)),
    )

    assert TrackRoi.from_dict(roi.to_dict()) == roi
    assert roi_contains_detection(roi, (40.0, 5.0, 60.0, 20.0), 100, 100)
    assert not roi_contains_detection(roi, (40.0, 5.0, 60.0, 80.0), 100, 100)


@pytest.mark.parametrize(
    "points",
    [
        ((0.5, 0.5),),
        ((0.5, 0.5), (0.5, 0.5)),
        ((0.1, 0.1), (0.9, 0.9), (0.1, 0.9), (0.9, 0.1)),
    ],
)
def test_invalid_stroke_is_rejected(points) -> None:
    with pytest.raises(ValueError):
        derive_track_region(points)


def test_middle_stroke_with_endpoint_jitter_derives_clean_partition() -> None:
    stroke = (
        (0.2, 0.5),
        (0.3, 0.5),
        (0.4, 0.5),
        (0.5, 0.5),
        (0.6, 0.5),
        (0.7, 0.5),
        (0.8, 0.5),
        (0.78, 0.52),
        (0.76, 0.54),
    )
    region = derive_track_region(stroke)
    assert len(region.tracking_region) >= 5
    assert point_in_polygon((0.5, 0.52), region.tracking_region)
