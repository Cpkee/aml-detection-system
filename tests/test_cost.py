"""Money gone before the first flag (src/evaluation/cost.py), closing plan item 7.

Hand-made mules, no data needed: rows on the flag day count as gone, rows after it do not; a mule never flagged loses
everything up to the end of the horizon; a model flag is dated at the end of its week, a rules flag on its alert day
(and a file week that disagrees with the alert day is refused); shares and the paired bootstrap add up.
On real data (skipped without data/v1_full): the committed month5_cost results are reproduced exactly.
"""
import os
import shutil

import numpy as np
import pandas as pd
import pytest

from evaluation import cost

# two mules opened on day 0 (week w ends on day 7w + 6); horizon end day 20 (end of week 2)
ROWS = pd.DataFrame({"account_id": ["A", "A", "A", "A", "B", "B", "X"],
                     "day": [5, 13, 14, 21, 3, 20, 4],
                     "amount": [100.0, 10.0, 1.0, 1000.0, 50.0, 5.0, 999.0]})     # X is not a mule
END = pd.Series({"A": 20.0, "B": 20.0})
MULES = pd.DataFrame({"open_day": [0.0, 0.0], "first_alert_day": [13.0, np.nan]}, index=["A", "B"])


def test_flag_day_rows_count_as_gone_later_rows_do_not():
    gone = cost.money_gone(ROWS, END, pd.Series({"A": 13.0, "B": np.nan}))
    assert gone.to_dict() == {"A": 110.0, "B": 55.0}             # A: days 5 and 13; B never flagged: all to day 20


def test_ceiling_stops_at_the_horizon_and_ignores_other_accounts():
    gone = cost.money_gone(ROWS, END, pd.Series(np.nan, index=END.index))
    assert gone.to_dict() == {"A": 111.0, "B": 55.0}             # day 21 is after the horizon; X is not a mule


def test_mule_without_rows_loses_nothing():
    gone = cost.money_gone(ROWS, pd.Series({"C": 20.0}), pd.Series({"C": np.nan}))
    assert gone.to_dict() == {"C": 0.0}


def test_model_flag_dated_at_end_of_week_rules_on_alert_day():
    weeks = pd.Series({"A": 1.0, "B": np.nan})
    assert cost.flag_days(MULES, weeks, rules=False).to_dict()["A"] == 13.0      # end of week 1
    rules = cost.flag_days(MULES, weeks, rules=True)
    assert rules["A"] == 13.0 and np.isnan(rules["B"])
    late = cost.flag_days(MULES, pd.Series({"A": 3.0, "B": np.nan}), rules=False, w_hi=2)
    assert late.isna().all()                                                    # a flag after the horizon: none


def test_rules_week_must_match_the_alert_day():
    with pytest.raises(ValueError):
        cost.flag_days(MULES, pd.Series({"A": 0.0, "B": np.nan}), rules=True)  # day 13 is in week 1, not 0


def test_summary_shares_and_split():
    per = pd.DataFrame({"profile": ["fake", "witting"], "ceiling": [111.0, 55.0],
                        "flag_day_p": [13.0, np.nan], "gone_p": [110.0, 55.0]}, index=["A", "B"])
    s = cost.summarise(per, ["p"]).iloc[0]
    assert (s["mules"], s["caught"], s["money_gone"], s["gone_caught_mules"], s["gone_missed_mules"]) == \
        (2, 1, 165.0, 110.0, 55.0)
    assert s["share_prevented"] == pytest.approx(1 / 166)
    by = cost.summarise(per, ["p"], by="profile").set_index("profile")
    assert by.loc["witting", "share_gone"] == 1.0 and by.loc["fake", "caught"] == 1


def test_bootstrap_is_paired_and_repeatable():
    assert cost.bootstrap_sum(pd.Series([0.0, 0.0, 0.0])) == (0.0, 0.0)
    d = pd.Series([10.0, 20.0, 30.0, 40.0])
    lo, hi = cost.bootstrap_sum(d)
    assert lo <= d.sum() <= hi and (lo, hi) == cost.bootstrap_sum(d)


DATA = os.environ.get("SIM_OUT", "data/v1_full")
COMMITTED = os.path.join(cost.score.RESULTS, "v1_full", cost.OUT_NAME)


@pytest.mark.skipif(not os.path.exists(os.path.join(DATA, "transactions.parquet"))
                    or os.path.basename(os.path.normpath(DATA)) != "v1_full", reason="no data/v1_full")
def test_real_data_reproduces_committed_results(tmp_path):
    results = os.path.join(cost.score.RESULTS, "v1_full")
    # copy the committed harness runs it reads into a scratch results folder, so nothing committed is written
    for run in cost.RUNS.values():
        os.makedirs(tmp_path / run)
        for f in ("launderers.csv", f"summary_w{cost.HORIZON}.csv"):
            shutil.copy(os.path.join(results, run, f), tmp_path / run / f)
    report = cost.run(DATA, results=str(tmp_path))
    for f in ("summary.csv", "by_type.csv", "per_mule.csv"):
        pd.testing.assert_frame_equal(pd.read_csv(os.path.join(report, f)), pd.read_csv(os.path.join(COMMITTED, f)))
    s = pd.read_csv(os.path.join(report, "summary.csv")).set_index("policy")
    assert (s["money_gone"] <= s["ceiling"]).all() and s["mules"].nunique() == 1
