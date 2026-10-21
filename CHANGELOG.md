# Changelog

Changes to the simulator and the data it generates, newest first. Settings changes are also noted in the
`source` of each value in `configs/sim.yaml`; decisions are recorded in the "Simulated Dataset: Logic,
Assumptions and Use" doc.



## 22 Oct 2026 — Feature store: weeks 0–77 (week 78 dropped)

No change to the simulated data. Every account's data ends 547 days after opening, so week 78 (days 546–552) held only
2 of its 7 days: 2.2 rows on average against 5.5 at week 77, an artificial drop in activity at the end of the 0–78
appendix horizon. The store now holds weeks 0–77 (`weekly.LAST_WEEK`); `build()` refuses later weeks and
`manifest.check()` refuses a store that still holds week 78. Rebuilt on v1_full (19,032,000 account-weeks) and v1
(3,900,000): exactly the old store and peer medians without week 78, row for row. Notebook 03's gate re-run on both
(passes); its end-of-window check and `test_whole_store_invariants` now compare week 77's running totals with the
transactions up to that week's cut-off. Appendix horizon in CLAUDE.md: weeks 0–77 (team decision 22 Oct 2026).

## 22 Oct 2026 — Feature store: code check in the manifest, simpler code (no result changes)

No data change; both stores rebuilt and byte-identical to before (`weekly.parquet` and `peer_medians.parquet`, v1_full and v1).
- **Code check:** the manifest now stores `code_sha256`, a fingerprint of the feature SQL, and `manifest.check()`
  refuses a store built by different feature code. Before, `check()` compared data, feature list, weeks and peer
  medians but not code, although its docstring said so, so an edited `weekly.py` silently reused the old store.
  Stores built before this change are refused once; rebuild with `python -m features weekly --out <folder> --force`.
- `load()` takes `months=` and `columns=` (rows now sorted by account and week); no private `amldata` import.
- The zero-fill of empty weeks is generated from one list (`ZERO_FILL`) instead of 20 hand-written lines.
- Docstring: the speed numbers match the report (1 h AUC 0.772 vs 0.951 for cash patterns); the two meanings of
  "new payer" are written down.
- Tests: a store built by other feature code is refused; `HIGH_RISK` equals `configs/sim.yaml`; `load()` filters.

## 21 Oct 2026 — EDA: simpler code (no result changes)

No data change. `notebooks/01_eda_train.ipynb` cleanups, re-run on v1_full and v1 (50k); every number in the reports
is unchanged apart from known float-sum noise (~1e-6) and the two items below.
- No global warning filters (they hid nothing: a run without them prints no warnings); the report path is two plain lines.
- §2: the Welch t-test p-value (computed, never shown; Mann-Whitney already tests the numeric columns) is dropped;
  information gain, which the plan lists, is now shown for the categorical columns.
- §3: the closure table is one `GROUP BY` instead of correlated subqueries (same table).
- §6: no redundant `lab_` query; `x` / `s` renamed `share_accounts` / `share_ends`; `two_xy()` takes its inputs instead
  of reading globals. Names no longer reused across cells (`lab_`, `s`).
- §6 shuffle test: the account list is sorted before shuffling, so it gives the same numbers every run (DuckDB returns
  rows in no fixed order). v1_full: 163 launderer–launderer links vs 9.6 on average (the 21 Oct run said 9.3), mixed
  links 5,663 vs 6,843; p = 0.001 as before.

## 21 Oct 2026 — EDA: claims tested directly (pre-start weeks, graph timing, shuffle test, missing flags)

No data change. `notebooks/01_eda_train.ipynb`, re-run on v1_full and v1 (50k). v1_full numbers:
- **Before laundering starts (§3).** The claim "activity carries nothing before a burst" is now tested: weeks 0–7
  (no fake starts before week 8), each launderer's weeks before its start vs normal accounts, one mean per account so
  the interval is honest. Counts, payers and speed match. Fakes' money features are higher (money in AUC 0.58) only
  through BAF income: 31% of fakes are in the top income band vs 20% of normal accounts, normal money scales with income
  (`src/sim/normal.py`), and inside an income band the AUC is 0.51. The weekly table now uses open weeks only and says
  which columns are medians and which are means.
- **Graph (§6).** Label-shuffle test (labels moved between accounts, each keeps its links, 1,000 shuffles): 163
  launderer–launderer links vs 9.3 on average, p = 0.001; mixed links 5,663 vs 6,845, p = 0.001. Only 1 of the 163
  links exists before both ends start laundering (4 before at least one): graph features can find network partners
  once a burst starts, not give a head start.
- **Missing flags (§2).** BAF's missing codes are scored as 0/1 flags: fakes `prev_address` 0.60, `intended_balcon`
  0.58, `bank_months` 0.57; real mules `intended_balcon_amount_missing` 0.45.
- **Text:** §1 `velocity_6h` note computed (0 negative rows in months 0–4), skew table without 0/1 columns, Phase 2
  decisions quoted for log and correlated pairs; §5 says what fixed weeks hide and points to Phase 3's first-week view;
  §8 hard-coded "~1.6% abroad" removed.
- **Bootstrap intervals** now sort the placement values first, so they no longer depend on the order DuckDB returns
  rows (run-to-run differences fall from ~0.01 to the known ~2e-6 float-sum noise). Point AUCs unchanged.

## 19 Oct 2026 — EDA tidy: closure filter, keep/drop rule with intervals, age allowed

No data change. `notebooks/01_eda_train.ipynb`, re-run on v1_full and v1 (50k); `notebooks/03_feature_store.ipynb`
re-run on both (gate (A) still within 1e-5).
- **Age decision (19 Oct 2026):** `customer_age` is allowed as a model input; Variant II tests fairness.
- **Closure filter:** the feature screen (§5) kept account-weeks with any rows (`n_rows > 0`); it now uses
  `labels()["open_by_day"] == 1`, as CLAUDE.md requires (normal accounts have 82 zero-row weeks in months 0–4). Notebook 03
  uses the same filter so its gate still reproduces the screen. v1_full started launderers at week 12: 167 -> 157 (10
  closed during that week).
- **§3 text:** the stale "decision needed: open at week w" note is replaced (`open_by_day` exists since 10 Oct); the
  closure numbers are printed from the data.
- **§5 / §8:** one AUC helper with a 95% interval (resampling the launderers) for §2 and §5. A candidate is kept when,
  at some screened week, |AUC − 0.5| ≥ 0.05 for `mule_by_day` or `started_by_day` and its interval excludes 0.5; the old
  rule had no interval. v1_full: drop cash / abroad / high-risk shares (as the team decided on 15 Oct); `night_share` and
  `internal_share` pass in 1 of 8 looks (weak). No change to the feature store.

## 18 Oct 2026 — EDA fixes: missing values rank lowest in the AUC; real mules separate on age

No data change. Two corrections to `notebooks/01_eda_train.ipynb`, re-run on v1_full and v1 (50k):
- **AUC helper.** `auc()` used pandas `rank(na_option="bottom")`, which gives NaN the *highest* rank, while its docstring
  said lowest. Share features are NaN in weeks with no money in (about half of normal weeks), so those weeks ranked above
  every launderer and the shares looked like noise. Now `na_option="top"` (NaN lowest, as the Phase 3 bootstrap already
  did). v1_full, best |AUC − 0.5| against started launderers: `out_1h_share` 0.02 -> 0.28, `out_24h_share` 0.05 -> 0.25,
  `new_payer_share` 0.11 -> 0.21, `passthrough_wk` 0.11 -> 0.20, self-vs-past 0.14 -> 0.17. The Phase 1 proposal to
  redefine the speed shares came from this bug; the store already keeps the EDA's definition (decision 15 Oct 2026).
  The same helper in `notebooks/03_feature_store.ipynb` (gate comparison and screen; its first-week bootstrap was
  correct and is unchanged) and `src/sim/eda/eda_sim_v1.py` is fixed too. Notebook 03 re-run on v1_full (store rebuilt,
  deterministic) and v1: gate (A) still within 1e-5. `eda_sim_v1` re-run on v1_full: no AUC changed (no NaN in its
  features), so its report was left as committed.
- **§2 application columns by type.** The table was sorted by the all-launderer AUC and cut at 16 rows, which hid
  `customer_age`: AUC 0.65 for fake accounts but 0.25 for real-customer mules (about 65% under 30 vs 27% of normal
  accounts, from `profiles.real_mule_age_weights`), 0.53 for all. §2 now sorts by the largest of the three separations,
  shows every column, and gives each AUC a 95% interval (resampling the launderers). Real mules: 8 columns' intervals
  exclude 0.5 on v1_full (age, housing_status, keep_alive_session, income, phone_home_valid, has_other_cards,
  bank_months_count, phone_mobile_valid); 1 on v1 (age, 20 real mules). The "real-customer mules do not separate at
  opening" finding is corrected in CLAUDE.md / AGENTS.md and the decision-record doc. Whether age may be a model input
  is open (fairness).

## 16 Oct 2026 — EDA §6: the homophily test is now the r < 2xy test

No data change. `notebooks/01_eda_train.ipynb` §6 called a lift (how often a launderer's payees are launderers vs the
base rate) "the L8 homophily test"; it was not that test. §6 now runs the homophily test itself on the payment network
inside the bank (one undirected link per pair of accounts that paid each other, both ends opened in months 0–4): with x the
launderer share of accounts, homophily means the share of launderer–normal links r is clearly below 2xy (one-sided z-test).
A second row allows for how many links each account has (x = launderer share of link ends). v1_full: r = 0.450% vs 2xy =
0.545% (r / 2xy 0.83, z −14.3); allowing for links per account 0.95, z −4.0; 163 launderer–launderer links vs 9 expected
by chance (17x). The lift (20x) is kept as the measure of strength. r / 2xy looks modest only because launderers are 0.3%
of accounts. v1 (50k): 0.86, z −5.2; 0.95, z −1.9. Re-running the notebook also moved a few weekly money AUCs and
correlations in the 7th–8th digit (DuckDB sums in parallel, in no fixed order); nothing else changed.

## 15 Oct 2026 — Phase 3 speed shares: back to the EDA's definition (team decision 15 Oct 2026)

No change to the simulated data. `out_1h_share_wk` / `out_24h_share_wk` replace `fwd_1h_share_wk` / `fwd_24h_share_wk`:
money paid out (any kind) within 1 h / 24 h of the latest payment in (any kind), over the week's money in, exactly as
in the Phase 1 EDA (Kee Chee Pheng, `notebooks/01_eda_train.ipynb`); it can exceed 1. The transfers-only, capped
redefinition (Phase 3 commit 9fb3caf) is dropped. Evidence, v1_full months 0–4, each launderer's first laundering week
(361) vs normal account-weeks:
- 1 h: EDA definition AUC 0.954 vs 0.919 for the redefinition; paired account-level bootstrap difference +0.035
  (95% interval +0.021 to +0.050). 24 h: no difference (+0.002 the other way, interval crosses 0).
- Why (`python -m evaluation.speed_by_pattern`, hidden pattern labels, training months only): for launderers who use
  transfers only (297) both definitions are equal (1 h AUC 0.955 vs 0.951). For the 64 whose pattern moves cash, the
  redefinition is blind: 0.951 vs 0.772 (Cash_Withdrawal 0.963 vs 0.727, reads 0 for all 9; Deposit-Send 0.944 vs
  0.809; Smurfing 0.994 vs 0.487). It ignores cash deposits as money in and cash withdrawals as money out. A
  launderer's pattern is the label on most of its laundering rows (rows forwarded from the previous chain member
  carry that member's label).
- The Phase 1 report's "swamped by everyday outflows" was right for the 24 h share (normal weeks average 0.59) but not
  for the 1 h share (only 2.5% of normal weeks have any money out within 1 h of money in). The EDA screen showed no
  signal because it scored weekly features at fixed weeks against `started_by_day`, not because of the definition.
Both speed shares now join the value-by-value gate (16 shared features). Tests updated: the synthetic test adds a cash
deposit followed by a cash withdrawal; the pandas re-implementation and whole-store checks follow the EDA definition
(speed shares may exceed 1; 0 ≤ 1 h ≤ 24 h still holds).

## 15 Oct 2026 — Modelling Phase 3: weekly feature store (28 features), gate passed on v1_full and v1

No change to the simulated data (`data/v1` was rebuilt from BAF Base: identical to the team's copy, 0 rows differ in
`accounts_truth`, `aml_alerts`, `aml_outcomes`). `python -m features weekly` builds the feature list fixed at the Phase 1
gate: volume, counterparties (distinct and first-time payers, distinct payees, cumulative distinct counts),
pass-through, speed, self vs past (money in, payers, rows), peer ratio of money in (medians frozen from months 0–4 in
`features/peer_medians.parquet`, hashed in the manifest), cumulative internal / cash / abroad / high-risk shares. Speed as
the gate asked: transfers out (ACH, Cross-border) within 1 h / 24 h of the latest transfer in, each inflow passed on at
most once. Money is summed as exact pence (DECIMAL), so totals do not depend on the order DuckDB adds them in.
One opening month at a time: v1_full weeks 0–78 = 19,276,000 account-weeks in ~4 min, 4.2 GB peak.

Gate (`python -m features store-check` -> `notebooks/03_feature_store.ipynb`, report `outputs/modelling/features/`):
- Value by value, the 14 features the EDA screened equal the EDA's own query (copied verbatim, rerun) on all 4,450,113
  account-weeks of months 0–4 (v1_full; relative difference ≤ 8.2e-14, identical NULL pattern); v1 likewise (912,627).
  The EDA's float sums are not bit-reproducible run to run (its AUCs move by up to 7e-7 on v1_full, 4e-6 on v1); the
  store's exact sums remove that noise.
- First laundering week vs normal account-weeks, 95% account-level (Poisson) bootstrap, 1,000 replicates, v1_full:
  25 of 28 features exclude AUC 0.5; strongest `fwd_1h_share_wk` 0.919 (0.902–0.936), `n_in_wk` 0.915, `fwd_24h_share_wk`
  0.909, `n_rows_wk` 0.906; no signal for `self_vs_past_payers`, `n_payees_cum`, `abroad_out_share_cum`.
- **Correction:** the redefined 1 h speed share is *not* better than the EDA's (any payment out after the latest payment
  in): paired bootstrap gain −0.035 (−0.050 to −0.021); 24 h: +0.002 (−0.012 to +0.016). Resolved in the entry above:
  the EDA's definition is restored.

Tests: `tests/test_feature_store.py` (real data, 3 seeded samples of 300 random accounts + 60 launderers, weeks 0–78):
all 28 features equal an independent pandas re-implementation; cutting test-month accounts' transactions at a random
week leaves every earlier value bit-identical; rebuilds are byte-identical; whole-store invariants (complete keys,
shares in [0, 1], 1 h ≤ 24 h, running totals never fall, week-78 totals equal the transactions file, peer medians equal
a recomputation). `tests/test_features.py` adds the speed cap, card rows out of speed, a week without a transfer in
(NULL, not 1.0), payers counted once, self vs past waiting 4 weeks, peer medians ignoring non-training months.
30 tests pass on v1 and v1_full. Two bugs were caught on the way: DuckDB's `least(1, NULL)` returning 1, and its median
of a DECIMAL rounding to 2 places.

## 10 Oct 2026 — Modelling Phase 2 (in progress): `open_by_day`, cleaning notebook `notebooks/02_preprocess.ipynb`

No change to the simulated data. New derived files per data folder: `<out>/features/accounts_linear.parquet`,
`accounts_tree.parquet` and `preprocess_manifest.json`, written by `python -m features preprocess` (all Phase 2 code is in
the notebook, team decision 10 Oct 2026); committed report and fitted numbers in `outputs/modelling/preprocess/`.
- `amldata.labels()` returns `open_by_day` with any cut-off for months 0–5 (0 once the bank has closed the account;
  only confirmed launderers are closed); withheld when test months are requested. Phase 3 drops training account-weeks
  with 0.
- Recipe fitted per dataset on its own months 0–4 (team decision 10 Oct 2026): BAF negative codes -> NaN + flag in 6
  columns, `velocity_6h` clipped at 0 (its negative rows are all in months 5–7), categories frozen from months 0–4;
  `linear` mode (median fill, log, one-hot, standardise) and `tree` mode (NaN kept, raw, `category` dtype).
- **Log change (team decision 10 Oct 2026):** the Phase 2 plan logged 9 columns in `linear` mode; the log made 4 of them
  more lopsided on v1_full months 0–4 (skew `intended_balcon_amount` 1.34 -> −1.15, `velocity_6h` 0.34 -> −1.20,
  `velocity_24h` 0.32 -> −0.34, `velocity_4w` 0.11 -> −0.45), so they are no longer logged. By the same rule
  `current_address_months_count` (1.41 -> −0.54) was added. Logged now: `days_since_request`, `prev_address_months_count`,
  `current_address_months_count`, `session_length_in_minutes`, `bank_branch_count_8w`, `zip_count_4w`. The notebook
  asserts that every logged column is less skewed after the log.
- Run on v1_full, v1, variant_II and variant_IV (15 Oct 2026): all 25 notebook checks pass on each; v1_full and v1 match
  the EDA report §1 exactly; 56 `linear` / 35 `tree` features. Both notebooks now find the repo root themselves, so
  "Run All" in VS Code works without `PYTHONPATH`.

## 9 Oct 2026 — Modelling Phase 1: EDA on the training months (`python -m features eda`)

No data change. `notebooks/01_eda_train.ipynb` (executed by `python -m features eda`) reads months 0–4 through `amldata` only (month 5 untouched, test months
closed) and writes `outputs/modelling/eda/` (report, 8 figures, `univariate_tests.csv`, `feature_screen.csv`; 50k copy in
`eda/v1_50k/`). Full-size findings: only fake accounts separate at opening; fakes start in weeks 8–17, real customers across
the window; cumulative volume, weekly rows/payers and the median in->out delay carry signal once a burst exists; weekly
abroad / high-risk / cash shares do not; homophily 20x the base rate. Found that a zero-activity week means the bank
closed the account (only confirmed launderers are closed): post-closure weeks must be dropped from training.

## 9 Oct 2026 — Modelling Phase 0: `labels(profile=True)`, feature-store skeleton with manifest, leak tests

No data change. `amldata.labels(profile=True)` returns each launderer's hidden type (fake / witting / unwitting, None for
everyone else) for months 0–5 only, for EDA breakdowns; it refuses test months even with `allow_test=True`. New packages
`src/features` (weekly feature store `python -m features weekly`, `features_manifest.json` recording the feature list, the
cut-off rule `day <= open_day + 7w + 6`, the code commit and a hash of the data's `run_manifest.json`; `load()` refuses a stale
store) and `src/models` (CLI stub). `tests/test_features.py` checks on a synthetic dataset that week-w features ignore later
rows, that rebuilds are byte-identical and that stale manifests are refused. Added lightgbm, networkx, torch to requirements.
Phased plan: doc tab "Modelling: phased plan".

## 9 Oct 2026 — `amldata.labels()`: the agreed weekly label and a weeks-since-opening cut-off

`labels()` now also returns `mule_by_day`, the main label agreed on 8 Oct: a fake account counts as a mule from
the day it opens, a real customer from the day they start laundering. A new `weeks_since_open=w` cut-off ends at
each account's own week w (open_day + 7w + 6), the clock of the fixed-cohort comparison; `as_of_day=` still gives
one calendar day. `is_launderer` remains the fixed final label. On the full-size training accounts:
`mule_by_day` 391 at week 0, 411 at week 8, 552 by week 78 (`started_by_day` 1, 34, 552). Data unchanged; new tests
check fakes count from week 0, started implies mule, and both labels reach `is_launderer` by the end.
## 8 Oct 2026 — R6 waits 8 weeks before judging a new account (team decision); all data regenerated

R6 ("sudden change") compared money in against the average of the previous weeks after only 4 weeks of history.
For many new accounts those weeks hold no salary yet, so the first monthly salary looked like a sudden change:
3,837 alerts at 244k (65% of all the rules' alerts), none on a launderer, almost all in an account's 4th–5th week.
They also put two-thirds of the test cohort's weekly alert budget into a single week. `rules.R6_history_weeks` is
now [8, 8] (was [4, 8]). At 50k with the scale held fixed: alerts 1,592 -> 756, the same 45 launderers caught,
false alarms 97.2% -> 94.0%. Checked on every early R6 alert at 50k: 835 of 840 fell in the week of the account's
first salary (the simulator pays it at a random point in the first pay period), the salary being all the money in.

Regenerated (9 Oct 2026, code 23fc46a; all datasets pass the 10 checks):
- `data/v1` (50k): 756 alerts, 94.0% false alarms, 45 of 150 caught (30%), median 7 days; scale 1.516.
- `data/v1_full` (244k): rules re-tuned to scale **1.516** (was 1.741): 3,614 alerts, 240 true, **93.4%** false
  alarms (inside 90–95% for the first time), **237 of 732 caught (32%)** (was 25%), median 9 days; weekly budget
  mean 33.2 / median 34 / max 95 (was 54.4 / 28 / 170). Test cohort alerts in week 4 after opening: 10 (was 1,006).
- Variants II / IV (frozen at 1.516): 93.2% / 93.1% false alarms, 34% / 33% caught.
- 42 sensitivity runs (frozen at 1.516): seeds 93.1–93.4% / 32–33%; transfers £1,500 75% caught, repeated bursts
  76%; prevalence 1% 81.3%, 0.1% 97.8% false alarms; doubled cash 98.4%. See `outputs/sensitivity/FINDINGS.md`.
- Rough baseline (application-only model, same number of flags as the rules on the test cohort, now 662): model
  19% vs rules 33%; together 44%. The rules are a stronger benchmark after the fix.
## 8 Oct 2026 — `amldata` reads the full-size dataset by default

`amldata.public()`, `labels()` and `evaluation()` now default to `data/v1_full` (244k, the main modelling dataset)
instead of `data/v1` (50k), so model code can't train on the small set by accident. Pass `out="data/v1"` for quick
experiments, or a variant folder. Data unchanged.

## 8 Oct 2026 — sensitivity results (42 runs, `outputs/sensitivity/`)

All 42 runs pass the 10 checks. Seeds 43/44 put chance at 96.7–96.9% false alarms and 24–26% caught. Large effects:
laundering transfers of £1,500 (71% caught) and repeated bursts (67% caught); prevalence 1% (90.8% false alarms)
and 0.1% (99.0%); doubled cash deposits (98.9%, R2 ~13,000 alerts); 15–22-payer group collections (R3 2,178
alerts). Everything else stays near the seed range. Details: `outputs/sensitivity/FINDINGS.md`.

## 8 Oct 2026 — repeated bursts and window-scaled start bands (team decisions 8 Oct 2026)

- `timing.bursts_per_launderer = repeat_until_closed` is now built: a new burst starts `timing.repeat_gap_days`
  (30, new setting, assumption) after each burst ends, until the window ends; the bank's closure removes the rest.
- `size.observe_days` shorter than 548: existing customers' start bands shrink in proportion, so every burst and
  its forwarding still end inside the window (365 days: starts up to day ~343). 548 and longer: unchanged.
- The sensitivity runner now includes `observe_days` (365, 730) and repeated bursts: 42 runs.
- Default unchanged: rebuilding `data/v1` is identical. 6,000-account smoke runs of all three pass 10/10 checks.
- Bug fix: every simulator process shared one DuckDB scratch folder (`/tmp/sim_duckdb`); two runs at the same time
  could corrupt each other's temporary files (a sensitivity run crashed with SIGBUS). Each process now uses its own.
- Bug fix: `finalize` settled closures in at most 4 passes; with repeated bursts they had not settled, leaving 219
  rows after closure (check 3 failed). It now repeats until settled (up to 20 passes) and stops with an error
  rather than write inconsistent files. Runs that settled within 4 passes (all others) are unaffected.
- DuckDB's memory cap can be raised with `SIM_DUCKDB_MEMORY` (default 1500MB); the 732k run needs ~8GB.

## 7 Oct 2026 — sensitivity runner, young-weighted fake ages, guard on unread settings

- `python -m sim.sensitivity`: one run per `test` value in the config (244k, seed 42, rules frozen at the
  main run's scale), plus seeds 43/44 and prevalence 0.1% (732k) / 1% (244k): 39 runs. Large files are
  deleted after the checks; summaries go to `outputs/sensitivity/`. Resumes where it stopped.
- `profiles.fake_age_rule = young_weighted` is now built (default unchanged: rebuilt accounts identical).
- `--set` refuses settings the code does not read (`sim.config.NOT_READ`), and `tests/test_config.py` fails
  if any setting is neither read nor listed there.

## 7 Oct 2026 — BAF Variants II and IV (`data/variant_II`, `data/variant_IV`)

No code change. 244k accounts, seed 42, rules frozen (`--set rules.fixed_scale=1.741`), BAF Variant II / IV files;
all 10 checks pass on both. Rules: 96.9% / 96.8% false alarms, 25% / 26% of launderers caught, median 8 days,
weekly budget 54.3 / 55.3. Launderer rate age 50+ vs under 50: Variant II 0.34% vs 0.23% (train) and 0.47% vs
0.20% (test); Variant IV 0.40% vs 0.21% (train) and 0.26% vs 0.32% (test), the planted drift. EDA reports in
`outputs/eda/variant_II/` and `outputs/eda/variant_IV/`.
## 7 Oct 2026 — frozen rules option (`rules.fixed_scale`)

Team decision: the bank's rules are frozen for variant and sensitivity runs. New setting `rules.fixed_scale`
(null = tune as before; a number = use that scale and skip tuning). Variant and sensitivity runs use
`--set rules.fixed_scale=1.741`, the scale tuned on `data/v1_full`. The data card states the scale and whether it
was frozen. Check: the 50k run with the scale fixed at its tuned value (1.516) reproduces `data/v1` exactly.

## 7 Oct 2026 — 23 hidden numbers moved into the config; R6 window bug fixed

An audit of the simulator code found 23 numbers that change results but were written into the code instead of
`configs/sim.yaml`. All are now settings with a source note (most honestly `modelling` or `assumption`: our
choice, no published figure), so they can be cited in the report and changed with `--set`:
- income: `anchor_points` (0.1/0.5/0.9); the average weekly spend now reads `spend_weekly_household` instead of a copy.
- normal: `card_split_exponent`, `card_week_sigma`, `dd_split_gamma_shape`, `transfer_in_sigma`, `cheque_amount`,
  `cash_withdrawal_sigma`, `cash_deposit_sigma`, `large_cash_amount`, `abroad_sigma`, `group_collection`.
- laundering: `piece_sigma`, `split_max_n_in`, `half_cash_share`, `layered_internal_multiplier`,
  `cash_out_piece_max`, `forward_delay_bands_minutes`.
- rules: `R2_window_weeks`, `R5_window_weeks`.

**Bug fixed:** `rules.R6_history_weeks` = [4, 8] was read, but the 8 (weeks averaged for R6's "usual week") was
ignored because the SQL had 8 written in. Changing it did nothing; now it works (at 6,000 accounts, 6 weeks
instead of 8 gives 251 alerts instead of 91).

**Effect on results: none.** Same values: rebuilding `data/v1` gives identical files, rows, labels, alerts and
tuning table. 10 checks and 5 tests pass.

**Test values and sources (approved 7 Oct 2026; main values unchanged):**
- `group_collection`: 8–15 payers matches Collection Pot's leaving collections (11.4 contributors). Tests: 15–22 payers
  (retirement size, 18.3), 4–8 payers, median £11 (source's £12.89 average) and £40. Main median stays £20 (team
  decision). Strength now `partly_sourced`. These collections cause 328 of the 329 R3 alerts at 244k.
- `large_cash_amount`: tests £10k–15k and £10k–30k; upper end consistent with Barclays/HSBC £20k-a-year caps.
- `cheque_amount`: tests median £50 and £200; Pay.UK's all-cheque average (£1,431, 2025) includes business cheques,
  so no personal figure exists.

## 7 Oct 2026 — rule-tuning scales moved into the config

The list of scales tried when tuning R3–R6 was fixed in `rules.py` (`np.geomspace(0.25, 8, 26)`). It is now
`rules.tune_scales` in `configs/sim.yaml` (low 0.25, high 8, 26 steps) with its source note, so it can be cited
and changed with `--set`. Same values: rebuilding `data/v1` gives identical files, tuning table and chosen
scale (1.516); 10 checks and 5 tests pass.

## 7 Oct 2026 — first full-size run (`data/v1_full`)

No code change. `sim.run all --out data/v1_full --set size.n_accounts=244000` at commit `e81d984` (seed 42):
all 10 checks pass; 732 launderers (180 in test months 6–7); 108.7M transactions; rules tuned to scale 1.741
(50k: 1.516) give 5,930 alerts, 96.9% false alarms, 25% of launderers alerted (median 9 days after start),
weekly alert budget mean 54.4 / median 28. Activity-model AUC 0.755, application-only 0.734. 11 min, 7.2 GB.
Also confirmed: rebuilding `data/v1` from scratch on Python 3.12 reproduces it exactly.

## 7 Oct 2026 — `--set` overrides and run manifests

**Change.**
- `sim.run` takes `--set key=value` (repeatable; value read as YAML) to change a setting for one run without
  editing `configs/sim.yaml`. Unknown keys and malformed values are refused before anything is written.
- The `accounts` step writes `<out>/run_manifest.json`: config file + hash, `--set` values, seed, BAF file +
  hash, git commit (and whether there were uncommitted changes), Python and package versions. Later steps refuse
  to run with different settings. `sim.checks`, the data card and `tests/test_data.py` re-apply the overrides.
- The data card shows the overrides, code version and BAF file, and its tables have a fixed order.
- The too-easy check is now repeatable (seeded model, rows sorted). It read 0.714 / 0.721 on earlier runs of
  the same data; it now reads AUC 0.741, average precision 0.103 every time on `data/v1`.
- `pytest` added to `requirements.txt`.

**Effect on results: none.** The generated data does not change; `data/v1` was made before manifests, so its
data card says "overrides unknown". All 10 checks and 5 tests pass on `data/v1` and on 2,000- and 6,000-account
test runs made with `--set`.

## 7 Oct 2026 — anonymous transaction ids (fixes a label leak)

**Problem.** `txn_id` in the public `transactions` file started with `L_` for every laundering transfer and
`N###_` for normal ones, so anyone reading the column could see which rows were laundering. Laundering rows
also sat together at the start of the file, so a row's position gave the label away too. Flagged in the EDA
report (§12); fix approved 7 Oct 2026.

**Change.**
- `finalize` now gives every transfer a new id: `T` + 16 hex characters of md5(provisional id + seed).
  Both rows of an internal transfer still share one id. Same config + seed still gives identical data.
- `transactions` is written sorted by `day`, `time` (ties by `txn_id`, `account_id`).
- The provisional `N###_` / `L_` ids remain only in the hidden working files under `_internal/`.
- New check 10 (`anonymous ids`) fails if any id is not `T` + 16 hex, if laundering ids are not spread
  evenly (mean position must be within 0.45–0.55), or if rows are out of time order.

**Effect on results: none.** Rebuilding `data/v1` (50,000 accounts, seed 42) left `accounts`,
`accounts_truth`, `aml_alerts` and `aml_outcomes` byte-identical; every transaction row and label is
unchanged (22,276,022 rows, 21,741,821 distinct ids, no collisions). Only `txn_id` values and row order
changed. All 10 checks and 5 tests pass.

**Action for the team.** Re-generate or re-run `finalize` on any local copy of `data/v1` made before this
change; old copies still carry the leak. Never build features from `txn_id`; use it only to join the two
rows of a transfer.
