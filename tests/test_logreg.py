"""Logistic regression on the frozen inputs (src/models/logreg.py), on small hand-made tables (no data needed)."""
import json

import numpy as np
import pandas as pd
import pytest

from models import logreg, train


def _table(n=4000, seed=0):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({c: rng.gamma(1.0, 50.0, n) for c in logreg.INPUTS})
    for c in logreg.SHARES:
        df[c] = rng.uniform(0, 1.3, n)                                # speed shares can pass 1
    for c in logreg.ZSCORE:
        df[c] = rng.normal(0, 4, n)
    df["app_score"] = rng.normal(-2, 1, n)
    df["weeks_since_open"] = rng.integers(0, 27, n).astype(float)
    df.loc[rng.random(n) < 0.3, "out_1h_share_wk"] = np.nan          # no money in -> no share
    logit = -4 + 1.5 * (df["app_score"] + 2) + 0.8 * np.log1p(df["n_payers_cum"]) - 0.8 * np.log1p(50)
    y = (rng.random(n) < 1 / (1 + np.exp(-logit))).astype(int)          # a signal a linear model can find
    return df, y


def test_every_frozen_input_has_one_kind():
    assert len(logreg.INPUTS) == 38 and logreg.INPUTS == train.INPUTS
    assert set(logreg.KIND) == set(logreg.INPUTS)
    assert logreg.KIND["out_1h_share_4wk"] == "share" and logreg.KIND["money_in_4wk"] == "log"
    assert logreg.KIND["app_score"] == "std" and logreg.KIND["self_vs_past_rows"] == "z"


def test_prep_fills_flags_clips_and_standardises():
    df, _ = _table()
    prep = logreg.fit_prep(df, logreg.INPUTS)
    x = logreg.transform(df, prep)
    cols = logreg.columns_out(prep)
    assert not np.isnan(x).any() and x.shape == (len(df), len(cols))
    assert cols[-1] == "out_1h_share_wk__missing" and sum(c.endswith("__missing") for c in cols) == 1
    flag = x[:, cols.index("out_1h_share_wk__missing")]
    assert np.array_equal(flag, df["out_1h_share_wk"].isna().to_numpy().astype(float))     # 0/1, not standardised
    body = x[:, :len(logreg.INPUTS)]
    assert np.allclose(body.mean(axis=0), 0, atol=1e-9) and np.allclose(body.std(axis=0), 1, atol=1e-9)
    # a share above 1 is clipped to 1 before standardising: same prepared value as exactly 1
    one = df.iloc[:2].copy()
    one["passthrough_wk"] = [1.0, 7.5]
    p = logreg.transform(one, prep)[:, cols.index("passthrough_wk")]
    assert p[0] == p[1]


def test_prep_is_fitted_on_training_rows_only():
    df, _ = _table()
    train_rows, other = df.iloc[:3000], df.iloc[3000:].copy()
    a = logreg.fit_prep(train_rows, logreg.INPUTS)
    other[logreg.INPUTS] = other[logreg.INPUTS] * 100                  # changing other rows changes nothing
    assert logreg.fit_prep(pd.concat([train_rows]), logreg.INPUTS) == a
    assert json.loads(json.dumps(a)) == a                              # plain numbers: JSON round trip is exact


def test_mulelogit_learns_and_round_trips_through_json():
    df, y = _table()
    m = logreg.MuleLogit(C=1.0).fit(df[logreg.INPUTS], y)
    s = m.predict(df)
    assert s.shape == (len(df),) and ((s > 0) & (s < 1)).all()
    from sklearn.metrics import roc_auc_score
    assert roc_auc_score(y, s) > 0.7                                    # it found the signal planted in _table
    again = logreg.MuleLogit.from_dict(json.loads(json.dumps(m.to_dict())))
    assert np.allclose(again.predict(df), s, rtol=0, atol=1e-12)
    assert np.allclose(m.predict_proba(df)[:, 1], s)
    c = m.coefficients()
    assert list(c.columns) == ["column", "coef", "odds_ratio"] and len(c) == len(logreg.columns_out(m.prep_))


def test_interactions_scale_a_share_by_the_money_behind_it():
    df, y = _table()
    m = logreg.MuleLogit(C=1.0, interactions=True).fit(df[logreg.INPUTS], y)
    cols = logreg.columns_out(m.prep_, m.inter_)
    assert "out_1h_share_4wk_x_money_in_4wk" in cols and len(m.inter_) == len(logreg.INTERACTIONS)
    assert cols.index("out_1h_share_4wk_x_money_in_4wk") < cols.index("out_1h_share_wk__missing")  # flags stay last
    two = df.iloc[:2].copy()
    two["out_1h_share_4wk"], two["money_in_4wk"] = [1.0, 1.0], [20.0, 5000.0]   # same share, little vs real money
    x = logreg.transform(two, m.prep_, m.inter_)[:, cols.index("out_1h_share_4wk_x_money_in_4wk")]
    assert x[1] > x[0]
    again = logreg.MuleLogit.from_dict(json.loads(json.dumps(m.to_dict())))
    assert np.allclose(again.predict(df), m.predict(df), rtol=0, atol=1e-12)
    assert logreg.MuleLogit().fit(df[logreg.INPUTS], y).inter_ == []          # off by default


def test_smaller_c_shrinks_coefficients():
    df, y = _table()
    big = logreg.MuleLogit(C=1.0).fit(df[logreg.INPUTS], y)
    small = logreg.MuleLogit(C=1e-4).fit(df[logreg.INPUTS], y)
    assert np.abs(small.coef_).sum() < np.abs(big.coef_).sum()


def test_from_dict_refuses_mismatched_columns():
    df, y = _table()
    d = logreg.MuleLogit().fit(df[logreg.INPUTS], y).to_dict()
    d["columns"] = d["columns"][:-1]
    with pytest.raises(ValueError):
        logreg.MuleLogit.from_dict(d)


def test_model_kind_by_file(tmp_path):
    assert train.model_kind(str(tmp_path)) is None
    (tmp_path / "logreg.json").write_text("{}")
    assert train.model_kind(str(tmp_path)) == "logreg"
    assert train.model_files(str(tmp_path))[0] == "logreg.json"
