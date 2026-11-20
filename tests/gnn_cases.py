"""models.gnn (GraphSAGE on the payment graph): neighbour rules, no look-ahead, preprocessing, learning, labels.

All on small hand-made graphs; no data folder needed. The real-data run belongs to the methods comparison once it is
pre-registered there."""
import duckdb
import numpy as np
import pandas as pd
import pytest

torch = pytest.importorskip("torch")

from models import gnn  # noqa: E402
from models.gnn import INPUTS, LINK  # noqa: E402


# ---------------------------------------------------------------- toy graphs
def payments(rng, ids, open_day, n, day_hi):
    """n payments between random pairs, each seen from both sides (as graph_edges.parquet holds them)."""
    rows = []
    for _ in range(n):
        a, b = rng.choice(len(ids), 2, replace=False)
        lo = max(open_day[a], open_day[b])
        d = int(rng.integers(lo, day_hi))
        amt = float(np.round(rng.uniform(1, 500), 2))
        rows += [(ids[a], ids[b], d, "out", amt), (ids[b], ids[a], d, "in", amt)]
    return pd.DataFrame(rows, columns=["account_id", "nb_id", "day", "direction", "amount"])


def con_with(edges, acc):
    con = duckdb.connect()
    con.register("edges_t", edges)
    con.register("acc_t", acc)
    return con


def reference_pairs(states, edges, acc, fanout):
    """Plain-Python version of gnn.pairs_sql."""
    open_day = acc.set_index("account_id")["open_day"]
    out = []
    for st, (a, w) in enumerate(zip(states.account_id, states.w)):
        cut = open_day[a] + 7 * w + 6
        e = edges[(edges.account_id == a) & (edges.day <= cut)]
        if e.empty:
            continue
        g = e.groupby("nb_id").agg(m_in=("amount", lambda s: s[e.loc[s.index, "direction"] == "in"].sum()),
                                   m_out=("amount", lambda s: s[e.loc[s.index, "direction"] == "out"].sum()),
                                   last_day=("day", "max")).reset_index()
        g = g.sort_values(["last_day", "nb_id"], ascending=[False, True]).head(fanout)
        for r in g.itertuples():
            k = cut - open_day[r.nb_id] - 6
            out.append({"state": st, "nb_id": r.nb_id, "nb_w": min(77, k // 7) if k >= 0 else None,
                        "n_nb": e.nb_id.nunique(), "log_money_in": np.log1p(r.m_in),
                        "log_money_out": np.log1p(r.m_out), "weeks_since_contact": (cut - r.last_day) / 7})
    return pd.DataFrame(out)


@pytest.fixture
def toy():
    rng = np.random.default_rng(0)
    ids = np.array([f"A{i:03d}" for i in range(40)])
    open_day = rng.integers(0, 60, len(ids))
    acc = pd.DataFrame({"account_id": ids, "open_day": open_day})
    edges = payments(rng, ids, open_day, 250, 200)
    states = acc[["account_id"]].merge(pd.DataFrame({"w": range(0, 8)}), how="cross")
    return acc, edges, states


# ---------------------------------------------------------------- graph
def test_pairs_match_the_reference(toy):
    acc, edges, states = toy
    st = states.assign(state=np.arange(len(states)))
    con = con_with(edges, acc)
    con.register("st", st)
    got = con.execute(gnn.pairs_sql("st", "edges_t", "acc_t", 3)).df()
    exp = reference_pairs(states, edges, acc, 3)
    assert len(got) == len(exp) > 50
    assert (got.groupby("state").size() <= 3).all()
    pd.testing.assert_series_equal(got["nb_id"], exp["nb_id"], check_names=False)
    assert (got["nb_w"].isna() == exp["nb_w"].isna()).all()
    assert (got["nb_w"].dropna().astype(int).to_numpy() == exp["nb_w"].dropna().astype(int).to_numpy()).all()
    for c in ["n_nb", "log_money_in", "log_money_out", "weeks_since_contact"]:
        np.testing.assert_allclose(got[c].to_numpy(float), exp[c].to_numpy(float), rtol=1e-9, err_msg=c)


def test_no_look_ahead(toy):
    """Payments after day D cannot change any state whose cut-off is on or before D, at any level."""
    acc, edges, states = toy
    d = 90
    od = acc.set_index("account_id")["open_day"]
    early = states[(states["account_id"].map(od) + 7 * states["w"] + 6 <= d).to_numpy()].reset_index(drop=True)
    assert len(early) > 50
    full = gnn.build_graph(con_with(edges, acc), early, "edges_t", "acc_t", (4, 3))
    cut = gnn.build_graph(con_with(edges[edges.day <= d], acc), early, "edges_t", "acc_t", (4, 3))
    assert len(full["pairs"][0]) > 20 and len(full["pairs"][1]) > 20
    for k in range(2):
        pd.testing.assert_frame_equal(full["pairs"][k], cut["pairs"][k])
        np.testing.assert_array_equal(full["n_nb"][k], cut["n_nb"][k])
        s = full["states"][k + 1]                           # every neighbour state is itself early
        assert (s["account_id"].map(od) + 7 * s["w"] + 6 <= d).all()
    for k in range(3):
        pd.testing.assert_frame_equal(full["states"][k], cut["states"][k])


def test_neighbour_week_is_never_later_and_unknown_when_new():
    acc = pd.DataFrame({"account_id": ["A1", "A2"], "open_day": [0, 10]})
    # A2 opened on day 10, paid A1 on day 12: at A1's week 1 (cut-off 13) A2 has not finished its week 0 (ends 16)
    edges = pd.DataFrame([("A1", "A2", 12, "in", 5.0), ("A2", "A1", 12, "out", 5.0)],
                         columns=["account_id", "nb_id", "day", "direction", "amount"])
    states = pd.DataFrame({"account_id": ["A1", "A1", "A1"], "w": [0, 1, 2]})
    g = gnn.build_graph(con_with(edges, acc), states, "edges_t", "acc_t", (5,))
    p = g["pairs"][0]
    assert list(p.state) == [1, 2]                         # week 0 (cut-off 6) is before the payment
    assert p.loc[0, "nb"] == -1 and p.loc[0, "nb_known"] == 0
    assert p.loc[1, "nb_known"] == 1                        # cut-off 20: A2's week 0 (ends 16) is known
    assert g["states"][1].to_dict("records") == [{"account_id": "A2", "w": 0}]
    assert list(g["n_nb"][0]) == [0, 1, 1]


def test_gather_returns_each_ids_rows_in_order():
    state = np.array([0, 0, 2, 3, 3, 3])
    off = gnn.csr(state, 5)
    rows, seg = gnn.gather(off, np.array([3, 1, 0, 2]))
    assert list(rows) == [3, 4, 5, 0, 1, 2]
    assert list(seg) == [0, 0, 0, 2, 2, 3]
    with pytest.raises(ValueError):
        gnn.csr(np.array([1, 0]), 2)


# ---------------------------------------------------------------- preprocessing
def frame(rng, n):
    d = pd.DataFrame(rng.random((n, len(INPUTS))) * 3, columns=INPUTS)
    d.loc[::7, "med_in_out_minutes_wk"] = np.nan
    return d


def test_prep_is_fitted_on_training_rows_only():
    rng = np.random.default_rng(1)
    tr, va = frame(rng, 200), frame(rng, 50)
    p = gnn.Prep().fit(tr)
    before = p.transform(tr)
    gnn.Prep().fit(tr).transform(va * 100)                  # another fit on the same rows, any validation rows
    np.testing.assert_array_equal(gnn.Prep().fit(tr).transform(tr), before)
    x = p.transform(tr)
    assert x.shape == (200, len(INPUTS) + 1) and not np.isnan(x).any()
    flag = x[:, -1]
    assert flag.sum() == tr["med_in_out_minutes_wk"].isna().sum()
    j = INPUTS.index("out_1h_share_wk")                      # shares clipped to [0, 1] before scaling
    assert np.isclose(p.transform(tr.assign(out_1h_share_wk=5.0))[:, j], p.transform(tr.assign(out_1h_share_wk=1.0))[:, j]).all()
    k = INPUTS.index("money_in_wk")
    assert abs(x[:, k].mean()) < 1e-6 and abs(x[:, k].std() - 1) < 1e-3


# ---------------------------------------------------------------- learning
def learnable(n=400, seed=0, links=True):
    """Week-0 accounts; an account is a mule when an account it exchanged money with is 'hot' (high money in).
    Its own inputs are noise, so only the graph can tell."""
    rng = np.random.default_rng(seed)
    ids = np.array([f"A{i:04d}" for i in range(n)])
    acc = pd.DataFrame({"account_id": ids, "open_day": 0})
    hot = rng.random(n) < 0.15
    x = frame(rng, n).assign(account_id=ids, weeks_since_open=0.0)
    x["money_in_wk"] = np.where(hot, 50.0, 1.0) * rng.uniform(0.8, 1.2, n)
    rows, nbs = [], {a: set() for a in range(n)}
    for a in range(n):
        for b in rng.choice(n, 2, replace=False):
            if b != a:
                rows += [(ids[a], ids[b], 3, "out", 10.0), (ids[b], ids[a], 3, "in", 10.0)]
                nbs[a].add(b), nbs[b].add(a)
    y = np.array([int(any(hot[b] for b in nbs[a])) for a in range(n)])
    edges = pd.DataFrame(rows if links else [], columns=["account_id", "nb_id", "day", "direction", "amount"])
    if not links:
        edges = edges.astype({"day": "int64", "amount": "float64"})
    states = acc[["account_id"]].assign(w=0)
    df = x.assign(mule_by_day=y, open_month=np.where(np.arange(n) < n // 2, 0, 1))
    df["own_money_in"] = df["money_in_wk"]
    df["money_in_wk"] = 1.0 * rng.uniform(0.8, 1.2, n)        # own value hidden; the neighbours' value is kept below
    return acc, edges, states, df


FAST = {"layers": 1, "fanout": (5,), "hidden": 32, "epochs": 20, "batch": 64, "lr": 1e-2, "seeds": (1,)}


def run(acc, edges, states, df, settings):
    from sklearn.metrics import roc_auc_score
    g = gnn.build_graph(con_with(edges, acc), states, "edges_t", "acc_t", settings["fanout"])
    look = df.set_index("account_id")
    level = []
    for st in g["states"][1:]:
        d = look.loc[st["account_id"]].reset_index()
        d["money_in_wk"] = d["own_money_in"].to_numpy()       # a neighbour shows its real money in
        level.append(d)
    train, valid = df[df.open_month == 0], df[df.open_month == 1]
    s = gnn.fit_score(g, level, train, valid, settings)
    return s, roc_auc_score(valid["mule_by_day"], s)


def test_learns_from_neighbours_and_not_without_links():
    acc, edges, states, df = learnable()
    _, auc = run(acc, edges, states, df, FAST)
    acc2, edges2, states2, df2 = learnable(links=False)
    _, auc_none = run(acc2, edges2, states2, df2, FAST)
    assert auc > 0.85, auc
    assert auc_none < 0.7, auc_none


def test_two_layers_run_and_same_seed_repeats():
    acc, edges, states, df = learnable(n=200)
    two = FAST | {"layers": 2, "fanout": (5, 3), "epochs": 3}
    a, _ = run(acc, edges, states, df, two)
    b, _ = run(acc, edges, states, df, two)
    np.testing.assert_array_equal(a, b)
    assert a.shape == (100,) and ((a > 0) & (a < 1)).all()


def test_validation_labels_are_never_read():
    acc, edges, states, df = learnable(n=200)
    s = FAST | {"epochs": 3}
    a, _ = run(acc, edges, states, df, s)
    shuffled = df.copy()
    v = shuffled.open_month == 1
    shuffled.loc[v, "mule_by_day"] = 1 - shuffled.loc[v, "mule_by_day"]
    b, _ = run(acc, edges, states, shuffled, s)
    np.testing.assert_array_equal(a, b)
