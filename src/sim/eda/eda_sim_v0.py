"""
EDA for the simulator output (data/v0).
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

#matplotlib.use("Agg")  # comment out if you want figures inline in the Interactive Window
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=FutureWarning)

# --- paths -------------------------------------------------------------------
def find_repo_root(marker: str = "data/v0") -> Path:
    try:
        start = Path(__file__).resolve().parent
    except NameError:  # Interactive Window / REPL
        start = Path.cwd().resolve()
    for d in [start, *start.parents]:
        if (d / marker).is_dir():
            return d
    raise FileNotFoundError(
        f"could not find '{marker}' in {start} or any parent.\n"
        f"Either run the simulator first, or set ROOT by hand below."
    )

ROOT = find_repo_root()
#ROOT = Path(r"C:/Users/FILE")   # uncomment and edit if auto-detect fails

# Full run (parquet, 50k accounts / ~22M txns):
DATA_DIR = ROOT / "data" / "v0"
# Dry run on the CSV samples instead:
# DATA_DIR = ROOT / "data" / "v0" / "samples"

OUT_DIR = ROOT / "outputs" / "eda"
CACHE_DIR = DATA_DIR / "eda_cache"

# --- knobs -------------------------------------------------------------------
CHUNK_ROWS = 1_000_000  # rows per streaming batch
USE_CACHE = True  # reuse data/v0/eda_cache/*.parquet if present
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
    """Print and accumulate into outputs/eda/eda_report.md."""
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
txn_truth = load("transactions_truth")
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

for nm, df in [
    ("accounts", accounts),
    ("accounts_truth", accounts_truth),
    ("transactions_truth", txn_truth),
    ("aml_alerts", aml_alerts),
    ("aml_outcomes", aml_outcomes),
]:
    log(f"{nm:<20} {df.shape[0]:>10,} rows x {df.shape[1]:>2} cols")
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
print(fig, "04_label_landscape")

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
    print(fig, "05_univariate_auc")

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
print(fig, "06_time_structure")

# %% ------------------------------------ 7. streaming pass over transactions
header("7. STREAMING PASS OVER TRANSACTIONS")

acct_day_path = CACHE_DIR / "acct_day.pkl"
glob_path = CACHE_DIR / "global_txn_stats.pkl"
cp_path = CACHE_DIR / "acct_cp.pkl"

TXN_COLS = [
    "txn_id",
    "account_id",
    "direction",
    "counterparty_id",
    "day",
    "time",
    "amount",
    "item_count",
    "payment_type",
    "sender_bank_location",
    "receiver_bank_location",
]

if USE_CACHE and acct_day_path.exists() and glob_path.exists() and cp_path.exists():
    log("cache hit -> loading acct_day / global stats / counterparty pairs from eda_cache/")
    acct_day = pd.read_pickle(acct_day_path)
    glob = pd.read_pickle(glob_path)
    acct_cp = pd.read_pickle(cp_path)
else:
    day_parts, cp_parts, glob_parts = [], [], []
    total_rows = 0
    orphan_rows = 0
    lead_counts = {}

    for i, ch in enumerate(iter_chunks("transactions", TXN_COLS)):
        total_rows += len(ch)

        aid = acc_index.get_indexer(ch["account_id"]).astype(np.int32)
        if (aid < 0).any():
            # Expected only when dry-running on the independently drawn CSV samples.
            # On the full parquet this should be zero; investigate if it is not.
            n_orphan = int((aid < 0).sum())
            orphan_rows += n_orphan
            keep = aid >= 0
            ch, aid = ch.loc[keep].reset_index(drop=True), aid[keep]

        is_out = (ch["direction"] == "out").to_numpy()
        amt = ch["amount"].to_numpy(dtype=np.float64)
        hour = ch["time"].str.slice(0, 2).astype(np.int16)
        cp = ch["counterparty_id"]
        internal = cp.str.fullmatch(r"A\d+").fillna(False).to_numpy()
        cross = (ch["sender_bank_location"] != ch["receiver_bank_location"]).to_numpy()

        # the simulator prefixes laundering txn_ids with "L" -- see the leakage check in §12
        lead = ch["txn_id"].str.slice(0, 1)
        for k, v in lead.value_counts().items():
            lead_counts[k] = lead_counts.get(k, 0) + int(v)

        part = pd.DataFrame(
            {
                "aid": aid,
                "day": ch["day"].to_numpy(dtype=np.int32),
                "n": 1,
                "n_out": is_out.astype(np.int32),
                "amt_out": np.where(is_out, amt, 0.0),
                "amt_in": np.where(~is_out, amt, 0.0),
                "amt_sq": amt**2,
                "n_internal": internal.astype(np.int32),
                "n_cross": cross.astype(np.int32),
                "n_night": np.isin(hour, list(NIGHT_HOURS)).astype(np.int32),
                "n_cash": ch["payment_type"].str.startswith("Cash").to_numpy().astype(np.int32),
                "items": ch["item_count"].to_numpy(dtype=np.int32),
            }
        )
        day_parts.append(part.groupby(["aid", "day"], as_index=False, sort=False).sum())

        cp_parts.append(
            pd.DataFrame(
                {
                    "aid": aid,
                    "cp_hash": pd.util.hash_pandas_object(cp, index=False).to_numpy(),
                    "is_out": is_out,
                }
            ).drop_duplicates()
        )

        glob_parts.append(
            ch.groupby(["payment_type", "direction"], as_index=False).agg(
                n=("amount", "size"), amt=("amount", "sum")
            )
        )
        print(f"  batch {i}: {len(ch):,} rows  (cumulative {total_rows:,})")

    if not day_parts:
        raise SystemExit("no transactions matched an account_id in accounts")

    acct_day = (
        pd.concat(day_parts, ignore_index=True)
        .groupby(["aid", "day"], as_index=False, sort=False)
        .sum()
    )
    acct_cp = pd.concat(cp_parts, ignore_index=True).drop_duplicates()
    glob = (
        pd.concat(glob_parts, ignore_index=True)
        .groupby(["payment_type", "direction"], as_index=False)
        .sum()
    )
    acct_day.to_pickle(acct_day_path)
    acct_cp.to_pickle(cp_path)
    glob.to_pickle(glob_path)
    log(f"streamed {total_rows:,} transaction rows -> {len(acct_day):,} account-days")
    if orphan_rows:
        log(f"WARNING: dropped {orphan_rows:,} rows whose account_id is absent from accounts")
        log("  (normal on the CSV samples, which are drawn independently; NOT normal on the")
        log("   full parquet -- if it appears there, the simulator wrote inconsistent keys)")
    log(f"txn_id prefixes: {lead_counts}")

log(f"\nacct_day: {acct_day.shape[0]:,} rows ({acct_day.memory_usage(deep=True).sum()/1e6:,.0f} MB)")
log("\ntransaction volume by payment_type x direction:")
glob["share"] = glob["n"] / glob["n"].sum()
log(glob.sort_values("n", ascending=False).to_string(index=False, float_format=lambda v: f"{v:,.4f}"))

# %% ------------------------------------- 8. account-level behaviour features
header("8. ACCOUNT-LEVEL TRANSACTION BEHAVIOUR")

g = acct_day.groupby("aid")
feat = pd.DataFrame(
    {
        "n_txn": g["n"].sum(),
        "n_out": g["n_out"].sum(),
        "amt_out": g["amt_out"].sum(),
        "amt_in": g["amt_in"].sum(),
        "amt_sq": g["amt_sq"].sum(),
        "n_internal": g["n_internal"].sum(),
        "n_cross": g["n_cross"].sum(),
        "n_night": g["n_night"].sum(),
        "n_cash": g["n_cash"].sum(),
        "items": g["items"].sum(),
        "active_days": g["day"].nunique(),
        "first_day": g["day"].min(),
        "last_day": g["day"].max(),
        "max_txn_in_a_day": g["n"].max(),
        "max_amt_in_a_day": (g["amt_out"].max() + g["amt_in"].max()),
    }
)
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

deg = acct_cp.groupby(["aid", "is_out"]).size().unstack(fill_value=0)
deg.columns = ["in_degree" if c is False else "out_degree" for c in deg.columns]
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
print(fig, "08_behaviour_distributions")

# %% -------------------------------------------- 9. laundering transaction layer
header("9. LAUNDERING AT THE TRANSACTION LEVEL")

log(f"transactions_truth rows        : {len(txn_truth):,}")
log(f"is_laundering rate             : {txn_truth['is_laundering'].mean():.5%}")
log("\nlaundering_type mix:")
lt = txn_truth["laundering_type"].value_counts()
log(pd.DataFrame({"n": lt, "share": lt / lt.sum()}).head(25).to_string(
    float_format=lambda v: f"{v:,.5f}"))

typ = txn_truth.loc[txn_truth["is_laundering"] == 1, "laundering_type"].value_counts()
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

acct_day["week"] = acct_day["day"] // 7
wk = (
    acct_day.groupby(["aid", "week"], as_index=False)
    .agg(n_txn=("n", "sum"), amt_out=("amt_out", "sum"), amt_in=("amt_in", "sum"),
         n_internal=("n_internal", "sum"), n_night=("n_night", "sum"))
)
wk["account_id"] = acc_index[wk["aid"].to_numpy()]
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
wk.to_pickle(CACHE_DIR / "weekly_panel.pkl")
wk.to_csv(CACHE_DIR / "weekly_panel.csv.gz", index=False, compression="gzip")

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
print(fig, "11_weekly_panel")

# %% --------------------------------- 12. leakage audit & modelling readiness
header("12. LEAKAGE AUDIT + MODELLING READINESS")

log("NEVER-FEATURE list (ground truth written by the simulator):")
for c in TRUTH_COLS:
    log(f"  - {c}")
log("\n  laundered_in / laundered_out are the amounts the simulator laundered through the")
log("  account. They are a perfect giveaway. profile and network_id likewise.")

log("\nID-based leakage:")
log("  txn_id prefix encodes provenance: 'N###_' = normal generator batch, 'L' = laundering.")
log("  Any feature derived from txn_id (or a join key built from it) leaks the label.")
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
