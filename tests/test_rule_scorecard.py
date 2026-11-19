"""Rule scorecard (src/models/rule_scorecard.py) on synthetic store-shaped rows, no data needed: nothing fired
scores 0, every condition of a scenario must hold, a missing value never fires, points are capped, only amounts,
counts and multiples move with the scale, and test months are refused."""
import numpy as np
import pandas as pd
import pytest

from models import rule_scorecard as sc


def _quiet(n=1) -> pd.DataFrame:
    """Account-weeks where no scenario fires."""
    return pd.DataFrame({c: np.zeros(n) for c in sc.INPUTS})


def _row(**values) -> pd.DataFrame:
    return _quiet().assign(**values)


def test_nothing_fired_scores_zero():
    assert (sc.score(_quiet(5)) == 0).all()
    assert not sc.fired(_quiet(5)).to_numpy().any()


def test_each_scenario_fires_alone_at_its_thresholds():
    cases = {"S1_fast_forwarding": dict(out_24h_share_wk=0.8, money_in_wk=1000.0),
             "S2_new_payers": dict(n_payers_wk=5.0, new_payer_share_wk=0.8),
             "S3_pass_through": dict(passthrough_wk=0.8, money_in_wk=2000.0)}
    for name, values in cases.items():
        hit = sc.fired(_row(**values)).iloc[0]
        assert hit[name] and hit.sum() == 1, name
        assert sc.score(_row(**values))[0] == pytest.approx(1.0), name


def test_every_condition_must_hold():
    assert sc.score(_row(out_24h_share_wk=0.9, money_in_wk=999.0))[0] == 0     # fast, but too little money
    assert sc.score(_row(out_24h_share_wk=0.79, money_in_wk=5000.0))[0] == 0   # enough money, not fast
    assert sc.score(_row(n_payers_wk=9.0, new_payer_share_wk=0.5))[0] == 0     # many payers, but known ones


def test_missing_value_never_fires():
    assert sc.score(_row(out_24h_share_wk=np.nan, money_in_wk=5000.0))[0] == 0
    assert sc.score(_row(passthrough_wk=np.nan, money_in_wk=5000.0))[0] == 0
    assert np.isfinite(sc.score(_row(n_payers_wk=np.nan, new_payer_share_wk=np.nan))).all()


def test_points_grow_with_the_excess_and_are_capped():
    low = sc.score(_row(out_24h_share_wk=0.8, money_in_wk=1000.0))[0]
    mid = sc.score(_row(out_24h_share_wk=1.6, money_in_wk=1000.0))[0]
    huge = sc.score(_row(out_24h_share_wk=400.0, money_in_wk=1000.0))[0]
    assert low == pytest.approx(1.0) and mid == pytest.approx(2.0) and huge == pytest.approx(sc.CAP)


def test_two_scenarios_add_up():
    one = sc.score(_row(out_24h_share_wk=0.8, money_in_wk=1000.0))[0]
    two = sc.score(_row(out_24h_share_wk=0.8, money_in_wk=1000.0, n_payers_wk=5.0, new_payer_share_wk=0.8))[0]
    assert two == pytest.approx(one + 1.0)


def test_scale_moves_amounts_counts_and_multiples_but_not_shares():
    r = _row(out_24h_share_wk=0.8, money_in_wk=1000.0)
    assert sc.score(r, scale=1.0)[0] > 0 and sc.score(r, scale=2.0)[0] == 0    # the money floor doubled
    assert sc.score(_row(out_24h_share_wk=0.8, money_in_wk=2000.0), scale=2.0)[0] == pytest.approx(1.0)  # share: still 0.8
    assert sc.score(_row(n_payers_wk=5.0, new_payer_share_wk=0.8), scale=2.0)[0] == 0          # needs 10 payers now
    with pytest.raises(ValueError):
        sc.score(r, scale=0)


def test_test_months_are_refused():
    for months in ([6], [7], [5, 6]):
        with pytest.raises(ValueError, match="never test months"):
            sc.run("data/does_not_matter", months)


def test_settings_list_every_scenario():
    s = sc.settings(1.0)
    assert set(s["scenarios"]) == set(sc.SCENARIOS) and s["scale"] == 1.0
    assert set(sc.INPUTS) == {"out_24h_share_wk", "money_in_wk", "n_payers_wk", "new_payer_share_wk",
                              "passthrough_wk"}
