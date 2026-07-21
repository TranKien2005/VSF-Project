"""Progress snapshots shared by the pipeline and desktop worker."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProcessingProgress:
    phase: str
    processed_samples: int
    total_samples: int | None
    source_timestamp_sec: float | None
    elapsed_seconds: float
    eta_seconds: float | None
    configured_batch_size: int
    effective_batch_size: int
    device: str
    message: str

    @property
    def percent(self) -> int | None:
        if not self.total_samples:
            return None
        return min(100, max(0, round(100 * self.processed_samples / self.total_samples)))


def estimated_sample_count(frame_count: float, source_fps: float, sample_fps: float) -> int | None:
    """Match the sampling loop's source-frame interval for a stable progress total."""
    if frame_count <= 0 or source_fps <= 0 or sample_fps <= 0:
        return None
    interval = max(1, round(source_fps / sample_fps))
    return int((int(frame_count) + interval - 1) // interval)


def estimate_eta(elapsed_seconds: float, processed_samples: int, total_samples: int | None) -> float | None:
    """Return a conservative ETA after enough completed samples to establish a rate."""
    if total_samples is None or processed_samples < 2 or elapsed_seconds <= 0:
        return None
    remaining = max(0, total_samples - processed_samples)
    return remaining * elapsed_seconds / processed_samples


def cuda_diagnostics() -> str:
    """Return best-effort CUDA memory diagnostics without requiring CUDA to be present."""
    try:
        import torch

        if not torch.cuda.is_available():
            return "CUDA unavailable; processing will use CPU"
        index = torch.cuda.current_device()
        total = torch.cuda.get_device_properties(index).total_memory
        allocated = torch.cuda.memory_allocated(index)
        reserved = torch.cuda.memory_reserved(index)
        free = max(0, total - reserved)
        mib = 1024 * 1024
        name = torch.cuda.get_device_name(index)
        return (
            f"CUDA: {name} · free {free / mib:.0f} MiB · reserved {reserved / mib:.0f} MiB · allocated {allocated / mib:.0f} MiB"
        )
    except (ImportError, RuntimeError):
        return "CUDA diagnostics unavailable"
