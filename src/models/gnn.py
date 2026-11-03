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


class Prep:
    """The comparison logistic's transforms, fitted on training rows only: clip / log, standardise, missing -> 0 +
    flag. The same fitted numbers transform focal rows and neighbour states. Works column by column in float32 and
    writes into a given matrix, so v1_full's ~5M-row levels need no float64 copy."""

    def fit(self, df: pd.DataFrame) -> "Prep":
        self.mean, self.sd, self.flags = np.zeros(len(INPUTS)), np.ones(len(INPUTS)), []
        for i, c in enumerate(INPUTS):
            x = self._col(df[c].to_numpy(dtype="float32"), c)
            ok = ~np.isnan(x)
            if not ok.all():
                self.flags.append(i)
            if ok.any():
                v = x[ok].astype("float64")
                self.mean[i] = v.mean()
                sd = v.std()
                self.sd[i] = sd if sd > 0 else 1.0
        return self

    @staticmethod
    def _col(x: np.ndarray, c: str) -> np.ndarray:
        if c in SHARES:
            return np.clip(x, 0, 1)
        if c in ZSCORE:
            return np.clip(x, -10, 10)
        if c in LOGGED:
            return np.log1p(np.clip(x, 0, None))
        return x

    def transform_into(self, df: pd.DataFrame, out: np.ndarray, rows: np.ndarray, app: np.ndarray | None = None):
        """Write df's transformed rows into out[rows, :width]. app: app_score values to use instead of df's column."""
        for b in range(0, len(df), CHUNK):
            part, r = df.iloc[b:b + CHUNK], rows[b:b + CHUNK]
            z = np.empty((len(part), len(INPUTS)), "float32")
            for i, c in enumerate(INPUTS):
                x = app[b:b + CHUNK] if (c == "app_score" and app is not None) else part[c].to_numpy(dtype="float32")
                z[:, i] = self._col(np.asarray(x, dtype="float32"), c)
            miss = np.isnan(z[:, self.flags])
            z = (z - self.mean.astype("float32")) / self.sd.astype("float32")
            z[np.isnan(z)] = 0.0
            out[r, :len(INPUTS)] = z
            out[r, len(INPUTS):self.width] = miss

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        out = np.empty((len(df), self.width), "float32")
        self.transform_into(df, out, np.arange(len(df)))
        return out

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


# ---------------------------------------------------------------- model
def _torch():
    import torch
    return torch


class Tensors:
    """Per level: node inputs (+ log neighbour count, + one all-zero 'unknown' row at the end), and per link level
    the pairs' offsets, neighbour index (unknown -> the zero row) and link inputs.

    x_levels[k]: float32 (n_k + 1, width + 1), filled except the last column; the last row stays zero."""

    def __init__(self, x_levels: list[np.ndarray], g: dict):
        torch = _torch()
        self.x, self.off, self.nb, self.link = [], [], [], []
        for k, x in enumerate(x_levels):
            if k < len(g["n_nb"]):
                x[:-1, -1] = np.log1p(g["n_nb"][k])
            self.x.append(torch.from_numpy(x))
        for k, p in enumerate(g["pairs"]):
            n_next = len(x_levels[k + 1]) - 1
            self.off.append(csr(p["state"].to_numpy(), len(x_levels[k]) - 1))
            self.nb.append(np.where(p["nb"].to_numpy() < 0, n_next, p["nb"].to_numpy()))
            lk = p[LINK].to_numpy(dtype="float32").copy()
            lk[:, 2] = np.log1p(lk[:, 2])                      # weeks since contact, 0-77
            self.link.append(torch.from_numpy(lk))


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

            def forward(self, t: Tensors, ids: np.ndarray):
                # nodes needed at each level, from the outermost hop inwards
                need, hops = [ids], []
                for k in range(self.layers):
                    rows, seg = gather(t.off[k], need[k])
                    nb = t.nb[k][rows]
                    uniq, inv = np.unique(nb, return_inverse=True)
                    hops.append((rows, torch.from_numpy(seg), torch.from_numpy(inv.reshape(-1))))
                    need.append(uniq)
                h = [t.x[k][torch.from_numpy(need[k])] for k in range(self.layers + 1)]
                for i in range(self.layers):              # layer i updates levels 0 .. layers-1-i
                    new = []
                    for k in range(self.layers - i):
                        rows, seg, inv = hops[k]
                        link = t.link[k][torch.from_numpy(rows)]
                        new.append(self.drop(self.conv(i, h[k], h[k + 1][inv], link, seg, len(need[k]))))
                    h = new
                return self.out(h[0]).squeeze(1)

        return _SAGE()


def _check_unknown_rows(t: Tensors, layers: int):
    """The zero 'unknown' row of a level has no pairs of its own: give it an empty offset slot."""
    for k in range(min(layers, len(t.off))):
        if len(t.off[k]) == t.x[k].shape[0]:              # n + 1 offsets for n real rows: add one for the zero row
            t.off[k] = np.append(t.off[k], t.off[k][-1])


def train_score(t: Tensors, train_ids: np.ndarray, y: np.ndarray, score_ids: np.ndarray, d_in: int,
                settings: dict, seed: int) -> np.ndarray:
    """Fit one GraphSAGE on level-0 nodes train_ids (labels y) and return probabilities for score_ids."""
    torch = _torch()
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    model = SAGE(d_in + 1, settings["layers"], settings["hidden"], settings["dropout"])
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
            logit = model(t, train_ids[i])
            loss = (torch.nn.functional.binary_cross_entropy_with_logits(logit, yt[i], reduction="none")
                    * wt[i]).sum() / wt[i].sum()
            opt.zero_grad()
            loss.backward()
            opt.step()
    model.eval()
    out = np.empty(len(score_ids))
    with torch.no_grad():
        for b in range(0, len(score_ids), 8192):
            out[b:b + 8192] = torch.sigmoid(model(t, score_ids[b:b + 8192])).numpy()
    return out


def fit_score(g: dict, level_inputs: list[pd.DataFrame], train: pd.DataFrame, valid: pd.DataFrame,
              settings: dict | None = None, level_app: list[np.ndarray] | None = None) -> np.ndarray:
    """The whole method once the graph exists: g from build_graph on the focal states; level_inputs[k] = INPUTS of
    level k+1's states (app_score from the frame, or from level_app[k] when given); train / valid = the caller's rows
    (KEY + INPUTS, train with mule_by_day). Level-0 inputs come from train / valid themselves. Only train's labels
    are read."""
    s = DEFAULTS | (settings or {})
    focal = g["states"][0]
    pos = pd.Series(np.arange(len(focal)), index=pd.MultiIndex.from_frame(focal))

    def ids(d):
        i = pos.reindex(pd.MultiIndex.from_arrays([d["account_id"], d["weeks_since_open"]])).to_numpy()
        if np.isnan(i).any():
            raise ValueError("rows outside the graph's focal states")
        return i.astype(np.int64)

    prep = Prep().fit(train)
    tr, va = ids(train), ids(valid)
    xs = [np.zeros((len(focal) + 1, prep.width + 1), "float32")]          # + log neighbours column, + zero row
    prep.transform_into(train, xs[0], tr)
    prep.transform_into(valid, xs[0], va)
    for k, d in enumerate(level_inputs):
        x = np.zeros((len(d) + 1, prep.width + 1), "float32")
        if len(d):
            prep.transform_into(d, x, np.arange(len(d)), None if level_app is None else level_app[k])
        xs.append(x)
    t = Tensors(xs, g)
    _check_unknown_rows(t, s["layers"])
    y = train["mule_by_day"].to_numpy()
    score = np.zeros(len(valid))
    for seed in s["seeds"]:
        score += train_score(t, tr, y, va, prep.width, s, seed)
    return score / len(s["seeds"])


# ---------------------------------------------------------------- the comparison's interface
def prepare(out: str, accounts_months=(0, 1, 2, 3, 4), weeks=FOCAL_WEEKS, fanout=DEFAULTS["fanout"]) -> dict:
    """Graph of every focal account-week (accounts opened in `accounts_months`, `weeks`) and the activity inputs of
    every neighbour state. Public inputs only; independent of the fold, so built once."""
    graph.check(out)
    con = amldata.public(out)
    acc = con.execute("SELECT account_id, open_month FROM accounts").df()
    focal = acc.loc[acc.open_month.isin(accounts_months), ["account_id"]].merge(
        pd.DataFrame({"w": range(weeks[0], weeks[1] + 1)}), how="cross").sort_values(["account_id", "w"])
    con.execute("PRAGMA memory_limit='6GB'")
    edges = f"read_parquet('{graph.edges(out).replace(os.sep, '/')}')"
    g = build_graph(con, focal, edges, "(SELECT account_id, open_day FROM accounts)", fanout)
    con.close()
    later = g["states"][1:]
    inputs = []
    keep = ["account_id"] + [c for c in INPUTS if c != "app_score"]
    for st in later:
        d = node_inputs(load_store(out, st), st) if len(st) else node_inputs(pd.DataFrame(), st)
        inputs.append(d[keep].astype({c: "float32" for c in keep[1:]}))
        del d
        gc.collect()
    g["month_of"] = acc.set_index("account_id")["open_month"]
    return {"graph": g, "inputs": inputs}


def method(out: str, settings: dict | None = None):
    """fit(train, valid) -> validation scores, for models.comparison. The fold is read from train's months; the
    neighbours' application scores come from that fold's application model (seed `app_seed`)."""
    from models import lgbm_baseline as base
    from models.feature_lab import app_scores
    s = DEFAULTS | (settings or {})
    cache = {}

    def fit(train: pd.DataFrame, valid: pd.DataFrame) -> np.ndarray:
        if "prep" not in cache:
            cache["prep"] = prepare(out, fanout=s["fanout"][:s["layers"]])
            months = sorted(cache["prep"]["graph"]["month_of"].unique().tolist())
            cache["app"] = app_scores(out, s["app_seed"], other_months=months)
        f = [i for i, (tm, _) in enumerate(base.FOLDS, start=1) if set(tm) == set(train.open_month.unique())]
        if len(f) != 1:
            raise ValueError("training months do not match a fold of lgbm_baseline.FOLDS")
        app = cache["app"][f[0]]["app_score"]
        for d in (train, valid):
            gap = np.abs(d["account_id"].map(app).to_numpy() - d["app_score"].to_numpy())
            if not np.nanmax(gap) < 1e-9:
                raise ValueError("app_score differs from feature_lab.app_scores(seed=app_seed): wrong seed or data")
        g, inputs = cache["prep"]["graph"], cache["prep"]["inputs"]
        level_app = [d["account_id"].map(app).to_numpy(dtype="float32") for d in inputs]
        score = fit_score(g, inputs, train, valid, s, level_app)
        gc.collect()
        return score
    return fit
