import cv2
import numpy as np
from candidate_mining.config import load_config
from candidate_mining.ffmpeg_frame_access import FfmpegFrameAccess
from candidate_mining.media_tools import resolve_media_tools


def test_ffmpeg_frame_access_decodes_complete_frames(tmp_path) -> None:
    source = tmp_path / "sample.avi"
    writer = cv2.VideoWriter(str(source), cv2.VideoWriter_fourcc(*"MJPG"), 10.0, (16, 12))
    for value in range(5):
        writer.write(np.full((12, 16, 3), value * 20, dtype=np.uint8))
    writer.release()
    tools = resolve_media_tools(load_config().paths.ffmpeg_dir)
    access = FfmpegFrameAccess(source, tools)
    try:
        frame = access.read_at_frame(2)
        following = access.read_next()
    finally:
        access.close()

    assert frame.source_frame_index == 2
    assert frame.bgr.shape == (12, 16, 3)
    assert following.source_frame_index == 3
