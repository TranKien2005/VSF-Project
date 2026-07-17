from candidate_mining.video_browser import discover_raw_videos


def test_discover_raw_videos_recurses_and_sorts_alphabetically(tmp_path) -> None:
    (tmp_path / "z-last.mp4").touch()
    nested = tmp_path / "Camera-A"
    nested.mkdir()
    (nested / "B-subvideo.MKV").touch()
    (nested / "notes.txt").touch()
    (tmp_path / "a-first.avi").touch()

    entries = discover_raw_videos(tmp_path)

    assert [relative.as_posix() for _, relative in entries] == [
        "a-first.avi",
        "Camera-A/B-subvideo.MKV",
        "z-last.mp4",
    ]
