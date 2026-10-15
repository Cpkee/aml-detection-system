"""Phase 3 gate on real simulator output: the weekly feature store is correct, leak-free and reproducible.

  1. Independent re-implementation: every one of the 28 features is recomputed in plain pandas (merge_asof, groupby,
     cumsum) from the definitions in src/features/weekly.py, on 3 seeded samples of real accounts (each 300 random +
     60 launderers, weeks 0-78), and
     must equal the DuckDB store (relative tolerance 1e-9, NaN where the store has NULL).
  2. No peeking: test-month accounts' transactions are cut at a random week each; every feature up to that week, and
     every feature of every other account, must be bit-identical to the uncut build.
  3. Reproducible: two builds of the sample are byte-identical parquet files.
  4. Whole-store invariants on <SIM_OUT>/features/weekly.parquet (skipped until it is built): complete keys, shares in
     [0, 1], running totals never fall, money and row totals equal the transactions file, frozen peer medians equal a
     recomputation from training months.

Run: PYTHONPATH=src SIM_OUT=data/v1_full pytest -q tests/test_feature_store.py
"""
import json
import os

import numpy as np
import pandas as pd
import pytest

import amldata
from features import manifest, weekly

OUT = os.environ.get("SIM_OUT", "data/v1")
W_MAX = 78
N_RANDOM, N_LAUNDERERS = 300, 60
SEEDS = (20261015, 7, 2024)                     # three independent samples
STORE = os.path.join(OUT, "features", "weekly.parquet")

needs_data = pytest.mark.skipif(not os.path.exists(os.path.join(OUT, "transactions.parquet")),
                                reason="no simulator output")
needs_store = pytest.mark.skipif(not os.path.exists(STORE), reason="feature store not built for SIM_OUT")


# ---------------------------------------------------------------- sample of real accounts
def _sample_ids(seed: int) -> list[str]:
    """300 accounts drawn by a seeded hash plus 60 launderers (so bursts, internal hops and closures are covered)."""
    con = amldata.evaluation(OUT)                   # test code only: to make sure launderers are in the sample
    rnd = con.execute(f"""SELECT account_id FROM accounts ORDER BY md5(account_id || '{seed}') LIMIT {N_RANDOM}""").df()
    lau = con.execute(f"""SELECT account_id FROM accounts_truth WHERE is_launderer = 1
                          ORDER BY md5(account_id || '{seed}') LIMIT {N_LAUNDERERS}""").df()
    return sorted(set(rnd.account_id) | set(lau.account_id))


def _write_sample(folder, ids, seed, cut: dict | None = None):
    """Copy the sample's accounts and transactions (optionally cut per account at a day) into a data folder."""
    os.makedirs(folder, exist_ok=True)
    con = amldata.public(OUT)
    con.register("ids", pd.DataFrame({"account_id": ids}))
    acc = con.execute("SELECT a.* FROM accounts a JOIN ids USING (account_id) ORDER BY account_id").df()
    tx = con.execute("SELECT t.* FROM transactions t JOIN ids USING (account_id) ORDER BY day, time, txn_id").df()
    if cut:
        last = tx["account_id"].map(cut)
        tx = tx[last.isna() | (tx["day"] <= last)].reset_index(drop=True)
    acc.to_parquet(os.path.join(folder, "accounts.parquet"), index=False)
    tx.to_parquet(os.path.join(folder, "transactions.parquet"), index=False)
    with open(os.path.join(folder, "run_manifest.json"), "w") as f:
        json.dump({"sample_of": OUT, "seed": seed, "cut": bool(cut)}, f)
    return acc, tx


@pytest.fixture(scope="module", params=SEEDS, ids=lambda s: f"seed{s}")
def sample(request, tmp_path_factory):
    seed = request.param
    folder = str(tmp_path_factory.mktemp(f"sample{seed}"))
    ids = _sample_ids(seed)
    acc, tx = _write_sample(folder, ids, seed)
    weekly.build(folder, (0, W_MAX), force=True)
    store = weekly.load(folder)
    return folder, ids, acc, tx, store, seed


# ---------------------------------------------------------------- independent pandas implementation
def reference(acc: pd.DataFrame, tx: pd.DataFrame, w_max: int = W_MAX) -> pd.DataFrame:
    """All 28 features from the written definitions, with pandas only (no SQL)."""
    a = acc.set_index("account_id")
    t = tx.copy()
    t["open_day"] = t["account_id"].map(a["open_day"])
    t = t[t["day"] <= t["open_day"] + 7 * w_max + 6]
    t["w"] = (t["day"] - t["open_day"]) // 7
    hms = t["time"].str.split(":", expand=True).astype(int)
    t["ts"] = t["day"] * 86400 + hms[0] * 3600 + hms[1] * 60 + hms[2]
    t = t.sort_values(["account_id", "day", "time", "txn_id"], kind="mergesort").reset_index(drop=True)
    inn, out = t["direction"] == "in", t["direction"] == "out"
    payer = inn & (t["counterparty_id"] != "CASH")
    payee = out & ~t["counterparty_id"].isin(["CASH", "CARD_MERCHANTS"])

    grid = pd.MultiIndex.from_product([a.index, range(w_max + 1)], names=["account_id", "w"])
    g = pd.DataFrame(index=grid)
    by = [t["account_id"], t["w"]]

    def add(name, series, fill=0.0):
        g[name] = series.reindex(grid).fillna(fill) if fill is not None else series.reindex(grid)

    add("n_rows_wk", t.groupby(by).size())
    add("n_in_wk", inn.groupby(by).sum())
    add("n_out_wk", out.groupby(by).sum())
    add("money_in_wk", t["amount"].where(inn, 0).groupby(by).sum())
    add("money_out_wk", t["amount"].where(out, 0).groupby(by).sum())
    add("max_in_wk", t[inn].groupby(["account_id", "w"])["amount"].max())
    add("max_out_wk", t[out].groupby(["account_id", "w"])["amount"].max())
    add("card_items_wk", t[t["counterparty_id"] == "CARD_MERCHANTS"].groupby(["account_id", "w"])["item_count"].sum())
    add("n_payers_wk", t[payer].groupby(["account_id", "w"])["counterparty_id"].nunique())
    add("n_payees_wk", t[payee].groupby(["account_id", "w"])["counterparty_id"].nunique())
    first_any = ~t.duplicated(["account_id", "counterparty_id"])          # first row ever with this counterparty
    add("n_new_payers", t[payer & first_any].groupby(["account_id", "w"])["counterparty_id"].nunique())
    first_payer_rows = t[payer].drop_duplicates(["account_id", "counterparty_id"])
    first_payee_rows = t[payee].drop_duplicates(["account_id", "counterparty_id"])
    add("first_payers", first_payer_rows.groupby(["account_id", "w"]).size())
    add("first_payees", first_payee_rows.groupby(["account_id", "w"]).size())
    ach_in = inn & (t["payment_type"] == "ACH")
    add("transfer_in", t["amount"].where(ach_in, 0).groupby(by).sum())
    add("cash_in", t["amount"].where(inn & (t["payment_type"] == "Cash Deposit"), 0).groupby(by).sum())
    add("internal_out", t["amount"].where(out & t["counterparty_id"].str.startswith("A"), 0).groupby(by).sum())
    add("abroad_out", t["amount"].where(out & (t["receiver_bank_location"] != "UK"), 0).groupby(by).sum())
    add("hr_out", t["amount"].where(out & t["receiver_bank_location"].isin(weekly.HIGH_RISK), 0).groupby(by).sum())

    # median minutes from the latest payment in (any kind) to each payment out
    o = t[out][["account_id", "w", "ts"]].sort_values("ts")
    i = t[inn][["account_id", "ts"]].rename(columns={"ts": "ts_in"}).sort_values("ts_in")
    d = pd.merge_asof(o, i, left_on="ts", right_on="ts_in", by="account_id").dropna(subset=["ts_in"])
    add("med_in_out_minutes_wk", ((d["ts"] - d["ts_in"]) / 60.0).groupby([d["account_id"], d["w"]]).median(), fill=None)

    # forwarding: transfers out after the latest transfer in, each inflow passed on at most once
    ti = t[ach_in][["account_id", "ts", "amount"]].sort_values(["account_id", "ts", "amount"], kind="mergesort")
    ti["in_id"] = ti.groupby("account_id").cumcount()
    ti = ti.rename(columns={"ts": "ts_in", "amount": "in_amt"}).sort_values("ts_in")
    to = t[out & t["payment_type"].isin(["ACH", "Cross-border"])][["account_id", "w", "ts", "amount"]].sort_values("ts")
    f = pd.merge_asof(to, ti, left_on="ts", right_on="ts_in", by="account_id").dropna(subset=["ts_in"])
    f = f.sort_values(["account_id", "in_id", "ts", "amount"], kind="mergesort")
    delay = f["ts"] - f["ts_in"]
    for lim, name in [(3600, "fwd_1h"), (86400, "fwd_24h")]:
        amt = f["amount"].where(delay <= lim, 0.0)
        prior = amt.groupby([f["account_id"], f["in_id"]]).cumsum() - amt
        f[name] = np.where(delay <= lim, np.clip(np.minimum(f["amount"], f["in_amt"] - prior), 0, None), 0.0)
        add(name, f.groupby(["account_id", "w"])[name].sum())

    g = g.reset_index()
    acct = g.groupby("account_id")
    r = pd.DataFrame({"account_id": g["account_id"], "weeks_since_open": g["w"]})
    for c in ["n_rows_wk", "n_in_wk", "n_out_wk", "money_in_wk", "money_out_wk", "max_in_wk", "max_out_wk",
              "card_items_wk", "n_payers_wk", "n_payees_wk", "med_in_out_minutes_wk"]:
        r[c] = g[c]
    for c in ["n_rows", "money_in", "money_out"]:
        r[f"{c}_cum"] = acct[f"{c}_wk"].cumsum()
    r["new_payer_share_wk"] = g["n_new_payers"] / g["n_payers_wk"].replace(0, np.nan)
    r["n_payers_cum"] = acct["first_payers"].cumsum()
    r["n_payees_cum"] = acct["first_payees"].cumsum()
    r["passthrough_wk"] = np.minimum(g["money_out_wk"], g["money_in_wk"]) / g["money_in_wk"].replace(0, np.nan)
    for name in ["fwd_1h", "fwd_24h"]:
        r[f"{name}_share_wk"] = np.where(g["transfer_in"] > 0, np.minimum(1.0, g[name] / g["transfer_in"].where(
            g["transfer_in"] > 0, 1.0)), np.nan)

    def self_vs_past(x: pd.Series) -> pd.Series:
        vals, res = x.to_numpy(dtype=float), np.full(len(x), np.nan)
        for k in range(weekly.SELF_MIN_WEEKS, len(vals)):
            past = vals[:k]
            med = np.median(past)
            mad = np.median(np.abs(past - med))
            if mad != 0:
                res[k] = (vals[k] - med) / mad
        return pd.Series(res, index=x.index)

    for name, col in [("money_in", "money_in_wk"), ("payers", "n_payers_wk"), ("rows", "n_rows_wk")]:
        r[f"self_vs_past_{name}"] = g.groupby("account_id")[col].transform(self_vs_past)

    meta = a.loc[g["account_id"], ["open_month", "income", "customer_age"]].reset_index(drop=True)
    gm = pd.concat([g[["w", "money_in_wk"]], meta], axis=1)
    peer = gm[gm["open_month"].isin(weekly.PEER_MONTHS)].groupby(["income", "customer_age", "w"])["money_in_wk"].median()
    pm = pd.MultiIndex.from_frame(gm[["income", "customer_age", "w"]]).map(lambda k: peer.get(k, np.nan))
    r["peer_ratio_money_in"] = g["money_in_wk"] / pd.Series(np.asarray(pm, dtype=float)).replace(0, np.nan)

    cs = lambda c: acct[c].cumsum()
    r["internal_out_share_cum"] = cs("internal_out") / cs("money_out_wk").replace(0, np.nan)
    r["cash_in_share_cum"] = cs("cash_in") / cs("money_in_wk").replace(0, np.nan)
    r["abroad_out_share_cum"] = cs("abroad_out") / cs("money_out_wk").replace(0, np.nan)
    r["high_risk_out_share_cum"] = cs("hr_out") / cs("money_out_wk").replace(0, np.nan)
    return r[weekly.KEYS + weekly.FEATURES]


# ---------------------------------------------------------------- 1. independent re-implementation
@needs_data
def test_every_feature_matches_an_independent_pandas_implementation(sample):
    folder, ids, acc, tx, store, _ = sample
    ref = reference(acc, tx)
    s = store.sort_values(weekly.KEYS).reset_index(drop=True)
    ref = ref.sort_values(weekly.KEYS).reset_index(drop=True)
    assert len(s) == len(ids) * (W_MAX + 1) and (s[weekly.KEYS] == ref[weekly.KEYS]).all().all()
    bad = {}
    for c in weekly.FEATURES:
        a, b = s[c].to_numpy(dtype=float), ref[c].to_numpy(dtype=float)
        ok = np.isclose(a, b, rtol=1e-9, atol=1e-9, equal_nan=True)
        if not ok.all():
            k = np.flatnonzero(~ok)[0]
            bad[c] = f"{(~ok).sum()} of {len(ok)} differ, e.g. {s.loc[k, weekly.KEYS].tolist()}: store {a[k]} vs {b[k]}"
    assert not bad, bad
    # the sample really exercises the hard features (otherwise agreement would prove little)
    assert (s["fwd_1h_share_wk"] > 0).sum() >= 50 and (s["internal_out_share_cum"] > 0).sum() >= 50
    assert s["self_vs_past_money_in"].notna().sum() >= 1000 and s["peer_ratio_money_in"].notna().sum() >= 1000


# ---------------------------------------------------------------- 2. no peeking, on real data
@needs_data
def test_cutting_future_transactions_changes_nothing_up_to_the_cut(sample, tmp_path):
    folder, ids, acc, tx, store, seed = sample
    rng = np.random.default_rng(seed)
    late = acc[acc["open_month"] >= 5]                      # not training months, so peer medians stay fixed
    assert len(late) >= 50
    k = pd.Series(rng.integers(0, W_MAX + 1, len(late)), index=late["account_id"].to_numpy())
    cut_day = (late.set_index("account_id")["open_day"] + 7 * k + 6).to_dict()
    _, tx_cut = _write_sample(str(tmp_path / "cut"), ids, seed, cut_day)
    assert len(tx_cut) < len(tx)                            # the cut removed real rows
    weekly.build(str(tmp_path / "cut"), (0, W_MAX), force=True)
    cut = weekly.load(str(tmp_path / "cut")).set_index(weekly.KEYS).sort_index()
    full = store.set_index(weekly.KEYS).sort_index()
    wk = cut.index.get_level_values("weeks_since_open").to_numpy()
    limit = cut.index.get_level_values("account_id").map(lambda x: k.get(x, W_MAX)).to_numpy()
    keep = wk <= limit
    assert full[keep].equals(cut[keep])                     # identical values (NaN-aware), every column
    changed = (full[~keep].fillna(-1) != cut[~keep].fillna(-1)).any(axis=1).sum()
    assert changed > 0                                      # and the cut did change later weeks (test has teeth)


# ---------------------------------------------------------------- 3. reproducible
@needs_data
def test_rebuild_of_real_sample_is_byte_identical(sample):
    folder = sample[0]
    p, _ = weekly.build(folder, (0, W_MAX), force=True)
    first = open(p, "rb").read()
    weekly.build(folder, (0, W_MAX), force=True)
    assert open(p, "rb").read() == first


# ---------------------------------------------------------------- 4. whole-store invariants
@needs_store
def test_whole_store_invariants():
    m = manifest.check(OUT, weekly.FEATURES)
    con = amldata.public(OUT)
    con.execute(f"CREATE VIEW s AS SELECT * FROM read_parquet('{STORE}')")
    q = lambda sql: con.execute(sql).fetchone()
    n_acc = q("SELECT count(*) FROM accounts")[0]
    w_lo, w_hi = m["weeks"]
    n, n_keys = q("SELECT count(*), count(DISTINCT (account_id, weeks_since_open)) FROM s")
    assert n == n_keys == n_acc * (w_hi - w_lo + 1) == m["rows"]

    counts = ["n_rows_wk", "n_in_wk", "n_out_wk", "money_in_wk", "money_out_wk", "max_in_wk", "max_out_wk",
              "card_items_wk", "n_payers_wk", "n_payees_wk", "n_rows_cum", "money_in_cum", "money_out_cum",
              "n_payers_cum", "n_payees_cum"]
    assert q(" + ".join(f"count(*) FILTER (WHERE {c} IS NULL OR {c} < 0)" for c in counts).join(["SELECT ", " FROM s"]))[0] == 0
    shares = ["new_payer_share_wk", "passthrough_wk", "fwd_1h_share_wk", "fwd_24h_share_wk", "internal_out_share_cum",
              "cash_in_share_cum", "abroad_out_share_cum", "high_risk_out_share_cum"]
    assert q(" + ".join(f"count(*) FILTER (WHERE {c} < 0 OR {c} > 1 + 1e-12)" for c in shares).join(["SELECT ", " FROM s"]))[0] == 0
    assert q("""SELECT count(*) FROM s WHERE n_payers_wk > n_in_wk OR n_payees_wk > n_out_wk
                OR max_in_wk > money_in_wk + 1e-6 OR max_out_wk > money_out_wk + 1e-6
                OR fwd_1h_share_wk > fwd_24h_share_wk + 1e-12 OR high_risk_out_share_cum > abroad_out_share_cum + 1e-12
                OR (weeks_since_open < 4 AND (self_vs_past_money_in IS NOT NULL OR self_vs_past_payers IS NOT NULL
                                              OR self_vs_past_rows IS NOT NULL))""")[0] == 0
    # running totals never fall
    assert q("""SELECT count(*) FROM (SELECT n_rows_cum - lag(n_rows_cum) OVER a AS d1, money_in_cum - lag(money_in_cum) OVER a AS d2,
                                             money_out_cum - lag(money_out_cum) OVER a AS d3, n_payers_cum - lag(n_payers_cum) OVER a AS d4,
                                             n_payees_cum - lag(n_payees_cum) OVER a AS d5
                                      FROM s WINDOW a AS (PARTITION BY account_id ORDER BY weeks_since_open))
                WHERE d1 < 0 OR d2 < -1e-6 OR d3 < -1e-6 OR d4 < 0 OR d5 < 0""")[0] == 0
    # nothing lost or counted twice: per account, the last week's totals equal the transactions file (whole window)
    if w_lo == 0 and w_hi >= 78:
        diff = q(f"""WITH tot AS (SELECT account_id, count(*) n, sum(amount) FILTER (WHERE direction = 'in') i,
                                         sum(amount) FILTER (WHERE direction = 'out') o FROM transactions GROUP BY 1)
                     SELECT count(*), max(abs(s.n_rows_cum - coalesce(tot.n, 0))),
                            max(abs(s.money_in_cum - coalesce(tot.i, 0))), max(abs(s.money_out_cum - coalesce(tot.o, 0)))
                     FROM s LEFT JOIN tot USING (account_id) WHERE s.weeks_since_open = {w_hi}""")
        assert diff[0] == n_acc and diff[1] == 0 and diff[2] < 1e-3 and diff[3] < 1e-3, diff
    # the frozen peer medians are exactly the training months' medians
    peers = os.path.join(OUT, "features", weekly.PEERS)
    months = ", ".join(map(str, weekly.PEER_MONTHS))
    bad = q(f"""WITH r AS (SELECT a.income, a.customer_age, s.weeks_since_open AS w, median(s.money_in_wk) AS m
                           FROM s JOIN accounts a USING (account_id) WHERE a.open_month IN ({months}) GROUP BY 1, 2, 3)
                SELECT count(*) FILTER (WHERE r.m IS DISTINCT FROM p.peer_median_money_in), count(*)
                FROM r FULL JOIN read_parquet('{peers}') p USING (income, customer_age, w)""")
    assert bad[0] == 0 and bad[1] > 0
