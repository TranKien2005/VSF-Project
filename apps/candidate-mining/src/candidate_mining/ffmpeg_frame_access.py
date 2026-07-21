"""Read preview frames with the configured FFmpeg decoder, not OpenCV's backend."""

from __future__ import annotations

import json
import subprocess
import threading
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

import numpy as np

from .frame_access import DecodedFrame, SourceMetadata
from .media_tools import MediaTools


@dataclass(frozen=True)
class _Probe:
    metadata: SourceMetadata


def _probe(video_path: Path, tools: MediaTools) -> _Probe:
    command = [
        str(tools.ffprobe),
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height,avg_frame_rate,nb_frames:format=duration",
        "-of",
        "json",
        str(video_path),
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    payload = json.loads(result.stdout)
    streams = payload.get("streams", [])
    if not streams:
        raise ValueError(f"No video stream found in {video_path}")
    stream = streams[0]
    width, height = int(stream["width"]), int(stream["height"])
    rate = str(stream.get("avg_frame_rate", "0/0"))
    numerator, denominator = rate.split("/", maxsplit=1)
    fps = float(numerator) / float(denominator) if float(denominator) else 0.0
    if fps <= 0:
        raise ValueError(f"Video has no usable frame rate: {video_path}")
    duration = float(payload.get("format", {}).get("duration", 0.0))
    frames = stream.get("nb_frames")
    frame_count = int(frames) if frames and str(frames).isdigit() else round(duration * fps)
    return _Probe(SourceMetadata(fps=fps, frame_count=max(0, frame_count), width=width, height=height))


class FfmpegFrameAccess:
    """Restart an exact FFmpeg decoder on seek and return complete BGR preview frames only."""

    def __init__(self, video_path: Path, tools: MediaTools, *, preview_width: int = 960) -> None:
        self.video_path = video_path
        self.tools = tools
        self.source_metadata = _probe(video_path, tools).metadata
        if preview_width <= 0:
            raise ValueError("Preview width must be positive")
        width = min(preview_width, self.source_metadata.width)
        height = max(2, round(self.source_metadata.height * width / self.source_metadata.width))
        height += height % 2
        self.metadata = SourceMetadata(
            fps=self.source_metadata.fps,
            frame_count=self.source_metadata.frame_count,
            width=width,
            height=height,
        )
        self.preview_scale_x = self.metadata.width / self.source_metadata.width
        self.preview_scale_y = self.metadata.height / self.source_metadata.height
        self._process: subprocess.Popen[bytes] | None = None
        self._process: subprocess.Popen[bytes] | None = None
        self._stderr_lines: deque[str] = deque(maxlen=20)
        self._stderr_thread: threading.Thread | None = None
        self._next_frame_index = 0
        self._last_frame_index: int | None = None
        self._start(0)

    def _start(self, frame_index: int) -> None:
        self.close()
        seek_seconds = max(0.0, frame_index / self.metadata.fps)
        command = [
            str(self.tools.ffmpeg),
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(self.video_path),
            "-ss",
            f"{seek_seconds:.6f}",
            "-map",
            "0:v:0",
            "-an",
            "-vf",
            f"scale={self.metadata.width}:{self.metadata.height}:flags=fast_bilinear",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "bgr24",
            "pipe:1",
        ]
        self._process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self._stderr_lines.clear()
        self._stderr_thread = threading.Thread(target=self._drain_stderr, args=(self._process.stderr,), daemon=True)
        self._stderr_thread.start()
        self._next_frame_index = frame_index
        self._last_frame_index = None

    def _drain_stderr(self, stream: BinaryIO | None) -> None:
        if stream is None:
            return
        for line in stream:
            self._stderr_lines.append(line.decode("utf-8", errors="replace").rstrip())

    def _read_exact(self, amount: int) -> bytes | None:
        if not self._process or not self._process.stdout:
            raise RuntimeError("FFmpeg decoder is not running")
        data = bytearray()
        while len(data) < amount:
            block = self._process.stdout.read(amount - len(data))
            if not block:
                return None
            data.extend(block)
        return bytes(data)

    def _decode_next(self) -> DecodedFrame | None:
        bytes_per_frame = self.metadata.width * self.metadata.height * 3
        raw = self._read_exact(bytes_per_frame)
        if raw is None:
            return None
        index = self._next_frame_index
        self._next_frame_index += 1
        self._last_frame_index = index
        frame = np.frombuffer(raw, dtype=np.uint8).reshape((self.metadata.height, self.metadata.width, 3))
        return DecodedFrame(frame, index, index / self.metadata.fps, self.metadata)

    def read_at_frame(self, frame_index: int) -> DecodedFrame:
        if frame_index < 0:
            raise ValueError("Source frame index must be non-negative")
        target = min(frame_index, self.metadata.frame_count - 1) if self.metadata.frame_count else frame_index
        if target != self._next_frame_index:
            self._start(target)
        decoded = self._decode_next()
        if decoded is None:
            detail = "\n".join(self._stderr_lines) or "no decoder detail"
            raise RuntimeError(f"FFmpeg could not decode frame {target} from {self.video_path}: {detail}")
        return decoded

    def read_at_time(self, timestamp_sec: float) -> DecodedFrame:
        if timestamp_sec < 0:
            raise ValueError("Source timestamp must be non-negative")
        return self.read_at_frame(round(timestamp_sec * self.metadata.fps))

    def read_next(self) -> DecodedFrame:
        decoded = self._decode_next()
        if decoded is None:
            raise EOFError("End of source video")
        return decoded

    def close(self) -> None:
        if not self._process:
            return
        if self._process.poll() is None:
            self._process.terminate()
        try:
            self._process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait()
        if self._process.stdout:
            self._process.stdout.close()
        if self._process.stderr:
            self._process.stderr.close()
        if self._stderr_thread:
            self._stderr_thread.join(timeout=1)
        self._stderr_thread = None
        self._process = None
