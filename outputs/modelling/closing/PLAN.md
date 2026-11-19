# Closing the modelling plan: implementation plan (drafted 19 Nov 2026)

**Status (19 Nov 2026): items 1–4 done, results under each heading; items 5–7 wait on the team's decisions below.** The modelling plan (decision-record doc, tab
"Modelling plan", 9 Oct 2026) promised some things that are not in the repo yet. This file says, for each one, what
to build, what it reads, how long it takes and how the result will be read. Report deadline: 22 Nov 2026.

Nothing here changes the simulator, the data, the feature store, the frozen feature list, the model of record or
`configs/sim.yaml`. Months 6–7 of v1_full are **not read again** by any item: items 1–3 use only the committed
output of the locked final test (`outputs/modelling/results/v1_full/final_test/`).

| # | Item | Reads | New compute | Effort | Do it? |
|---|---|---|---|---|---|
| 1 | Paired significance test for the headline | Committed final-test output | None | 30 min | Yes |
| 2 | Fairness as a ratio of false-positive rates | Committed final-test output | None | 30 min | Yes |
| 3 | Interpretability and scoring time | PR #39; one timing run on month 5 | ~5 min | 1 h | Yes |
| 4 | Which inputs rest on which simulator assumptions | Robustness results, source check | None | 1–2 h writing | Yes |
| 5 | Evasion test: patient launderers | One new sensitivity dataset | ~45 min | Half a day | Yes, if the team approves the test value |
| 6 | Fairness on Variant II | `data/variant_II` (store already built) | ~30 min | 2–3 h | Optional |
| 7 | Money gone before the first flag (£) | Month 5 hidden transactions | ~5 min | 2–3 h | Optional |
| 8 | Unseen shapes, PCA / autoencoder, CNN, LLM | – | – | – | No: state as limits |
| 9 | Model vs rules at 0.1% and 1% prevalence (professor's comment 1) | Two sensitivity datasets, rebuilt | ~35 min + ~2 h | Half a day | Yes: plan in `outputs/modelling/prevalence/PLAN.md` |

Suggested order: 19 Nov items 1–4; 20 Nov item 5 (then 6 if time); 21 Nov report text. Items 1–4 need no decision.

## 1. Paired significance test (McNemar)

- **Why:** the plan promised a test that the model-vs-rules gap is real. The robustness runs have a bootstrap; the
  headline itself has no test stated.
- **What:** McNemar's test on the mules where exactly one method made the catch (weeks 0–26). The locked report
  already holds the counts: caught by both 43, model only 77, rules only 7, neither 36 (163 mules).
- **Expected arithmetic** (from those committed counts, so not a new look): chi-square with continuity correction
  = (|77 − 7| − 1)² / (77 + 7) = 56.7; exact two-sided p ≈ 5 × 10⁻¹⁶.
- **Build:** `mcnemar(run)` in `src/evaluation/robustness.py`, beside `mules(run)` which already loads these rows;
  returns both, model_only, rules_only, chi-square, exact p. One test in `tests/test_robustness.py` on a small
  made-up table. Print it for `v1_full` and the 7 robustness runs.
- **Report wording:** the test covers mules only. It says the model catches more mules than the rules at the same
  budget; it says nothing about false alarms, which precision covers.
- **Also state** (plan, 9 Oct): with ~160 mules, a gap of 3–5 catches is not significant. That applies to the
  onboarding comparison (65 vs 61 of 78 on month 5).
- **Result (done 19 Nov 2026):** `mcnemar(run)` in `src/evaluation/robustness.py`; `python -m evaluation.robustness`
  prints it (not saved in `summary.csv`). Weeks 0–26, mules of the test cohort (months 6–7), from the committed
  `final_test/launderers.csv` of each run; nothing re-scored. v1_full matches the expected arithmetic above.

  | Run | Both | Model only | Rules only | Neither | Chi-square | Exact p |
  |---|---|---|---|---|---|---|
  | v1_full (headline) | 43 | 77 | 7 | 36 | 56.68 | 5.1e-16 |
  | seed__44 | 35 | 79 | 0 | 31 | 77.01 | 3.3e-24 |
  | in_window_mix__1 | 24 | 75 | 6 | 19 | 57.09 | 2.9e-16 |
  | bursts_per_launderer__1 | 70 | 80 | 5 | 8 | 64.42 | 1.8e-18 |
  | fake_start_days__2 | 29 | 62 | 1 | 71 | 57.14 | 1.4e-17 |
  | fake_start_days__1 | 46 | 72 | 8 | 37 | 49.61 | 5.4e-14 |
  | out_transfer_mean__1 | 118 | 30 | 2 | 13 | 22.78 | 2.5e-07 |
  | fake_age_rule__1 | 42 | 86 | 5 | 30 | 70.33 | 4.0e-20 |

  In every run the model catches many mules the rules miss, and the rules catch few that the model misses. The
  gap is far beyond chance in all 8 runs. It is smallest with £1,500 transfers (30 vs 2), where the rules
  already catch most mules. The test covers mules only: it says the model catches more mules than the rules at
  the same budget, and nothing about false alarms (precision covers those).

## 2. Fairness: ratio of false-positive rates between age groups

- **Why:** the plan names the BAF paper's fairness measure. The harness already writes the rates per age band but
  no ratio, and the report has no fairness number for the headline.
- **What the committed file already shows** (`final_test/by_age_w26.csv`, share of normal accounts flagged):

  | Age band | Model | Rules |
  |---|---|---|
  | Under 30 | 0.19% | 0.42% |
  | 30–49 | 0.29% | 0.43% |
  | 50+ | 0.61% | 0.44% |

  Lowest ÷ highest rate: model 0.31, rules 0.94 (1.0 = equal treatment). The model flags fewer normal customers
  overall but spreads its false alarms much less evenly.
- **Build:** `fpr_ratio(run)` in `src/evaluation/robustness.py` reading `by_age_w26.csv`: lowest ÷ highest rate per
  policy, for the three bands and for under-50 vs 50+ (BAF's own grouping; recomputed from the counts in the
  file). One test on a made-up table.
- **How we read it (decided now):** reported as a cost of the model, with the cause already found in robustness
  run 7 (false alarms follow the fake accounts' ages). No threshold is applied and nothing is tuned to improve it.
- **Result (done 19 Nov 2026; `robustness.fpr_ratio(run)`, `tests/test_robustness.py`).** Weeks 0–26, test cohort,
  read only from the committed `final_test/by_age_w26.csv` files. The rate is the harness's own: normal accounts
  flagged ÷ (accounts − mules) in the band, where a mule is a mule by the end of week 26 (`score.by_age`). The code
  first rebuilds the file's three rates from its counts this way and stops if they differ. Under 50 pools the
  counts of the two younger bands. Ratio = lowest rate ÷ highest rate (1.0 = equal treatment).

  *Headline (v1_full).* Normal accounts: 12,500 under 30, 29,255 aged 30–49, 8,143 aged 50+.

  | Policy | Under 30 | 30–49 | 50+ | Ratio, 3 bands | Under 50 | Ratio, under 50 vs 50+ |
  |---|---|---|---|---|---|---|
  | Model | 0.19% (24) | 0.29% (86) | 0.61% (50) | **0.31** | 0.26% (110) | **0.43** |
  | Rules | 0.42% (52) | 0.43% (126) | 0.44% (36) | 0.94 | 0.43% (178) | 0.96 |

  (In brackets: normal accounts flagged.) **This is a cost of the model.** It raises fewer false alarms overall
  than the rules (160 vs 214), but it puts them unevenly: a normal customer aged 50+ is about 3 times as likely to
  be flagged as one under 30 (0.61% vs 0.19%), and 1.4 times as likely as under the rules (0.61% vs 0.44%). The
  rules treat the age groups almost equally. The cause is known (robustness run 7): the model's false alarms
  follow the fake accounts' ages, and in this data the fakes are older.

  *Robustness runs* (each its own `robust_avg5` model, months 6–7 scored once; model rates per band, then the
  ratios):

  | Run | Model: under 30 / 30–49 / 50+ | Model, 3 bands | Model, 2 groups | Rules, 3 bands | Rules, 2 groups |
  |---|---|---|---|---|---|
  | seed__44 | 0.09% / 0.25% / 0.54% | 0.16 | 0.37 | 0.79 | 0.92 |
  | in_window_mix__1 | 0.30% / 0.28% / 0.51% | 0.55 | 0.55 | 0.94 | 0.97 |
  | bursts_per_launderer__1 | 0.22% / 0.30% / 0.58% | 0.37 | 0.48 | 0.94 | 0.96 |
  | fake_start_days__2 | 0.17% / 0.28% / 0.82% | 0.20 | 0.30 | 0.94 | 0.96 |
  | fake_start_days__1 | 0.22% / 0.29% / 0.64% | 0.35 | 0.43 | 0.94 | 0.96 |
  | out_transfer_mean__1 | 0.22% / 0.36% / 0.90% | 0.24 | 0.36 | 0.94 | 0.96 |
  | fake_age_rule__1 | 0.35% / 0.30% / 0.23% | 0.67 | 0.75 | 0.95 | 0.97 |

  The model is less even than the rules in every run (3-band ratio 0.16–0.67 vs the rules' 0.79–0.95). In six runs
  the 50+ band carries the highest rate. With young fakes (`fake_age_rule__1`) the gap shrinks and turns round: the
  under-30s now have the highest rate. That supports the cause above: the model learns the fakes' ages, so whichever
  age group the fakes come from pays for it in false alarms. With fewer fakes (`in_window_mix__1`, 53%) the ratio is
  also better (0.55). The rules' rates barely move, because the rules do not see age.

## 3. Interpretability and scoring time

- **Interpretability:** PR #39 (`frozen-importance`, `models.frozen_importance`, importance of the 38 inputs) is
  open and unmerged. Bring it up to date with `main`, check its numbers are for `frozen_tuned_avg5` (it was written
  for the earlier `frozen_tuned`; if so, re-run it on the model of record: reads the model files only), merge.
- **Scoring time:** time `python -m models predict --out data/v1_full --months 5 --weeks 0-26` three times; report
  the median seconds, account-weeks per second and the machine (the harness already records `machine`). Feature
  build time is already known (~4 min for 19.0M account-weeks).
- **Report wording:** two of the three criteria the plan cites from lecture 1 (the third is fairness, item 2).

**Result (19 Nov 2026; model files and month 5 only, no labels read, months 6-7 not read):**

- **Which model each importance table is for.**
  - `outputs/modelling/models/v1_full/frozen_tuned_avg5/importance.csv` is for the **model of record**. It was
    written by `models.train.train` when the model was trained (commit 8e45df0): the mean split gain of the 5 LightGBM
    seeds and each input's share of the total. It rebuilds from the 5 committed `lgbm_seed1-5.txt` files alone:
    loading each with `lightgbm.Booster` and averaging `feature_importance("gain")` gives the committed table (largest
    relative difference 2e-16, same order). No re-run is needed.
  - PR #39's `frozen_importance/importance.csv` is for **neither** `frozen_tuned` nor `frozen_tuned_avg5`. It is
    the feature lab's baseline: the same 38 inputs with the lab's untuned LightGBM settings, seed 42, refitted on
    the 3 temporal folds, averaged over the folds. The brief's assumption that it was written for `frozen_tuned` was
    wrong. It stays a cross-check: it agrees closely with the model of record (Spearman 0.96 over the 38 inputs;
    `app_score` 51% in both; top 5 80% in both; top 10 89% vs 90%).
  - Branch `frozen-importance-update` (local, not pushed) is PR #39 with `main` merged in. It is not merged into
    `main`, because that is a team decision.
- **Top 10 inputs of the model of record** (share of split gain; the rank in PR #39's table is in brackets):

  | rank | input | share | PR #39 |
  |---|---|---|---|
  | 1 | `app_score` | 0.507 | 0.510 (1) |
  | 2 | `out_1h_share_4wk` | 0.127 | 0.115 (2) |
  | 3 | `n_payers_cum` | 0.074 | 0.067 (4) |
  | 4 | `internal_out_share_cum` | 0.046 | 0.041 (5) |
  | 5 | `money_in_4wk` | 0.046 | 0.067 (3) |
  | 6 | `weeks_since_open` | 0.027 | 0.019 (8) |
  | 7 | `money_out_cum` | 0.023 | 0.019 (7) |
  | 8 | `money_in_cum` | 0.020 | 0.022 (6) |
  | 9 | `n_rows_cum` | 0.016 | 0.017 (9) |
  | 10 | `money_out_4wk` | 0.016 | 0.012 (12) |

  Group shares for the model of record: application score 50.7%, the 28 store features 24.5%, the 8 four-week windows
  22.1%, `weeks_since_open` 2.7%. The top 5 carry 80%, the top 10 90%. PR #39's top 10 has `n_rows_4wk` in place of
  `money_out_4wk`. Gain share shows what the trees lean on, not what the model could do without: inputs that measure
  the same thing share the credit.
- **Scoring time.** I ran `python -m models predict --out data/v1_full --months 5 --weeks 0-26 --to <scratch>`
  (`frozen_tuned_avg5`) three times: 6.79 / 5.19 / 5.60 s wall time, so the **median is 5.60 s**. Each run scored
  786,240 account-weeks (29,120 accounts x 27 weeks), which is **about 140,000 account-weeks per second**. Peak memory
  was 1.6-2.0 GB. The three outputs are identical, and they equal the existing
  `data/v1_full/scores/frozen_tuned_avg5_m5.parquet` restricted to weeks 0-26 (largest difference 0). The time
  covers loading the 5 models and the application model, reading the feature store and cleaned table, adding the
  four-week windows and predicting. It does not include building the feature store (~4 min for 19.0M
  account-weeks). Machine: Apple M5 Pro (arm64), 15 cores (5 performance + 10 efficiency), 24 GB RAM, macOS 26.5.1.
  Other jobs were running at the same time (load average 11-13), so these times are on the slow side.
- **For the report:**
  - *Interpretability:* "The model is a LightGBM ensemble whose split-gain importance can be read directly from the
    saved model files. Half of the credit goes to the application score, and most of the rest goes to a handful of
    readable activity measures: how fast money leaves after it arrives, how many different people pay in, and how
    much money moves through the account in four weeks."
  - *Scoring time:* "Scoring a whole month's intake for its first 27 weeks (29,120 accounts, 786,240 account-weeks)
    takes about 6 seconds on a laptop (Apple M5 Pro), about 140,000 account-weeks a second. Weekly scoring is
    therefore cheap next to building the weekly features."

## 4. Which inputs rest on which simulator assumptions

**Done 19 Nov 2026 (writing only; nothing run).** One table for the report's limitations section. It says, for
each group of the model's 38 inputs, which simulator setting makes that input useful, how good the evidence for the
setting is, and whether a robustness run changed the setting. Sources:

- Importance: `outputs/modelling/models/v1_full/frozen_tuned_avg5/importance.csv` (gain share per input, written by
  `models train` for the model of record). **The order of the rows rests on this file.** Item 3 confirmed it
  belongs to `frozen_tuned_avg5`: it rebuilds exactly from the 5 committed seed files.
- Results: `outputs/modelling/robustness/summary.csv` and `report.md` (lead = (model caught − rules caught) / mules,
  weeks 0–26, months 6–7 of each dataset; chance band 0.31–0.55; v1_full lead 0.43, 0.35–0.52).
- Evidence: the `source` and `strength` of each setting in `configs/sim.yaml` as corrected by the source check of
  18 Nov 2026 (PR #59, open; no values changed). Strength words are the file's own: sourced, derived, samld
  (measured on SAML-D, itself a synthetic dataset), modelling (our shape choice), assumption (no source).

**Table A. Each input once; the shares add to 1.00.** "Share" = summed gain share of the row's inputs in the model of
record. Rows run from the inputs the model uses most to the least.

| Share | Model inputs (frozen 38) | Simulator setting they rest on | Evidence for the setting | Tested by | Result |
|--:|---|---|---|---|---|
| 0.507 | `app_score` (logistic score of the 29 application columns) | `profiles.in_window_mix` (73% of mules are fake accounts, taken from BAF `fraud_bool = 1` rows) | Derived. Lloyds via Which? 2018 states only the witting and unwitting thirds; the fake third is our inference, and so is the 45 in RUSI's "33/45" (PR #59) | `in_window_mix__1` (53% fakes) | Holds: lead 0.56 (0.46–0.66). Real-customer mules caught 18 of 21 vs rules 6 (a small number) |
| (part of the 0.507 above) | `app_score` through `customer_age` | `profiles.fake_age_rule` (fakes keep their BAF ages) and `profiles.real_mule_age_weights` (real-customer mules weighted to Cifas ages) | Sourced. Fake ages: Cifas (identity-fraud victims skew old) and BAF's own fraud rows. Real-mule ages: Cifas Fraudscape 2026 six-month update (40% / 24% / 17%; citation corrected in PR #59; the annual report gives 39% / 23% / 18%) | `fake_age_rule__1` (young fake ages). Real-mule ages: not tested | Holds: lead 0.50 (0.42–0.58). False alarms follow the fakes' ages (v1_full: 6.1 per 1,000 normal 50+ accounts vs rules 4.4) |
| 0.146 | Forwarding speed and pass-through: `out_1h_share_4wk`, `out_24h_share_4wk`, `out_1h_share_wk`, `out_24h_share_wk`, `med_in_out_minutes_wk`, `passthrough_4wk`, `passthrough_wk` | `laundering.forward_delay_shares` (28% out within 15 min, 25% more within 1 h, 15% after 24 h); band edges `forward_delay_bands_minutes`; `holder_keeps` (0–10%) | Shares: sourced, RUSI 2025 (the 1–24 h share is derived); checked 18 Nov, note unchanged. Band edges: modelling (1-minute minimum and 7-day maximum ours). `holder_keeps`: assumption (no official percentage found, PR #59) | Not yet (item 5, pending approval) | – |
| 0.129 | Money amounts: `money_in_4wk`, `money_out_cum`, `money_in_cum`, `money_out_4wk`, `max_in_wk`, `self_vs_past_money_in`, `money_in_wk`, `max_out_wk`, `money_out_wk`, `peer_ratio_money_in` | `laundering.out_transfer_mean` (£532) and each shape's `amount_rel` | £532: sourced, RUSI 2025 (Lloyds Faster Payments out of mule accounts); checked 18 Nov, note unchanged. `amount_rel`: samld (SAML-D medians) | `out_transfer_mean__1` (£1,500) | **Shrinks**: lead 0.17 (0.10–0.24). Rules catch 120 of 163 (vs 50); model 148 |
| 0.085 | Counterparties: `n_payers_cum`, `n_payees_cum`, `n_payers_4wk`, `new_payer_share_wk`, `n_payees_wk`, `n_payers_wk`, `self_vs_past_payers` | Laundering shapes' `senders` / `recipients` (`laundering.shapes`); for normal accounts `normal.group_collection` (8–15 payers in a week) and `group_collection_yearly_rate` (1% a year) | Shapes: samld (measured on SAML-D). Group collection: partly sourced (Collection Pot's 11.4 contributors; online pots, so separate transfers are ours). Yearly rate: assumption | Not tested for the model (6 rules-only sensitivity runs on the group collection) | – |
| 0.046 | `internal_out_share_cum` (share of money out sent to accounts in the same bank) | `networks.big_network_share` (25% in one network), `networks.internal_pieces_share` (0.5), layered shapes; for normal accounts `normal.internal_share_of_transfers` (10%) | Network share: sourced, Vocalink 2017 (PDF could not be re-opened on 18 Nov). Pieces share: modelling. Normal internal share: assumption | Not tested for the model (2 rules-only sensitivity runs on the normal internal share) | – |
| 0.039 | Payment counts: `n_rows_cum`, `n_rows_4wk`, `n_in_4wk`, `self_vs_past_rows`, `n_in_wk`, `n_rows_wk`, `n_out_wk`, `card_items_wk` | `timing.incoming_per_burst` (3–4 payments in), `timing.burst_days` (14), `laundering.out_pieces_mean` (2 pieces out per payment in) | Payments in and burst length: sourced, Synectics 2024. Pieces out: modelling | Not tested for the model (`bursts_per_launderer__1` changes the number of bursts, not the payments in one) | – |
| 0.027 | `weeks_since_open` | `timing.fake_start_days` (fakes start 60–120 days after opening); `timing.existing_start_bands` for real customers | Fake start: assumption, no source. Real-customer start: derived from RUSI 2025 (~60% of mule accounts older than one year) | `fake_start_days__1` (15–45 days), `fake_start_days__2` (150–210 days) | Holds, borderline: leads 0.39 (0.31–0.48) and 0.37 (0.30–0.45); both intervals reach just below the band floor 0.31. Read as "no clear change" |
| 0.020 | Cash and abroad mix: `cash_in_share_cum`, `abroad_out_share_cum`, `high_risk_out_share_cum` | Cash shapes (Deposit-Send, Smurfing); `laundering.abroad_ratio_vs_normal` (3.15); for normal accounts `normal.cash_depositor_share` (6%) and `normal.abroad_sender_share` (7%) | Abroad ratio: samld, our measurement on the SAML-D file, not in the paper (PR #59). Cash depositors: FCA 6% measures paying with cash, not depositing (PR #59). Abroad senders: the FCA chart gives 9%, not 7% (PR #59; value kept until the team decides) | Not tested for the model (rules-only sensitivity runs on the abroad ratio and normal cash use) | – |

**Table B. One setting that touches all activity inputs at once** (overlaps Table A).

| Share | Model inputs | Simulator setting | Evidence | Tested by | Result |
|--:|---|---|---|---|---|
| 0.466 | All 36 activity inputs (everything except `app_score` and `weeks_since_open`) | `timing.bursts_per_launderer` (one ~2-week burst per launderer) | Assumption, no source | `bursts_per_launderer__1` (a new burst 30 days after each one, until closed) | Holds: lead 0.46 (0.37–0.54). Both sides catch more: model 150, rules 75 of 163 |

**How to read it.** Half of the model's gain comes from the application score, and its main assumption (73% of mules
are fake accounts) is our own inference; with 53% fakes the lead still holds. The next most-used input, forwarding
speed (0.146), rests on a sourced figure but has not been tested: item 5 would test it. The one tested setting that
shrinks the lead is the transfer size (money inputs, 0.129). Counterparties and internal links (0.13 together) rest
on SAML-D shapes and our own choices and were tested for the rules only.

**What changed versus the draft (19 Nov 2026).**
- Rows now cover all 38 inputs by their real names, each input in one row, with its summed gain share; ordered by
  share. Two new rows: `internal_out_share_cum` (the 4th most used input, 0.046, had no row) and cash / abroad mix
  (0.020; three of its settings had their notes corrected in PR #59). The draft's "Payers" row is now
  "Counterparties" (payees too); a "Payment counts" row is split off from the draft's "All activity inputs".
- Pass-through moved from the money row to the forwarding row: it measures how much money in leaves in the same
  week, which forwarding speed sets.
- "All activity inputs / `bursts_per_launderer`" moved to Table B: it touches every activity input, so it cannot sit
  in the ordered table without counting inputs twice.
- Weeks since opening: the result was "Borderline"; the plan's verdict in `summary.csv` is "holds", borderline only
  because the intervals reach below 0.31 (as `report.md` says). Now "Holds, borderline". Added the real-customer
  start setting.
- Age row: evidence was "Cifas, confirmed"; PR #59 corrected the citation to the Cifas six-month update (annual
  report 39 / 23 / 18%); fake ages also rest on BAF's own fraud rows. Real-mule ages were never tested: now said.
- Application score: evidence now names the strength (derived) and that the 45 in "33/45" is also ours (PR #59).
- Forwarding: "Not yet: item 5" is now "Not yet (item 5, pending approval)"; added the band edges and `holder_keeps`.
- Counterparties: evidence was "SAML-D; assumption"; the group collection is partly sourced (Collection Pot), its
  yearly rate is the assumption, and rules-only sensitivity runs exist.
- Results: 95% intervals added from `summary.csv`. Run 5 (`fake_start_days__1`): `report.md` gives 0.31–0.49, but
  `summary.csv` gives 0.307–0.485, so 0.31–0.48 here.

## 5. Evasion test: patient launderers

- **Why:** the plan's evasion test was never run, and it matters more now. The model and the rule scorecard both
  lean on forwarding speed, and forwarding speed is the one heavily used input with no robustness run (item 4).
- **What:** one new sensitivity dataset where launderers forward slowly, everything else as v1_full (244,000
  accounts, seed 42, rules frozen at 1.516). One change only, as in every sensitivity run. The plan's other ideas
  (amounts under the R4 limit, extra hops) are not run: `out_transfer_mean__1` already covers amounts.
- **Test value (an assumption; needs a team yes before the run):**

  | Share of money forwarded | Main run (RUSI) | Patient launderers (proposed) |
  |---|---|---|
  | Within 15 minutes | 28% | 5% |
  | 15–60 minutes | 25% | 10% |
  | 1–24 hours | 32% | 35% |
  | After 24 hours (up to 7 days) | 15% | 50% |

  No source: no published figure describes launderers who deliberately slow down. Passed with `--set` for this run
  only; `configs/sim.yaml` is not edited.
- **Steps** (the robustness plan's recipe, unchanged):
  1. Write this run into `outputs/modelling/robustness/PLAN.md` as an amendment and commit it before the run.
  2. Build `data/sensitivity/forward_delay_shares__1` with `sim.run all` and the three `--set` values; run
     `sim.checks`.
  3. Build its store and cleaned tables; train `robust_avg5` on its months 0–4 (nothing tuned).
  4. Score its months 6–7 once (its own lock). Add the run to `evaluation.robustness` and `summary.csv`.
- **How we read it (the robustness plan's rule, unchanged):** holds / shrinks / fails by the lead and its interval
  against the chance band 0.31–0.55. A "shrinks" or "fails" is reported as a dependence on forwarding speed.
- **Expectation, stated in advance:** the rules do not use forwarding speed inside a week, so they should lose
  little; the model should lose more. A smaller lead is the likely outcome.

## 6. Fairness on Variant II (optional)

- **Why:** Variant II was generated for fairness (launderer rate higher for 50+ in every month) and has never been
  modelled. Item 2 gives a fairness number on the main data; this checks it where the age bias is stronger.
- **State:** `data/variant_II` exists with its weekly store and cleaned tables. Variant IV's store is not built
  and is left out.
- **Steps:** train `robust_avg5` on its months 0–4, score its months 6–7 once (own lock), report the lead and the
  item-2 ratio. Added to the robustness plan in the same amendment as item 5.
- **How we read it:** reported beside item 2, never used to change the model.

## 7. Money gone before the first flag, month 5 (optional)

- **Why:** the plan's cost measure: what a miss or a late catch costs, in pounds.
- **What:** for each month-5 mule, the laundering money paid out up to its first flag (all of it by week 26 if
  never flagged), summed per policy: rules, rule scorecard, model. Month 5 only: months 6–7 would be another counted
  look at the test months.
- **Build:** `src/evaluation/cost.py`, reading the committed `launderers.csv` of each month-5 run and the hidden
  transaction labels through `amldata.evaluation()` (scoring code, so allowed).
- **Left out:** investigator cost in pounds. There is no sourced cost per alert, and all policies flag the same
  number of accounts by design, so it would add an invented number and no information.

**Result (19 Nov 2026, branch `closing-item7`).** `python -m evaluation.cost --out data/v1_full` ->
`outputs/modelling/results/v1_full/month5_cost/` (`summary.csv`, `by_type.csv`, `per_mule.csv`, `settings.json` with
the sha256 of the 4 committed inputs, the data's `run_manifest.json` and the git commit; tests `tests/test_cost.py`).
Month-5 cohort, weeks 0-26, the 78 mules of the harness. All laundering money these mules paid out by the end of
week 26 (the ceiling): **GBP 310,207**.

| Policy | Mules caught (of 78) | Money paid out before the first flag | Share of the ceiling gone | Share prevented |
|---|---|---|---|---|
| Rules | 16 | GBP 284,193 | 91.6% | 8.4% |
| Rule scorecard | 34 | GBP 263,191 | 84.8% | 15.2% |
| Model of record (`frozen_tuned_avg5`) | 65 | GBP 208,129 | 67.1% | 32.9% |

Money stopped compared with the rules (paired bootstrap over the 78 mules, 10,000 draws, 95% interval): model
GBP 76,063 (47,723 to 106,933); scorecard GBP 21,002 (-4,503 to 47,674, so not clearly more than the rules).

- **Most money leaves before any flag.** Even for the mules a policy catches, most of their money is already gone at
  the flag: 64% for the model's 65 (22 of them had paid out everything), 71% for the rules' 16, 73% for the scorecard's
  34. No policy flags any mule before its first laundering payment out. Most of the model's gain comes from catching
  mules at all (its 13 missed mules lose GBP 23,994; the rules' 62 missed mules lose GBP 219,771), not from flagging
  them early in the burst.
- **By type:** fakes (70 mules, GBP 288,214) prevented rules 8.5%, scorecard 15.8%, model 34.1%; witting (5, GBP
  16,012) 9.6% / 9.7% / 23.7%; unwitting (3, GBP 5,981) 0% for every policy (all their money leaves before any
  flag). Real-customer mules are 8 of 78, so these splits are small.

Definitions, in plain words:
- *Paid out:* a transaction out of the mule's account (transfer, cash withdrawal or cross-border payment) that the
  hidden label marks as laundering. These are the same rows as each launderer's `laundered_out` total.
- *First flag:* taken from each run's committed `launderers.csv` (rules: `rules_first_alert_week`; model and scorecard:
  `model_flag_week_w26`), dated as the harness dates it: a rules flag on its first alert day (read from the hidden
  alerts, checked against the file's week), a weekly model flag at the end of its week, the day its score exists. Both
  see every transaction up to and including that day, so payments **on the flag day count as gone**; the flag is
  assumed to stop every later payment (the bank's 3-30 day review is ignored for every policy alike, so all three
  shares prevented are best cases).
- *Never flagged by the end of week 26:* everything the mule paid out up to the end of week 26 counts as gone.
- *Closed accounts:* the bank closes an account only after a rule alert, and the simulator removes everything after
  closure. As in the harness, a model can no longer flag a closed account; for such a mule the money paid out before
  closure counts as gone. This happens for 2 mules under the model and 1 under the scorecard; the money they would
  have paid out had the rules not closed them does not exist in the data, which slightly flatters the model and
  scorecard.

Limits: month 5 only (78 mules), so this is a dry-run figure, not a test-month result; months 6-7 would be another
counted look. Investigator cost is left out (no sourced cost per alert; all policies use the same weekly budget).
Amounts are the simulator's (anchored to RUSI's GBP 532), so the pounds compare policies, not real losses.

## 8. Not done: stated as limits

| Plan item | Why not | Where it is said |
|---|---|---|
| Unseen laundering shapes | About 12 test mules per shape: too few to conclude anything | Limitations |
| PCA / autoencoder | Dropped by decision D4 (31 Oct 2026); the outlier appendix covers label-free detection | Outlier appendix |
| MLP / 1D CNN, LLM case summary | Marked "skip unless time is left" in the plan itself | Further work |

The "Modelling plan" doc tab still describes the autoencoder as a challenger and gives the old baseline's McNemar
example. Add one line at its top pointing here.

## Decisions for the team

1. Item 5: is the patient-launderer test value acceptable as an assumption? (Blocks item 5.)
2. Items 6 and 7: do them, or state them as not done?
3. ~~Item 3: re-run importance on `frozen_tuned_avg5` if PR #39 used `frozen_tuned`?~~ Not needed (19 Nov): the
   model of record's own importance is committed and rebuilds from its files; PR #39 is the lab baseline, a cross-check.
