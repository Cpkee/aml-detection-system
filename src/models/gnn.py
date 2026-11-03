"""GraphSAGE on the payment graph between accounts of the bank (proposal 3 Nov 2026, Keith Tan).

Status: code and tests only. Not trained on the folds until the methods comparison pre-registers it as a dated
amendment (outputs/modelling/comparison/PLAN.md on branch methods-comparison); then it runs there like any rival,
judged on catch_rules.

Question: does a model that also reads the accounts an account pays and is paid by catch mules earlier than the model
of record, which reads each account on its own?

Graph (agreed 3 Nov 2026 with the team lead's question "payment links between the accounts?": yes)
  nodes   account-weeks: an account as it stood at the end of one of its weeks since opening (cut-off
          open_day + 7w + 6, the store's clock)
  links   payments between two accounts of the bank (counterparty A*; features/graph_edges.parquet, built by
          `python -m features graph`). External ids are unique per account, so no other links exist. A focal
          account-week (v, w) links to every account u that v paid or was paid by on or before v's cut-off c; u enters
          as its own latest week whose cut-off is on or before c (never later), or as "not yet known" when u has not
          finished its first week by c
  link    log(1 + money in from u so far), log(1 + money out to u so far), weeks since the last payment with u,
  inputs  and whether u's state is known
  cap     the most recent `fanout` neighbours per node (ties by account id): deterministic, unlike GraphSAGE's random
          sampling; the full count enters as log(1 + neighbours) beside the node's own inputs
  who     neighbours may have opened in any month, including months 5-7 (decided 3 Nov 2026: a bank sees every
          payment between its own accounts); only their public inputs are read, never a label of any neighbour.
          Labels come only from the training rows the caller passes, as for every other method

Node inputs: the 38 frozen inputs (28 store + 8 roll4 + weeks_since_open + app_score). A neighbour's app_score comes
from the same fold's application model (feature_lab.app_scores, seed 42, other months scored by the model fitted on
the training months); fit() refuses to run if those scores differ from the app_score column it was given.
Preprocessing as the comparison's logistic (A4): shares clipped to [0, 1], self_vs_past clipped to [-10, 10], other
counts and money log1p, then standardised on the training rows; a missing value becomes 0 plus a 0/1 flag.

Model (GraphSAGE, Hamilton et al. 2017, mean aggregator), written in plain PyTorch (no PyG needed):
  layer   h'(v) = relu(W_self h(v) + mean over neighbours u of W_nb [h(u), link(u, v)])
  layers  2 (an account's neighbours' neighbours; fanout 10 then 5), hidden 64, dropout 0.1, then one logit
  fit     balanced class weights (as LightGBM's class_weight='balanced'), Adam lr 1e-3, weight decay 1e-5,
          4 epochs of shuffled mini-batches of 2,048 training account-weeks, no early stopping (no peek at the
          validation month); the score is the mean probability over seeds 1-5, as the other rivals
These settings are the proposal's fixed values (`DEFAULTS`); none was tuned on the folds.

    from models import gnn
    fit = gnn.method("data/v1_full")        # fit(train, valid) -> scores, the comparison's interface
"""
from __future__ import annotations
import gc
import os

import numpy as np
import pandas as pd

import amldata
from features import candidates, graph, manifest
from features.weekly import FEATURES as WEEKLY
from features.weekly import LAST_WEEK

KEY = ["account_id", "weeks_since_open"]
INPUTS = WEEKLY + candidates.ADOPTED + ["weeks_since_open", "app_score"]   # the 38 frozen inputs (28 Oct 2026)
SHARES = [c for c in INPUTS if "share" in c or c.startswith("passthrough")]
ZSCORE = [c for c in INPUTS if c.startswith("self_vs_past")]
PLAIN = ["weeks_since_open", "app_score"]
LOGGED = [c for c in INPUTS if c not in SHARES + ZSCORE + PLAIN]
LINK = ["log_money_in", "log_money_out", "weeks_since_contact", "nb_known"]
DEFAULTS = {"layers": 2, "fanout": (10, 5), "hidden": 64, "dropout": 0.1, "lr": 1e-3, "weight_decay": 1e-5,
            "epochs": 4, "batch": 2048, "seeds": (1, 2, 3, 4, 5), "app_seed": 42}
FOCAL_WEEKS = (0, 26)


# ---------------------------------------------------------------- graph
def pairs_sql(states: str, edges: str, accounts: str, fanout: int) -> str:
    """Neighbours of each state, on registered tables: states (state, account_id, w), edges (account_id, nb_id, day,
    direction, amount; one row per payment, seen from account_id's side), accounts (account_id, open_day).

    Only payments on or before the state's cut-off count. Output, the `fanout` most recent neighbours per state:
    state, nb_id, nb_w (the neighbour's latest week with cut-off <= the state's; NULL if it has none yet), n_nb
    (neighbours before the cap) and the link inputs."""
    return f"""
    WITH s AS (SELECT s.state, s.account_id, a.open_day + 7 * s.w + 6 AS cut
               FROM {states} s JOIN {accounts} a USING (account_id)),
    p AS (SELECT s.state, s.cut, e.nb_id,
                 coalesce(sum(e.amount) FILTER (WHERE e.direction = 'in'), 0)  AS m_in,
                 coalesce(sum(e.amount) FILTER (WHERE e.direction = 'out'), 0) AS m_out,
                 max(e.day) AS last_day
          FROM s JOIN {edges} e ON e.account_id = s.account_id AND e.day <= s.cut
          GROUP BY 1, 2, 3),
    r AS (SELECT *, row_number() OVER (PARTITION BY state ORDER BY last_day DESC, nb_id) AS rk,
                 count(*) OVER (PARTITION BY state) AS n_nb
          FROM p)
    SELECT r.state, r.nb_id,
           CASE WHEN r.cut - a.open_day - 6 >= 0
                THEN least({LAST_WEEK}, CAST((r.cut - a.open_day - 6) // 7 AS INTEGER)) END AS nb_w,
           r.n_nb, ln(1 + r.m_in) AS log_money_in, ln(1 + r.m_out) AS log_money_out,
           (r.cut - r.last_day) / 7.0 AS weeks_since_contact
    FROM r JOIN {accounts} a ON a.account_id = r.nb_id
    WHERE r.rk <= {int(fanout)}
    ORDER BY r.state, r.rk"""


def build_graph(con, states0: pd.DataFrame, edges: str, accounts: str, fanout=DEFAULTS["fanout"]) -> dict:
    """The neighbourhoods a GraphSAGE of len(fanout) layers needs, level by level.

    states0: account_id, w of the focal account-weeks (level 0). Level k+1 holds the distinct known neighbour states
    of level k. Returns {"states": [DataFrame account_id, w per level], "pairs": [per level k < len(fanout):
    DataFrame state, nb (index into level k+1, -1 if not known), LINK ...], "n_nb": [array per level k]}.
    edges / accounts: names of tables (or parquet reads) on con."""
    levels = [states0[["account_id", "w"]].reset_index(drop=True)]
    pairs, n_nb = [], []
    for k, cap in enumerate(fanout):
        st = levels[k].assign(state=np.arange(len(levels[k]), dtype=np.int64))
        con.register("_gnn_states", st)
        p = con.execute(pairs_sql("_gnn_states", edges, accounts, cap)).df()
        con.unregister("_gnn_states")
        known = p.dropna(subset=["nb_w"])
        nxt = (known[["nb_id", "nb_w"]].drop_duplicates().rename(columns={"nb_id": "account_id", "nb_w": "w"})
               .astype({"w": "int64"}).sort_values(["account_id", "w"], kind="stable").reset_index(drop=True))
        idx = pd.Series(np.arange(len(nxt)), index=pd.MultiIndex.from_frame(nxt))
        nb = np.full(len(p), -1, dtype=np.int64)
        ok = p["nb_w"].notna().to_numpy()
        nb[ok] = idx.reindex(pd.MultiIndex.from_arrays([p.loc[ok, "nb_id"], p.loc[ok, "nb_w"].astype("int64")])).to_numpy()
        p = p.assign(nb=nb, nb_known=ok.astype(float))
        deg = np.zeros(len(levels[k]))
        first = p.drop_duplicates("state")
        deg[first["state"].to_numpy()] = first["n_nb"].to_numpy()
        pairs.append(p[["state", "nb"] + LINK].astype({"state": "int32", "nb": "int32", **{c: "float32" for c in LINK}})
                     .reset_index(drop=True))
        n_nb.append(deg)
        levels.append(nxt)
    return {"states": levels, "pairs": pairs, "n_nb": n_nb}


def node_inputs(store: pd.DataFrame, states: pd.DataFrame) -> pd.DataFrame:
    """The 37 activity inputs (all but app_score) of each state (account_id, w), in the states' order.

    store: KEY + the 28 store features for the states' accounts, every week from 0 up to at least each state's week
    (roll4 is a window over earlier weeks, built exactly as the comparison's table: candidates.add)."""
    if states.empty:
        return pd.DataFrame(columns=["account_id", "w"] + [c for c in INPUTS if c != "app_score"])
    s = store.sort_values(KEY, kind="stable").reset_index(drop=True)
    for c in WEEKLY:
        s[c] = s[c].astype("float32")
    s, names = candidates.add(s, [candidates.ADOPTED_GROUP])
    s = s.drop(columns=[c for c in names[candidates.ADOPTED_GROUP] if c not in candidates.ADOPTED])
    s = s.rename(columns={"weeks_since_open": "w"})
    out = states[["account_id", "w"]].merge(s, on=["account_id", "w"], how="left", validate="m:1", indicator=True)
    if out["_merge"].ne("both").any():
        raise ValueError("store rows missing for some neighbour states")
    out = out.drop(columns="_merge")
    out["weeks_since_open"] = out["w"].astype("float32")
    return out


def load_store(out: str, states: pd.DataFrame) -> pd.DataFrame:
    """Store rows (weeks 0..max week needed) of the accounts in states, through amldata.public (public inputs)."""
    manifest.check(out)
    need = states.groupby("account_id", as_index=False)["w"].max()
    con = amldata.public(out)
    con.register("_need", need)
    path = os.path.join(out, "features", "weekly.parquet").replace("\\", "/")
    df = con.execute(f"SELECT s.* FROM read_parquet('{path}') s JOIN _need n USING (account_id) "
                     f"WHERE s.weeks_since_open <= n.w ORDER BY s.account_id, s.weeks_since_open").df()
    con.close()
    return df[KEY + WEEKLY]


# ---------------------------------------------------------------- preprocessing
CHUNK = 500_000                                     # rows transformed at a time (memory on v1_full)
APP = INPUTS.index("app_score")


def _col(x: np.ndarray, c: str) -> np.ndarray:
    """The fold-free part of the A4 recipe: shares clipped to [0, 1], self_vs_past to [-10, 10], counts and money
    log1p (negatives clipped to 0); NaN stays NaN."""
    if c in SHARES:
        return np.clip(x, 0, 1)
    if c in ZSCORE:
        return np.clip(x, -10, 10)
    if c in LOGGED:
        return np.log1p(np.clip(x, 0, None))
    return x


def raw_into(df: pd.DataFrame, out: np.ndarray, rows: np.ndarray, skip=()) -> None:
    """out[rows] = the clipped / logged INPUTS of df (float32, NaN kept), in chunks; columns in `skip` untouched."""
    for b in range(0, len(df), CHUNK):
        part, r = df.iloc[b:b + CHUNK], rows[b:b + CHUNK]
        for i, c in enumerate(INPUTS):
            if c not in skip:
                out[r, i] = _col(part[c].to_numpy(dtype="float32"), c)


class Prep:
    """The fold-fitted part of the A4 recipe, from training rows only: mean and SD per input (after _col) and which
    inputs get a missing flag. Applied per batch (standardise; missing -> 0 + flag), so no standardised copy of the
    ~5M-row neighbour levels is ever stored."""

    def fit(self, df: pd.DataFrame) -> "Prep":
        self.mean, self.sd, self.flags = np.zeros(len(INPUTS)), np.ones(len(INPUTS)), []
        for i, c in enumerate(INPUTS):
            x = _col(df[c].to_numpy(dtype="float32"), c)
            ok = ~np.isnan(x)
            if not ok.all():
                self.flags.append(i)
            if ok.any():
                v = x[ok].astype("float64")
                self.mean[i] = v.mean()
                sd = v.std()
                self.sd[i] = sd if sd > 0 else 1.0
        return self

    def apply(self, raw):
        """Standardised inputs + missing flags of raw rows (numpy or torch, float32)."""
        if isinstance(raw, np.ndarray):
            miss = np.isnan(raw[:, self.flags]).astype("float32")
            z = (raw - self.mean.astype("float32")) / self.sd.astype("float32")
            return np.hstack([np.nan_to_num(z, nan=0.0), miss])
        torch = _torch()
        if not hasattr(self, "_t"):
            self._t = (torch.tensor(self.mean, dtype=torch.float32), torch.tensor(self.sd, dtype=torch.float32),
                       torch.tensor(self.flags, dtype=torch.long))
        mean, sd, flags = self._t
        miss = torch.isnan(raw[:, flags]).float()
        return torch.cat([torch.nan_to_num((raw - mean) / sd, nan=0.0), miss], dim=1)

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        raw = np.empty((len(df), len(INPUTS)), "float32")
        raw_into(df, raw, np.arange(len(df)))
        return self.apply(raw)

    @property
    def width(self) -> int:
        return len(INPUTS) + len(self.flags)


def csr(state: np.ndarray, n: int) -> np.ndarray:
    """Offsets of a pairs table sorted by state: rows of state i are off[i]:off[i+1]."""
    if len(state) and np.any(np.diff(state) < 0):
        raise ValueError("pairs must be sorted by state")
    return np.concatenate([[0], np.cumsum(np.bincount(state, minlength=n))]).astype(np.int64)


def gather(off: np.ndarray, ids: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Rows of the pairs of `ids` (in order) and, for each, its position in ids."""
    lo, n = off[ids], off[ids + 1] - off[ids]
    seg = np.repeat(np.arange(len(ids)), n)
    start = np.repeat(lo - np.concatenate([[0], np.cumsum(n)[:-1]]), n)
    return start + np.arange(n.sum()), seg


# ---------------------------------------------------------------- compact graph
def _torch():
    import torch
    return torch


class Compact:
    """Everything the model reads that does not depend on the fold, in plain arrays (no account-id strings).

    Per level k (0 = focal account-weeks): raw[k] float32 (n_k + 1, 38) clipped / logged inputs, NaN kept, the last
    row an 'unknown neighbour' that is zeroed after standardising; logdeg[k] log(1 + neighbours); codes[k] the
    account code of each state (for the fold's app_score). Per link level k: off[k] (n_k + 2 offsets: the unknown row
    has no pairs), nb[k] (index into level k + 1; unknown -> its last row), link[k] the link inputs.
    Level 0's raw is filled per fold from the caller's rows; key0 / order0 map (account code, week) to a state."""

    def __init__(self, g: dict, level_inputs: list[pd.DataFrame], code_of: pd.Series):
        torch = _torch()
        n = [len(s) for s in g["states"]]
        s0 = g["states"][0]
        key = code_of.reindex(s0["account_id"]).to_numpy().astype(np.int64) * 128 + s0["w"].to_numpy()
        self.order0 = np.argsort(key, kind="stable")
        self.key0 = key[self.order0]
        self.code_of = code_of
        self.n = n
        self.raw, self.codes, self.logdeg = [None], [None], []
        for k, d in enumerate(level_inputs, start=1):
            r = np.full((n[k] + 1, len(INPUTS)), np.nan, "float32")
            raw_into(d, r, np.arange(len(d)), skip=() if "app_score" in d.columns else ("app_score",))
            self.raw.append(r)
            self.codes.append(code_of.reindex(d["account_id"]).to_numpy().astype(np.int32))
        for k in range(len(n)):
            ld = np.zeros(n[k] + 1, "float32")
            if k < len(g["n_nb"]):
                ld[:-1] = np.log1p(g["n_nb"][k])
            self.logdeg.append(torch.from_numpy(ld))
        self.off, self.nb, self.link = [], [], []
        for k, p in enumerate(g["pairs"]):
            off = csr(p["state"].to_numpy(), n[k])
            self.off.append(np.append(off, off[-1]))
            nb = p["nb"].to_numpy().astype(np.int64)
            self.nb.append(np.where(nb < 0, n[k + 1], nb))
            lk = p[LINK].to_numpy(dtype="float32").copy()
            lk[:, 2] = np.log1p(lk[:, 2])                      # weeks since contact, 0-77
            self.link.append(torch.from_numpy(lk))

    def ids(self, d: pd.DataFrame) -> np.ndarray:
        """Level-0 state of each row (account_id, weeks_since_open) of d."""
        code = self.code_of.reindex(d["account_id"]).to_numpy()
        if np.isnan(code).any():
            raise ValueError("rows outside the graph's focal states")
        key = code.astype(np.int64) * 128 + d["weeks_since_open"].to_numpy().astype(np.int64)
        pos = np.searchsorted(self.key0, key).clip(0, len(self.key0) - 1)
        if not (self.key0[pos] == key).all():
            raise ValueError("rows outside the graph's focal states")
        return self.order0[pos]

    def features(self, prep: Prep, k: int, idx: np.ndarray):
        torch = _torch()
        x = prep.apply(torch.from_numpy(self.raw[k][idx]))
        x[torch.from_numpy(idx == self.n[k])] = 0.0           # unknown neighbour: all zero
        return torch.cat([x, self.logdeg[k][torch.from_numpy(idx)][:, None]], dim=1)


# ---------------------------------------------------------------- model
class SAGE:
    """GraphSAGE with the mean aggregator and link inputs; `layers` 1 or 2."""

    def __new__(cls, d_in: int, layers: int, hidden: int, dropout: float):
        torch = _torch()
        nn = torch.nn

        class _SAGE(nn.Module):
            def __init__(self):
                super().__init__()
                self.layers = layers
                dims = [d_in] + [hidden] * layers
                self.self_lin = nn.ModuleList(nn.Linear(dims[i], hidden) for i in range(layers))
                self.nb_lin = nn.ModuleList(nn.Linear(dims[i] + len(LINK), hidden, bias=False) for i in range(layers))
                self.drop = nn.Dropout(dropout)
                self.out = nn.Linear(hidden, 1)

            def conv(self, i, h_self, h_nb, link, seg, n):
                m = self.nb_lin[i](torch.cat([h_nb, link], dim=1))
                agg = torch.zeros(n, m.shape[1]).index_add_(0, seg, m)
                cnt = torch.zeros(n).index_add_(0, seg, torch.ones(len(seg))).clamp(min=1)
                return torch.relu(self.self_lin[i](h_self) + agg / cnt[:, None])

            def forward(self, c: Compact, prep: Prep, ids: np.ndarray):
                need, hops = [ids], []                  # nodes needed at each level, hop by hop
                for k in range(self.layers):
                    rows, seg = gather(c.off[k], need[k])
                    uniq, inv = np.unique(c.nb[k][rows], return_inverse=True)
                    hops.append((rows, torch.from_numpy(seg), torch.from_numpy(inv.reshape(-1))))
                    need.append(uniq)
                h = [c.features(prep, k, need[k]) for k in range(self.layers + 1)]
                for i in range(self.layers):              # layer i updates levels 0 .. layers-1-i
                    new = []
                    for k in range(self.layers - i):
                        rows, seg, inv = hops[k]
                        link = c.link[k][torch.from_numpy(rows)]
                        new.append(self.drop(self.conv(i, h[k], h[k + 1][inv], link, seg, len(need[k]))))
                    h = new
                return self.out(h[0]).squeeze(1)

        return _SAGE()


def train_score(c: Compact, prep: Prep, train_ids: np.ndarray, y: np.ndarray, score_ids: np.ndarray,
                settings: dict, seed: int) -> np.ndarray:
    """Fit one GraphSAGE on level-0 nodes train_ids (labels y) and return probabilities for score_ids."""
    torch = _torch()
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    model = SAGE(prep.width + 1, settings["layers"], settings["hidden"], settings["dropout"])
    opt = torch.optim.Adam(model.parameters(), lr=settings["lr"], weight_decay=settings["weight_decay"])
    n, n_pos = len(y), int(y.sum())
    if n_pos == 0 or n_pos == n:
        raise ValueError("training rows need both classes")
    w = np.where(y == 1, n / (2 * n_pos), n / (2 * (n - n_pos))).astype("float32")
    yt, wt = torch.from_numpy(y.astype("float32")), torch.from_numpy(w)
    rng = np.random.default_rng(seed)
    model.train()
    for _ in range(settings["epochs"]):
        order = rng.permutation(n)
        for b in range(0, n, settings["batch"]):
            i = order[b:b + settings["batch"]]
            logit = model(c, prep, train_ids[i])
            loss = (torch.nn.functional.binary_cross_entropy_with_logits(logit, yt[i], reduction="none")
                    * wt[i]).sum() / wt[i].sum()
            opt.zero_grad()
            loss.backward()
            opt.step()
    model.eval()
    out = np.empty(len(score_ids))
    with torch.no_grad():
        for b in range(0, len(score_ids), 8192):
            out[b:b + 8192] = torch.sigmoid(model(c, prep, score_ids[b:b + 8192])).numpy()
    return out


def fit_compact(c: Compact, train: pd.DataFrame, valid: pd.DataFrame, settings: dict | None = None,
                app_by_code: np.ndarray | None = None, log=None) -> np.ndarray:
    """Fit on train's rows (labels mule_by_day), score valid's rows, seeds averaged. app_by_code: the fold's
    app_score per account code, written into the neighbour levels (level 0 takes the caller's column)."""
    s = DEFAULTS | (settings or {})
    prep = Prep().fit(train)
    tr, va = c.ids(train), c.ids(valid)
    c.raw[0] = np.full((c.n[0] + 1, len(INPUTS)), np.nan, "float32")
    raw_into(train, c.raw[0], tr)
    raw_into(valid, c.raw[0], va)
    if app_by_code is not None:
        for k in range(1, len(c.raw)):
            c.raw[k][:-1, APP] = app_by_code[c.codes[k]]
    y = train["mule_by_day"].to_numpy()
    score = np.zeros(len(valid))
    for seed in s["seeds"]:
        score += train_score(c, prep, tr, y, va, s, seed)
        if log:
            log(f"seed {seed} done")
    c.raw[0] = None
    return score / len(s["seeds"])


def fit_score(g: dict, level_inputs: list[pd.DataFrame], train: pd.DataFrame, valid: pd.DataFrame,
              settings: dict | None = None) -> np.ndarray:
    """fit_compact on a graph from build_graph: level_inputs[k] = INPUTS (app_score included) of level k+1's
    states; train / valid = the caller's rows (KEY + INPUTS, train with mule_by_day). Only train's labels are read."""
    ids = pd.Index(pd.concat([s["account_id"] for s in g["states"]] + [train["account_id"], valid["account_id"]])
                   .unique()).sort_values()
    c = Compact(g, level_inputs, pd.Series(np.arange(len(ids), dtype=np.int32), index=ids))
    return fit_compact(c, train, valid, settings)


# ---------------------------------------------------------------- the comparison's interface
def _rss() -> str:
    try:
        import psutil
        return f"{psutil.Process().memory_info().rss / 2**30:.1f} GB"
    except ImportError:
        return "?"


def _log(msg: str) -> None:
    print(f"  G1 {msg} (memory {_rss()})", flush=True)


def prepare(out: str, accounts_months=(0, 1, 2, 3, 4), weeks=FOCAL_WEEKS, fanout=DEFAULTS["fanout"]) -> Compact:
    """Compact graph of every focal account-week (accounts opened in `accounts_months`, `weeks`) with the activity
    inputs of every neighbour state. Public inputs only; independent of the fold, so built once."""
    graph.check(out)
    con = amldata.public(out)
    acc = con.execute("SELECT account_id, open_month FROM accounts ORDER BY account_id").df()
    code_of = pd.Series(np.arange(len(acc), dtype=np.int32), index=acc["account_id"].to_numpy())
    focal = acc.loc[acc.open_month.isin(accounts_months), ["account_id"]].merge(
        pd.DataFrame({"w": range(weeks[0], weeks[1] + 1)}), how="cross").sort_values(["account_id", "w"])
    con.execute("PRAGMA memory_limit='6GB'")
    edges = f"read_parquet('{graph.edges(out).replace(os.sep, '/')}')"
    g = build_graph(con, focal, edges, "(SELECT account_id, open_day FROM accounts)", fanout)
    con.close()
    del focal
    _log("graph built: " + ", ".join(f"level {k} {len(s):,}" for k, s in enumerate(g["states"])))
    keep = ["account_id"] + [c for c in INPUTS if c != "app_score"]
    inputs = []
    for st in g["states"][1:]:
        d = node_inputs(load_store(out, st), st) if len(st) else node_inputs(pd.DataFrame(), st)
        inputs.append(d[keep])
        del d
        gc.collect()
    c = Compact(g, inputs, code_of)
    c.month_of = acc["open_month"].to_numpy()
    del g, inputs
    gc.collect()
    _log("neighbour inputs ready")
    return c


def method(out: str, settings: dict | None = None):
    """fit(train, valid) -> validation scores, for models.comparison. The fold is read from train's months; the
    neighbours' application scores come from that fold's application model (seed `app_seed`)."""
    from models import lgbm_baseline as base
    from models.feature_lab import app_scores
    s = DEFAULTS | (settings or {})
    cache = {}

    def fit(train: pd.DataFrame, valid: pd.DataFrame) -> np.ndarray:
        if "c" not in cache:
            cache["c"] = prepare(out, fanout=s["fanout"][:s["layers"]])
            cache["app"] = app_scores(out, s["app_seed"], other_months=sorted(set(cache["c"].month_of.tolist())))
            _log("application scores ready")
        c = cache["c"]
        f = [i for i, (tm, _) in enumerate(base.FOLDS, start=1) if set(tm) == set(train.open_month.unique())]
        if len(f) != 1:
            raise ValueError("training months do not match a fold of lgbm_baseline.FOLDS")
        app = cache["app"][f[0]]["app_score"]
        for d in (train, valid):
            gap = np.abs(d["account_id"].map(app).to_numpy() - d["app_score"].to_numpy())
            if not np.nanmax(gap) < 1e-9:
                raise ValueError("app_score differs from feature_lab.app_scores(seed=app_seed): wrong seed or data")
        app_by_code = app.reindex(c.code_of.index).to_numpy(dtype="float32")
        _log(f"fold {f[0]}: training ({len(train):,} rows, {len(s['seeds'])} seeds)")
        score = fit_compact(c, train, valid, s, app_by_code, log=lambda m: _log(f"fold {f[0]}: {m}"))
        gc.collect()
        return score
    return fit
