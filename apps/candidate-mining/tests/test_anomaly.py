import numpy as np
from candidate_mining.frame_sampling import SampledFrame
from candidate_mining.providers.anomaly import AnomalyProvider, AnomalySettings


def test_black_frames_emit_unknown_anomaly() -> None:
    provider = AnomalyProvider(AnomalySettings(minimum_consecutive_signals=2))
    black = np.zeros((40, 60, 3), dtype=np.uint8)

    first = provider.process(SampledFrame(0.0, black), has_accepted_person=False)
    provider.process(SampledFrame(0.5, black), has_accepted_person=False)
    third = provider.process(SampledFrame(1.0, black), has_accepted_person=False)

    assert any("black_screen" in signal.anomaly_types for signal in first)
    assert any("frozen_video" in signal.anomaly_types for signal in third)


def test_sustained_motion_without_person_emits_anomaly() -> None:
    settings = AnomalySettings(motion_score_threshold=0.01, minimum_consecutive_signals=1)
    provider = AnomalyProvider(settings)
    dark = np.zeros((40, 60, 3), dtype=np.uint8)
    bright = np.full((40, 60, 3), 255, dtype=np.uint8)

    provider.process(SampledFrame(0.0, dark), has_accepted_person=False)
    signals = provider.process(SampledFrame(0.5, bright), has_accepted_person=False)

    assert any("motion_without_person" in signal.anomaly_types for signal in signals)
