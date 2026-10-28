"""Phase 5 harness (src/evaluation/score.py) and the frozen-model trainer (src/models/train.py).

Hand-made cohorts, no data needed: flags are permanent and follow the weekly budget, closed accounts leave the pool,
the any-time policy spends exactly its total, and the measures match a hand count. Guards: test months need
--final-test and are scored once. On data/v1 (skipped without its store): a model trains, reloads and refuses to
score its own training months.
"""
import json
import os
import shutil

import numpy as np
import pandas as pd
import pytest

from evaluation import score as sc

# cohort of 6 accounts opened on day 0 (week w ends on day 7w + 6)
# F: fake, mule from opening; R: real customer starting day 20 (week 2); C: fake closed by the bank on day 16;
# N1-N3: normal
TRUTH = pd.DataFrame({
    "account_id": ["C", "F", "N1", "N2", "N3", "R"], "open_month": 5, "open_day": 0,
    "is_launderer": [1, 1, 0, 0, 0, 1], "profile": ["fake", "fake", None, None, None, "witting"],
    "start_day": [10.0, 90.0, np.nan, np.nan, np.nan, 20.0], "exit_day": [16.0, np.nan, np.nan, np.nan, np.nan, np.nan],
    "first_alert_day": [12.0, np.nan, 3.0, np.nan, np.nan, 22.0]})


def _scores():
    s = {"C": [0.1, 0.2, 0.3, 0.3], "F": [0.5, 0.6, 0.7, 0.7], "N1": [0.9, 0.1, 0.1, 0.1],
         "N2": [0.4, 0.8, 0.1, 0.1], "N3": [0.0, 0.0, 0.0, 0.0], "R": [0.0, 0.0, 0.95, 0.9]}
    return pd.DataFrame([{"account_id": a, "weeks_since_open": w, "score": v} for a, vs in s.items()
                         for w, v in enumerate(vs)])


def test_mule_label_fakes_from_opening_real_from_start():
    assert sc.mule_at(TRUTH, 0).tolist() == [True, True, False, False, False, False]
    assert sc.mule_at(TRUTH, 2).tolist() == [True, True, False, False, False, True]   # R starts day 20 <= 20


def test_closed_accounts_leave_the_pool():
    live = sc.open_rows(_scores(), TRUTH)
    assert sorted(live.loc[live.account_id == "C", "weeks_since_open"]) == [0, 1]     # closed day 16, in week 2


def test_permanent_flags_follow_the_budget():
    live = sc.open_rows(_scores(), TRUTH)
    f = sc.permanent_flags(live, {0: 1, 1: 1, 2: 2})
    # week 0: N1 (0.9); week 1: N2 (0.8); week 2: R (0.95) and F (0.7); never twice, none in week 3 (no budget)
    assert f.to_dict() == {"N1": 0, "N2": 1, "R": 2, "F": 2}


def test_anytime_spends_exactly_the_total():
    live = sc.open_rows(_scores(), TRUTH)
    f = sc.anytime_flags(live, 3)
    assert set(f.index) == {"R", "N1", "N2"} and f.to_dict() == {"R": 2, "N1": 0, "N2": 1}


def test_measures_by_hand():
    live = sc.open_rows(_scores(), TRUTH)
    flags = {"model": sc.permanent_flags(live, {0: 1, 1: 1, 2: 2}), "rules": sc.rules_flags(TRUTH, 3)}
    summary, weekly = sc.measures(TRUTH, flags, 3)
    m, r = summary.set_index("policy").loc["model"], summary.set_index("policy").loc["rules"]
    assert (m.mules, m.flagged, m.caught) == (3, 4, 2)               # F and R caught, C missed (closed first)
    assert (r.flagged, r.caught) == (3, 2)                           # alerts on N1 (week 0), C (week 1), R (week 3)
    assert np.isclose(m.precision, 0.5) and np.isclose(r.precision, 2 / 3)
    assert m.caught_fake == "1/2" and m.caught_witting == "1/1" and r.caught_witting == "1/1"
    assert m.median_days_from_start == np.median([20 - 90, 20 - 20])  # F flagged day 20, 70 days before its start
    assert m.flagged_before_start == 1
    assert weekly.loc[weekly.week == 2, "open_accounts"].item() == 5
    h = sc.head_to_head(TRUTH, flags["model"], flags["rules"], 3)
    assert (h["both"], h["model_only"], h["rules_only"], h["neither"]) == (1, 1, 1, 0)
    assert h["median_days_model_earlier_when_both"] == 22 - 20       # R: model day 20, rules day 22


def test_test_months_need_the_flag_and_are_scored_once(tmp_path, monkeypatch):
    monkeypatch.setattr(sc, "RESULTS", str(tmp_path))
    with pytest.raises(SystemExit):
        sc.run("data/v1_full", [6, 7], [26], "x")
    with pytest.raises(SystemExit):
        sc.run("data/v1_full", [5], [26], "x", final_test=True)
    lock = tmp_path / "v1_full" / "final_test"
    lock.mkdir(parents=True)
    (lock / "LOCK.json").write_text("{}")
    with pytest.raises(SystemExit):
        sc.run("data/v1_full", [6, 7], [26], "x", final_test=True)


def test_rules_budget_guards_test_months():
    from evaluation import budget
    with pytest.raises(ValueError):
        budget._months((6,))
    assert budget._months((6, 7), allow_test=True) == "6, 7"


DATA = "data/v1"
needs_store = pytest.mark.skipif(not os.path.exists(os.path.join(DATA, "features", "weekly.parquet")),
                                 reason="data/v1 feature store not built")


@needs_store
def test_model_trains_reloads_and_refuses_its_training_months(tmp_path):
    from models import train
    name = "pytest_tmp"
    try:
        m = train.train(DATA, name, report_root=str(tmp_path))
        assert m["n_inputs"] == 38 and m["inputs"] == train.INPUTS
        booster, app, man = train.load(DATA, name)
        assert booster.num_feature() == 38 and len(app["coef"]) == len(app["columns"])
        with pytest.raises(ValueError):
            sc.score_cohort(DATA, [4], (0, 2), name)
        s = sc.score_cohort(DATA, [5], (0, 2), name)
        assert s["score"].between(0, 1).all() and set(s["weeks_since_open"]) == {0, 1, 2}
    finally:
        shutil.rmtree(train.model_dir(DATA, name), ignore_errors=True)
