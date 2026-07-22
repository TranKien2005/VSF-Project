import numpy as np
from candidate_mining.frame_sampling import SampledFrame
from candidate_mining.providers.camera_anomaly import CameraAnomalyProvider, CameraAnomalySettings


def test_camera_anomaly_detects_covered_black_frame() -> None:
    provider = CameraAnomalyProvider(CameraAnomalySettings(anomaly_threshold=0.40, minimum_consecutive_signals=1))

    # Normal frame with texture
    normal_bgr = (np.random.rand(480, 640, 3) * 255).astype(np.uint8)
    frame1 = SampledFrame(source_frame_index=0, timestamp_sec=0.0, bgr=normal_bgr)
    assert provider.process(frame1) is None

    # Covered frame (almost pure black with a white line)
    black_bgr = np.zeros((480, 640, 3), dtype=np.uint8)
    black_bgr[100:105, 50:400] = 255  # White streak line
    frame2 = SampledFrame(source_frame_index=1, timestamp_sec=0.2, bgr=black_bgr)

    sig = provider.process(frame2)
    assert sig is not None
    assert sig.category == "camera_anomaly"
    assert sig.motion_score >= 0.40
