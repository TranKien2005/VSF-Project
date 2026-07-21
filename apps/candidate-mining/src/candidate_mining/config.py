"""Configuration loading for the local pipeline."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PathsConfig:
    processed_dir: Path
    results_dir: Path
    log_dir: Path
    ffmpeg_dir: Path
    model_weights_dir: Path
    torch_cache_dir: Path


@dataclass(frozen=True)
class ProviderConfig:
    person_yolo: dict[str, object]
    person_rtdetr: dict[str, object]
    cover_heuristic: dict[str, object]
    camera_movement: dict[str, object]
    anomaly: dict[str, object]
    yolo11n_weights: Path
    rtdetr_l_weights: Path


@dataclass(frozen=True)
class PipelineConfig:
    sample_fps: float
    person_presence_merge_gap_seconds: float
    merge_gap_seconds: float
    pre_roll_seconds: float
    post_roll_seconds: float
    random_background_count: int
    random_background_duration_seconds: float
    random_exclusion_seconds: float
    random_seed: int


@dataclass(frozen=True)
class AppConfig:
    root: Path
    paths: PathsConfig
    pipeline: PipelineConfig
    providers: ProviderConfig


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _under_root(root: Path, value: str) -> Path:
    resolved = (root / value).resolve()
    if root not in (resolved, *resolved.parents):
        raise ValueError(f"Configured path escapes repository: {value}")
    return resolved


def load_config(config_path: Path | None = None) -> AppConfig:
    root = repository_root()
    path = config_path or root / "configs" / "candidate-mining.toml"
    with path.open("rb") as handle:
        raw = tomllib.load(handle)

    paths_raw = raw["paths"]
    pipeline_raw = raw["pipeline"]
    paths = PathsConfig(
        processed_dir=_under_root(root, paths_raw["processed_dir"]),
        results_dir=_under_root(root, paths_raw["results_dir"]),
        log_dir=_under_root(root, paths_raw["log_dir"]),
        ffmpeg_dir=_under_root(root, paths_raw["ffmpeg_dir"]),
        model_weights_dir=_under_root(root, paths_raw["model_weights_dir"]),
        torch_cache_dir=_under_root(root, paths_raw["torch_cache_dir"]),
    )
    providers_raw = raw["providers"]
    providers = ProviderConfig(
        person_yolo=providers_raw["person_yolo"],
        person_rtdetr=providers_raw["person_rtdetr"],
        cover_heuristic=providers_raw["cover_heuristic"],
        camera_movement=providers_raw["camera_movement"],
        anomaly=providers_raw["anomaly"],
        yolo11n_weights=_under_root(root, raw["models"]["yolo11n_weights"]),
        rtdetr_l_weights=_under_root(root, raw["models"]["rtdetr_l_weights"]),
    )
    pipeline = PipelineConfig(
        sample_fps=float(pipeline_raw["sample_fps"]),
        person_presence_merge_gap_seconds=float(pipeline_raw["person_presence_merge_gap_seconds"]),
        merge_gap_seconds=float(pipeline_raw["merge_gap_seconds"]),
        pre_roll_seconds=float(pipeline_raw["pre_roll_seconds"]),
        post_roll_seconds=float(pipeline_raw["post_roll_seconds"]),
        random_background_count=int(pipeline_raw["random_background_count"]),
        random_background_duration_seconds=float(pipeline_raw["random_background_duration_seconds"]),
        random_exclusion_seconds=float(pipeline_raw["random_exclusion_seconds"]),
        random_seed=int(pipeline_raw["random_seed"]),
    )
    if pipeline.sample_fps <= 0:
        raise ValueError("sample_fps must be positive")
    if (
        min(
            pipeline.person_presence_merge_gap_seconds,
            pipeline.merge_gap_seconds,
            pipeline.pre_roll_seconds,
            pipeline.post_roll_seconds,
        )
        < 0
    ):
        raise ValueError("Gap and context durations must be non-negative")
    if pipeline.random_background_duration_seconds <= 0 or pipeline.random_background_count < 0:
        raise ValueError("Random-background duration must be positive and count non-negative")
    return AppConfig(root=root, paths=paths, pipeline=pipeline, providers=providers)
