from candidate_mining.models import ClipWindow
from candidate_mining.sampling import select_background_windows


def test_background_sampling_is_reproducible_and_respects_exclusions() -> None:
    exclusion = [ClipWindow(40.0, 80.0, "sufficient")]
    first = select_background_windows(180.0, 2, 20.0, exclusion, 10.0, seed=7)
    second = select_background_windows(180.0, 2, 20.0, exclusion, 10.0, seed=7)

    assert first == second
    assert len(first) == 2
    for window in first:
        assert not (window.start_sec < 90.0 and 30.0 < window.end_sec)


def test_background_sampling_returns_shortfall_without_duplicates() -> None:
    windows = select_background_windows(30.0, 3, 20.0, [], 0.0, seed=1)

    assert len(windows) == 1
