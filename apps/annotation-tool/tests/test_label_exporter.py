from __future__ import annotations

import json
from pathlib import Path

from annotation_tool.label_exporter import build_export_path, export_label_metadata
from annotation_tool.label_store import LabelCategory, OutputLabel


def test_build_export_path_xam_nhap():
    label = OutputLabel(
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
        lighting_condition="dem_khong_den",
    )
    export_dir = Path("/export")
    expected = (
        export_dir
        / "cam1"
        / "positive"
        / "xam_nhap_hoac_treo_rao_dem_khong_den"
        / "10m"
        / "xam_nhap_hoac_treo_rao_dem_khong_den_10m_label-1.mp4"
    )
    assert build_export_path(label, export_dir) == expected


def test_build_export_path_che_camera():
    label = OutputLabel(
        label_id="label-2",
        camera_name="cam2",
        video_name="vid2",
        source_id="src2",
        label=LabelCategory.CHE_CAMERA_NGAN.value,
        label_group="positive",
        event_start_time=10.0,
        event_end_time=20.0,
        subvideo_start_time=0.0,
        subvideo_end_time=50.0,
    )
    export_dir = Path("/export")
    expected = export_dir / "cam2" / "positive" / "che_camera_ngan" / "che_camera_ngan_label-2.mp4"
    assert build_export_path(label, export_dir) == expected


def test_build_export_path_normal():
    label = OutputLabel(
        label_id="label-3",
        camera_name="cam3",
        video_name="vid3",
        source_id="src3",
        label=LabelCategory.NORMAL.value,
        label_group="negative",
        event_start_time=10.0,
        event_end_time=20.0,
        subvideo_start_time=0.0,
        subvideo_end_time=50.0,
    )
    export_dir = Path("/export")
    expected = export_dir / "cam3" / "negative" / "normal" / "normal_label-3.mp4"
    assert build_export_path(label, export_dir) == expected


def test_export_label_metadata(tmp_path):
    label = OutputLabel(
        label_id="label-1",
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
    target = tmp_path / "normal_label-1.mp4"
    export_label_metadata(label, target)

    json_path = tmp_path / "normal_label-1.json"
    assert json_path.exists()

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    assert data["label_id"] == "label-1"
    assert data["schema_version"] == "output-label.v1"
