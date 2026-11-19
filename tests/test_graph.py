"""Payment-graph features (src/features/graph.py) and neighbour-suspicion features (src/models/graph_nb.py).

Hand-made tables for the neighbour step (no data needed): a neighbour counts only from its first contact, and only
its scores with a cut-off on or before the focal week's cut-off. On data/v1 (skipped without its graph store): weeks
ending before a day D do not change when every transaction after D is removed, and the neighbour counts equal a
direct pandas count from the public transactions.
"""
import os

import duckdb
import numpy as np
import pandas as pd
import pytest

from models.graph_nb import FEATURES as NB, nb_sql

DATA = os.environ.get("SIM_OUT", "data/v1")


def _nb(grid, edges, scores, hot=0.5):
    con = duckdb.connect()
    for name, t in (("grid_t", grid), ("edges_t", edges), ("scores_t", scores)):
        con.register(name, t)
    return con.execute(nb_sql("grid_t", "edges_t", "scores_t", hot)).df().set_index(["account_id", "weeks_since_open"])


def test_neighbour_scores_never_look_ahead():
    grid = pd.DataFrame({"account_id": "F", "open_day": 0, "w": range(6)})     # cut-offs 6, 13, 20, 27, 34, 41
    edges = pd.DataFrame({"account_id": ["F", "F"], "nb_id": ["N1", "N2"], "day": [8, 30]})   # weeks 1 and 4
    scores = pd.DataFrame({"account_id": ["N1", "N1", "N1", "N2"], "cutoff_day": [5, 13, 21, 30],
                           "score": [0.1, 0.2, 0.9, 0.7]})
    r = _nb(grid, edges, scores)
    assert np.isnan(r.loc[("F", 0), "g_nb_max_score"])                       # no contact yet
    assert np.isclose(r.loc[("F", 1), "g_nb_max_score"], 0.2)                 # N1's score as of day 13, not 0.9
    assert np.isclose(r.loc[("F", 2), "g_nb_max_score"], 0.2)                 # day 21 > cut-off 20
    assert np.isclose(r.loc[("F", 3), "g_nb_max_score"], 0.9)
    assert np.isclose(r.loc[("F", 4), "g_nb_max_score"], 0.9)                 # N2 (0.7) now counts too
    assert np.isclose(r.loc[("F", 4), "g_nb_max_score_4wk"], 0.9)             # N1 contacted in week 1 = w - 3
    assert np.isclose(r.loc[("F", 5), "g_nb_max_score_4wk"], 0.7)             # week 1 left the 4-week window
    assert r["g_nb_n_hot"].tolist() == [0, 0, 0, 1, 2, 2]


def test_neighbour_features_do_not_mix_accounts():
    grid = pd.DataFrame({"account_id": ["F", "G"], "open_day": [0, 0], "w": [2, 2]})
    edges = pd.DataFrame({"account_id": ["F"], "nb_id": ["N1"], "day": [3]})
    scores = pd.DataFrame({"account_id": ["N1"], "cutoff_day": [10], "score": [0.8]})
    r = _nb(grid, edges, scores)
    assert np.isclose(r.loc[("F", 2), "g_nb_max_score"], 0.8)
    assert np.isnan(r.loc[("G", 2), "g_nb_max_score"]) and r.loc[("G", 2), "g_nb_n_hot"] == 0
    assert list(r.columns) == NB


needs_graph = pytest.mark.skipif(not os.path.exists(os.path.join(DATA, "features", "graph_weekly.parquet")),
                                 reason="graph store not built (python -m features graph --out data/v1)")


@needs_graph
def test_graph_weeks_ending_before_a_day_ignore_later_rows():
    import amldata
    from features import graph
    con = amldata.public(DATA)
    store = os.path.join(DATA, "features", "weekly.parquet")
    cap = 90
    full = con.execute(graph.weekly_sql(0, store)).df()
    cut = con.execute(graph.weekly_sql(0, store, max_day=cap)).df()
    open_day = con.execute("SELECT account_id, open_day FROM accounts WHERE open_month = 0").df()
    key = ["account_id", "weeks_since_open"]
    a = full.merge(open_day, on="account_id")
    keep = a["open_day"] + 7 * a["weeks_since_open"] + 6 <= cap
    assert keep.sum() > 10_000
    x = a[keep].set_index(key)[graph.FEATURES].sort_index()
    y = cut.set_index(key).loc[x.index, graph.FEATURES]
    pd.testing.assert_frame_equal(x, y, check_dtype=False)


@needs_graph
def test_graph_neighbour_count_matches_pandas():
    import amldata
    from features import graph
    con = amldata.public(DATA)
    g = graph.load(DATA, (0, 26), months=(0,))
    acc = con.execute("SELECT account_id, open_day FROM accounts WHERE open_month = 0 ORDER BY account_id LIMIT 300").df()
    tx = con.execute(f"""SELECT account_id, counterparty_id, day FROM transactions WHERE counterparty_id LIKE 'A%'
                         AND account_id IN (SELECT account_id FROM accounts WHERE open_month = 0
                                            ORDER BY account_id LIMIT 300)""").df().merge(acc, on="account_id")
    tx["w"] = (tx["day"] - tx["open_day"]) // 7
    first = tx.groupby(["account_id", "counterparty_id"])["w"].min().reset_index()
    for w in (0, 5, 26):
        want = first[first.w <= w].groupby("account_id").size().reindex(acc.account_id, fill_value=0)
        got = g[g.weeks_since_open == w].set_index("account_id")["g_n_nb_cum"].reindex(acc.account_id)
        assert (got.to_numpy() == want.to_numpy()).all()
