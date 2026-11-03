"""Phase 2: run notebooks/02_preprocess.ipynb on the 50k data and check the files it promises.

The notebook's section 7 asserts every cleaning check (no NaN in linear mode, fit uses months 0-4 only, files and
JSON reproduce the tables...), so a run that finishes means those passed; this test makes pytest run it.
It runs on a temporary folder that links to SIM_OUT's files, so SIM_OUT/features (real model inputs) is never written.
"""
import json
import os
import shutil

import pandas as pd
import pytest

from features.__main__ import run_notebook

OUT = os.environ.get("SIM_OUT", "data/v1")
KEYS = ["account_id", "open_month"]

needs_data = pytest.mark.skipif(not os.path.exists(os.path.join(OUT, "accounts.parquet")), reason="no simulator output")


@needs_data
def test_preprocess_notebook_runs_and_writes_its_files(tmp_path, monkeypatch):
    data, report = tmp_path / "data", tmp_path / "report"
    data.mkdir()
    for name in os.listdir(OUT):                                # link the data files; features/ stays out
        if os.path.isfile(os.path.join(OUT, name)):
            src = os.path.abspath(os.path.join(OUT, name))
            try:
                os.symlink(src, data / name)
            except OSError:                                     # Windows: symlinks need admin or Developer Mode
                try:
                    os.link(src, data / name)                   # hard link: same file, no copy (same drive)
                except OSError:
                    shutil.copy2(src, data / name)
    monkeypatch.setenv("EDA_DATA", str(data))                   # restored after the test
    monkeypatch.setenv("EDA_REPORT", str(report))
    run_notebook("02_preprocess.ipynb", str(data), str(report))
    for name in ("02_preprocess.ipynb", "report.md", "params.json"):
        assert (report / name).exists(), name

    feats = os.path.join(data, "features")
    m = json.load(open(os.path.join(feats, "preprocess_manifest.json")))
    assert m["params"]["fitted_on"]["months"] == [0, 1, 2, 3, 4]
    assert json.load(open(report / "params.json"))["params"] == m["params"]
    n_accounts = len(pd.read_parquet(os.path.join(OUT, "accounts.parquet"), columns=["account_id"]))
    for mode in ("linear", "tree"):
        f = pd.read_parquet(os.path.join(feats, f"accounts_{mode}.parquet"))
        assert len(f) == n_accounts and f["account_id"].is_unique
        assert list(f.columns[:2]) == KEYS and list(f.columns[2:]) == m["columns"][mode]
        assert "open_day" not in f.columns
    lin = pd.read_parquet(os.path.join(feats, "accounts_linear.parquet"))
    assert not lin.drop(columns=KEYS).isna().any().any()
