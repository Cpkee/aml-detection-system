"""Small helpers shared by the simulator steps."""
from __future__ import annotations
import numpy as np
import pandas as pd

ANCHOR_X = np.array([0.1, 0.5, 0.9])   # BAF income values where published anchors sit
MONTH = 30.4375                        # average days per month

BAF_FEATURES = [
    "income", "name_email_similarity", "prev_address_months_count", "current_address_months_count",
    "customer_age", "days_since_request", "intended_balcon_amount", "payment_type", "zip_count_4w",
    "velocity_6h", "velocity_24h", "velocity_4w", "bank_branch_count_8w", "date_of_birth_distinct_emails_4w",
    "employment_status", "credit_risk_score", "email_is_free", "housing_status", "phone_home_valid",
    "phone_mobile_valid", "bank_months_count", "has_other_cards", "proposed_credit_limit", "foreign_request",
    "source", "session_length_in_minutes", "device_os", "keep_alive_session", "device_distinct_emails_8w",
]


def interp_anchor(x, anchors):
    """Straight lines between the anchors at income 0.1, 0.5, 0.9 (flat outside)."""
    return np.interp(x, ANCHOR_X, np.asarray(anchors, dtype=float))


def lognormal_mean(rng, mean, sigma, size):
    """Right-skewed amounts whose average is `mean`."""
    mean = np.asarray(mean, dtype=float)
    return rng.lognormal(np.log(mean) - sigma ** 2 / 2, sigma, size)


def lognormal_median(rng, median, sigma, size):
    """Right-skewed amounts whose middle value is `median`."""
    return rng.lognormal(np.log(np.asarray(median, dtype=float)), sigma, size)


def sample_seconds(rng, n, hour_weights):
    """Seconds after midnight, with the hour drawn from SAML-D's hourly shape."""
    w = np.asarray(hour_weights, dtype=float)
    hours = rng.choice(24, size=n, p=w / w.sum())
    return hours * 3600 + rng.integers(0, 3600, size=n)


def ext_ids(rng, n):
    return np.char.add("EXT_", rng.integers(10_000_000, 99_999_999, size=n).astype(str))


class Rows:
    """Collects transaction rows as column arrays (fast, no per-row Python)."""

    COLS = ["acct", "day", "sec", "direction", "cp", "amount", "item_count",
            "ptype", "sloc", "rloc", "label", "is_l", "pair"]

    def __init__(self):
        self.parts = []

    def add(self, acct, day, sec, direction, cp, amount, ptype, label, *,
            item_count=1, sloc="UK", rloc="UK", is_l=0, pair=-1):
        n = len(acct)
        if n == 0:
            return
        full = lambda v, dt=None: np.full(n, v, dtype=dt) if np.isscalar(v) else np.asarray(v)
        self.parts.append(dict(
            acct=np.asarray(acct, dtype=np.int64), day=np.asarray(day, dtype=np.int64),
            sec=np.asarray(sec, dtype=np.int64), direction=full(direction, object),
            cp=full(cp, object), amount=np.asarray(amount, dtype=float),
            item_count=full(item_count, np.int64), ptype=full(ptype, object),
            sloc=full(sloc, object), rloc=full(rloc, object), label=full(label, object),
            is_l=full(is_l, np.int8), pair=full(pair, np.int64)))

    def frame(self) -> pd.DataFrame:
        if not self.parts:
            return pd.DataFrame({c: [] for c in self.COLS})
        return pd.DataFrame({c: np.concatenate([p[c] for p in self.parts]) for c in self.COLS})


def to_output(df: pd.DataFrame, account_ids: np.ndarray, prefix: str):
    """Turn internal rows into the public `transactions` and hidden `transactions_truth` frames."""
    df = df.reset_index(drop=True)
    # One txn_id per transfer: rows sharing a pair key share an id.
    key = np.where(df["pair"].to_numpy() >= 0, df["pair"].to_numpy(), -(np.arange(len(df)) + 1))
    codes, _ = pd.factorize(key)
    txn_id = (prefix + pd.Series(codes).astype(str)).to_numpy()
    sec = df["sec"].to_numpy()
    time = pd.Series(sec // 3600).astype(str).str.zfill(2) + ":" + \
        pd.Series((sec % 3600) // 60).astype(str).str.zfill(2) + ":" + \
        pd.Series(sec % 60).astype(str).str.zfill(2)
    cp = df["cp"].to_numpy(dtype=object)
    is_acct = pd.Series(cp).map(lambda c: isinstance(c, (int, np.integer))).to_numpy(dtype=bool)
    cp_out = cp.copy()
    if is_acct.any():
        cp_out[is_acct] = account_ids[cp[is_acct].astype(np.int64)]
    tx = pd.DataFrame({
        "txn_id": txn_id,
        "account_id": account_ids[df["acct"].to_numpy()],
        "direction": df["direction"].to_numpy(),
        "counterparty_id": cp_out.astype(str),
        "day": df["day"].to_numpy(),
        "time": time.to_numpy(),
        "amount": np.round(df["amount"].to_numpy(), 2),
        "item_count": df["item_count"].to_numpy(),
        "payment_type": df["ptype"].to_numpy(),
        "sender_bank_location": df["sloc"].to_numpy(),
        "receiver_bank_location": df["rloc"].to_numpy(),
    })
    truth = pd.DataFrame({"txn_id": txn_id, "is_laundering": df["is_l"].to_numpy(),
                          "laundering_type": df["label"].to_numpy()}).drop_duplicates("txn_id")
    return tx, truth
