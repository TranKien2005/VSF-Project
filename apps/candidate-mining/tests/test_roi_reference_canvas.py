import numpy as np
from candidate_mining.frame_access import DecodedFrame, SourceMetadata
from candidate_mining.gui.app import RoiReferenceCanvas
from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest


def _frame() -> DecodedFrame:
    image = np.full((50, 100, 3), 200, dtype=np.uint8)
    metadata = SourceMetadata(fps=10.0, frame_count=10, width=100, height=50)
    return DecodedFrame(image, source_frame_index=0, timestamp_sec=0.0, metadata=metadata)


def test_roi_canvas_draws_a_visible_stroke_on_one_static_reference(qtbot, tmp_path) -> None:
    canvas = RoiReferenceCanvas()
    canvas.resize(200, 200)
    qtbot.addWidget(canvas)
    canvas.load_reference(tmp_path / "source.avi", _frame(), None)
    canvas.show()
    qtbot.waitExposed(canvas)

    before = canvas.grab().toImage()
    canvas.set_drawing(True)
    QTest.mousePress(canvas, Qt.LeftButton, pos=QPoint(20, 80))
    QTest.mouseMove(canvas, QPoint(100, 90))
    QTest.mouseRelease(canvas, Qt.LeftButton, pos=QPoint(180, 80))

    assert canvas.roi is not None
    assert canvas.roi.reference_frame_size_px == (100, 50)
    assert canvas.roi.reference_timestamp_sec == 0.0
    assert canvas.grab().toImage() != before


def test_clear_roi_ends_drawing_and_allows_an_immediate_new_stroke(qtbot, tmp_path) -> None:
    canvas = RoiReferenceCanvas()
    canvas.resize(200, 200)
    qtbot.addWidget(canvas)
    canvas.load_reference(tmp_path / "source.avi", _frame(), None)
    canvas.show()
    qtbot.waitExposed(canvas)

    drawing_states: list[bool] = []
    canvas.drawing_changed.connect(drawing_states.append)
    canvas.set_drawing(True)
    canvas.clear_roi()
    canvas.set_drawing(True)
    QTest.mousePress(canvas, Qt.LeftButton, pos=QPoint(20, 80))
    QTest.mouseMove(canvas, QPoint(100, 90))
    QTest.mouseRelease(canvas, Qt.LeftButton, pos=QPoint(180, 80))

    assert drawing_states == [True, False, True, False]
    assert canvas.roi is not None


def test_roi_canvas_ignores_pointer_events_in_letterbox_margin(qtbot, tmp_path) -> None:
    canvas = RoiReferenceCanvas()
    canvas.resize(200, 200)
    qtbot.addWidget(canvas)
    canvas.load_reference(tmp_path / "source.avi", _frame(), None)
    canvas.show()
    qtbot.waitExposed(canvas)

    canvas.set_drawing(True)
    QTest.mousePress(canvas, Qt.LeftButton, pos=QPoint(100, 20))
    QTest.mouseRelease(canvas, Qt.LeftButton, pos=QPoint(100, 20))

    assert canvas.roi is None


def test_flip_roi_flips_tracking_partition(qtbot, tmp_path) -> None:
    canvas = RoiReferenceCanvas()
    canvas.resize(200, 200)
    qtbot.addWidget(canvas)
    canvas.load_reference(tmp_path / "source.avi", _frame(), None)
    canvas.show()
    qtbot.waitExposed(canvas)

    canvas.set_drawing(True)
    QTest.mousePress(canvas, Qt.LeftButton, pos=QPoint(20, 80))
    QTest.mouseMove(canvas, QPoint(100, 90))
    QTest.mouseRelease(canvas, Qt.LeftButton, pos=QPoint(180, 80))

    initial_region = canvas.roi.tracking_region_normalized
    canvas.flip_roi()
    flipped_region = canvas.roi.tracking_region_normalized

    assert initial_region != flipped_region
