from pathlib import Path
from types import SimpleNamespace

from candidate_mining.cli import _export_span, _span_action


class Span:
    span_id = "person_detected-0001"
    context_start_sec = 1.0
    context_end_sec = 6.0


def app_config(tmp_path: Path):
    return SimpleNamespace(paths=SimpleNamespace(ffmpeg_dir=tmp_path / "tools" / "ffmpeg"))


def test_span_action_view_passes_selected_context(monkeypatch, tmp_path) -> None:
    calls: list[tuple] = []
    responses = iter(["v", "b"])
    monkeypatch.setattr("candidate_mining.cli.typer.prompt", lambda _: next(responses))
    monkeypatch.setattr("candidate_mining.cli.typer.echo", lambda _: None)
    monkeypatch.setattr("candidate_mining.cli.inspect_raw_video", lambda *args, **kwargs: calls.append((args, kwargs)))
    source = tmp_path / "source.mp4"
    store = object()

    _span_action(source, store, Span(), app_config(tmp_path))

    assert calls == [((source, store), {"context_start_sec": 1.0, "context_end_sec": 6.0})]


def test_export_span_cancelled_does_not_resolve_tools(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("candidate_mining.cli.choose_export_path", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("candidate_mining.cli.typer.echo", lambda _: None)
    monkeypatch.setattr(
        "candidate_mining.cli.resolve_media_tools",
        lambda _: (_ for _ in ()).throw(AssertionError("tools should not be resolved")),
    )

    _export_span(tmp_path / "source.mp4", object(), Span(), app_config(tmp_path))


def test_export_span_uses_context_bounds_and_resolved_ffmpeg(monkeypatch, tmp_path) -> None:
    source = tmp_path / "source.mp4"
    target = tmp_path / "export.mp4"
    calls: list[tuple] = []
    monkeypatch.setattr("candidate_mining.cli.choose_export_path", lambda *_args, **_kwargs: target)
    monkeypatch.setattr("candidate_mining.cli.typer.echo", lambda _: None)
    monkeypatch.setattr(
        "candidate_mining.cli.resolve_media_tools",
        lambda _: SimpleNamespace(ffmpeg=tmp_path / "tools" / "ffmpeg" / "ffmpeg.exe"),
    )
    monkeypatch.setattr("candidate_mining.cli.export_clip", lambda *args, **kwargs: calls.append((args, kwargs)))

    _export_span(source, object(), Span(), app_config(tmp_path))

    assert calls == [((source, 1.0, 6.0, target), {"ffmpeg": tmp_path / "tools" / "ffmpeg" / "ffmpeg.exe"})]


def test_bbox_export_span_uses_store_and_context_bounds(monkeypatch, tmp_path) -> None:
    source = tmp_path / "source.mp4"
    target = tmp_path / "export_bbox.mp4"
    store = object()
    calls: list[tuple] = []
    monkeypatch.setattr("candidate_mining.cli.choose_export_path", lambda *_args, **_kwargs: target)
    monkeypatch.setattr("candidate_mining.cli.typer.echo", lambda _: None)
    monkeypatch.setattr(
        "candidate_mining.cli.resolve_media_tools",
        lambda _: SimpleNamespace(ffmpeg=tmp_path / "tools" / "ffmpeg" / "ffmpeg.exe"),
    )
    monkeypatch.setattr("candidate_mining.cli.export_clip_with_bboxes", lambda *args, **kwargs: calls.append((args, kwargs)))

    _export_span(source, store, Span(), app_config(tmp_path), annotated=True)

    assert calls == [
        ((source, 1.0, 6.0, target, store), {"ffmpeg": tmp_path / "tools" / "ffmpeg" / "ffmpeg.exe"})
    ]


def test_export_span_declined_overwrite_leaves_existing_target(monkeypatch, tmp_path) -> None:
    source = tmp_path / "source.mp4"
    target = tmp_path / "export.mp4"
    target.touch()
    monkeypatch.setattr("candidate_mining.cli.choose_export_path", lambda *_args, **_kwargs: target)
    monkeypatch.setattr("candidate_mining.cli.typer.echo", lambda _: None)
    monkeypatch.setattr("candidate_mining.cli.typer.confirm", lambda *_args, **_kwargs: False)
    monkeypatch.setattr(
        "candidate_mining.cli.export_clip",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("export should not run")),
    )

    _export_span(source, object(), Span(), app_config(tmp_path))
