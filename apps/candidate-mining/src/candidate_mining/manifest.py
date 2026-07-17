"""Candidate manifest serialization."""

from __future__ import annotations

import csv
from pathlib import Path

from .models import MANIFEST_FIELDS, CandidateSample


def find_manifest_row(manifest_path: Path, sample_id: str) -> dict[str, str]:
    try:
        with manifest_path.open(newline="", encoding="utf-8") as handle:
            matches = [row for row in csv.DictReader(handle) if row.get("sample_id") == sample_id]
    except FileNotFoundError as error:
        raise FileNotFoundError(f"Candidate manifest is missing: {manifest_path}") from error
    if not matches:
        raise ValueError(f"sample_id was not found in candidate manifest: {sample_id}")
    if len(matches) > 1:
        raise ValueError(f"sample_id is duplicated in candidate manifest: {sample_id}")
    return matches[0]


def write_manifest(samples: list[CandidateSample], directory: Path, filename: str = "candidate_events.csv") -> Path:
    sample_ids = [sample.sample_id for sample in samples]
    if len(sample_ids) != len(set(sample_ids)):
        raise ValueError("Manifest contains duplicate sample_id values")
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / filename
    temporary = target.with_suffix(f"{target.suffix}.tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        for sample in sorted(samples, key=lambda item: (item.clip_start_sec, item.sample_id)):
            writer.writerow(sample.to_manifest_row())
    temporary.replace(target)
    return target
