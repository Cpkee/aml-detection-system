# Changelog

Changes to the simulator and the data it generates, newest first. Settings changes are also noted in the
`source` of each value in `configs/sim.yaml`; decisions are recorded in the "Simulated Dataset: Logic,
Assumptions and Use" doc.

## 8 Oct 2026 — repeated bursts and window-scaled start bands (team decisions 8 Oct 2026)

- `timing.bursts_per_launderer = repeat_until_closed` is now built: a new burst starts `timing.repeat_gap_days`
  (30, new setting, assumption) after each burst ends, until the window ends; the bank's closure removes the rest.
- `size.observe_days` shorter than 548: existing customers' start bands shrink in proportion, so every burst and
  its forwarding still end inside the window (365 days: starts up to day ~343). 548 and longer: unchanged.
- The sensitivity runner now includes `observe_days` (365, 730) and repeated bursts: 42 runs.
- Default unchanged: rebuilding `data/v1` is identical. 6,000-account smoke runs of all three pass 10/10 checks.
- Bug fix: every simulator process shared one DuckDB scratch folder (`/tmp/sim_duckdb`); two runs at the same time
  could corrupt each other's temporary files (a sensitivity run crashed with SIGBUS). Each process now uses its own.

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
