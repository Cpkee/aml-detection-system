"""Leak and reproducibility guards for the weekly feature store (Phase 0 of the modelling plan).

Runs on a tiny synthetic dataset (3 accounts, a few rows) so it needs no simulator output.
"""
import json
import os

import pandas as pd
import pytest

from amldata import HIDDEN
from features import manifest, weekly

ACCOUNTS = pd.DataFrame({"account_id": ["A1", "A2", "A3"], "open_month": [0, 0, 1], "open_day": [0, 10, 40],
                         "income": [0.1, 0.5, 0.9], "customer_age": [20, 30, 40]})
TX_COLS = ["txn_id", "account_id", "direction", "counterparty_id", "day", "time", "amount", "item_count",
           "payment_type", "sender_bank_location", "receiver_bank_location"]


def _tx(rows):
    return pd.DataFrame([dict(zip(TX_COLS, r)) for r in rows], columns=TX_COLS)


BASE = _tx([
    ("T1", "A1", "in", "EXT_1", 2, "09:00:00", 100.0, 1, "ACH", "UK", "UK"),       # A1 week 0
    ("T2", "A1", "out", "EXT_2", 6, "10:00:00", 40.0, 1, "ACH", "UK", "UK"),       # A1 week 0 (cut-off day)
    ("T3", "A1", "in", "EXT_3", 7, "11:00:00", 500.0, 1, "ACH", "UK", "UK"),       # A1 week 1
    ("T4", "A2", "out", "CASH", 12, "12:00:00", 20.0, 1, "Cash Withdrawal", "UK", "UK"),  # A2 week 0
    ("T5", "A3", "in", "EXT_4", 55, "13:00:00", 999.0, 1, "ACH", "UK", "UK"),      # A3 week 2
])


def _write(folder, tx, accounts=ACCOUNTS):
    os.makedirs(folder, exist_ok=True)
    accounts.to_parquet(os.path.join(folder, "accounts.parquet"), index=False)
    tx.to_parquet(os.path.join(folder, "transactions.parquet"), index=False)
    with open(os.path.join(folder, "run_manifest.json"), "w") as f:
        json.dump({"seed": 1, "set": []}, f)
    return folder


def _store(folder, weeks=(0, 3)):
    weekly.build(folder, weeks, force=True)
    return weekly.load(folder).set_index(["account_id", "weeks_since_open"]).sort_index()


def test_week_windows_and_cumulative(tmp_path):
    f = _store(_write(tmp_path / "d", BASE))
    assert len(f) == 3 * 4                                        # every account x weeks 0-3, even with no rows
    a1 = f.loc["A1"]
    assert a1.loc[0, "n_rows_wk"] == 2 and a1.loc[0, "money_in_wk"] == 100 and a1.loc[0, "money_out_wk"] == 40
    assert a1.loc[1, "n_rows_wk"] == 1 and a1.loc[1, "money_in_cum"] == 600
    assert f.loc[("A3", 2), "money_in_wk"] == 999 and f.loc[("A3", 1), "n_rows_wk"] == 0   # A3 opened day 40


def test_features_never_peek_past_the_cutoff(tmp_path):
    before = _store(_write(tmp_path / "d", BASE))
    late = _tx([("T9", "A1", "in", "EXT_9", 7, "00:00:01", 1e6, 1, "ACH", "UK", "UK")])   # day 7 = A1 week 1
    after = _store(_write(tmp_path / "e", pd.concat([BASE, late])))
    assert after.loc[("A1", 0)].equals(before.loc[("A1", 0)])     # week 0 unchanged by a week-1 row
    assert after.loc[("A1", 1), "money_in_wk"] == before.loc[("A1", 1), "money_in_wk"] + 1e6
    assert after.drop(index="A1", level=0).equals(before.drop(index="A1", level=0))


def test_rebuild_is_byte_identical(tmp_path):
    folder = _write(tmp_path / "d", BASE)
    p, _ = weekly.build(folder, (0, 3), force=True)
    first = open(p, "rb").read()
    weekly.build(folder, (0, 3), force=True)
    assert open(p, "rb").read() == first


def test_speed_counts_transfers_only_and_caps_at_the_inflow(tmp_path):
    tx = _tx([
        ("S1", "A2", "in", "EXT_P", 11, "10:00:00", 200.0, 1, "ACH", "UK", "UK"),            # transfer in
        ("S2", "A2", "out", "EXT_Q", 11, "10:10:00", 80.0, 1, "ACH", "UK", "UK"),            # +10 min
        ("S3", "A2", "out", "CARD_MERCHANTS", 11, "10:20:00", 30.0, 1, "Debit card", "UK", "UK"),  # not a transfer
        ("S4", "A2", "out", "EXT_R", 11, "10:30:00", 50.0, 1, "Cross-border", "UK", "Spain"),  # +30 min
        ("S5", "A2", "out", "EXT_S", 11, "15:00:00", 40.0, 1, "ACH", "UK", "UK"),            # +5 h
        ("S6", "A2", "out", "EXT_T", 11, "16:00:00", 90.0, 1, "ACH", "UK", "UK"),            # +6 h, over the cap
        ("S7", "A2", "in", "EXT_P", 12, "09:00:00", 10.0, 1, "ACH", "UK", "UK"),             # same payer again
    ])
    f = _store(_write(tmp_path / "d", tx))
    w0 = f.loc[("A2", 0)]                                         # A2 opens day 10: days 10-16 are week 0
    assert w0["fwd_1h_share_wk"] == (80 + 50) / 210               # card row ignored; within 1 h of the 200 in
    assert w0["fwd_24h_share_wk"] == 200 / 210                    # 80 + 50 + 40 + only 30 of the 90 (cap 200)
    assert w0["n_payers_wk"] == 1 and w0["n_payers_cum"] == 1    # one payer, paid twice
    assert w0["n_payees_wk"] == 4                                 # card merchants are not payees
    assert w0["abroad_out_share_cum"] == 50 / 290
    assert pd.isna(f.loc[("A2", 1), "fwd_1h_share_wk"])            # no transfer in that week: no share, not 1.0


def test_self_vs_past_waits_for_four_weeks_and_peers_use_training_months(tmp_path):
    f = _store(_write(tmp_path / "d", BASE), weeks=(0, 5))
    assert f.loc[pd.IndexSlice[:, 0:3], "self_vs_past_money_in"].isna().all()
    late = ACCOUNTS.iloc[[0]].assign(account_id="A9", open_month=5, open_day=150)     # A1's income and age band
    rich = _tx([("T9", "A9", "in", "EXT_9", 151, "10:00:00", 1e6, 1, "ACH", "UK", "UK")])
    g = _store(_write(tmp_path / "e", pd.concat([BASE, rich]), pd.concat([ACCOUNTS, late])), weeks=(0, 5))
    assert g.loc[("A9", 0), "money_in_wk"] == 1e6
    assert g.drop(index="A9", level=0).equals(f)                  # a month-5 account never moves the peer medians


def test_no_feature_named_after_hidden_data():
    bad = [c for c in weekly.FEATURES if c == "txn_id" or any(h in c for h in HIDDEN)]
    assert not bad, bad


def test_manifest_refuses_stale_store(tmp_path):
    folder = _write(tmp_path / "d", BASE)
    weekly.build(folder, (0, 3), force=True)
    manifest.check(folder, weekly.FEATURES, (0, 3))
    with pytest.raises(ValueError):                                # asks for weeks the store does not hold
        manifest.check(folder, weekly.FEATURES, (0, 10))
    with pytest.raises(ValueError):                                # a different feature list
        manifest.check(folder, weekly.FEATURES + ["extra"], (0, 3))
    with open(os.path.join(folder, "run_manifest.json"), "w") as f:
        json.dump({"seed": 2, "set": []}, f)                       # the data run changed underneath
    with pytest.raises(ValueError):
        weekly.load(folder)
