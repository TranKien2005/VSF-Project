from pathlib import Path

from candidate_mining.export_dialog import choose_export_path, suggested_export_name


class FakeRoot:
    def __init__(self) -> None:
        self.withdrawn = False
        self.destroyed = False

    def withdraw(self) -> None:
        self.withdrawn = True

    def destroy(self) -> None:
        self.destroyed = True


def test_suggested_export_name_includes_source_span_and_range() -> None:
    assert suggested_export_name(Path("front gate.mp4"), "person_detected-0001", 0.0, 42.0) == (
        "front gate_person_detected-0001_0.0s-42.0s.mp4"
    )


def test_choose_export_path_returns_none_and_destroys_root(monkeypatch) -> None:
    root = FakeRoot()
    monkeypatch.setattr("tkinter.Tk", lambda: root)
    monkeypatch.setattr("tkinter.filedialog.asksaveasfilename", lambda **_: "")

    result = choose_export_path(Path("source.mp4"), "person_detected-0001", 1.0, 2.0)

    assert result is None
    assert root.withdrawn
    assert root.destroyed


def test_annotated_export_name_is_distinct() -> None:
    assert suggested_export_name(Path("source.mp4"), "person_detected-0001", 1.0, 2.0, annotated=True) == (
        "source_person_detected-0001_1.0s-2.0s_bbox.mp4"
    )


def test_choose_export_path_passes_mp4_defaults(monkeypatch, tmp_path) -> None:
    root = FakeRoot()
    captured: dict[str, object] = {}
    target = tmp_path / "chosen.mp4"
    monkeypatch.setattr("tkinter.Tk", lambda: root)

    def select(**kwargs):
        captured.update(kwargs)
        return str(target)

    monkeypatch.setattr("tkinter.filedialog.asksaveasfilename", select)

    assert choose_export_path(Path("source.mp4"), "person_detected-0001", 1.0, 2.0) == target
    assert captured["defaultextension"] == ".mp4"
    assert captured["initialfile"] == "source_person_detected-0001_1.0s-2.0s.mp4"
    assert root.destroyed
