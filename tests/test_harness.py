"""Phase 5 harness (src/evaluation/score.py) and the frozen-model trainer (src/models/train.py).

Hand-made cohorts, no data needed: flags are permanent and follow the weekly budget, closed accounts leave the pool,
the any-time policy spends exactly its total, and the measures match a hand count. Guards: test months need
--final-test and are scored once. On data/v1 (skipped without its store): a model trains, reloads and refuses to
score its own training months.
"""
import json
import os
import shutil

import numpy as np
import pandas as pd
import pytest

from evaluation import score as sc

# cohort of 6 accounts opened on day 0 (week w ends on day 7w + 6)
# F: fake, mule from opening; R: real customer starting day 20 (week 2); C: fake closed by the bank on day 16;
# N1-N3: normal
TRUTH = pd.DataFrame({
    "account_id": ["C", "F", "N1", "N2", "N3", "R"], "open_month": 5, "open_day": 0,
    "is_launderer": [1, 1, 0, 0, 0, 1], "profile": ["fake", "fake", None, None, None, "witting"],
    "start_day": [10.0, 90.0, np.nan, np.nan, np.nan, 20.0], "exit_day": [16.0, np.nan, np.nan, np.nan, np.nan, np.nan],
    "first_alert_day": [12.0, np.nan, 3.0, np.nan, np.nan, 22.0],
    "customer_age": [50, 30, 20, 20, 60, 20]})


def _scores():
    s = {"C": [0.1, 0.2, 0.3, 0.3], "F": [0.5, 0.6, 0.7, 0.7], "N1": [0.9, 0.1, 0.1, 0.1],
         "N2": [0.4, 0.8, 0.1, 0.1], "N3": [0.0, 0.0, 0.0, 0.0], "R": [0.0, 0.0, 0.95, 0.9]}
    return pd.DataFrame([{"account_id": a, "weeks_since_open": w, "score": v} for a, vs in s.items()
                         for w, v in enumerate(vs)])


def test_mule_label_fakes_from_opening_real_from_start():
    assert sc.mule_at(TRUTH, 0).tolist() == [True, True, False, False, False, False]
    assert sc.mule_at(TRUTH, 2).tolist() == [True, True, False, False, False, True]   # R starts day 20 <= 20


def test_closed_accounts_leave_the_pool():
    live = sc.open_rows(_scores(), TRUTH)
    assert sorted(live.loc[live.account_id == "C", "weeks_since_open"]) == [0, 1]     # closed day 16, in week 2


def test_permanent_flags_follow_the_budget():
    live = sc.open_rows(_scores(), TRUTH)
    f = sc.permanent_flags(live, {0: 1, 1: 1, 2: 2})
    # week 0: N1 (0.9); week 1: N2 (0.8); week 2: R (0.95) and F (0.7); never twice, none in week 3 (no budget)
    assert f.to_dict() == {"N1": 0, "N2": 1, "R": 2, "F": 2}


def test_anytime_spends_exactly_the_total():
    live = sc.open_rows(_scores(), TRUTH)
    f = sc.anytime_flags(live, 3)
    assert set(f.index) == {"R", "N1", "N2"} and f.to_dict() == {"R": 2, "N1": 0, "N2": 1}


def test_measures_by_hand():
    live = sc.open_rows(_scores(), TRUTH)
    flags = {"model": sc.permanent_flags(live, {0: 1, 1: 1, 2: 2}), "rules": sc.rules_flags(TRUTH, 3)}
    summary, weekly = sc.measures(TRUTH, flags, 3)
    m, r = summary.set_index("policy").loc["model"], summary.set_index("policy").loc["rules"]
    assert (m.mules, m.flagged, m.caught) == (3, 4, 2)               # F and R caught, C missed (closed first)
    assert (r.flagged, r.caught) == (3, 2)                           # alerts on N1 (week 0), C (week 1), R (week 3)
    assert np.isclose(m.precision, 0.5) and np.isclose(r.precision, 2 / 3)
    assert m.caught_fake == "1/2" and m.caught_witting == "1/1" and r.caught_witting == "1/1"
    assert m.median_days_from_start == np.median([20 - 90, 20 - 20])  # F flagged day 20, 70 days before its start
    assert m.flagged_before_start == 1
    assert weekly.loc[weekly.week == 2, "open_accounts"].item() == 5
    h = sc.head_to_head(TRUTH, flags["model"], flags["rules"], 3)
    assert (h["both"], h["model_only"], h["rules_only"], h["neither"]) == (1, 1, 1, 0)
    assert h["median_days_model_earlier_when_both"] == 22 - 20       # R: model day 20, rules day 22


def test_test_months_need_the_flag_and_are_scored_once(tmp_path, monkeypatch):
    monkeypatch.setattr(sc, "RESULTS", str(tmp_path))
    with pytest.raises(SystemExit):
        sc.run("data/v1_full", [6, 7], [26], "x")
    with pytest.raises(SystemExit):
        sc.run("data/v1_full", [5], [26], "x", final_test=True)
    lock = tmp_path / "v1_full" / "final_test"
    lock.mkdir(parents=True)
    (lock / "LOCK.json").write_text("{}")
    with pytest.raises(SystemExit):
        sc.run("data/v1_full", [6, 7], [26], "x", final_test=True)


def test_rules_budget_guards_test_months():
    from evaluation import budget
    with pytest.raises(ValueError):
        budget._months((6,))
    assert budget._months((6, 7), allow_test=True) == "6, 7"


DATA = "data/v1"
needs_store = pytest.mark.skipif(not os.path.exists(os.path.join(DATA, "features", "weekly.parquet")),
                                 reason="data/v1 feature store not built")


@needs_store
def test_model_trains_reloads_and_refuses_its_training_months(tmp_path):
    from models import train
    name = "pytest_tmp"
    try:
        m = train.train(DATA, name, report_root=str(tmp_path))
        assert m["n_inputs"] == 38 and m["inputs"] == train.INPUTS
        booster, app, man = train.load(DATA, name)
        assert booster.num_feature() == 38 and len(app["coef"]) == len(app["columns"])
        with pytest.raises(ValueError):
            sc.score_cohort(DATA, [4], (0, 2), name)
        s = sc.score_cohort(DATA, [5], (0, 2), name)
        assert s["score"].between(0, 1).all() and set(s["weeks_since_open"]) == {0, 1, 2}
    finally:
        shutil.rmtree(train.model_dir(DATA, name), ignore_errors=True)


def test_by_age_counts_recall_and_false_positives():
    live = sc.open_rows(_scores(), TRUTH)
    flags = {"model": sc.permanent_flags(live, {0: 1, 1: 1, 2: 2})}            # N1, N2, R, F
    t = sc.by_age(TRUTH, flags, 3).set_index("age")
    # under 30: R (mule, caught), N1 and N2 (normal, both flagged); 30-49: F (caught); 50+: C (missed), N3
    assert (t.loc["under 30", "mules"], t.loc["under 30", "caught"], t.loc["under 30", "normal_flagged"]) == (1, 1, 2)
    assert t.loc["under 30", "false_positive_rate"] == 1.0 and t.loc["50+", "recall"] == 0.0
    assert t.loc["50+", "false_positive_rate"] == 0.0 and t["accounts"].sum() == len(TRUTH)


def test_calibration_keeps_order_and_matches_rates():
    from models import calibrate as cal
    rng = np.random.default_rng(0)
    score = rng.uniform(size=20000)
    y = (rng.uniform(size=20000) < 0.02 * score).astype(int)               # true chance = 2% x score
    for method in ("isotonic", "platt"):
        m = cal.fit(method, score, y)
        p = cal.apply(m, np.sort(score))
        assert np.all(np.diff(p) >= -1e-12)                                 # never reverses the ranking
        assert abs(p.mean() - y.mean()) < 0.005                             # probabilities, not class-weighted scores
        json_roundtrip = cal.apply(json.loads(json.dumps(m)), score)
        assert np.allclose(json_roundtrip, cal.apply(m, score))
    q = cal.quality(y, cal.apply(cal.fit("platt", score, y), score))
    assert q["brier"] < cal.quality(y, score)["brier"]                      # raw scores are poor probabilities
    r = cal.reliability(y, score)
    assert r["rows"].sum() == len(y)


def test_compare_refuses_different_cohorts(tmp_path, monkeypatch):
    from evaluation import compare
    monkeypatch.setattr(compare, "RESULTS", str(tmp_path))
    for name, months in (("a", [5]), ("b", [4])):
        d = tmp_path / "v1_full" / name
        d.mkdir(parents=True)
        (d / "settings.json").write_text(json.dumps({"cohort_months": months, "horizons": [26],
                                                     "budget_per_horizon": {"26": 1}, "cohort_accounts": 1}))
    with pytest.raises(ValueError):
        compare.compare("data/v1_full", "a", "b", "x")


def test_activity_inputs_are_the_frozen_ones_without_the_application():
    from models.train import INPUT_SETS
    assert len(INPUT_SETS["frozen"]) == 38 and INPUT_SETS["activity"] == [c for c in INPUT_SETS["frozen"]
                                                                            if c != "app_score"]


# ---------------------------------------------------------------- option B: share a model file between machines
def _data_folder(tmp, values, manifest=None):
    from features.fingerprint import FILES
    for f in FILES:
        p = tmp / f
        p.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame({"a": values, "b": [x * 0.1 for x in values]}).to_parquet(p, index=False)
    (tmp / "run_manifest.json").write_text(json.dumps(manifest or {"seed": 42, "baf_file": "data/raw/BAF_Base.csv"}))
    return str(tmp)


def test_fingerprint_ignores_row_order_and_catches_one_change(tmp_path):
    from features.fingerprint import FILES, differences, fingerprints
    a = fingerprints(_data_folder(tmp_path / "a", [1, 2, 3, 4]), use_cache=False)
    b = fingerprints(_data_folder(tmp_path / "b", [4, 3, 2, 1]), use_cache=False)
    c = fingerprints(_data_folder(tmp_path / "c", [1, 2, 3, 5]), use_cache=False)
    assert differences(a, b) == [] and set(differences(a, c)) == set(FILES)
    assert a[FILES[0]]["rows"] == 4 and isinstance(a[FILES[0]]["fingerprint"], int)


def test_data_check_accepts_same_content_from_another_machine(tmp_path):
    from features.fingerprint import fingerprints
    from models import train
    from features import manifest as fm
    out = _data_folder(tmp_path / "mine", [1, 2, 3], {"seed": 42, "baf_file": "data/raw/Base.csv"})
    other = _data_folder(tmp_path / "theirs", [1, 2, 3], {"seed": 42, "baf_file": "data\\raw\\BAF_Base.csv"})
    folder = tmp_path / "model"
    folder.mkdir()
    for f in train.MODEL_FILES:
        (folder / f).write_text(f)
    theirs = {"run_manifest_sha256": fm._sha256(os.path.join(other, "run_manifest.json"))}
    assert train.data_problems(out, str(folder), theirs)                          # old model: no fingerprints
    assert train.data_problems(out, str(folder), {**theirs, "input_fingerprints": fingerprints(other)}) == []
    changed = _data_folder(tmp_path / "changed", [1, 2, 4])
    assert train.data_problems(out, str(folder), {**theirs, "input_fingerprints": fingerprints(changed)})
    # an old model accepted through verified.json, only while the model files are the ones verified
    (folder / train.VERIFIED).write_text(json.dumps({"input_fingerprints": fingerprints(out),
                                                    "model_files_sha256": train.model_files_sha256(str(folder))}))
    assert train.data_problems(out, str(folder), theirs) == []
    (folder / "lgbm.txt").write_text("another model")
    assert train.data_problems(out, str(folder), theirs)


def test_final_test_cannot_skip_checks(tmp_path, monkeypatch):
    monkeypatch.setattr(sc, "RESULTS", str(tmp_path))
    with pytest.raises(SystemExit):
        sc.run("data/v1_full", [6, 7], [26], "x", final_test=True, check_data=False)


def test_shared_model_in_git_wins_and_cannot_be_overwritten(tmp_path, monkeypatch):
    from models import train
    monkeypatch.setattr(train, "REPORT_ROOT", str(tmp_path / "outputs"))
    out = str(tmp_path / "data" / "v1_full")
    local = tmp_path / "data" / "v1_full" / "models" / "m"
    local.mkdir(parents=True)
    (local / "lgbm.txt").write_text("local")
    assert train.find_model_dir(out, "m") == str(local)                      # nothing shared yet: the local model
    shared = tmp_path / "outputs" / "v1_full" / "m"
    shared.mkdir(parents=True)
    (shared / "manifest.json").write_text("{}")
    assert train.find_model_dir(out, "m") == str(local)                      # a manifest alone is not a model
    (shared / "lgbm.txt").write_text("shared")
    assert train.find_model_dir(out, "m") == str(shared)                     # the committed model of record
    with pytest.raises(ValueError):
        train.train(out, "m", report_root=str(tmp_path / "outputs"))          # never retrained over


def test_model_hashes_ignore_line_endings(tmp_path):
    from models import train
    for folder, eol in (("unix", "\n"), ("windows", "\r\n")):
        (tmp_path / folder).mkdir()
        for f in train.MODEL_FILES:
            (tmp_path / folder / f).write_bytes(f"line one{eol}line two{eol}".encode())
    assert train.model_files_sha256(str(tmp_path / "unix")) == train.model_files_sha256(str(tmp_path / "windows"))
