"""
EDA for the simulator output, v1 (default: the full-size run in data/v1_full).

Copy of eda_sim_v0.py (left unchanged for the v0 report). Differences from v0:
  - reads data/v1_full and writes outputs/eda/v1_full/ (override with env vars EDA_DATA / EDA_OUT,
    e.g. EDA_DATA=data/v1 EDA_OUT=outputs/eda/v1_50k python src/sim/eda/eda_sim_v1.py)
  - figures are saved (v0 passed them to print() instead of savefig())
  - txn_id note updated: ids are anonymous since 7 Oct 2026
  - the transaction pass (sections 2, 7, 8, 9, 11) runs in DuckDB instead of pandas: v0's pandas version
    peaked at ~11 GB on 50k accounts and would need ~50 GB at 244k. Same statistics, checked on data/v1.
    The cache now holds parquet files (acct_day, weekly_panel) instead of pickles.

Run from the repo root:  venv/bin/python src/sim/eda/eda_sim_v1.py
"""

# %% ---------------------------------------------------------------- 1. config
from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

if "ipykernel" not in sys.modules:  # plain script run: draw off-screen; Interactive Window keeps inline figures
    matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=FutureWarning)

# --- paths -------------------------------------------------------------------
def find_repo_root(marker: str = "configs/sim.yaml") -> Path:
    try:
        start = Path(__file__).resolve().parent
    except NameError:  # Interactive Window / REPL
        start = Path.cwd().resolve()
    for d in [start, *start.parents]:
        if (d / marker).exists():
            return d
    raise FileNotFoundError(
        f"could not find '{marker}' in {start} or any parent.\n"
        f"Either run the simulator first, or set ROOT by hand below."
    )

ROOT = find_repo_root()
#ROOT = Path(r"C:/Users/FILE")   # uncomment and edit if auto-detect fails

# Full-size run (parquet, 244k accounts / ~109M txns). 50k run: EDA_DATA=data/v1
DATA_DIR = ROOT / os.environ.get("EDA_DATA", "data/v1_full")
OUT_DIR = ROOT / os.environ.get("EDA_OUT", "outputs/eda/v1_full")
CACHE_DIR = DATA_DIR / "eda_cache"

# --- knobs -------------------------------------------------------------------
CHUNK_ROWS = 1_000_000  # rows per streaming batch
USE_CACHE = True  # reuse <DATA_DIR>/eda_cache/* if present
NIGHT_HOURS = range(0, 6)  # 00:00-05:59 counted as "night"
TOP_N_CAT = 12  # categories shown per bar chart
SAVE_FIGS = True

OUT_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Columns the simulator writes as ground truth. Not to be used as model features.
TRUTH_COLS = [
    "profile",
    "baf_fraud_bool",
    "network_id",
    "is_launderer",
    "launder_start_day",
    "laundered_in",
    "laundered_out",
]
LABEL = "is_launderer"
_report_lines: list[str] = []


def log(msg: str = "") -> None:
    """Print and accumulate into <OUT_DIR>/eda_report.md."""
    print(msg)
    _report_lines.append(str(msg))


def header(title: str) -> None:
    log("\n" + "=" * 78)
    log(title)
    log("=" * 78)


def savefig(fig, name: str) -> None:
    if not SAVE_FIGS:
        plt.close(fig)
        return
    path = OUT_DIR / f"{name}.png"
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    print(f"  [fig] {path}")

def resolve(stem: str) -> Path:
    """Find <stem>.parquet, <stem>.csv or <stem>_SAMPLE.csv in DATA_DIR."""
    for cand in (f"{stem}.parquet", f"{stem}.csv", f"{stem}_SAMPLE.csv"):
        p = DATA_DIR / cand
        if p.exists():
            return p
    raise FileNotFoundError(f"no file for '{stem}' in {DATA_DIR.resolve()}")

def load(stem: str, columns: list[str] | None = None) -> pd.DataFrame:
    p = resolve(stem)
    if p.suffix == ".parquet":
        return pd.read_parquet(p, columns=columns)
    return pd.read_csv(p, usecols=columns)

def iter_chunks(stem: str, columns: list[str]):
    """Yield DataFrame batches from parquet (row groups) or CSV (chunksize)."""
    p = resolve(stem)
    if p.suffix == ".parquet":
        import pyarrow.parquet as pq

        pf = pq.ParquetFile(p)
        for batch in pf.iter_batches(batch_size=CHUNK_ROWS, columns=columns):
            yield batch.to_pandas()
    else:
        for chunk in pd.read_csv(p, usecols=columns, chunksize=CHUNK_ROWS):
            yield chunk


import duckdb

con = duckdb.connect()
con.execute("PRAGMA memory_limit='6GB'")
con.execute(f"PRAGMA temp_directory='{(CACHE_DIR / 'duckdb_tmp').as_posix()}'")


def rel(stem: str) -> str:
    """DuckDB table expression for a data file (parquet or CSV sample)."""
    p = resolve(stem).as_posix()
    return f"read_parquet('{p}')" if p.endswith(".parquet") else f"read_csv_auto('{p}')"


def auc_vs_label(x: pd.Series, y: np.ndarray) -> float:
    """Rank-based AUC (Mann-Whitney). NaNs ranked as the lowest values."""
    y = np.asarray(y).astype(bool)
    n_pos, n_neg = y.sum(), (~y).sum()
    if n_pos == 0 or n_neg == 0:
        return np.nan
    r = pd.Series(x).rank(method="average", na_option="bottom").to_numpy()
    return (r[y].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)


log(f"ROOT     : {ROOT}")
log(f"DATA_DIR : {DATA_DIR.resolve()}")
log(f"OUT_DIR  : {OUT_DIR.resolve()}")
log(f"pandas {pd.__version__} | python {sys.version.split()[0]}")

# %% ------------------------------------------------- 2. load the small tables
header("2. FILE INVENTORY")

accounts = load("accounts")
accounts_truth = load("accounts_truth")
# transactions_truth has one row per transfer (~106M at 244k accounts): summarise it in DuckDB
txn_truth_rows = con.execute(f"SELECT count(*) FROM {rel('transactions_truth')}").fetchone()[0]
txn_truth_cols = len(con.execute(f"DESCRIBE SELECT * FROM {rel('transactions_truth')}").fetchall())
try:
    aml_alerts = load("aml_alerts")
except FileNotFoundError:
    aml_alerts = pd.DataFrame()
try:
    aml_outcomes = load("aml_outcomes")
except FileNotFoundError:
    aml_outcomes = pd.DataFrame()

txn_path = resolve("transactions")
txn_size_mb = txn_path.stat().st_size / 1e6

for nm, (nr, nc) in [
    ("accounts", accounts.shape),
    ("accounts_truth", accounts_truth.shape),
    ("transactions_truth", (txn_truth_rows, txn_truth_cols)),
    ("aml_alerts", aml_alerts.shape),
    ("aml_outcomes", aml_outcomes.shape),
]:
    log(f"{nm:<20} {nr:>10,} rows x {nc:>2} cols")
log(f"{'transactions':<20} {'(streamed)':>10}      {txn_path.name}  {txn_size_mb:,.0f} MB")

# key integrity
acc_ids = pd.Index(accounts["account_id"])
log("")
log(f"account_id unique in accounts        : {acc_ids.is_unique}")
log(f"accounts_truth covers every account  : {accounts_truth['account_id'].isin(acc_ids).all()}")
log(f"row counts match (accounts == truth) : {len(accounts) == len(accounts_truth)}")
if len(aml_alerts) == 0:
    log("aml_alerts is EMPTY -> the 6-rules module has not been written yet;")
    log("  any 'alert-based' baseline or review-capacity comparison is blocked on it.")
if len(aml_outcomes):
    log(f"aml_outcomes non-null alert days      : {aml_outcomes['aml_alert_day'].notna().sum():,}")

acc = accounts.merge(accounts_truth, on="account_id", how="left", validate="1:1")
acc_index = pd.Index(acc["account_id"])  # positional lookup used by the streaming pass
y = acc[LABEL].to_numpy()

# %% ---------------------------------------------- 3. schema & missingness
header("3. SCHEMA, DTYPES, MISSINGNESS, SENTINELS")

feature_cols = [c for c in accounts.columns if c != "account_id"]
num_cols = accounts[feature_cols].select_dtypes("number").columns.tolist()
cat_cols = [c for c in feature_cols if c not in num_cols]

log(f"{len(num_cols)} numeric, {len(cat_cols)} categorical feature columns")
log(f"categoricals: {cat_cols}")

na = accounts.isna().mean()
na = na[na > 0].sort_values(ascending=False)
log(f"\ntrue NaNs: {'none' if na.empty else ''}")
if not na.empty:
    log(na.to_string())

# BAF encodes missing as -1 (and intended_balcon_amount as negative), not NaN.
log("\nnegative-coded missingness (BAF sentinels, NOT real NaN):")
sent = {c: float((accounts[c] < 0).mean()) for c in num_cols if (accounts[c] < 0).any()}
log(pd.Series(sent).sort_values(ascending=False).to_frame("share_negative").to_string())
log("\n  -> treat these as missing indicators before modelling; a raw -1 is not 'one month'.")

log("\ncategorical cardinality:")
log(accounts[cat_cols].nunique().to_string())

# %% ------------------------------------------------------- 4. label landscape
header("4. LABEL LANDSCAPE")

n = len(acc)
log(f"accounts                     : {n:,}")
log(f"is_launderer  (model target) : {acc[LABEL].sum():,}  ({acc[LABEL].mean():.3%})")
log(f"baf_fraud_bool (onboarding)  : {acc['baf_fraud_bool'].sum():,}  ({acc['baf_fraud_bool'].mean():.3%})")

log("\nprofile mix:")
prof = acc["profile"].value_counts(dropna=False)
log(pd.DataFrame({"n": prof, "share": prof / n}).to_string())

log("\nprofile x is_launderer:")
log(pd.crosstab(acc["profile"], acc[LABEL]).to_string())

log("\nbaf_fraud_bool x is_launderer  (this is the authored onboarding<->laundering link")
log("that replaces the rho/p linkage parameter from the SAML-D+BAF join):")
ct = pd.crosstab(acc["baf_fraud_bool"], acc[LABEL])
log(ct.to_string())

if ct.shape == (2, 2):
    a_, b_, c_, d_ = ct.iloc[0, 0], ct.iloc[0, 1], ct.iloc[1, 0], ct.iloc[1, 1]
    p_l_given_f = d_ / (c_ + d_) if (c_ + d_) else np.nan
    p_l_given_nf = b_ / (a_ + b_) if (a_ + b_) else np.nan
    phi = (a_ * d_ - b_ * c_) / np.sqrt(
        max((a_ + b_) * (c_ + d_) * (a_ + c_) * (b_ + d_), 1)
    )
    log(f"\n  P(launderer | baf_fraud=1) = {p_l_given_f:.3%}")
    log(f"  P(launderer | baf_fraud=0) = {p_l_given_nf:.3%}")
    log(f"  lift                       = {p_l_given_f / p_l_given_nf:,.1f}x" if p_l_given_nf else "")
    log(f"  phi coefficient            = {phi:.4f}")
    log("\n  Report this number explicitly. It is the simulator's answer to 'how are the two")
    log("  datasets related', and unlike the join it is known exactly rather than assumed.")

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
prof.plot(kind="barh", ax=axes[0], color="#4c72b0")
axes[0].set_title("profile mix")
axes[0].set_xlabel("accounts")
(ct / ct.values.sum()).plot(kind="bar", stacked=True, ax=axes[1])
axes[1].set_title("baf_fraud_bool x is_launderer (share of all accounts)")
axes[1].set_yscale("log")
savefig(fig, "04_label_landscape")

# %% ------------------------------- 5. onboarding features vs the label
header("5. ONBOARDING (BAF) FEATURES VS is_launderer")

if acc[LABEL].sum() >= 5:
    rows = []
    for c in num_cols:
        rows.append(
            {
                "feature": c,
                "auc": auc_vs_label(acc[c], y),
                "mean_pos": acc.loc[y == 1, c].mean(),
                "mean_neg": acc.loc[y == 0, c].mean(),
            }
        )
    uni = pd.DataFrame(rows)
    uni["sep"] = (uni["auc"] - 0.5).abs()
    uni = uni.sort_values("sep", ascending=False).drop(columns="sep")
    log("univariate AUC vs is_launderer (0.5 = no signal):")
    log(uni.head(20).to_string(index=False, float_format=lambda v: f"{v:,.4f}"))
    uni.to_csv(OUT_DIR / "univariate_auc_onboarding.csv", index=False)

    top = uni.head(8)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(top["feature"][::-1], (top["auc"] - 0.5)[::-1], color="#c44e52")
    ax.axvline(0, color="k", lw=0.8)
    ax.set_xlabel("AUC - 0.5")
    ax.set_title("strongest onboarding features (univariate)")
    savefig(fig, "05_univariate_auc")

    log("\ncategorical features: P(launderer) by level")
    for c in cat_cols:
        g = acc.groupby(c)[LABEL].agg(["size", "mean"])
        g = g[g["size"] >= max(20, 0.001 * n)].sort_values("mean", ascending=False)
        if len(g):
            log(f"\n-- {c}")
            log(g.head(TOP_N_CAT).to_string(float_format=lambda v: f"{v:,.4f}"))
else:
    log("too few positives in this file for univariate analysis (expected on the sample).")

# %% ------------------------------------------ 6. time structure of the panel
header("6. TIME STRUCTURE (concern #2: changing cohort composition)")

log("account opening:")
log(acc[["open_month", "open_day"]].describe().to_string())
log("\naccounts opened per open_month:")
om = acc.groupby("open_month").agg(n=("account_id", "size"), launder_rate=(LABEL, "mean"))
log(om.to_string(float_format=lambda v: f"{v:,.4f}"))

ls = acc["launder_start_day"].dropna()
if len(ls):
    log(f"\nlaunder_start_day: n={len(ls):,}  min={ls.min():.0f}  med={ls.median():.0f}  max={ls.max():.0f}")
    lag = (acc["launder_start_day"] - acc["open_day"]).dropna()
    log(f"lag from open_day to launder_start_day: med={lag.median():.0f} days, "
        f"p10={lag.quantile(.1):.0f}, p90={lag.quantile(.9):.0f}")
    log("  -> this lag sets the earliest week a mule is detectable. If your weekly panel")
    log("     starts before it, those weeks are structurally unlabelable, not just hard.")

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].hist(acc["open_day"], bins=60, color="#4c72b0")
axes[0].set_title("accounts by open_day")
axes[0].set_xlabel("day")
if len(ls):
    axes[1].hist(ls, bins=60, color="#c44e52")
    axes[1].set_title("launder_start_day")
    axes[1].set_xlabel("day")
savefig(fig, "06_time_structure")

# %% ------------------------------------ 7. pass over transactions (DuckDB)
header("7. PASS OVER TRANSACTIONS (DuckDB)")

acct_day_path = CACHE_DIR / "acct_day.parquet"
TX = rel("transactions")
NIGHT_LO, NIGHT_HI = min(NIGHT_HOURS), max(NIGHT_HOURS)

if not (USE_CACHE and acct_day_path.exists()):
    # one row per account per active day; same sums as v0's per-chunk pandas groupby
    con.execute(f"""COPY (
        SELECT account_id, day,
               count(*)::BIGINT n,
               sum(CASE WHEN direction = 'out' THEN 1 ELSE 0 END)::BIGINT n_out,
               sum(CASE WHEN direction = 'out' THEN amount ELSE 0 END) amt_out,
               sum(CASE WHEN direction = 'out' THEN 0 ELSE amount END) amt_in,
               sum(amount * amount) amt_sq,
               sum(CASE WHEN regexp_full_match(counterparty_id, 'A\\d+') THEN 1 ELSE 0 END)::BIGINT n_internal,
               sum(CASE WHEN sender_bank_location IS DISTINCT FROM receiver_bank_location THEN 1 ELSE 0 END)::BIGINT n_cross,
               sum(CASE WHEN CAST(substr(time, 1, 2) AS INT) BETWEEN {NIGHT_LO} AND {NIGHT_HI} THEN 1 ELSE 0 END)::BIGINT n_night,
               sum(CASE WHEN payment_type LIKE 'Cash%' THEN 1 ELSE 0 END)::BIGINT n_cash,
               sum(item_count)::BIGINT items
        FROM {TX} GROUP BY 1, 2) TO '{acct_day_path.as_posix()}' (FORMAT PARQUET)""")
else:
    log("cache hit -> reusing eda_cache/acct_day.parquet")
AD = f"read_parquet('{acct_day_path.as_posix()}')"

total_rows = con.execute(f"SELECT count(*) FROM {TX}").fetchone()[0]
orphan_rows = con.execute(
    f"SELECT count(*) FROM {TX} t ANTI JOIN {rel('accounts')} a USING (account_id)").fetchone()[0]
lead_counts = dict(con.execute(f"SELECT substr(txn_id, 1, 1), count(*) FROM {TX} GROUP BY 1 ORDER BY 1").fetchall())
n_acct_day = con.execute(f"SELECT count(*) FROM {AD}").fetchone()[0]
log(f"read {total_rows:,} transaction rows -> {n_acct_day:,} account-days")
if orphan_rows:
    log(f"WARNING: {orphan_rows:,} rows whose account_id is absent from accounts")
    log("  (normal on the CSV samples, which are drawn independently; NOT normal on the")
    log("   full parquet -- if it appears there, the simulator wrote inconsistent keys)")
log(f"txn_id prefixes: {lead_counts}")

glob = con.execute(f"""SELECT payment_type, direction, count(*) n, sum(amount) amt FROM {TX}
                       GROUP BY 1, 2 ORDER BY 1, 2""").df()
log(f"\nacct_day: {n_acct_day:,} rows ({acct_day_path.stat().st_size/1e6:,.0f} MB on disk)")
log("\ntransaction volume by payment_type x direction:")
glob["share"] = glob["n"] / glob["n"].sum()
log(glob.sort_values("n", ascending=False).to_string(index=False, float_format=lambda v: f"{v:,.4f}"))

# %% ------------------------------------- 8. account-level behaviour features
header("8. ACCOUNT-LEVEL TRANSACTION BEHAVIOUR")

feat = con.execute(f"""SELECT account_id,
        sum(n)::BIGINT n_txn, sum(n_out)::BIGINT n_out, sum(amt_out) amt_out, sum(amt_in) amt_in, sum(amt_sq) amt_sq,
        sum(n_internal)::BIGINT n_internal, sum(n_cross)::BIGINT n_cross, sum(n_night)::BIGINT n_night,
        sum(n_cash)::BIGINT n_cash, sum(items)::BIGINT items,
        count(DISTINCT day) active_days, min(day) first_day, max(day) last_day,
        max(n) max_txn_in_a_day, max(amt_out) + max(amt_in) max_amt_in_a_day
    FROM {AD} GROUP BY 1""").df()
feat["aid"] = acc_index.get_indexer(feat["account_id"])
feat = feat[feat["aid"] >= 0].drop(columns="account_id").set_index("aid").sort_index()
feat["n_in"] = feat["n_txn"] - feat["n_out"]
feat["amt_total"] = feat["amt_out"] + feat["amt_in"]
feat["amt_mean"] = feat["amt_total"] / feat["n_txn"]
feat["amt_std"] = np.sqrt(
    (feat["amt_sq"] / feat["n_txn"] - feat["amt_mean"] ** 2).clip(lower=0)
)
feat["share_out"] = feat["n_out"] / feat["n_txn"]
feat["share_internal"] = feat["n_internal"] / feat["n_txn"]
feat["share_night"] = feat["n_night"] / feat["n_txn"]
feat["share_cash"] = feat["n_cash"] / feat["n_txn"]
feat["span_days"] = feat["last_day"] - feat["first_day"] + 1
feat["txn_per_active_day"] = feat["n_txn"] / feat["active_days"]
feat["activity_density"] = feat["active_days"] / feat["span_days"]
# flow-through ratio: mules move money on, they do not accumulate it
feat["passthrough"] = feat["amt_out"] / feat["amt_in"].replace(0, np.nan)

deg = con.execute(f"""SELECT account_id,
        count(DISTINCT CASE WHEN direction <> 'out' THEN counterparty_id END) in_degree,
        count(DISTINCT CASE WHEN direction = 'out' THEN counterparty_id END) out_degree
    FROM {TX} GROUP BY 1""").df()
deg["aid"] = acc_index.get_indexer(deg["account_id"])
deg = deg[deg["aid"] >= 0].drop(columns="account_id").set_index("aid")
feat = feat.join(deg).fillna({"in_degree": 0, "out_degree": 0})

feat = feat.drop(columns="amt_sq").reset_index()
feat["account_id"] = acc_index[feat["aid"].to_numpy()]
panel = acc.merge(feat.drop(columns="aid"), on="account_id", how="left")

no_txn = panel["n_txn"].isna().sum()
log(f"accounts with zero transactions: {no_txn:,} ({no_txn/len(panel):.2%})")
log("\nbehaviour features, launderers vs the rest:")
beh = [
    "n_txn", "share_out", "share_internal", "share_night", "share_cash",
    "amt_total", "amt_mean", "max_amt_in_a_day", "max_txn_in_a_day",
    "passthrough", "in_degree", "out_degree", "active_days", "txn_per_active_day",
]
beh = [c for c in beh if c in panel.columns]
cmp = panel.groupby(LABEL)[beh].median().T
cmp.columns = ["non_launderer_median", "launderer_median"] if cmp.shape[1] == 2 else cmp.columns
if cmp.shape[1] == 2:
    cmp["ratio"] = cmp.iloc[:, 1] / cmp.iloc[:, 0].replace(0, np.nan)
log(cmp.to_string(float_format=lambda v: f"{v:,.3f}"))

if panel[LABEL].sum() >= 5:
    rows = [{"feature": c, "auc": auc_vs_label(panel[c], panel[LABEL].to_numpy())} for c in beh]
    uni_beh = pd.DataFrame(rows)
    uni_beh["sep"] = (uni_beh["auc"] - 0.5).abs()
    uni_beh = uni_beh.sort_values("sep", ascending=False).drop(columns="sep")
    log("\nunivariate AUC, behaviour features:")
    log(uni_beh.to_string(index=False, float_format=lambda v: f"{v:,.4f}"))
    log("\n  Compare these against §5. If behaviour dominates onboarding by a wide margin,")
    log("  the BAF half of the dataset is contributing little and you should say so.")

fig, axes = plt.subplots(1, 3, figsize=(14, 4))
for ax, c in zip(axes, ["n_txn", "amt_total", "share_internal"]):
    for lab, sub in panel.groupby(LABEL):
        v = sub[c].dropna()
        if len(v):
            ax.hist(v, bins=40, alpha=0.55, density=True, label=f"{LABEL}={lab}")
    ax.set_title(c)
    ax.legend()
savefig(fig, "08_behaviour_distributions")

# %% -------------------------------------------- 9. laundering transaction layer
header("9. LAUNDERING AT THE TRANSACTION LEVEL")

TT = rel("transactions_truth")
log(f"transactions_truth rows        : {txn_truth_rows:,}")
log(f"is_laundering rate             : {con.execute(f'SELECT avg(is_laundering) FROM {TT}').fetchone()[0]:.5%}")
log("\nlaundering_type mix:")
lt = con.execute(f"SELECT laundering_type, count(*) n FROM {TT} GROUP BY 1 ORDER BY 2 DESC, 1").df() \
    .set_index("laundering_type")["n"].rename("count")
log(pd.DataFrame({"n": lt, "share": lt / lt.sum()}).head(25).to_string(
    float_format=lambda v: f"{v:,.5f}"))

typ = con.execute(f"""SELECT laundering_type, count(*) n FROM {TT} WHERE is_laundering = 1
                     GROUP BY 1 ORDER BY 2 DESC, 1""").df().set_index("laundering_type")["n"].rename("count")
log(f"\ntypologies actually generated: {len(typ)}")
if len(typ):
    log(typ.to_string())
log("  -> SAML-D ships 28 typology names. Any with zero rows exist in the vocabulary")
log("     but not in your data; do not claim coverage you do not have.")

# %% ------------------------------------------------------ 10. network structure
header("10. NETWORK STRUCTURE")

net = acc["network_id"].dropna()
log(f"accounts attached to a network : {len(net):,} ({len(net)/n:.3%})")
if len(net):
    sizes = net.value_counts()
    log(f"distinct networks              : {len(sizes):,}")
    log("\nnetwork size distribution:")
    log(sizes.value_counts().sort_index().to_frame("n_networks").to_string())
    log("\nlargest networks:")
    log(sizes.head(10).to_string())
    log("\nlaundering rate inside networks vs outside:")
    log(acc.assign(in_net=acc["network_id"].notna()).groupby("in_net")[LABEL].agg(
        ["size", "sum", "mean"]).to_string(float_format=lambda v: f"{v:,.4f}"))
    log("\n  -> network_id is truth-only. If you build graph features, derive them from the")
    log("     internal A->A edges in transactions, never from this column.")

log(f"\ninternal (account-to-account) edges seen in transactions: "
    f"{int(panel['n_internal'].fillna(0).sum()):,}")

# %% --------------------------------------- 11. weekly panel & cohort check
header("11. WEEKLY PANEL + COHORT COMPOSITION")

wk = con.execute(f"""SELECT account_id, day // 7 AS week, sum(n)::BIGINT n_txn, sum(amt_out) amt_out,
        sum(amt_in) amt_in, sum(n_internal)::BIGINT n_internal, sum(n_night)::BIGINT n_night
    FROM {AD} GROUP BY 1, 2""").df()
wk.insert(0, "aid", acc_index.get_indexer(wk["account_id"]))
wk = wk[wk["aid"] >= 0].sort_values(["aid", "week"]).reset_index(drop=True)
wk = wk[["aid", "week", "n_txn", "amt_out", "amt_in", "n_internal", "n_night", "account_id"]]
wk = wk.merge(acc[["account_id", LABEL, "launder_start_day", "open_day"]], on="account_id")
wk["is_active_launderer"] = (
    (wk[LABEL] == 1) & (wk["week"] * 7 + 6 >= wk["launder_start_day"])
).astype(int)

by_week = wk.groupby("week").agg(
    n_accounts=("account_id", "nunique"),
    n_txn=("n_txn", "sum"),
    n_launderers=(LABEL, "sum"),
    n_active_launderers=("is_active_launderer", "sum"),
)
by_week["launder_share"] = by_week["n_launderers"] / by_week["n_accounts"]
log("weekly panel (head/tail):")
log(pd.concat([by_week.head(8), by_week.tail(8)]).to_string(
    float_format=lambda v: f"{v:,.5f}"))
wk.to_parquet(CACHE_DIR / "weekly_panel.parquet", index=False)

log("\nCOHORT CHECK — the composition your prof flagged:")
log(f"  accounts active in week  {by_week.index.min()}: {by_week['n_accounts'].iloc[0]:,}")
log(f"  accounts active in week  {by_week.index.max()}: {by_week['n_accounts'].iloc[-1]:,}")
log("  If this count drifts across weeks, a week-over-week comparison is confounded by")
log("  who is present, not just by behaviour. Fix: restrict to the fixed cohort of")
log("  accounts active in EVERY week you compare, and report the cohort size.")

always = wk.groupby("account_id")["week"].nunique()
full = int((always == wk["week"].nunique()).sum())
log(f"\n  accounts active in every one of the {wk['week'].nunique()} weeks: {full:,} "
    f"({full/len(acc):.2%} of all accounts)")

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].plot(by_week.index, by_week["n_accounts"], color="#4c72b0")
axes[0].set_title("active accounts per week (cohort drift)")
axes[0].set_xlabel("week")
axes[1].plot(by_week.index, by_week["n_txn"], color="#55a868")
axes[1].set_title("transactions per week")
axes[1].set_xlabel("week")
savefig(fig, "11_weekly_panel")

# %% --------------------------------- 12. leakage audit & modelling readiness
header("12. LEAKAGE AUDIT + MODELLING READINESS")

log("NEVER-FEATURE list (ground truth written by the simulator):")
for c in TRUTH_COLS:
    log(f"  - {c}")
log("\n  laundered_in / laundered_out are the amounts the simulator laundered through the")
log("  account. They are a perfect giveaway. profile and network_id likewise.")

log("\nID-based leakage:")
log("  txn_id: anonymous since 7 Oct 2026 ('T' + 16 hex); older runs used 'N###_' / 'L_' prefixes")
log("  that leaked the label. Still never build features from txn_id; it only joins pair rows.")
log("  counterparty_id: 'EXT_*' external, 'CARD_MERCHANTS'/'CASH_*' synthetic sinks,")
log("  'A#######' internal accounts. Only the internal ones carry real graph signal.")

log("\nclass balance for modelling:")
pos, tot = int(acc[LABEL].sum()), len(acc)
log(f"  positives {pos:,} / {tot:,} = {pos/tot:.3%}  (1 in {tot/max(pos,1):,.0f})")
log("  With this prevalence, accuracy is meaningless. Use PR-AUC plus precision@k where")
log("  k is the analyst review capacity, which is the framing in your proposal.")
for k in (50, 100, 250, 500):
    if k <= tot:
        log(f"    reviewing top {k:>4} accounts = {k/tot:.3%} of the book; "
            f"perfect ranking would catch {min(k,pos)/max(pos,1):.1%} of launderers")

log("\nrecommended split, given §6:")
log("  Split by TIME (train on early days, test on later), not at random. A random split")
log("  lets the same account's later behaviour inform its earlier prediction.")
log("  Hold the test-set prevalence at the natural rate; resample the TRAIN set only.")

out_cols = (
    ["account_id"]
    + [c for c in accounts.columns if c != "account_id"]
    + [c for c in panel.columns if c in feat.columns and c not in ("aid", "account_id")]
    + [LABEL]
)
out_cols = list(dict.fromkeys([c for c in out_cols if c in panel.columns]))
model_table = panel[out_cols]
model_table.to_csv(CACHE_DIR / "account_model_table.csv", index=False)
model_table.to_pickle(CACHE_DIR / "account_model_table.pkl")
log(f"\nwrote {CACHE_DIR / 'account_model_table.csv'}  "
    f"({model_table.shape[0]:,} x {model_table.shape[1]})")
log("  Onboarding + behaviour features + label, truth columns excluded. This is the table")
log("  the baseline model should read.")

(OUT_DIR / "eda_report.md").write_text("\n".join(_report_lines), encoding="utf-8")
print(f"\nreport -> {(OUT_DIR / 'eda_report.md').resolve()}")
print(f"figures -> {OUT_DIR.resolve()}")

# %%
