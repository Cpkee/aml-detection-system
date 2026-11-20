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


# ---------------------------------------------------------------- group B (amendment 16 Nov 2026)
def test_draws_start_with_defaults_and_repeat():
    for learner in ("xgboost", "catboost"):
        d = cmp.draws(learner)
        assert len(d) == 40 and d[0] == {} and d == cmp.draws(learner)       # seeded: the same 40 trials every run
        assert all(set(x) == set(cmp.spaces()[learner]) for x in d[1:])


def test_draws_stay_inside_the_registered_ranges():
    for x in cmp.draws("xgboost")[1:]:
        assert 0.01 <= x["learning_rate"] <= 0.3 and x["n_estimators"] in cmp.TREES
        assert x["max_leaves"] in (15, 23, 31, 47, 63, 95, 127, 191, 255)
        assert 0.5 <= x["subsample"] <= 1 and 0.5 <= x["colsample_bytree"] <= 1
    for x in cmp.draws("catboost")[1:]:
        assert x["depth"] in (4, 5, 6, 7, 8) and x["iterations"] in cmp.TREES and 0.5 <= x["rsm"] <= 1


def test_balanced_row_weights_equal_lightgbm_class_weights():
    from sklearn.utils.class_weight import compute_sample_weight
    y = np.array([0] * 98 + [1] * 2)
    w = compute_sample_weight("balanced", y)
    assert np.isclose(w[0], 100 / (2 * 98)) and np.isclose(w[-1], 100 / (2 * 2))   # n / (2 x class count)


def toy():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(400, 2))
    d = pd.DataFrame({"a": x[:, 0], "b": x[:, 1], "mule_by_day": (x[:, 0] > 1.5).astype(int)})
    return d.iloc[:300], d.iloc[300:]


def test_boosted_averages_seeds_and_ranks_the_signal():
    train, valid = toy()
    for learner, params in (("xgboost", {"n_estimators": 100, "max_leaves": 15}), ("catboost", {"iterations": 100,
                                                                                                 "depth": 4})):
        fit = cmp.boosted(learner, params, seeds=(1, 2), cols=["a", "b"])
        s = fit(train, valid)
        one = [cmp.boosted(learner, params, seeds=(k,), cols=["a", "b"])(train, valid) for k in (1, 2)]
        assert np.allclose(s, (one[0] + one[1]) / 2)
        from sklearn.metrics import roc_auc_score
        assert roc_auc_score(valid["mule_by_day"], s) > 0.9


def test_best_trial_breaks_ties_by_lower_trial():
    t = pd.DataFrame({"trial": [2, 0, 1], "weekly_recall": [0.4, 0.3, 0.4]})
    assert cmp.best_trial(t)["trial"] == 1


def test_interim_tests_judge_every_rival_against_ref(tmp_path, monkeypatch):
    monkeypatch.setattr(cmp, "REPORT_ROOT", str(tmp_path))
    rows = [("b", 1.0, "ref"), ("f", 2.0, "ref"),                       # ref catches b, then f
            ("b", 1.0, "same"), ("f", 2.0, "same"),                     # a copy of ref
            ("b", 1.0, "better"), ("d", 1.0, "better"), ("f", 1.0, "better")]
    flags = pd.DataFrame(rows, columns=["account_id", "week", "method"]).assign(fold=1)
    (tmp_path / "run").mkdir()
    flags.to_csv(tmp_path / "run" / "first_flags.csv", index=False)
    r = cmp.interim_tests("data/run", mules()).set_index("method")
    assert list(r.index) == ["better", "same"]                          # ref is never its own rival
    assert r.loc["same", "gain"] == 0 and not r.loc["same", "wins_on_folds"]
    assert r.loc["better", "gain"] > cmp.NOISE and r.loc["better", "cohorts_ahead"] == 2
    assert r.loc["better", "wins_on_folds"] == r.loc["better", "holm_pass"]
