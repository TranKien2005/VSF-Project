from candidate_mining.processing_progress import estimate_eta, estimated_sample_count


def test_estimated_sample_count_matches_sampling_interval() -> None:
    assert estimated_sample_count(300.0, 30.0, 5.0) == 50
    assert estimated_sample_count(301.0, 30.0, 5.0) == 51
    assert estimated_sample_count(0.0, 30.0, 5.0) is None


def test_eta_waits_for_two_completed_samples() -> None:
    assert estimate_eta(1.0, 1, 10) is None
    assert estimate_eta(2.0, 2, 10) == 8.0
    assert estimate_eta(2.0, 10, 10) == 0.0
    assert estimate_eta(2.0, 2, None) is None
