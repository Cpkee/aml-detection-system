"""Candidate features (src/features/candidates.py) use only the same and earlier weeks of the same account.

Synthetic store-shaped rows, no data needed: changing week w + 1 onwards must leave every candidate at weeks <= w
unchanged, accounts must not leak into each other, and the windows must equal a hand computation.
"""
import numpy as np
import pandas as pd
import pytest

from features import candidates
from features.weekly import FEATURES

GROUPS = list(candidates.GROUPS)


def _store(n_acc=5, n_weeks=12, seed=0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n = n_acc * n_weeks
    df = pd.DataFrame({"account_id": np.repeat([f"A{i}" for i in range(n_acc)], n_weeks),
                       "weeks_since_open": np.tile(np.arange(n_weeks), n_acc)})
    for c in FEATURES:
        df[c] = rng.gamma(2.0, 50.0, n)
    for c in ("out_1h_share_wk", "out_24h_share_wk", "passthrough_wk"):
        df[c] = rng.uniform(0, 1, n)
    no_money = rng.uniform(size=n) < 0.3                     # weeks with no money in: shares undefined
    df.loc[no_money, "money_in_wk"] = 0.0
    df.loc[no_money, ["out_1h_share_wk", "out_24h_share_wk", "passthrough_wk"]] = np.nan
    return df


@pytest.mark.parametrize("group", GROUPS)
def test_no_peeking(group):
    df = _store()
    base, names = candidates.add(df, [group])
    for w in (0, 3, 7):
        changed = df.copy()
        later = changed.weeks_since_open > w
        changed.loc[later, FEATURES] = changed.loc[later, FEATURES] * 7 + 3
        after, _ = candidates.add(changed, [group])
        upto = df.weeks_since_open <= w
        pd.testing.assert_frame_equal(base.loc[upto, names[group]], after.loc[upto, names[group]])


@pytest.mark.parametrize("group", GROUPS)
def test_accounts_do_not_mix(group):
    df = _store()
    base, names = candidates.add(df, [group])
    changed = df.copy()
    other = changed.account_id != "A2"
    changed.loc[other, FEATURES] = changed.loc[other, FEATURES] + 11
    after, _ = candidates.add(changed, [group])
    mine = df.account_id == "A2"
    pd.testing.assert_frame_equal(base.loc[mine, names[group]], after.loc[mine, names[group]])


def test_core_is_part_of_roll4():
    df = _store()
    full, _ = candidates.add(df, ["roll4"])
    core, names = candidates.add(df, ["roll4_core"])
    pd.testing.assert_frame_equal(core[names["roll4_core"]], full[names["roll4_core"]])
    with pytest.raises(ValueError):                    # same column names: one or the other, never both
        candidates.add(df, ["roll4", "roll4_core"])


def test_windows_by_hand():
    df = _store(n_acc=1)
    out, _ = candidates.add(df, ["lag1", "roll2", "running_max"])
    m, s = df["money_in_wk"].to_numpy(), df["out_1h_share_wk"].to_numpy()
    assert np.isnan(out["money_in_wk_lag1"].iloc[0])
    np.testing.assert_allclose(out["money_in_wk_lag1"].iloc[1:], m[:-1], rtol=1e-6)
    np.testing.assert_allclose(out["money_in_2wk"], m + np.r_[0, m[:-1]], rtol=1e-6)
    amount = np.nan_to_num(s) * m
    two = m + np.r_[0, m[:-1]]
    want = np.where(two > 0, (amount + np.r_[0, amount[:-1]]) / np.where(two > 0, two, 1), np.nan)
    np.testing.assert_allclose(out["out_1h_share_2wk"], want, rtol=1e-5)
    np.testing.assert_allclose(out["out_1h_share_wk_max_so_far"], np.maximum.accumulate(np.nan_to_num(s)), rtol=1e-6)


def test_new_cp4_by_hand():
    df = _store(n_acc=1, n_weeks=8)
    df["n_payers_cum"] = [1, 1, 3, 3, 4, 9, 9, 10]          # cumulative distinct payers, weeks 0-7
    out, _ = candidates.add(df, ["new_cp4"])
    # weeks 0-3: everything so far; week 4: 4 - 1 (week 0); week 5: 9 - 1; week 6: 9 - 3; week 7: 10 - 3
    np.testing.assert_allclose(out["new_payers_4wk"], [1, 1, 3, 3, 3, 8, 6, 7])


def test_self4_by_hand():
    df = _store(n_acc=1, n_weeks=9)
    df["money_in_wk"] = [0, 0, 0, 0, 0, 0, 0, 0, 0.0]
    df.loc[[0, 4], "money_in_wk"] = 1000.0                   # salary in weeks 0 and 4
    df.loc[7, "money_in_wk"] = 3000.0                        # a burst in week 7
    out, _ = candidates.add(df, ["self4"])
    got = out["self4_money_in"].to_numpy()
    assert np.isnan(got[:7]).all()                           # fewer than 4 earlier weeks before the window
    # week 7: window weeks 4-7 = 4000; usual = 4 x 1000 / 4 weeks (0-3) = 1000 -> 4.0
    # week 8: window weeks 5-8 = 3000; usual = 4 x 2000 / 5 weeks (0-4) = 1600 -> 1.875
    np.testing.assert_allclose(got[7:], [4.0, 1.875], rtol=1e-6)


def test_speed_cum_by_hand():
    df = _store(n_acc=1, n_weeks=4)
    df["money_in_wk"] = [0.0, 1000.0, 0.0, 3000.0]
    df["out_1h_share_wk"] = [np.nan, 0.1, np.nan, 0.9]       # no money in -> no share
    out, _ = candidates.add(df, ["speed_cum"])
    # week 0: no money in yet; week 1: 100 / 1000; week 2: unchanged; week 3: (100 + 2700) / 4000
    np.testing.assert_allclose(out["out_1h_share_cum"], [np.nan, 0.1, 0.1, 0.7], rtol=1e-6)


def test_max_out_hist_by_hand():
    df = _store(n_acc=1, n_weeks=6)
    df["max_out_wk"] = [0.0, 50.0, 20.0, 0.0, 100.0, 60.0]
    out, _ = candidates.add(df, ["max_out_hist"])
    # largest earlier: -, 0, 50, 50, 50, 100 -> NaN until an earlier week has money out; 0 in a week with none
    np.testing.assert_allclose(out["max_out_vs_hist"], [np.nan, np.nan, 0.4, 0.0, 2.0, 0.6], rtol=1e-6)


def test_internal_out_by_hand():
    df = _store(n_acc=1, n_weeks=6)
    money_out = np.array([0.0, 100.0, 50.0, 0.0, 200.0, 0.0])
    internal = np.array([0.0, 30.0, 0.0, 0.0, 100.0, 0.0])          # money out to A* accounts, per week
    df["money_out_wk"], df["money_out_cum"] = money_out, money_out.cumsum()
    df["internal_out_share_cum"] = np.where(money_out.cumsum() > 0, internal.cumsum() / np.where(
        money_out.cumsum() > 0, money_out.cumsum(), 1), np.nan)    # as the store: NaN until money goes out
    out, _ = candidates.add(df, ["internal_out"])
    # weekly: no money out in weeks 0, 3, 5 -> NaN; week 1: 30/100; week 2: 0/50; week 4: 100/200
    np.testing.assert_allclose(out["internal_out_share_wk"], [np.nan, 0.3, 0.0, np.nan, 0.5, np.nan], rtol=1e-6)
    assert (out["internal_out_share_wk"].dropna() >= 0).all()
    # 4 weeks: week 0 none; 1: 30/100; 2: 30/150; 3: 30/150; 4 (weeks 1-4): 130/350; 5 (weeks 2-5): 100/250
    np.testing.assert_allclose(out["internal_out_share_4wk"], [np.nan, 0.3, 0.2, 0.2, 130 / 350, 0.4], rtol=1e-6)


def test_refuses_gaps_and_unsorted_rows():
    df = _store()
    with pytest.raises(ValueError):
        candidates.add(df[df.weeks_since_open != 4], ["roll4"])
    with pytest.raises(ValueError):
        candidates.add(df.sample(frac=1, random_state=0), ["roll4"])
    with pytest.raises(ValueError):
        candidates.add(df, ["no_such_group"])


def test_adopted_is_the_roll4_group():
    _, names = candidates.add(_store(), [candidates.ADOPTED_GROUP])
    assert set(candidates.ADOPTED) <= set(names[candidates.ADOPTED_GROUP])
