"""Feature selection helpers (src/models/feature_selection.py) and the feature lab's --drop variants, on small
hand-made tables (no data needed)."""
import numpy as np
import pandas as pd

from features import candidates
from features.weekly import FEATURES as WEEKLY
from models import feature_lab as lab
from models import feature_selection as fs


def test_families_cover_every_input_once():
    cols = [c for g in fs.FAMILIES.values() for c in g]
    assert len(cols) == len(set(cols)) == 38                        # no feature in two families
    assert set(cols) == set(WEEKLY) | set(candidates.ADOPTED) | {"weeks_since_open", "app_score"}
    assert sorted(cols) == sorted(fs.ALL_INPUTS)


def test_spearman_clusters_groups_near_copies():
    rng = np.random.default_rng(0)
    a, b = rng.normal(size=2000), rng.normal(size=2000)
    df = pd.DataFrame({"a": a, "a_cubed": a ** 3,                    # same order as a: rho = 1
                       "a_noisy": a + rng.normal(scale=0.1, size=2000),
                       "b": b, "neg_b": -b,                          # rho = -1 counts as a copy too
                       "c": rng.normal(size=2000)})
    df.loc[:99, "c"] = np.nan                                        # gaps are allowed
    rho, cl = fs.spearman_clusters(df, list(df.columns), threshold=0.8)
    assert np.isclose(rho.loc["a", "a_cubed"], 1.0) and np.isclose(rho.loc["b", "neg_b"], -1.0)
    assert cl["a"] == cl["a_cubed"] == cl["a_noisy"]
    assert cl["b"] == cl["neg_b"] != cl["a"]
    assert (cl == cl["c"]).sum() == 1                                # c stands alone


def test_permute_columns_moves_a_group_as_a_block():
    x = pd.DataFrame({"p": np.arange(50.0), "q": np.arange(50.0) * 10, "r": np.arange(50.0)})
    y = fs.permute_columns(x, ["p", "q"], np.random.default_rng(1))
    assert sorted(y["p"]) == sorted(x["p"]) and not y["p"].equals(x["p"])   # same values, new order
    assert (y["q"] == y["p"] * 10).all()                                    # one order for the whole group
    assert y["r"].equals(x["r"]) and x["p"].equals(pd.Series(np.arange(50.0)))   # others and the input untouched


class _OnlyP:
    """A stand-in model whose score is column p: shuffling p must hurt, shuffling r must not."""
    def predict_proba(self, x):
        s = x["p"].to_numpy() / 100
        return np.c_[1 - s, s]


def test_permutation_drop_finds_the_used_feature():
    rng = np.random.default_rng(2)
    valid = pd.DataFrame({"p": rng.uniform(0, 100, 500), "r": rng.uniform(0, 100, 500)})
    valid["y"] = (valid["p"] > 90).astype(int)

    def measure(v, s):
        top = np.argsort(-s)[:50]
        return v["y"].to_numpy()[top].mean()                         # precision in the top 50

    d = fs.permutation_drop(_OnlyP(), valid, ["p", "r"], {"p": ["p"], "r": ["r"]}, measure, repeats=2)
    mean = d.groupby("group")["drop"].mean()
    assert mean["p"] > 0.5 and mean["r"] == 0.0
    assert len(d) == 4 and np.allclose(d["base"], measure(valid, valid["p"].to_numpy()))   # unshuffled score

    # several measures on the same shuffles: one row per measure, the same shuffles give the same drops
    two = fs.permutation_drop(_OnlyP(), valid, ["p", "r"], {"p": ["p"], "r": ["r"]},
                              lambda v, s: {"m1": measure(v, s), "m2": 2 * measure(v, s)}, repeats=2)
    assert len(two) == 8 and set(two["measure"]) == {"m1", "m2"}
    m1, m2 = (two[two.measure == k].reset_index(drop=True) for k in ("m1", "m2"))
    assert np.allclose(m1["drop"], d["drop"]) and np.allclose(m2["drop"], 2 * d["drop"])


def test_read_params_and_lgbm_settings(tmp_path):
    import json
    p = tmp_path / "tuned.json"
    p.write_text(json.dumps({"n_estimators": 500.0, "num_leaves": 15, "learning_rate": 0.03, "subsample_freq": 1}))
    got = lab.read_params(str(p))
    assert got["n_estimators"] == 500 and isinstance(got["n_estimators"], int) and got["learning_rate"] == 0.03
    assert lab.read_params(None) == {}
    s = lab.lgbm_settings(7, got)
    assert s["random_state"] == 7 and s["class_weight"] == "balanced" and s["deterministic"] and s["num_leaves"] == 15
    assert lab.lgbm_settings(42) == lab.lgbm_settings(42, {})            # no file -> the lab's defaults


def test_drop_variants_take_families_and_single_inputs():
    v = lab.drop_variants(["peer", "n_out_wk"])
    assert v == {"-peer": ["peer_ratio_money_in"], "-n_out_wk": ["n_out_wk"],
                 "-all": ["peer_ratio_money_in", "n_out_wk"]}
    assert lab.drop_variants(["mix", "abroad_out_share_cum"], together=True) == {"-set": fs.FAMILIES["mix"]}  # no repeats
    assert lab.drop_variants([]) == {}
    import pytest
    with pytest.raises(ValueError):
        lab.drop_variants(["not_a_feature"])


def test_variant_columns_adds_and_drops():
    base = ["a", "b", "c", "app_score"]
    assert lab.variant_columns(base, [], []) == base
    assert lab.variant_columns(base, ["x"], []) == base + ["x"]
    assert lab.variant_columns(base, [], ["b", "c"]) == ["a", "app_score"]
    assert lab.variant_columns(base, [], ["app_score", "absent"]) == ["a", "b", "c"]   # absent column ignored
    assert base == ["a", "b", "c", "app_score"]                      # the input list is not changed
