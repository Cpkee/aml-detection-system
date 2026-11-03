"""Carry-forward flagging policy (src/evaluation/policy.py) and the drift helpers (src/models/drift.py).

Hand-made inputs only, no data needed: the policy never spends more than the rules' cumulative alerts, carries unused
budget forward, respects the weekly cap, breaks ties by account id as score.permanent_flags does, and the
pre-registered choice and verdict follow their rules.
"""
import numpy as np
import pandas as pd

from evaluation import policy as pol
from evaluation import score as sc
from models import drift


def _scores(table: dict) -> pd.DataFrame:
    return pd.DataFrame([{"account_id": a, "weeks_since_open": w, "score": v} for a, vs in table.items()
                         for w, v in enumerate(vs) if v is not None])


def test_threshold_and_cumulative_budget():
    s = _scores({"A": [0.9, 0.9, 0.9, 0.9], "B": [0.2, 0.8, 0.6, 0.6], "C": [0.1, 0.1, 0.7, 0.7],
                 "D": [0.0, 0.0, 0.55, 0.55]})
    f = pol.carry_forward_flags(s, {0: 1, 1: 0, 2: 2, 3: 1}, tau=0.5)
    # week 0: A; week 1: no budget left (1 used of 1); week 2: room 2 -> C (0.7), B (0.6); week 3: room 1 -> D
    assert f.to_dict() == {"A": 0, "C": 2, "B": 2, "D": 3}


def test_unused_budget_carries_forward_and_cap():
    s = _scores({"A": [0.3, 0.3, 0.99], "B": [0.2, 0.2, 0.98], "C": [0.1, 0.1, 0.97], "D": [0.0, 0.0, 0.96]})
    k = {0: 1, 1: 1, 2: 1}
    assert pol.carry_forward_flags(s, k, tau=0.9).to_dict() == {"A": 2, "B": 2, "C": 2}       # 3 alerts so far
    assert pol.carry_forward_flags(s, k, tau=0.9, cap=2).to_dict() == {"A": 2, "B": 2}        # 2 x week 2's 1
    assert sc.permanent_flags(s, k).to_dict() == {"A": 0, "B": 1, "C": 2}                     # weekly top-k
    assert pol.carry_forward_flags(s, k, tau=0.0).to_dict() == sc.permanent_flags(s, k).to_dict()


def test_cap_blocks_weeks_without_rule_alerts():
    s = _scores({"A": [0.9, 0.9]})
    assert pol.carry_forward_flags(s, {0: 0, 1: 1}, tau=0.5, cap=2).to_dict() == {"A": 1}


def test_ties_by_account_id_and_flags_are_permanent():
    s = _scores({"X": [0.9, 0.95], "W": [0.9, 0.1]})
    assert pol.carry_forward_flags(s, {0: 1, 1: 1}, tau=0.5).to_dict() == {"W": 0, "X": 1}


def test_never_ahead_of_the_rules():
    rng = np.random.default_rng(0)
    s = pd.DataFrame({"account_id": np.repeat([f"a{i:03d}" for i in range(200)], 10),
                      "weeks_since_open": np.tile(range(10), 200), "score": rng.random(2000)})
    k = {w: int(n) for w, n in enumerate(rng.integers(0, 6, 10))}
    for tau in (0.0, 0.9, 0.99, 0.999):
        for cap in (None, 2):
            f = pol.carry_forward_flags(s, k, tau, cap)
            assert pol.within_budget(f, k) and f.index.is_unique and len(f) <= sum(k.values())
    assert not pol.within_budget(pd.Series({"a": 0.0, "b": 0.0}), {0: 1, 1: 5})


def test_quantile_tau():
    s = pd.DataFrame({"account_id": list("abcde"), "weeks_since_open": 0, "score": [1, 2, 3, 4, 5.0]})
    assert pol.quantile_tau(s, 0.5) == 3.0 and pol.quantile_tau(s, 1.0) == 5.0


def test_choose_quantile_uses_selection_folds_only_and_ties_go_high():
    summ = pd.DataFrame({"fold": [1, 1, 2, 2, 3, 3], "quantile": [0.99, 0.999] * 3,
                         "caught": [5, 4, 5, 6, 0, 100]})
    assert pol.choose_quantile(summ) == 0.999                                      # 10 vs 10: tie -> higher
    summ.loc[0, "caught"] = 6
    assert pol.choose_quantile(summ) == 0.99                                       # 11 vs 10; fold 3 ignored


def test_policy_verdict():
    t = pd.DataFrame({"fold": [1, 2, 3], "caught": [10, 10, 10], "median_days_from_start": [5.0, 5.0, 5.0]})
    p = t.copy()
    assert pol.policy_verdict(p, t) == "holds up"                                  # equal everywhere
    p["caught"] = [11, 11, 10]
    assert pol.policy_verdict(p, t) == "better"
    p.loc[2, "median_days_from_start"] = 6.0                                       # later on fold 3
    assert pol.policy_verdict(p, t) == "does not hold up"
    p = t.assign(caught=[11, 11, 9])
    assert pol.policy_verdict(p, t) == "does not hold up"


def test_caught_by_start_week():
    truth = pd.DataFrame({"account_id": ["F", "R", "S"], "open_day": 0, "start_day": [90.0, 20.0, 20.0]})
    first = pd.Series({"F": 3.0, "R": 2.0, "S": 3.0})                              # start weeks 12, 2, 2
    assert pol.caught_by_start_week(truth, first, ["F", "R", "S"]) == 2


def test_month_tilt_and_summary():
    s = pd.DataFrame({"account_id": list("abcd"), "open_month": [6, 6, 6, 7], "app_score": [4.0, 3.0, 1.0, 2.0]})
    t = drift.month_tilt(s, (6, 7), tops=(0.25, 0.5)).set_index("open_month")
    assert t.loc[6, "share_accounts"] == 0.75 and t.loc[6, "top_0.25_n"] == 1 and t.loc[7, "top_0.5_n"] == 0
    assert t.loc[6, "top_0.5_ratio"] == 1 / 0.75
    m = drift.month_summary(s).set_index("open_month")
    assert m.loc[6, "accounts"] == 3 and m.loc[7, "mean"] == 2.0


def test_flag_shares():
    month_of = pd.Series({"a": 3, "b": 3, "c": 4, "d": 4})
    t = drift.flag_shares(pd.Series({"a": 0.0, "b": 1.0, "c": 1.0}), month_of, ["a", "c", "d"]).set_index("open_month")
    assert t.loc[3, "flags"] == 2 and abs(t.loc[3, "share_flags"] - 2 / 3) < 1e-12
    assert t.loc[4, "mules"] == 2 and abs(t.loc[4, "share_mules"] - 2 / 3) < 1e-12
