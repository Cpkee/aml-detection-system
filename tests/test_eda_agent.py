"""The EDA agent's insights ledger (outputs/modelling/eda_agent/insights.csv) stays well formed.

The eda-explorer agent appends rows; /feature-round and the feature-engineer agent change only status, trial and
note. No data needed.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "outputs" / "modelling" / "eda_agent" / "insights.csv"
COLUMNS = ["id", "round", "date", "finding", "evidence", "who", "before_start", "closest_store_feature", "sim_setting",
           "sim_strength", "artefact", "buildable", "feature_sketch", "status", "trial", "note"]
CHOICES = {"who": {"fake", "real", "all"}, "before_start": {"yes", "no"}, "buildable": {"store", "raw"},
           "status": {"new", "approved", "rejected", "tried", "candidate", "confirmed", "not_confirmed", "dropped"}}
FILLED = ["id", "round", "date", "finding", "evidence", "who", "before_start", "sim_setting", "artefact", "buildable",
          "status"]


def test_ledger_is_well_formed():
    df = pd.read_csv(LEDGER, dtype=str)
    assert list(df.columns) == COLUMNS
    assert df["id"].is_unique
    assert df[FILLED].notna().all().all(), "every insight needs these fields"
    for col, ok in CHOICES.items():
        assert set(df[col].dropna()) <= ok, f"{col}: unexpected values {set(df[col].dropna()) - ok}"
    assert (df["artefact"].str.split().str[0].str.rstrip(":,").isin({"no", "partly", "yes"})).all()
    assert (df["id"].str.split("-").str[0] == df["round"]).all(), "id starts with its round, e.g. r01-3"
    for rnd in df["round"].unique():
        assert (ROOT / "notebooks" / f"07_eda_agent_{rnd}.ipynb").exists(), f"round {rnd} has no notebook"
