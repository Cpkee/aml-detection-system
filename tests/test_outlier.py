"""Outlier scores (src/models/outlier.py) on synthetic store-shaped rows, no data needed: a value most weeks share is
not rare, only the suspicious side counts, a missing value is no evidence, each week since opening is judged against
its own week, fitting is deterministic, and test months are refused."""
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


def test_rarity_common_value_is_not_rare_and_only_the_suspicious_side_counts():
    ref = np.sort(np.r_[np.zeros(900), np.linspace(0.01, 1, 100)]).astype("float32")
    x = np.array([0.0, 0.5, 5.0, -1.0], dtype="float32")
    r = outlier.rarity(ref, x)
    assert r[0] < 0.05                                       # 90% of weeks are 0: not rare
    assert r[2] == pytest.approx(np.log10(len(ref) + 1))     # beyond the top: the rarest possible
    assert r[3] == 0.0                                       # unusually low is not suspicious here
    assert r[0] < r[1] < r[2]
    low = outlier.rarity(ref, x, low=True)                   # e.g. minutes from money in to money out
    assert low[3] == pytest.approx(np.log10(len(ref) + 1)) and low[2] == 0.0


def test_only_forwarding_time_is_low_side():
    assert set(outlier.LOW_IS_SUSPICIOUS) == {"med_in_out_minutes_wk"} <= set(outlier.INPUTS)


def test_rarity_sum_adds_every_input():
    train = _rows()
    new = _rows(n_acc=20, seed=1)
    f = outlier.fit(train, "rarity")
    top3, total = outlier.score(new, f, "rarity"), outlier.score(new, f, "rarity_sum")
    assert (total >= top3 * outlier.TOP_K - 1e-9).all()      # the sum includes the 3 rarest
    assert not np.allclose(total, top3 * outlier.TOP_K)


def test_missing_is_no_evidence():
    ref = np.arange(10, dtype="float32")
    x = np.array([np.nan], dtype="float32")
    assert outlier.rarity(ref, x)[0] == 0.0
    assert outlier.rank(ref, x)[0] == 0.5
    assert outlier.rarity(np.array([], dtype="float32"), np.array([3.0], dtype="float32"))[0] == 0.0


def test_rank_is_mid_rank():
    ref = np.array([0, 0, 1, 2], dtype="float32")
    assert outlier.rank(ref, np.array([0, 1, 9], dtype="float32")).tolist() == [0.25, 0.625, 1.0]


def test_each_week_uses_its_own_reference():
    train = _rows(weeks=[1, 20])
    train.loc[train.weeks_since_open == 20, "passthrough_wk"] += 100     # later weeks: much larger values
    fitted = outlier.fit(train, "rarity")
    probe = pd.DataFrame({"account_id": ["X", "X"], "weeks_since_open": [1, 20]})   # the same value, two weeks
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


def test_notebook_12_runs_on_the_committed_look(tmp_path, monkeypatch):
    """The write-up reads only committed files, so it runs anywhere; its asserts check every quoted number."""
    from features.__main__ import run_notebook
    monkeypatch.setenv("EDA_REPORT", str(tmp_path))
    run_notebook("12_outlier_detection.ipynb", "data/v1_full", str(tmp_path))
    for name in ("12_outlier_detection.ipynb", "report.md", "01_vs_rules.png", "02_caught_by_week.png"):
        assert (tmp_path / name).exists(), name
