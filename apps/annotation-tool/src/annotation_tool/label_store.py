from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from uuid import uuid4


class LabelCategory(StrEnum):
    XAM_NHAP = "xam_nhap_hoac_treo_rao"
    LANG_VANG = "lang_vang_gan_hang_rao"
    CHE_CAMERA_NGAN = "che_camera_ngan"
    CHE_CAMERA_DAI = "che_camera_dai"
    CAMERA_RUNG_LAC = "camera_rung_lac"
    CAMERA_XOAY_LECH_HUONG = "camera_xoay_lech_huong"
    CHOI_SANG = "choi_sang"
    NUOC_MUA_LAM_NHIEU_HINH = "nuoc_mua_lam_nhieu_hinh"
    NORMAL = "normal"


PERSON_LABELS = {LabelCategory.XAM_NHAP.value, LabelCategory.LANG_VANG.value}
DISTANCE_VALUES = ("5m", "10m", "15m", "20m", "25m", "30m", "35m", "40m")
LIGHTING_VALUES = ("ngay", "dem_co_den", "dem_khong_den")
SCHEMA_VERSION = "output-label.v1"


@dataclass(frozen=True)
class OutputLabel:
    label_id: str
    camera_name: str
    video_name: str
    source_id: str
    label: str
    label_group: str
    event_start_time: float
    event_end_time: float
    subvideo_start_time: float
    subvideo_end_time: float
    distance_to_camera: str | None = None
    lighting_condition: str | None = None
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        data = asdict(self)
        data["schema_version"] = SCHEMA_VERSION
        return data

    @classmethod
    def from_dict(cls, raw: dict) -> OutputLabel:
        if raw.get("schema_version") != SCHEMA_VERSION:
            raise ValueError(f"Invalid schema version, expected {SCHEMA_VERSION}")
        
        data = {k: v for k, v in raw.items() if k != "schema_version"}
        return cls(**data)


def generate_label_id() -> str:
    return "label-" + uuid4().hex[:12]


def compute_subvideo_bounds(event_start: float, event_end: float, video_duration: float) -> tuple[float, float]:
    start = max(0.0, event_start - 30.0)
    end = min(video_duration, event_end + 30.0)
    return start, end


def label_group_for(label: str) -> str:
    return "negative" if label == LabelCategory.NORMAL.value else "positive"


def validate_label(label: OutputLabel) -> list[str]:
    errors = []
    if label.event_start_time >= label.event_end_time:
        errors.append("event_start_time must be less than event_end_time")
        
    if label.label == LabelCategory.LANG_VANG.value:
        if label.event_end_time - label.event_start_time < 300:
            errors.append("lang_vang requires event_end - event_start >= 300")
            
    if label.label in PERSON_LABELS:
        if not label.distance_to_camera:
            errors.append("distance_to_camera is required for person labels")
        elif label.distance_to_camera not in DISTANCE_VALUES:
            errors.append(f"distance_to_camera must be one of {DISTANCE_VALUES}")
            
        if not label.lighting_condition:
            errors.append("lighting_condition is required for person labels")
        elif label.lighting_condition not in LIGHTING_VALUES:
            errors.append(f"lighting_condition must be one of {LIGHTING_VALUES}")
            
    return errors


def label_directory(labels_dir: Path, label: OutputLabel) -> Path:
    return labels_dir / "cameras" / label.camera_name / "videos" / label.source_id / label.label_id


def save_label(labels_dir: Path, label: OutputLabel) -> Path:
    dir_path = label_directory(labels_dir, label)
    dir_path.mkdir(parents=True, exist_ok=True)
    
    file_path = dir_path / "label.json"
    tmp_path = dir_path / "label.json.tmp"
    
    data = label.to_dict()
    if not data["created_at"]:
        data["created_at"] = datetime.now(UTC).isoformat()
    data["updated_at"] = datetime.now(UTC).isoformat()
    
    # Re-instantiate to include updated timestamps in JSON
    updated_label = OutputLabel.from_dict(data)
    
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(updated_label.to_dict(), f, indent=2, ensure_ascii=False)
        
    tmp_path.replace(file_path)
    return file_path


def read_label(path: Path) -> OutputLabel:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return OutputLabel.from_dict(data)


def list_labels(labels_dir: Path) -> list[OutputLabel]:
    labels = []
    for path in labels_dir.rglob("label.json"):
        labels.append(read_label(path))
    return sorted(labels, key=lambda lbl: (lbl.camera_name, lbl.video_name, lbl.event_start_time))


def delete_label(label_dir: Path) -> None:
    if label_dir.exists():
        shutil.rmtree(label_dir)
