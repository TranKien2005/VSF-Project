from candidate_mining.config import load_config, repository_root


def test_repository_root_and_default_config_are_resolved() -> None:
    config = load_config()

    assert config.root == repository_root()
    assert config.paths.manifest_dir == config.root / "data" / "manifests"
    assert config.paths.ffmpeg_dir == config.root / "tools" / "ffmpeg"
    assert config.pipeline.sample_fps == 5.0
    assert config.pipeline.pre_roll_seconds == 5.0
    assert config.pipeline.post_roll_seconds == 5.0
