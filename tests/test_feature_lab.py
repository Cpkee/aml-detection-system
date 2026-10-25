"""The feature lab's measures (src/models/feature_lab.py) on a small hand-made validation table, no data needed."""
import numpy as np
import pandas as pd

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
