"""Methods comparison helpers on small made-up data (no data folder needed)."""
import numpy as np
import pandas as pd

from evaluation import hybrid
from models import comparison as cmp
from models import feature_lab as fl


def cohort():
    """6 accounts open for weeks 0-2; scores rank f > e > d > c > b > a every week."""
    ids = list("abcdef")
    v = pd.DataFrame([(a, w, i / 10) for w in range(3) for i, a in enumerate(ids)],
                     columns=["account_id", "weeks_since_open", "score"])
    return v


def test_share_one_is_the_model_alone():
    v, k = cohort(), {0: 1, 1: 2, 2: 1}
    alerts = pd.DataFrame({"week": [0, 1, 1, 2], "account_id": ["a", "b", "c", "a"]})
    got = hybrid.split_flags(v, alerts, k, 1.0)
    pd.testing.assert_series_equal(got.sort_index(), fl.first_flag_weeks(v, k).sort_index())


def test_share_zero_is_the_rules_first_alerts():
    v, k = cohort(), {0: 1, 1: 2, 2: 1}
    alerts = pd.DataFrame({"week": [0, 1, 1, 2], "account_id": ["a", "b", "c", "d"]})
    got = hybrid.split_flags(v, alerts, k, 0.0)
    assert got.sort_index().to_dict() == {"a": 0, "b": 1, "c": 1, "d": 2}


def test_unused_rule_slot_goes_to_the_model():
    v, k = cohort(), {0: 1, 1: 0, 2: 1}
    alerts = pd.DataFrame({"week": [0, 2], "account_id": ["a", "a"]})   # second alert on an account already flagged
    got = hybrid.split_flags(v, alerts, k, 0.0)
    assert got.to_dict() == {"a": 0, "f": 2}


def test_half_share_splits_the_budget():
    v, k = cohort(), {0: 3}
    alerts = pd.DataFrame({"week": [0, 0, 0], "account_id": ["a", "b", "c"]})
    got = hybrid.split_flags(v, alerts, k, 0.5)
    assert set(got.index) == {"a", "f", "e"}                            # floor(3 x 0.5) = 1 rule slot, 2 model


def mules():
    """b, d, f are mules from week 1 in two cohorts of three accounts."""
    return [pd.DataFrame([(a, w, m) for a in acc for w in (1, 2)], columns=["account_id", "weeks_since_open",
                                                                            "open_month"])
            for acc, m in ((["b", "d"], 2), (["f"], 3))]


def test_paired_test_of_a_method_with_itself_is_zero():
    first = pd.Series({"b": 1.0, "f": 2.0})
    r = cmp.paired_test(first, first, mules())
    assert r["gain"] == 0 and r["lo"] == 0 and r["hi"] == 0 and r["cohorts_ahead"] == 0


def test_paired_test_sees_a_clear_gain():
    better, worse = pd.Series({"b": 1.0, "d": 1.0, "f": 1.0}), pd.Series(dtype=float)
    r = cmp.paired_test(better, worse, mules())
    assert r["gain"] == 1.0 and r["lo"] == 1.0 and r["cohorts_ahead"] == 2


def test_holm_steps_down():
    p = pd.Series({"x": 0.001, "y": 0.02, "z": 0.04})
    assert cmp.holm(p).to_dict() == {"x": True, "y": True, "z": True}   # 0.05/3, 0.05/2, 0.05/1
    p = pd.Series({"x": 0.001, "y": 0.03, "z": 0.04})
    assert cmp.holm(p).to_dict() == {"x": True, "y": False, "z": False}


def test_budget_measures_counts():
    m = pd.concat(mules())
    first = pd.Series({"b": 1.0, "a": 0.0, "f": 2.0})
    start = pd.Series({"b": 1.0, "d": 1.0, "f": 1.0})
    prof = pd.Series({"b": "fake", "d": "witting", "f": "fake"})
    r = cmp.budget_measures(first, m, start, prof)
    assert (r["caught"], r["mules"], r["flags"]) == (2, 3, 3)
    assert np.isclose(r["recall_w26"], 2 / 3) and np.isclose(r["precision"], 2 / 3)
    assert r["median_weeks_from_start"] == 0.5 and r["rules_budget_fake"] == "2/2"
