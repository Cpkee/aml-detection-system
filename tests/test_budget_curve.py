"""Budget curve (src/evaluation/budget_curve.py): rules vs model at several alert volumes.

Hand-made cohort, no data needed: the cohort seen under another scale's alerts (first alert, earlier closure,
weekly budget), and the refusal of test months. On a data folder (SIM_OUT, default data/v1; skipped without it):
the re-applied rules at the run's own scale reproduce the cohort's alerts in the data exactly.
"""
import json
import os

import numpy as np
import pandas as pd
import pytest

from evaluation import budget_curve as bc

OUT = os.environ.get("SIM_OUT", "data/v1")
needs_data = pytest.mark.skipif(not os.path.exists(os.path.join(OUT, "transactions.parquet")),
                                reason="no simulator output")

TRUTH = pd.DataFrame({"account_id": ["A", "B", "C"], "open_day": [0, 7, 0],
                      "exit_day": [30.0, np.nan, np.nan], "first_alert_day": [20.0, np.nan, np.nan]})


def test_truth_at_uses_the_scale_alerts_and_the_earlier_closure():
    alerts = pd.DataFrame({"account_id": ["A", "B", "B"], "alert_day": [27, 13, 48]})
    exits = pd.Series({"A": 40.0, "B": 20.0})
    t, k = bc.truth_at(TRUTH, alerts, exits)
    t = t.set_index("account_id")
    assert t.loc["A", "first_alert_day"] == 27 and t.loc["B", "first_alert_day"] == 13
    assert np.isnan(t.loc["C", "first_alert_day"])
    assert t.loc["A", "exit_day"] == 30                    # the data's closure is earlier
    assert t.loc["B", "exit_day"] == 20                    # closed only under this scale
    assert np.isnan(t.loc["C", "exit_day"])
    assert k == {3: 1, 0: 1, 5: 1}                         # weeks since each account opened; B counts twice
    assert TRUTH.loc[0, "first_alert_day"] == 20           # the input is not changed


def test_no_alerts_gives_an_empty_budget():
    t, k = bc.truth_at(TRUTH, pd.DataFrame({"account_id": [], "alert_day": []}), pd.Series(dtype=float))
    assert k == {} and t["first_alert_day"].isna().all() and t["exit_day"].tolist()[0] == 30


def test_refuses_test_months():
    with pytest.raises(ValueError):
        bc.main(["--out", OUT, "--months", "6", "7"])


def test_scale_of_record_is_in_the_plan():
    assert 1.516 in bc.SCALES and list(bc.SCALES) == sorted(bc.SCALES)


@needs_data
def test_reapplied_rules_reproduce_the_data():
    scale = json.load(open(os.path.join(OUT, "_internal/rules_state.json")))["scale"]
    f, acc = bc.rule_features(OUT, (5,))
    alerts, exits = bc.alerts_at(f, acc, OUT, scale)
    bc.check_reproduces(OUT, (5,), alerts)                 # raises SystemExit if they differ
    assert len(alerts) > 0
