import numpy as np
from candidate_mining.frame_sampling import SampledFrame
from candidate_mining.providers.cover_heuristic import CoverHeuristicProvider, CoverSettings


def test_dark_uniform_frames_emit_cover_candidate_after_debounce() -> None:
    provider = CoverHeuristicProvider(CoverSettings(minimum_consecutive_signals=2))
    frame = np.zeros((80, 120, 3), dtype=np.uint8)

    assert provider.process(SampledFrame(0.0, frame)) is None
    signal = provider.process(SampledFrame(0.5, frame))

    assert signal is not None
    assert signal.category == "camera_cover"
    assert 0.0 <= signal.brightness_score <= 1.0
    assert 0.0 <= signal.blur_score <= 1.0
