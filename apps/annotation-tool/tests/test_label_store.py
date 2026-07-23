from __future__ import annotations

from annotation_tool.label_store import (
    LabelCategory,
    OutputLabel,
    compute_subvideo_bounds,
    delete_label,
    generate_label_id,
    label_group_for,
    list_labels,
    read_label,
    save_label,
    validate_label,
)


def test_generate_label_id():
    label_id = generate_label_id()
    assert label_id.startswith("label-")
    assert len(label_id) == 18  # 'label-' (6) + 12 hex chars


def test_compute_subvideo_bounds():
    assert compute_subvideo_bounds(40.0, 50.0, 100.0) == (10.0, 80.0)
    assert compute_subvideo_bounds(10.0, 50.0, 100.0) == (0.0, 80.0)
    assert compute_subvideo_bounds(90.0, 95.0, 100.0) == (60.0, 100.0)


def test_label_group_for():
    assert label_group_for(LabelCategory.NORMAL.value) == "negative"
    assert label_group_for(LabelCategory.XAM_NHAP.value) == "positive"
    assert label_group_for(LabelCategory.CHOI_SANG.value) == "positive"


def test_validate_label():
    valid_label = OutputLabel(
        label_id="label-1",
        camera_name="cam1",
        video_name="vid1",
        source_id="src1",
        label=LabelCategory.XAM_NHAP.value,
        label_group="positive",
        event_start_time=10.0,
        event_end_time=20.0,
        subvideo_start_time=0.0,
        subvideo_end_time=50.0,
        distance_to_camera="10m",
        lighting_condition="ngay",
    )
    assert not validate_label(valid_label)
    
    invalid_times = OutputLabel(
        label_id="label-2",
        camera_name="cam1",
        video_name="vid1",
        source_id="src1",
        label=LabelCategory.NORMAL.value,
        label_group="negative",
        event_start_time=20.0,
        event_end_time=10.0,
        subvideo_start_time=0.0,
        subvideo_end_time=50.0,
    )
    errors = validate_label(invalid_times)
    assert "event_start_time must be less than event_end_time" in errors[0]
    
    lang_vang_short = OutputLabel(
        label_id="label-3",
        camera_name="cam1",
        video_name="vid1",
        source_id="src1",
        label=LabelCategory.LANG_VANG.value,
        label_group="positive",
        event_start_time=10.0,
        event_end_time=100.0,
        subvideo_start_time=0.0,
        subvideo_end_time=130.0,
        distance_to_camera="10m",
        lighting_condition="ngay",
    )
    errors = validate_label(lang_vang_short)
    assert "lang_vang requires event_end - event_start >= 300" in errors[0]
    
    missing_person_meta = OutputLabel(
        label_id="label-4",
        camera_name="cam1",
        video_name="vid1",
        source_id="src1",
        label=LabelCategory.XAM_NHAP.value,
        label_group="positive",
        event_start_time=10.0,
        event_end_time=20.0,
        subvideo_start_time=0.0,
        subvideo_end_time=50.0,
    )
    errors = validate_label(missing_person_meta)
    assert any("distance_to_camera is required" in e for e in errors)
    assert any("lighting_condition is required" in e for e in errors)


def test_save_read_delete(tmp_path):
    labels_dir = tmp_path / "labels"
    label = OutputLabel(
        label_id="label-1234567890ab",
        camera_name="cam1",
        video_name="vid1",
        source_id="src1",
        label=LabelCategory.NORMAL.value,
        label_group="negative",
        event_start_time=10.0,
        event_end_time=20.0,
        subvideo_start_time=0.0,
        subvideo_end_time=50.0,
    )
    
    saved_path = save_label(labels_dir, label)
    assert saved_path.exists()
    
    read_lbl = read_label(saved_path)
    assert read_lbl.label_id == label.label_id
    assert read_lbl.created_at
    assert read_lbl.updated_at
    
    delete_label(saved_path.parent)
    assert not saved_path.exists()


def test_list_labels(tmp_path):
    labels_dir = tmp_path / "labels"
    label1 = OutputLabel(
        label_id="label-1", camera_name="B", video_name="V", source_id="S",
        label=LabelCategory.NORMAL.value, label_group="negative",
        event_start_time=20.0, event_end_time=30.0, subvideo_start_time=0.0, subvideo_end_time=60.0
    )
    label2 = OutputLabel(
        label_id="label-2", camera_name="A", video_name="V", source_id="S",
        label=LabelCategory.NORMAL.value, label_group="negative",
        event_start_time=10.0, event_end_time=20.0, subvideo_start_time=0.0, subvideo_end_time=50.0
    )
    label3 = OutputLabel(
        label_id="label-3", camera_name="B", video_name="V", source_id="S",
        label=LabelCategory.NORMAL.value, label_group="negative",
        event_start_time=10.0, event_end_time=20.0, subvideo_start_time=0.0, subvideo_end_time=50.0
    )
    
    save_label(labels_dir, label1)
    save_label(labels_dir, label2)
    save_label(labels_dir, label3)
    
    labels = list_labels(labels_dir)
    assert len(labels) == 3
    assert labels[0].camera_name == "A"
    assert labels[1].camera_name == "B"
    assert labels[1].event_start_time == 10.0
    assert labels[2].camera_name == "B"
    assert labels[2].event_start_time == 20.0
