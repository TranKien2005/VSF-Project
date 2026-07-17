import pytest
from candidate_mining.exporter import normalize_export_target


def test_normalize_export_target_adds_mp4_suffix(tmp_path) -> None:
    source = tmp_path / "source.avi"
    source.touch()

    assert normalize_export_target(source, tmp_path / "selected") == tmp_path / "selected.mp4"


def test_normalize_export_target_rejects_raw_source(tmp_path) -> None:
    source = tmp_path / "source.mp4"
    source.touch()

    with pytest.raises(ValueError, match="must not overwrite"):
        normalize_export_target(source, source)


def test_normalize_export_target_rejects_directory(tmp_path) -> None:
    source = tmp_path / "source.mp4"
    source.touch()
    directory = tmp_path / "exports"
    directory.mkdir()

    with pytest.raises(ValueError, match="is a directory"):
        normalize_export_target(source, directory)
