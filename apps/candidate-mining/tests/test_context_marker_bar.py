from candidate_mining.gui.app import ContextMarkerBar
from PySide6.QtGui import QColor


def _red_pixel_count(image) -> int:  # type: ignore[no-untyped-def]
    total = 0
    for y in range(image.height()):
        for x in range(image.width()):
            color = QColor(image.pixel(x, y))
            if color.red() > 210 and color.green() < 120 and color.blue() < 120:
                total += 1
    return total


def test_marker_bar_has_visible_neutral_state(qtbot) -> None:
    bar = ContextMarkerBar()
    bar.resize(600, 40)
    qtbot.addWidget(bar)
    bar.show()
    qtbot.waitExposed(bar)

    assert bar.objectName() == "timelineSlider"
    assert bar.height() == 40


def test_marker_bar_paints_start_and_end_for_full_source_duration(qtbot) -> None:
    bar = ContextMarkerBar()
    bar.resize(600, 40)
    qtbot.addWidget(bar)
    bar.show()
    qtbot.waitExposed(bar)

    bar.set_context(2_000, 6_000, 10_000)
    image = bar.grab().toImage()
    positions = bar.marker_x_positions()

    assert positions == (121, 360)
    scale_x = image.width() / bar.width()
    scale_y = image.height() / bar.height()
    assert _red_pixel_count(image) > 100
    for x in positions:
        px = int(round(x * scale_x))
        assert any(QColor(image.pixel(px, int(round(y * scale_y)))).red() > 210 for y in range(bar.height()))


def test_marker_bar_preserves_context_when_duration_arrives_later(qtbot) -> None:
    bar = ContextMarkerBar()
    bar.resize(600, 40)
    qtbot.addWidget(bar)
    bar.show()
    qtbot.waitExposed(bar)

    bar.set_context(2_000, 6_000, 0)
    pending_positions = bar.marker_x_positions()
    bar.set_context(2_000, 6_000, 10_000)

    assert pending_positions == (201, 598)
    assert bar.marker_x_positions() == (121, 360)
    assert bar.has_context


def test_video_workspace_timeline_formatting_and_autoplay(qtbot) -> None:
    from candidate_mining.gui.app import VideoWorkspace

    workspace = VideoWorkspace(editable=False)
    qtbot.addWidget(workspace)

    assert workspace._format_time(1234) == "00:01.2"
    assert workspace._format_time(65432) == "01:05.4"

    workspace.source_fps = 25.0
    workspace.source_width = 1920
    workspace.source_height = 1080
    workspace.source = "mock_source.mp4"

    workspace.set_review_context(
        detections=[],
        source_fps=25.0,
        frame_width=1920,
        frame_height=1080,
        start_sec=2.0,
        end_sec=6.0,
        autoplay=True,
    )

    assert workspace._context_start_ms == 2000
    assert workspace._context_end_ms == 6000
    assert workspace._should_autoplay_context is True
    assert workspace.timeline.has_context
    assert "[Subvideo: 00:02.0 – 00:06.0 (4.0s)]" in workspace.info.text()

