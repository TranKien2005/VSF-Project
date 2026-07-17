import cv2
import numpy as np
from candidate_mining.frame_sampling import SampledFrame
from candidate_mining.providers.camera_movement import CameraMovementProvider, MovementSettings


def _textured_frame() -> np.ndarray:
    image = np.zeros((180, 240, 3), dtype=np.uint8)
    for x in range(20, 230, 30):
        for y in range(20, 170, 30):
            cv2.circle(image, (x, y), 5, (255, 255, 255), -1)
    return image


def test_translation_emits_movement_candidate_after_debounce() -> None:
    settings = MovementSettings(minimum_consecutive_signals=1, translation_threshold_px=5.0)
    provider = CameraMovementProvider(settings)
    first = _textured_frame()
    matrix = np.float32([[1, 0, 15], [0, 1, 0]])
    shifted = cv2.warpAffine(first, matrix, (240, 180))

    assert provider.process(SampledFrame(0.0, first)) is None
    signal = provider.process(SampledFrame(0.5, shifted))

    assert signal is not None
    assert signal.category == "camera_movement"
    assert signal.camera_shift_score >= settings.shift_score_threshold
