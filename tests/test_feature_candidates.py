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
