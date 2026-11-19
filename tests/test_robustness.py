"""Robustness summary (src/evaluation/robustness.py): verdict rule, band, and agreement with the harness.

The second half reads only committed harness outputs (outputs/modelling/results/<run>/final_test/), so it runs
without any data folder.
"""
import os
import shutil

import pandas as pd
import pytest

from evaluation import robustness as rb


def test_verdict_boundaries():
    assert rb.verdict(lead=0.31, lead_lo=0.20, band_lo=0.31) == "holds"      # on the floor counts as inside
    assert rb.verdict(lead=0.60, lead_lo=0.50, band_lo=0.31) == "holds"      # above the band
    assert rb.verdict(lead=0.30, lead_lo=0.01, band_lo=0.31) == "shrinks"
    assert rb.verdict(lead=0.30, lead_lo=0.00, band_lo=0.31) == "fails"      # interval includes 0
    assert rb.verdict(lead=-0.10, lead_lo=-0.20, band_lo=0.31) == "fails"    # the rules catch more


def _write(root, run, rows):
    d = root / run / "final_test"
    d.mkdir(parents=True)
    pd.DataFrame(rows, columns=["profile", "start_week", "rules_first_alert_week", "model_flag_week_w26"]
                 ).to_csv(d / "launderers.csv", index=False)
    _by_age(d, {"model": (1, 2, 4), "rules": (2, 2, 2)})


def _by_age(d, flagged):
    """A made-up by_age_w26.csv: per band 1,010 / 2,020 / 505 accounts, of which 10 / 20 / 5 mules, so 1,000 /
    2,000 / 500 normal accounts; flagged = normal accounts flagged per band."""
    rows = []
    for policy, f in flagged.items():
        for age, acc, mul, n in zip(["under 30", "30-49", "50+"], [1010, 2020, 505], [10, 20, 5], f):
            rows.append({"policy": policy, "age": age, "accounts": acc, "mules": mul, "caught": 0, "recall": 0.0,
                         "normal_flagged": n, "false_positive_rate": n / (acc - mul), "precision": 0.0})
    pd.DataFrame(rows).to_csv(d / "by_age_w26.csv", index=False)


@pytest.fixture
def fake_results(tmp_path, monkeypatch):
    """Hand-made runs: 10 mules each, plus one real customer starting after week 26 (not a mule by the horizon)."""
    late = ("witting", 40, None, None)
    caught = lambda model, rules: ([("fake", 10, 12, 11)] * rules + [("fake", 10, None, 11)] * (model - rules)
                                   + [("unwitting", 5, None, None)] * (10 - model) + [late])
    _write(tmp_path, "v1_full", caught(6, 2))          # lead 0.4
    _write(tmp_path, "seed__44", caught(7, 2))         # lead 0.5 -> band 0.3 to 0.5
    _write(tmp_path, "good", caught(8, 4))             # lead 0.4 -> holds
    _write(tmp_path, "bad", [("fake", 10, 12, None)] * 5 + [("fake", 10, None, 11)] * 5)   # lead 0 -> fails
    _write(tmp_path, "rules_late", [("fake", 10, 27, 11)] * 10)    # rules alert after week 26: not caught
    monkeypatch.setattr(rb, "RESULTS", str(tmp_path))


def test_table_on_hand_made_runs(fake_results):
    t = rb.table(["seed__44", "good", "bad", "rules_late"]).set_index("run")
    assert t.mules.tolist() == [10, 10, 10, 10, 10]
    assert t.loc["v1_full", ["model_caught", "rules_caught"]].tolist() == [6, 2]
    assert t.loc["rules_late", ["model_caught", "rules_caught"]].tolist() == [10, 0]
    assert t.band_lo.iloc[0] == pytest.approx(0.3) and t.band_hi.iloc[0] == pytest.approx(0.5)
    assert t.verdict.tolist() == ["", "", "holds", "fails", "holds"]


def test_band_has_a_minimum_width(fake_results, tmp_path):
    """A yardstick equal to the headline still gives a band of +/- 0.05."""
    shutil.rmtree(tmp_path / "seed__44")
    shutil.copytree(tmp_path / "v1_full", tmp_path / "seed__44")
    t = rb.table(["seed__44"])
    assert t.band_lo.iloc[0] == pytest.approx(0.4 - rb.MIN_HALF_BAND)


def test_mcnemar_on_a_hand_made_run(fake_results):
    """'good': 4 caught by both, 4 by the model only, 0 by the rules only, 2 by neither (the late starter is out).
    chi2 = (|4 - 0| - 1)^2 / 4 = 2.25; exact p = 2 * (1/2)^4 = 0.125."""
    r = rb.mcnemar("good")
    assert (r["both"], r["model_only"], r["rules_only"], r["neither"]) == (4, 4, 0, 2)
    assert r["chi2"] == pytest.approx(2.25) and r["p_exact"] == pytest.approx(0.125)


def test_mcnemar_is_symmetric_and_capped(fake_results):
    """'bad': 5 rules only, 5 model only -> no evidence either way, p capped at 1."""
    r = rb.mcnemar("bad")
    assert (r["model_only"], r["rules_only"]) == (5, 5)
    assert r["chi2"] == pytest.approx(0.1) and r["p_exact"] == 1.0


def test_no_yardstick_no_verdict(fake_results):
    assert "verdict" not in rb.table(["good"]).columns


@pytest.mark.parametrize("runs", [["v1_full"], ["good", "good"], ["no_such_run"]])
def test_bad_run_names_are_refused(fake_results, runs):
    with pytest.raises(SystemExit):
        rb.table(runs)


def test_subset_does_not_overwrite_the_committed_summary(fake_results, tmp_path, monkeypatch):
    out = tmp_path / "summary.csv"
    out.write_text("the committed record")
    monkeypatch.setattr(rb, "OUT", str(out))
    monkeypatch.setattr("sys.argv", ["robustness", "seed__44", "good"])
    rb.main()
    assert out.read_text() == "the committed record"
    monkeypatch.setattr("sys.argv", ["robustness", "seed__44", "good", "--to", str(tmp_path / "sub.csv")])
    rb.main()
    assert len(pd.read_csv(tmp_path / "sub.csv")) == 3 and out.read_text() == "the committed record"


def test_amendment_rows_use_the_plan_band(fake_results):
    """An amendment run gets the row it would have in table(): same columns, band from the headline and seed__44."""
    a = rb.amendment_table(["good", "bad"])
    full = rb.table(["seed__44", "good", "bad"])
    assert a.run.tolist() == ["good", "bad"] and a.columns.tolist() == full.columns.tolist()
    pd.testing.assert_frame_equal(a, full.iloc[2:].reset_index(drop=True))
    assert a.verdict.tolist() == ["holds", "fails"] and a.band_lo.tolist() == pytest.approx([0.3, 0.3])


def test_amendment_cli_skips_missing_runs(fake_results, tmp_path, monkeypatch, capsys):
    out, summary = tmp_path / "summary_amendments.csv", tmp_path / "summary.csv"
    summary.write_text("the committed record")
    monkeypatch.setattr(rb, "AMENDMENT_RUNS", ["not_run_yet", "good"])
    monkeypatch.setattr(rb, "AMENDMENT_OUT", str(out))
    monkeypatch.setattr(rb, "OUT", str(summary))
    monkeypatch.setattr("sys.argv", ["robustness", "--amendment"])
    rb.main()
    assert "skipped, no final test yet: not_run_yet" in capsys.readouterr().out
    t = pd.read_csv(out, keep_default_na=False)
    assert t.run.tolist() == ["good"] and t.verdict.tolist() == ["holds"]
    assert summary.read_text() == "the committed record"


def test_amendment_cli_writes_nothing_without_runs(fake_results, tmp_path, monkeypatch):
    monkeypatch.setattr(rb, "AMENDMENT_RUNS", ["not_run_yet"])
    monkeypatch.setattr(rb, "AMENDMENT_OUT", str(tmp_path / "summary_amendments.csv"))
    monkeypatch.setattr("sys.argv", ["robustness", "--amendment"])
    with pytest.raises(SystemExit):
        rb.main()
    assert not (tmp_path / "summary_amendments.csv").exists()


def test_fpr_ratio_on_a_made_up_table(tmp_path, monkeypatch):
    d = tmp_path / "run" / "final_test"
    d.mkdir(parents=True)
    _by_age(d, {"model": (1, 6, 4), "rules": (2, 4, 1)})
    monkeypatch.setattr(rb, "RESULTS", str(tmp_path))
    t = rb.fpr_ratio("run").set_index("policy")
    # model: rates 0.001 / 0.003 / 0.008; under 50 pools (1 + 6) / (1,000 + 2,000)
    assert t.loc["model", ["fpr_under30", "fpr_30_49", "fpr_50plus"]].tolist() == pytest.approx([0.001, 0.003, 0.008])
    assert t.loc["model", "ratio_3band"] == pytest.approx(0.001 / 0.008)
    assert t.loc["model", "fpr_under50"] == pytest.approx(7 / 3000)
    assert t.loc["model", "ratio_2group"] == pytest.approx((7 / 3000) / 0.008)
    # rules: 0.002 / 0.002 / 0.002 -> equal treatment
    assert t.loc["rules", ["ratio_3band", "ratio_2group"]].tolist() == pytest.approx([1.0, 1.0])


def test_fpr_ratio_refuses_rates_it_cannot_rebuild(tmp_path, monkeypatch):
    d = tmp_path / "run" / "final_test"
    d.mkdir(parents=True)
    _by_age(d, {"model": (1, 2, 4)})
    f = pd.read_csv(d / "by_age_w26.csv")
    f["false_positive_rate"] = f.normal_flagged / f.accounts          # wrong denominator (mules not removed)
    f.to_csv(d / "by_age_w26.csv", index=False)
    monkeypatch.setattr(rb, "RESULTS", str(tmp_path))
    with pytest.raises(AssertionError):
        rb.fpr_ratio("run")


# --- committed harness outputs ---------------------------------------------------------------------------------

committed = pytest.mark.skipif(not os.path.exists(os.path.join(rb.RESULTS, rb.PLAN_RUNS[-1], "final_test")),
                               reason="robustness final tests not in this checkout")


@committed
@pytest.mark.parametrize("run", [rb.HEADLINE, *rb.PLAN_RUNS])
def test_counts_equal_the_harness(run):
    """mules() repeats the harness's definitions; this keeps the two equal."""
    h = pd.read_csv(os.path.join(rb.RESULTS, run, "final_test", f"summary_w{rb.HORIZON}.csv")).set_index("policy")
    r = rb.lead(run)
    assert (r["mules"], r["model_caught"], r["rules_caught"]) == (h.mules["model"], h.caught["model"],
                                                                 h.caught["rules"])


@committed
def test_headline_is_120_vs_50_of_163():
    r = rb.lead(rb.HEADLINE)
    assert (r["model_caught"], r["rules_caught"], r["mules"]) == (120, 50, 163)


@committed
def test_committed_summary_is_reproduced():
    saved = pd.read_csv(rb.OUT, keep_default_na=False)
    pd.testing.assert_frame_equal(rb.table(rb.PLAN_RUNS), saved, check_exact=False, rtol=1e-12)


amended = [r for r in rb.AMENDMENT_RUNS if rb.has_final_test(r)]


@pytest.mark.skipif(not amended or not os.path.exists(rb.AMENDMENT_OUT), reason="no amendment run scored yet")
def test_committed_amendment_summary_is_reproduced():
    saved = pd.read_csv(rb.AMENDMENT_OUT, keep_default_na=False)
    pd.testing.assert_frame_equal(rb.amendment_table(amended), saved, check_exact=False, rtol=1e-12)


@pytest.mark.parametrize("run", amended)
def test_amendment_counts_equal_the_harness(run):
    h = pd.read_csv(os.path.join(rb.RESULTS, run, "final_test", f"summary_w{rb.HORIZON}.csv")).set_index("policy")
    r = rb.lead(run)
    assert (r["mules"], r["model_caught"], r["rules_caught"]) == (h.mules["model"], h.caught["model"],
                                                                 h.caught["rules"])


@committed
def test_headline_mcnemar():
    r = rb.mcnemar(rb.HEADLINE)
    assert (r["both"], r["model_only"], r["rules_only"], r["neither"]) == (43, 77, 7, 36)
    assert round(r["chi2"], 2) == 56.68 and r["p_exact"] == pytest.approx(5.1e-16, rel=0.02)


@committed
def test_headline_fpr_ratio():
    """Closing plan item 2 check: model 0.00192 / 0.00294 / 0.00614 -> 0.31; rules 0.00416 / 0.00431 / 0.00442 -> 0.94."""
    t = rb.fpr_ratio(rb.HEADLINE).set_index("policy")
    cols = ["fpr_under30", "fpr_30_49", "fpr_50plus"]
    assert t.loc["model", cols].tolist() == pytest.approx([0.00192, 0.00294, 0.00614], abs=5e-6)
    assert t.loc["rules", cols].tolist() == pytest.approx([0.00416, 0.00431, 0.00442], abs=5e-6)
    assert round(t.loc["model", "ratio_3band"], 2) == 0.31 and round(t.loc["rules", "ratio_3band"], 2) == 0.94
