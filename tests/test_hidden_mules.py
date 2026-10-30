"""Outlier appendix scoring (src/evaluation/hidden_mules.py) and M2's bank label (models.train.bank_confirmed).

The counting and the bootstrap run on small hand-made inputs (no data needed); the bank label is checked on real data
(SIM_OUT, default data/v1): closed accounts are launderers only, and test months are refused."""
import os

import pandas as pd
import pytest

import amldata
from evaluation import hidden_mules
from models import train as trainer

OUT = os.environ.get("SIM_OUT", "data/v1")
needs_data = pytest.mark.skipif(not os.path.exists(os.path.join(OUT, "accounts.parquet")), reason="no simulator output")


def test_caught_by_counts_each_group():
    groups = pd.Series({"a": "bank_confirmed", "b": "never_confirmed", "c": "never_confirmed"})
    t = hidden_mules.caught_by(groups, {"rules": {"a"}, "rarity": {"b", "c", "x"}})
    assert t.set_index("group").to_dict("index") == {"never_confirmed": {"mules": 2, "rules": 0, "rarity": 2},
                                                     "bank_confirmed": {"mules": 1, "rules": 1, "rarity": 0}}


def test_bootstrap_difference_and_interval():
    mules = [f"M{i}" for i in range(40)]
    caught = {"a": set(mules[:30]), "b": set(mules[:10]), "c": set(mules[:30])}
    b = hidden_mules.bootstrap(mules, caught).set_index(["a", "b"])
    assert b.loc[("a", "b"), "difference"] == 20 and b.loc[("a", "b"), "clear"]
    assert b.loc[("a", "c"), "difference"] == 0 and not b.loc[("a", "c"), "clear"]
    assert b.loc[("a", "b"), "low_95"] <= 20 <= b.loc[("a", "b"), "high_95"]


def test_test_months_are_refused():
    with pytest.raises(SystemExit, match="D1"):
        hidden_mules.run("data/none", (6, 7), {}, "unused")


def test_unknown_label_is_refused():
    with pytest.raises(ValueError):
        trainer.train("data/none", "x", label="oracle")


@needs_data
def test_bank_label_is_closed_launderers_only():
    months = (0, 1, 2, 3, 4)
    bank = trainer.bank_confirmed(OUT, months)
    y = amldata.labels(OUT, months=months).set_index("account_id")["is_launderer"]
    assert bank.sum() > 0 and (y.loc[bank.index[bank == 1]] == 1).all()   # only launderers are ever closed
    assert bank.sum() < y.sum()                                          # the bank knows only some of them
    with pytest.raises(ValueError):
        trainer.bank_confirmed(OUT, (6,))
