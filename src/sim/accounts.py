"""Steps 1-3: pick BAF applications, plant hidden profiles, plan timelines and networks."""
from __future__ import annotations
import duckdb
import numpy as np
import pandas as pd

from .common import BAF_FEATURES


def load_baf(path: str) -> pd.DataFrame:
    df = duckdb.sql(f"SELECT * FROM read_csv_auto('{path}')").df()
    df["baf_row"] = np.arange(len(df))
    return df


def _age_bin(age: np.ndarray) -> np.ndarray:
    return np.where(age >= 40, "40plus", age.astype(int).astype(str))


def _age_weights(age: np.ndarray, target: dict) -> np.ndarray:
    """Sampling weights that make the picked rows' age bins match `target` shares."""
    bins = _age_bin(age)
    counts = pd.Series(bins).value_counts()
    w = np.array([target[b] / counts[b] for b in bins])
    return w / w.sum()


def build_accounts(cfg, baf: pd.DataFrame, rng: np.random.Generator):
    n = cfg.get("size.n_accounts")
    picked = np.sort(rng.choice(len(baf), size=n, replace=False))
    a = baf.iloc[picked].reset_index(drop=True)

    account_id = np.array([f"A{i:07d}" for i in range(1, n + 1)])
    open_month = a["month"].to_numpy().astype(int)
    open_day = 30 * open_month + rng.integers(0, 30, size=n)

    accounts = pd.DataFrame({"account_id": account_id, "open_month": open_month, "open_day": open_day})
    for c in BAF_FEATURES:
        accounts[c] = a[c].to_numpy()

    # ---- Step 2: hidden profiles -------------------------------------------------
    fraud = a["fraud_bool"].to_numpy().astype(int)
    n_l = int(round(cfg.get("profiles.launderer_share") * n))
    mix = cfg.get("profiles.in_window_mix")
    n_fake = int(round(n_l * mix["fake"]))
    n_wit = int(round((n_l - n_fake) * mix["witting"] / (mix["witting"] + mix["unwitting"])))
    n_unw = n_l - n_fake - n_wit

    profile = np.where(fraud == 1, "app_fraud_only", "normal").astype(object)
    fraud_idx = np.flatnonzero(fraud == 1)
    if n_fake > len(fraud_idx):
        raise ValueError(f"Need {n_fake} fake accounts but sample has only {len(fraud_idx)} fraud rows")
    target = {str(k): v for k, v in cfg.get("profiles.real_mule_age_weights").items()}
    rule = cfg.get("profiles.fake_age_rule")
    if rule == "baf_own_ages":            # fake accounts keep the ages of BAF's fraud rows
        fake_idx = rng.choice(fraud_idx, size=n_fake, replace=False)
    elif rule == "young_weighted":        # test: fraud rows re-weighted to the Cifas mule ages
        fake_idx = rng.choice(fraud_idx, size=n_fake, replace=False,
                              p=_age_weights(a["customer_age"].to_numpy()[fraud_idx], target))
    else:
        raise ValueError(f"unknown profiles.fake_age_rule '{rule}'")
    profile[fake_idx] = "fake"

    # Real customers who become mules: fraud_bool = 0 rows, weighted to Cifas mule ages.
    clean_idx = np.flatnonzero(fraud == 0)
    bins = _age_bin(a["customer_age"].to_numpy()[clean_idx])
    counts = pd.Series(bins).value_counts()
    w = np.array([target[b] / counts[b] for b in bins])
    real_idx = rng.choice(clean_idx, size=n_wit + n_unw, replace=False, p=w / w.sum())
    profile[real_idx[:n_wit]] = "witting"
    profile[real_idx[n_wit:]] = "unwitting"

    is_l = np.isin(profile, ["fake", "witting", "unwitting"]).astype(int)

    # ---- Step 3: when laundering starts (days after opening) ---------------------
    rel = np.full(n, -1)
    lo, hi = cfg.get("timing.fake_start_days")
    rel[fake_idx] = rng.integers(lo, hi + 1, size=n_fake)
    bands = cfg.get("timing.existing_start_bands")
    shares = np.array([b["share"] for b in bands])
    pick = rng.choice(len(bands), size=len(real_idx), p=shares / shares.sum())
    for k, b in enumerate(bands):
        sel = real_idx[pick == k]
        rel[sel] = rng.integers(b["days"][0], b["days"][1] + 1, size=len(sel))
    start_day = np.where(is_l == 1, open_day + rel, -1)

    # ---- Step 3b: networks -------------------------------------------------------
    laund = rng.permutation(np.flatnonzero(is_l == 1))
    network_id = np.full(n, None, dtype=object)
    successor = np.full(n, -1)
    n_big = int(round(cfg.get("networks.big_network_share") * len(laund)))
    big = laund[:n_big]
    network_id[big] = "NET_BIG"
    if len(big) > 1:
        for i, m in enumerate(big):            # each member passes money to a random other member
            others = big[big != m]
            successor[m] = rng.choice(others)
    rest = laund[n_big:]
    cmin, cmax = cfg.get("networks.chain_size")
    pos, chain_no = 0, 0
    while pos < len(rest):
        size = int(rng.integers(cmin, cmax + 1))
        members = rest[pos:pos + size]
        pos += size
        if len(members) < 2:
            break                               # a leftover single launderer stays unlinked
        chain_no += 1
        members = members[np.argsort(-start_day[members])]  # money flows to members who started earlier (already active)
        network_id[members] = f"CH_{chain_no:04d}"
        successor[members[:-1]] = members[1:]

    truth = pd.DataFrame({
        "account_id": account_id,
        "profile": profile,
        "baf_fraud_bool": fraud,
        "network_id": network_id,
        "is_launderer": is_l,
        "launder_start_day": pd.array(np.where(is_l == 1, start_day, pd.NA), dtype="Int64"),
        "laundered_in": 0.0,
        "laundered_out": 0.0,
    })
    internal = pd.DataFrame({"account_id": account_id, "baf_row": a["baf_row"].to_numpy(),
                             "successor": successor})
    return accounts, truth, internal
