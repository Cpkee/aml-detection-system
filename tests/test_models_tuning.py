"""Phase 4 tuning helpers (src/models/tuning.py) on tiny made-up data; no simulator output needed."""
import numpy as np

from models.tuning import account_weights, app_score


def test_every_account_counts_once_and_classes_balance():
    ids = ["A", "A", "A", "B", "C", "C"]          # A: 3 normal weeks, B: 1 normal week, C: 1 normal + 1 mule week
    y = [0, 0, 0, 0, 0, 1]
    w = account_weights(ids, y)
    assert np.isclose(w[:3].sum(), w[3])          # a 3-week normal account weighs the same as a 1-week one
    assert np.isclose(w[np.array(y) == 1].sum(), w[np.array(y) == 0].sum())


def test_app_score_is_out_of_fold_and_repeatable():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(400, 3))
    y = (x[:, 0] + rng.normal(scale=0.5, size=400) > 1).astype(int)
    oof, other = app_score(x[:300], y[:300], x[300:])
    assert oof.shape == (300,) and other.shape == (100,)
    oof2, other2 = app_score(x[:300], y[:300], x[300:])
    assert np.array_equal(oof, oof2) and np.array_equal(other, other2)
    in_sample = app_score(x[:300], y[:300], x[:300])[1]       # a model that saw these accounts
    assert not np.allclose(oof, in_sample)                    # the training scores come from models that did not
    assert np.corrcoef(oof, x[:300, 0])[0, 1] > 0.8           # and still carry the signal


def test_app_score_split_scores_fakes_and_real_mules_separately():
    from models.tuning import app_score_split
    rng = np.random.default_rng(1)
    x = rng.normal(size=(600, 3))
    fake = (x[:, 0] + rng.normal(scale=0.5, size=600) > 1.3).astype(int)            # signal in column 0
    real = ((x[:, 1] + rng.normal(scale=0.5, size=600) > 1.3) & (fake == 0)).astype(int)   # signal in column 1
    s = app_score_split(x[:450], fake[:450], (fake | real)[:450], x[450:])
    assert set(s) == {"fake", "real"}
    for tr, other in s.values():
        assert tr.shape == (450,) and other.shape == (150,)
    assert np.corrcoef(s["fake"][0], x[:450, 0])[0, 1] > 0.8
    assert np.corrcoef(s["real"][0], x[:450, 1])[0, 1] > 0.8                      # not drowned by the fakes
    again = app_score_split(x[:450], fake[:450], (fake | real)[:450], x[450:])
    assert all(np.array_equal(a, b) for k in s for a, b in zip(s[k], again[k]))
