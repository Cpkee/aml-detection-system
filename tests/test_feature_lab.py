"""The feature lab's measures (src/models/feature_lab.py) on a small hand-made validation table, no data needed;
and the adopted features in lgbm_baseline.load_table on data/v1 (skipped without its feature store)."""
import os

import numpy as np
import pandas as pd
import pytest

from models import feature_lab as lab
from models.lgbm_baseline import by_week


def _valid():
    """2 weeks x 200 accounts (top 1% = 2 per week). Mules: M0 from week 0, M1 from week 1, M2 never flagged."""
    ids = ["M0", "M1", "M2"] + [f"N{i}" for i in range(197)]
    rows = []
    for w in (0, 1):
        for i, a in enumerate(ids):
            mule = a == "M0" or a == "M2" or (a == "M1" and w == 1)
            score = {"M0": 0.9, "M1": 0.8 if w == 1 else 0.1, "M2": 0.05}.get(a, 0.5 - i / 1000)
            rows.append({"account_id": a, "weeks_since_open": w, "mule_by_day": int(mule), "score": score})
    return pd.DataFrame(rows)


def test_weekly_recall_by_hand():
    d = _valid()
    v = lab.weekly_top1(d, d["score"].to_numpy())
    assert v.groupby("weeks_since_open")["flag"].sum().tolist() == [2, 2]
    # week 0: mules M0, M2 -> M0 flagged (1/2); week 1: mules M0, M1, M2 -> M0, M1 flagged (2/3)
    assert np.isclose(lab.weekly_recall(v), (1 / 2 + 2 / 3) / 2)
    # same number as lgbm_baseline.by_week, which notebook 06 reports
    assert np.isclose(lab.pooled_weekly_recall(d), by_week(d.assign(view="v"))["recall_top_1pct"].mean())


def test_caught_2wk_by_hand():
    d = _valid()
    v = lab.weekly_top1(d, d["score"].to_numpy())
    start = pd.Series({"M0": 0, "M1": 1, "M2": 0, "X9": 3})     # X9 is not in this validation month
    assert np.isclose(lab.caught_2wk(v, start), 2 / 3)


def test_verdict():
    assert lab.verdict(pd.Series([0.05, 0.03, 0.04]), 0.02) == "better"
    assert lab.verdict(pd.Series([0.05, -0.01, 0.04]), 0.02) == "no clear change"
    assert lab.verdict(pd.Series([0.01, 0.01, 0.01]), 0.02) == "no clear change"
    assert lab.verdict(pd.Series([-0.05, -0.01, -0.04]), 0.02) == "worse"


DATA = "data/v1"
needs_store = pytest.mark.skipif(not os.path.exists(os.path.join(DATA, "features", "weekly.parquet")),
                                 reason="data/v1 feature store not built")


@needs_store
def test_load_table_adds_adopted_features():
    from features import candidates
    from models.lgbm_baseline import load_table
    plain, _ = load_table(DATA, (0,), (0, 26))
    with_adopted, _ = load_table(DATA, (0,), (0, 26), adopted=True)
    assert set(candidates.ADOPTED) <= set(with_adopted.columns) and not set(candidates.ADOPTED) & set(plain.columns)
    pd.testing.assert_frame_equal(with_adopted[plain.columns], plain)          # nothing else changes
    with pytest.raises(ValueError):
        load_table(DATA, (0,), (1, 26), adopted=True)


def test_phase_recall_by_hand():
    d = _valid()
    v = lab.weekly_top1(d, d["score"].to_numpy())
    # flags: week 0 M0 + top normal; week 1 M0 + M1. Mule rows: M0 w0, w1; M1 w1; M2 w0, w1 (never flagged)
    r = lab.phase_recall(v, pd.Series({"M0": 1, "M1": 1, "M2": 0}))
    assert r["pre_start_recall"] == 1.0                      # M0 at week 0, before its start
    assert np.isclose(r["start_recall"], 2 / 4)              # M0 w1, M1 w1 flagged; M2 w0, w1 not
    assert np.isnan(r["later_recall"])


def test_permanent_flags_by_hand():
    d = _valid()
    v = d.assign(flag=False)
    first = lab.first_flag_weeks(v)
    # week 0: M0 and N0 (best normal); week 1 draws from the rest: M1 and N1 (M0 is not flagged twice)
    assert first.to_dict() == {"M0": 0, "N0": 0, "M1": 1, "N1": 1}
    assert np.isclose(lab.first_caught_2wk(v, pd.Series({"M0": 0, "M1": 1, "M2": 0})), 2 / 3)


def test_frozen_inputs_are_the_lab_baseline():
    """The frozen feature list (28 Oct 2026): 28 store features + 8 roll4 + weeks_since_open + app_score = 38."""
    from features import candidates
    from features.weekly import FEATURES
    from models.frozen_importance import INPUTS
    assert len(INPUTS) == len(set(INPUTS)) == 38
    assert INPUTS == list(FEATURES) + candidates.ADOPTED + ["weeks_since_open", "app_score"]
    assert candidates.ADOPTED_GROUP == "roll4"


# ---------------------------------------------------------------- proposal 28 Oct 2026: rules' budget, catch, noise
def test_permanent_flags_with_a_budget_by_hand():
    d = _valid()
    first = lab.first_flag_weeks(d, {0: 1, 1: 2})          # 1 flag in week 0, 2 in week 1; week 2 not in k
    assert first.to_dict() == {"M0": 0, "M1": 1, "N0": 1}
    assert lab.first_flag_weeks(d, {}).empty                # no budget, no flags
    assert lab.pct_budget(d, 0.01) == {0: 2, 1: 2} and lab.pct_budget(d, 0.0001) == {0: 1, 1: 1}


def test_catch_curve_by_hand():
    first = pd.Series({"M0": 0, "M1": 3})
    mules = pd.DataFrame({"account_id": ["M0", "M1", "M2", "M0", "M1", "M2"],
                          "weeks_since_open": [0, 0, 0, 1, 1, 1]})
    curve = lab.catch_curve(first, mules)
    assert np.isclose(curve[0], 1 / 3) and np.isclose(curve[1], 1 / 3)   # M1 flagged only at week 3: not yet
    assert np.isclose(lab.catch_mean(first, mules), 1 / 3)
    assert lab.catch_boot_sd(first, mules) >= 0


def test_placebo_keeps_each_week_and_breaks_accounts():
    from models.feature_lab import PLACEBO_COLS
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"account_id": np.repeat([f"A{i}" for i in range(50)], 3),
                       "weeks_since_open": np.tile([0, 1, 2], 50)})
    for c in PLACEBO_COLS:
        df[c] = rng.normal(size=len(df)).astype("float32")
    out, cols = lab.add_placebo(df, 1)
    assert len(cols) == len(PLACEBO_COLS)
    for c in PLACEBO_COLS:
        for w in (0, 1, 2):                                  # same values inside each week, in another order
            a, b = df.loc[df.weeks_since_open == w, c], out.loc[out.weeks_since_open == w, f"placebo1_{c}"]
            assert np.allclose(np.sort(a), np.sort(b)) and not np.allclose(a, b)


def test_verdict_without_a_noise_level():
    assert lab.verdict(pd.Series([0.05, 0.03, 0.04]), None) == "no noise level yet"


def test_ledger_new_columns_keep_old_lines(tmp_path, monkeypatch):
    path = tmp_path / "ledger.csv"
    path.write_text('date,trial,x\n2026-10-26,"a, b",0.57046485261439\n')
    monkeypatch.setattr(lab, "LEDGER", str(path))
    lab.append_ledger(pd.DataFrame({"date": ["2026-10-28"], "trial": ["t"], "x": [1.0], "y": [2.0]}))
    lines = path.read_text().splitlines()
    assert lines[0] == "date,trial,x,y"
    assert lines[1] == '2026-10-26,"a, b",0.57046485261439,'           # old line untouched, one empty field added
    assert lines[2] == "2026-10-28,t,1.0,2.0"
