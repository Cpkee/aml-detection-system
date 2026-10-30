"""Outlier scores (src/models/outlier.py) on synthetic store-shaped rows, no data needed: a value most weeks share is
not rare, a missing value is no evidence, each week band is judged against its own band, fitting is deterministic,
and test months are refused."""
import numpy as np
import pandas as pd
import pytest

from models import outlier


def _rows(n_acc=400, weeks=range(27), seed=0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    df = pd.DataFrame([(f"A{i}", w) for i in range(n_acc) for w in weeks], columns=outlier.KEY)
    for c in outlier.INPUTS:
        df[c] = rng.gamma(2.0, 1.0, len(df)).astype("float32")
    df["out_1h_share_wk"] = np.where(rng.uniform(size=len(df)) < 0.9, 0.0, rng.uniform(size=len(df))).astype("float32")
    return df


def test_rarity_common_value_is_not_rare_and_extremes_are():
    ref = np.sort(np.r_[np.zeros(900), np.linspace(0.01, 1, 100)]).astype("float32")
    r = outlier.rarity(ref, np.array([0.0, 0.5, 5.0, -1.0], dtype="float32"))
    assert r[0] < 0.05                                       # 90% of weeks are 0: not rare
    assert r[2] == r[3] == pytest.approx(np.log10(len(ref) + 1))   # beyond either end: the rarest possible
    assert r[1] < r[2]


def test_missing_is_no_evidence():
    ref = np.arange(10, dtype="float32")
    x = np.array([np.nan], dtype="float32")
    assert outlier.rarity(ref, x)[0] == 0.0
    assert outlier.rank(ref, x)[0] == 0.5
    assert outlier.rarity(np.array([], dtype="float32"), np.array([3.0], dtype="float32"))[0] == 0.0


def test_rank_is_mid_rank():
    ref = np.array([0, 0, 1, 2], dtype="float32")
    assert outlier.rank(ref, np.array([0, 1, 9], dtype="float32")).tolist() == [0.25, 0.625, 1.0]


def test_each_band_uses_its_own_reference():
    train = _rows(weeks=[1, 20])
    train.loc[train.weeks_since_open == 20, "passthrough_wk"] += 100     # later weeks: much larger values
    fitted = outlier.fit(train, "rarity")
    probe = pd.DataFrame({"account_id": ["X", "X"], "weeks_since_open": [1, 20]})   # the same value, two bands
    for c in outlier.INPUTS:
        probe[c] = np.float32(np.nan)
    probe["passthrough_wk"] = np.float32(101)
    r = outlier.score(probe, fitted, "rarity") * outlier.TOP_K           # the only non-missing input
    assert r[0] > 2.5 and r[1] < 1                       # rare among week-1 rows, ordinary among week-20 rows


@pytest.mark.parametrize("method", outlier.METHODS)
def test_deterministic_and_pure(method):
    train = _rows()
    new = _rows(n_acc=50, seed=1)
    a = outlier.score(new, outlier.fit(train, method), method)
    changed = new.copy()
    changed[outlier.INPUTS] = changed[outlier.INPUTS] * 3                # scoring other rows changes no fit
    outlier.score(changed, outlier.fit(train, method), method)
    b = outlier.score(new, outlier.fit(train, method), method)
    assert np.array_equal(a, b) and np.isfinite(a).all()


@pytest.mark.parametrize("method", outlier.METHODS)
def test_an_obvious_outlier_scores_highest(method):
    train = _rows()
    new = _rows(n_acc=50, seed=1)
    new.loc[0, outlier.INPUTS] = 1000.0
    s = outlier.score(new, outlier.fit(train, method), method)
    assert s[0] == s.max() and s[0] > np.quantile(s, 0.99)


def test_weeks_outside_bands_get_no_score():
    s = outlier.score(_rows(n_acc=5, weeks=[26, 27]), outlier.fit(_rows(), "rarity"), "rarity")
    assert np.isfinite(s[::2]).all() and np.isnan(s[1::2]).all()


def test_test_months_are_refused():
    with pytest.raises(ValueError, match="D1"):
        outlier.run("data/none", "rarity", months=(6,))
