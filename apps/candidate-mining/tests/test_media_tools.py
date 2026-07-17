from pathlib import Path

import pytest
from candidate_mining.media_tools import resolve_media_tools


def test_prefers_portable_executables_over_path(tmp_path, monkeypatch) -> None:
    portable_dir = tmp_path / "tools" / "ffmpeg"
    portable_dir.mkdir(parents=True)
    ffmpeg = portable_dir / "ffmpeg.exe"
    ffprobe = portable_dir / "ffprobe.exe"
    ffmpeg.touch()
    ffprobe.touch()
    monkeypatch.setattr("candidate_mining.media_tools.shutil.which", lambda _: "C:/system/tool.exe")

    tools = resolve_media_tools(portable_dir)

    assert tools.ffmpeg == ffmpeg.resolve()
    assert tools.ffprobe == ffprobe.resolve()


def test_falls_back_to_path_when_portable_tools_are_absent(tmp_path, monkeypatch) -> None:
    resolved = {"ffmpeg": "C:/system/ffmpeg.exe", "ffprobe": "C:/system/ffprobe.exe"}
    monkeypatch.setattr("candidate_mining.media_tools.shutil.which", resolved.get)

    tools = resolve_media_tools(tmp_path / "missing")

    assert tools.ffmpeg == Path(resolved["ffmpeg"]).resolve()
    assert tools.ffprobe == Path(resolved["ffprobe"]).resolve()


def test_error_identifies_missing_tools_and_documentation(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("candidate_mining.media_tools.shutil.which", lambda _: None)

    with pytest.raises(RuntimeError, match="ffmpeg, ffprobe") as error:
        resolve_media_tools(tmp_path / "tools" / "ffmpeg")

    assert "docs/ffmpeg-portable-windows.md" in str(error.value)
