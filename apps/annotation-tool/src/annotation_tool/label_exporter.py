from __future__ import annotations

import json
import subprocess
from pathlib import Path

from candidate_mining.processed_store import read_source, resolve_source, source_path

from annotation_tool.label_store import PERSON_LABELS, OutputLabel, list_labels


def build_export_path(label: OutputLabel, export_dir: Path) -> Path:
    camera = label.camera_name or "standalone"

    if label.label in PERSON_LABELS:
        if label.lighting_condition:
            nhom_nhan = f"{label.label}_{label.lighting_condition}"
        else:
            nhom_nhan = label.label

        dist = label.distance_to_camera or ""
        file_stem = f"{nhom_nhan}_{dist}_{label.label_id}" if dist else f"{nhom_nhan}_{label.label_id}"

        if dist:
            return export_dir / camera / label.label_group / nhom_nhan / dist / f"{file_stem}.mp4"
        return export_dir / camera / label.label_group / nhom_nhan / f"{file_stem}.mp4"

    nhom_nhan = label.label
    file_stem = f"{nhom_nhan}_{label.label_id}"
    return export_dir / camera / label.label_group / nhom_nhan / f"{file_stem}.mp4"


def export_subvideo(
    source_path: Path, start_sec: float, end_sec: float, target: Path, *, ffmpeg: Path
) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp_target = target.with_suffix(".tmp.mp4")

    duration = end_sec - start_sec

    cmd = [
        str(ffmpeg),
        "-y",
        "-ss",
        str(start_sec),
        "-i",
        str(source_path),
        "-t",
        str(duration),
        "-map",
        "0:v:0",
        "-map",
        "0:a?",
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        str(tmp_target),
    ]

    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    tmp_target.replace(target)


def export_label_metadata(label: OutputLabel, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    json_path = target.with_suffix(".json")
    tmp_json_path = json_path.with_suffix(".tmp.json")

    with open(tmp_json_path, "w", encoding="utf-8") as f:
        json.dump(label.to_dict(), f, indent=2, ensure_ascii=False)

    tmp_json_path.replace(json_path)


def _find_and_resolve_source(processed_dir: Path, label: OutputLabel) -> Path:
    src_json = source_path(processed_dir, label.source_id, camera_id=label.camera_name if label.camera_name else None)
    if not src_json.exists():
        src_json = source_path(processed_dir, label.source_id, camera_id=None)
    if not src_json.exists():
        raise FileNotFoundError(f"Source metadata json missing for source {label.source_id}")
    record = read_source(src_json)
    return resolve_source(record)


def export_all(
    labels_dir: Path,
    processed_dir: Path,
    export_dir: Path,
    *,
    ffmpeg: Path,
    on_progress: object | None = None,
) -> tuple[int, list[str]]:
    labels = list_labels(labels_dir)
    total = len(labels)
    success_count = 0
    error_messages: list[str] = []

    for i, label in enumerate(labels, start=1):
        try:
            real_source_path = _find_and_resolve_source(processed_dir, label)
            target_path = build_export_path(label, export_dir)

            export_subvideo(
                real_source_path,
                label.subvideo_start_time,
                label.subvideo_end_time,
                target_path,
                ffmpeg=ffmpeg,
            )

            export_label_metadata(label, target_path)

            success_count += 1
        except Exception as e:
            error_messages.append(f"Failed to export {label.label_id}: {e}")

        if callable(on_progress):
            on_progress(i, total)

    return success_count, error_messages
