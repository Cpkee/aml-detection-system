"""Top N by application score at opening (src/evaluation/opening_topk.py) on a hand-made cohort, no data needed:
the top N follow the score (ties: lower account id), launderers are counted by the final label and by type, chance
and lift match a hand count, the head start is opening to start, and only month 5 is scored."""
import numpy as np
import pandas as pd
import pytest

from evaluation import opening_topk as ot

# 10 accounts opened on day 100. Launderers: F1, F2 (fake, start day 190 / 200), W (witting, start day 400).
TRUTH = pd.DataFrame({
    "account_id": ["F1", "F2", "N1", "N2", "N3", "N4", "N5", "N6", "N7", "W"], "open_month": 5, "open_day": 100,
    "is_launderer": [1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    "profile": ["fake", "fake", None, None, None, None, None, None, None, "witting"],
    "start_day": [190.0, 200.0] + [np.nan] * 7 + [400.0]})
#                  F1   F2   N1   N2   N3   N4   N5   N6   N7   W
SCORES = pd.Series([9.0, 2.0, 8.0, 7.0, 1.0, 1.0, 0.5, 0.4, 0.3, 6.0], index=TRUTH["account_id"])


def test_counts_precision_chance_and_lift_match_a_hand_count():
    t = ot.table(SCORES, TRUTH, top_n=(2, 4, 10)).set_index("top_n")
    assert t.loc[2, "launderers"] == 1 and t.loc[2, "fake"] == 1 and t.loc[2, "witting"] == 0     # F1, N1
    assert t.loc[4, "launderers"] == 2 and t.loc[4, "witting"] == 1                              # + N2, W
    assert t.loc[4, "precision"] == pytest.approx(0.5) and t.loc[4, "reviews_per_launderer"] == pytest.approx(2.0)
    assert t.loc[4, "chance"] == pytest.approx(4 * 3 / 10) and t.loc[4, "lift"] == pytest.approx(2 / 1.2)
    assert t.loc[4, "share_caught"] == pytest.approx(2 / 3) and t.loc[4, "share_of_accounts"] == pytest.approx(0.4)
    assert t.loc[10, "launderers"] == 3 and t.loc[10, "lift"] == pytest.approx(1.0)
    assert t.loc[10, "p_chance"] == pytest.approx(1.0)              # the whole cohort: certain by chance


def test_head_start_is_opening_to_start():
    t = ot.table(SCORES, TRUTH, top_n=(2, 4)).set_index("top_n")
    assert t.loc[2, "median_days_opening_to_start"] == 90.0                      # F1: 190 - 100
    assert t.loc[4, "median_days_opening_to_start"] == pytest.approx(195.0)      # F1 90, W 300


def test_no_launderer_in_the_top_gives_zero_not_an_error():
    t = ot.table(-SCORES, TRUTH, top_n=(3,)).iloc[0]                             # N7, N6, N5
    assert t["launderers"] == 0 and t["precision"] == 0 and np.isnan(t["reviews_per_launderer"])
    assert np.isnan(t["median_days_opening_to_start"]) and t["p_chance"] == pytest.approx(1.0)


def test_ties_go_to_the_lower_account_id():
    flat = pd.Series(1.0, index=TRUTH["account_id"])
    t = ot.table(flat, TRUTH, top_n=(2,)).iloc[0]                                # F1, F2 by id
    assert t["launderers"] == 2 and t["fake"] == 2


def test_p_chance_is_small_for_a_perfect_pick():
    perfect = TRUTH.set_index("account_id")["is_launderer"].astype(float)
    t = ot.table(perfect, TRUTH, top_n=(3,)).iloc[0]
    assert t["launderers"] == 3 and t["p_chance"] == pytest.approx(1 / 120)      # 1 of C(10, 3) picks


def test_scores_must_cover_the_cohort_once_and_be_finite():
    with pytest.raises(ValueError, match="every cohort account"):
        ot.table(SCORES.iloc[:-1], TRUTH)
    with pytest.raises(ValueError, match="missing or infinite"):
        ot.table(SCORES.where(SCORES.index != "N1"), TRUTH, top_n=(2,))
    with pytest.raises(ValueError, match="more than the cohort"):
        ot.table(SCORES, TRUTH, top_n=(11,))


def test_only_month_5_is_scored():
    for months in ([6], [7], [5, 6], [4]):
        with pytest.raises(ValueError, match="month 5 only"):
            ot.run("data/does_not_matter", months)
    assert ot.TOP_N == (25, 50, 100, 200, 500)
