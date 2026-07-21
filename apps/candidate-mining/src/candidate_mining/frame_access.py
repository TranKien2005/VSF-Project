"""OpenCV source-frame access shared by desktop authoring and review."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SourceMetadata:
    fps: float
    frame_count: int
    width: int
    height: int

    @property
    def duration_seconds(self) -> float:
        return self.frame_count / self.fps if self.fps > 0 else 0.0


@dataclass(frozen=True)
class DecodedFrame:
    bgr: object
    source_frame_index: int
    timestamp_sec: float
    metadata: SourceMetadata


class FrameAccess:
    """Seek safely, verifying random OpenCV seeks before trusting decoded output."""

    def __init__(self, video_path: Path) -> None:
        self.video_path = video_path
        self._capture = None
        self._last_frame_index: int | None = None
        self._open_capture()

    def _open_capture(self) -> None:
        import cv2

        self._capture = cv2.VideoCapture(str(self.video_path))
        if not self._capture.isOpened():
            self._capture.release()
            raise RuntimeError(f"OpenCV could not open video: {self.video_path}")
        fps = float(self._capture.get(cv2.CAP_PROP_FPS))
        if fps <= 0:
            self._capture.release()
            raise RuntimeError(f"Video has no usable FPS: {self.video_path}")
        self.metadata = SourceMetadata(
            fps=fps,
            frame_count=max(0, int(self._capture.get(cv2.CAP_PROP_FRAME_COUNT))),
            width=max(0, int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH))),
            height=max(0, int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT))),
        )

    def _reopen_capture(self) -> None:
        self.close()
        self._last_frame_index = None
        self._open_capture()

    def read_at_time(self, timestamp_sec: float) -> DecodedFrame:
        if timestamp_sec < 0:
            raise ValueError("Source timestamp must be non-negative")
        return self.read_at_frame(round(timestamp_sec * self.metadata.fps))

    def read_at_frame(self, frame_index: int) -> DecodedFrame:
        import cv2

        if frame_index < 0:
            raise ValueError("Source frame index must be non-negative")
        target = min(frame_index, self.metadata.frame_count - 1) if self.metadata.frame_count else frame_index
        if self._last_frame_index is not None and target == self._last_frame_index + 1:
            return self.read_next()
        self._capture.set(cv2.CAP_PROP_POS_FRAMES, target)
        decoded = self._decode_next()
        if decoded and decoded.source_frame_index == target:
            return decoded
        return self._decode_sequentially(target)

    def _decode_sequentially(self, target: int) -> DecodedFrame:
        """Reopen and decode from source start when random seek is not trustworthy."""
        self._reopen_capture()
        decoded: DecodedFrame | None = None
        for _ in range(target + 1):
            decoded = self._decode_next()
            if decoded is None:
                break
        if decoded is None or decoded.source_frame_index != target:
            raise RuntimeError(f"Could not decode verified frame {target} from {self.video_path}")
        return decoded

    def _decode_next(self) -> DecodedFrame | None:
        import cv2

        ok, frame = self._capture.read()
        if not ok:
            return None
        position = self._capture.get(cv2.CAP_PROP_POS_FRAMES)
        actual_index = max(0, int(position) - 1)
        self._last_frame_index = actual_index
        return DecodedFrame(frame, actual_index, actual_index / self.metadata.fps, self.metadata)

    def read_next(self) -> DecodedFrame:
        decoded = self._decode_next()
        if decoded is None:
            raise EOFError("End of source video")
        return decoded

    def close(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None
        self._last_frame_index = None
