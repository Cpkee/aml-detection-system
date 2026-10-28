"""The 1:20 undersampling and the seed summary of src/models/stability.py on tiny made-up data; no data needed."""
import numpy as np
import pandas as pd

from models.stability import seed_summary, undersample


def _train():
    """3 launderer accounts (L0 a fake: mule all 10 weeks; L1, L2 real: mule from week 6) + 200 normal accounts of
    1 to 10 weeks each."""
    rng = np.random.default_rng(0)
    rows = [{"account_id": "L0", "weeks_since_open": w, "mule_by_day": 1} for w in range(10)]
    for a in ("L1", "L2"):
        rows += [{"account_id": a, "weeks_since_open": w, "mule_by_day": int(w >= 6)} for w in range(10)]
    for i in range(200):
        rows += [{"account_id": f"N{i:03d}", "weeks_since_open": w, "mule_by_day": 0}
                 for w in range(int(rng.integers(1, 11)))]
    return pd.DataFrame(rows).sample(frac=1, random_state=1)       # rows in no particular order


def test_undersample_keeps_mules_and_whole_accounts():
    t = _train()
    s = undersample(t, ratio=20, seed=42)
    mule_rows = int(t.mule_by_day.sum())                            # 10 + 4 + 4 = 18
    assert int(s.mule_by_day.sum()) == mule_rows                    # every mule week kept
    assert {"L0", "L1", "L2"} <= set(s.account_id)                  # launderers kept whole, pre-start weeks too
    assert (s.loc[s.account_id == "L1", "mule_by_day"] == 0).sum() == 6
    full = t.groupby("account_id").size()
    kept = s.groupby("account_id").size()
    assert kept.equals(full.reindex(kept.index))                    # whole accounts only
    neg = int((s.mule_by_day == 0).sum())
    assert 20 * mule_rows <= neg < 20 * mule_rows + 10              # stops at the first account reaching 20x
    assert list(s.index) == [i for i in t.index if i in set(s.index)]   # original row order


def test_undersample_is_seeded():
    t = _train()
    a, b, c = undersample(t, 20, 42), undersample(t, 20, 42), undersample(t, 20, 7)
    assert a.index.equals(b.index) and not a.index.equals(c.index)


def test_seed_summary():
    runs = pd.DataFrame({"variant": "v", "seed": [1, 2, 3] * 2, "fold": [1] * 3 + [2] * 3,
                         "weekly_recall": [0.1, 0.2, 0.3, 0.5, 0.5, 0.5]})
    s = seed_summary(runs, ["weekly_recall"]).set_index("fold")
    assert np.isclose(s.loc[1, "weekly_recall_mean"], 0.2) and np.isclose(s.loc[1, "weekly_recall_sd"], 0.1)
    assert s.loc[2, "weekly_recall_sd"] == 0 and s.loc[1, "weekly_recall_max"] == 0.3
