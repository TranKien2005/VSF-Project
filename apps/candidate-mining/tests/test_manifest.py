import csv

from candidate_mining.manifest import write_manifest
from candidate_mining.models import MANIFEST_FIELDS, CandidateSample


def test_manifest_uses_contract_header_and_blanks_optional_background_fields(tmp_path) -> None:
    sample = CandidateSample(
        sample_id="source_background_001",
        source_id="source",
        source_path="D:/videos/source.mp4",
        camera_id="unknown",
        clip_path="data/review_queue/random_background/source_background_001.mp4",
        clip_start_sec=30.0,
        clip_end_sec=90.0,
        categories=("random_background",),
        candidate_start_sec=None,
        candidate_end_sec=None,
        selection_source="random_background",
    )

    target = write_manifest([sample], tmp_path)

    with target.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
        assert tuple(rows[0]) == MANIFEST_FIELDS
        assert rows[0]["candidate_start_sec"] == ""
        assert rows[0]["categories"] == "random_background"
        assert rows[0]["anomaly_types"] == ""
        assert rows[0]["person_episode_ids"] == ""
