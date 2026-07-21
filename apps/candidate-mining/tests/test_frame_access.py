import cv2
import numpy as np
from candidate_mining.frame_access import FrameAccess


def test_frame_access_reports_actual_source_frame(tmp_path) -> None:
    source = tmp_path / "sample.avi"
    writer = cv2.VideoWriter(str(source), cv2.VideoWriter_fourcc(*"MJPG"), 10.0, (16, 12))
    for value in range(5):
        writer.write(np.full((12, 16, 3), value * 20, dtype=np.uint8))
    writer.release()

    access = FrameAccess(source)
    try:
        frame = access.read_at_time(0.2)
    finally:
        access.close()

    assert frame.metadata.fps == 10.0
    assert frame.metadata.frame_count == 5
    assert frame.source_frame_index == 2
    assert frame.timestamp_sec == 0.2


def test_frame_access_preserves_actual_index_after_adjacent_reads(tmp_path) -> None:
    source = tmp_path / "sample.avi"
    writer = cv2.VideoWriter(str(source), cv2.VideoWriter_fourcc(*"MJPG"), 10.0, (16, 12))
    for value in range(5):
        writer.write(np.full((12, 16, 3), value * 20, dtype=np.uint8))
    writer.release()

    access = FrameAccess(source)
    try:
        first = access.read_at_frame(2)
        following = access.read_at_frame(3)
        backward = access.read_at_frame(1)
    finally:
        access.close()

    assert first.source_frame_index == 2
    assert following.source_frame_index == 3
    assert backward.source_frame_index == 1
    assert backward.timestamp_sec == 0.1
