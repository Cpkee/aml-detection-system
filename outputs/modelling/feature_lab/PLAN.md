# Feature lab: trials planned before they were run (written 28 Oct 2026)

Every trial against the same three folds is one more look, and the more looks, the more likely one group wins by
chance (17 on v1_full before this plan, see `ledger.csv`). This file lists the remaining trials **before** they run,
so the ledger can be checked against the plan. It is a proposal for the team (Emmy Li, 28 Oct 2026).

## Measure and budget (proposal)

- **Deciding measure: `catch_rules`.** Flags are permanent and limited to the rules' alert count in each week since
  opening, on the same month's accounts (about 6 a week per validation month on v1_full, against about 300 for the
  current top 1%). Per week, the share of mule accounts already flagged; averaged over weeks 0–26. The rules' own
  value is reported beside it on the same scale.
- **Beside it:** `catch_0.1pct` (0.1% of open accounts per week, steadier), `weekly_recall` (the 26 Oct measure),
  `start_recall`, account-level PR-AUC, real-customer mules caught at the rules' budget per fold.
- **Noise levels:** measured by the placebo trial `noise-placebo5` (5 groups of shuffled columns), not assumed.

## Trials, in order (v1_full, `--decide catch_rules`)

| # | Trial | Groups | Question | Promotion rule |
|---|---|---|---|---|
| 0 | `noise-placebo5` | 5 placebos | How much does refitting alone move each measure? | none (sets `NOISE`) |
| 1 | `roll4-recheck-rules-budget` | `roll4`, baseline = store only | Does the adopted roll4 still help at the rules' budget? | report only (already adopted) |
| 2 | `app-split` | `app_split` | Do two application scores (fake / real customer) beat one? | `better` on catch_rules; real-customer mules caught not lower in any fold |
| 3 | `graph` | `graph_struct`, `graph_nb`, all | Do directed, money-weighted, time-respecting graph features help? | as #2, and `start_recall` not lower |

After trial 3: **freeze the feature list** (write it in CLAUDE.md, which the `feature-engineer` agent respects).

## Confirmation on fresh data (once, after the freeze)

The seed-43 and seed-44 main runs are the same simulator with new accounts: an honest check of the frozen list that
leaves month 5 for calibration. They are not on disk; each needs about 10 GB (simulate, preprocess, store, graph):

```bash
PYTHONPATH=src python -m sim.sensitivity --run --only seed__43
PYTHONPATH=src python -m features preprocess --out data/sensitivity/seed__43 --report outputs/modelling/preprocess/seed__43
PYTHONPATH=src python -m features weekly --out data/sensitivity/seed__43 --weeks 0-77
PYTHONPATH=src python -m features graph --out data/sensitivity/seed__43
PYTHONPATH=src python -m models.feature_lab --out data/sensitivity/seed__43 --baseline store \
    --groups roll4 <frozen groups> --decide catch_rules --name confirm-seed43
```

Then the same for `seed__44`. A group that is `better` on v1_full but not on both seeds is reported as unconfirmed.

**Update after the pull of 28 Oct 2026:** the team froze the list (store + `roll4` + `app_score`, 38 inputs) and made
`seed__43` the one-look holdout for any feature-lab candidate (`.claude/agents/feature-engineer.md`, step 5). Trials 2-3
produced no candidate, so the only fresh-data question left is whether `roll4` (the one adopted group) holds there:
one look, `--baseline store --groups roll4`, as above. It is a robustness check, like re-checking `roll4` on
Variants II / IV, and does not reopen the list.

## Results (28 Oct 2026, v1_full, decided on `catch_rules`; the rules' own value is 0.141)

| # | Trial | catch_rules (per fold change) | Verdict | Also |
|---|---|---|---|---|
| 0 | `noise-placebo5` | placebo gains RMS 0.006 | sets NOISE 0.012 (catch_0.1pct 0.005) | weekly_recall 0.006, PR-AUC 0.008 measured |
| 1 | `roll4-recheck-rules-budget` | 0.381 -> 0.457 (+0.128 / +0.072 / +0.027) | better | adoption holds at the rules' budget |
| 2 | `app-split` | 0.457 -> 0.449 (-0.008 / -0.022 / +0.006) | no clear change; catch_0.1pct worse | PR-AUC 0.870 -> 0.811; drop |
| 3 | `graph` `graph_struct` | 0.452 (-0.011 / -0.004 / -0.001) | worse (each fall below noise) | start_recall +0.02 to +0.03 |
| 3 | `graph` `graph_nb` | 0.469 (-0.008 / +0.006 / +0.038) | no clear change | start_recall +0.02 to +0.04, PR-AUC 0.895 |
| 3 | `graph` both | 0.469 (+0.001 / +0.004 / +0.029) | no clear change | |

None of trials 2-3 is a promotion candidate. Next step for the team: decide on the measure and the freeze.

## Fresh-data check, seed 43 (28 Oct 2026, one look)

`data/sensitivity/seed__43` rebuilt from its committed `run_manifest.json` (same BAF hash and setting values; the
data card matches the committed one, 10 of 10 checks pass), then its preprocess, store and one lab run
`roll4-confirm-seed43` (`--baseline store --groups roll4 --decide catch_rules`):

| | baseline (store) | + roll4 | per fold | verdict |
|---|---|---|---|---|
| catch_rules (rules' own: 0.162) | 0.382 | 0.452 | +0.076 / +0.079 / +0.055 | better |
| weekly_recall (pooled) | 0.347 | 0.400 | +0.047 / +0.048 / +0.045 | better |
| account PR-AUC | 0.691 | 0.859 | | better |
| start_recall | | | +0.069 / +0.051 / +0.104 | (no verdict) |

Real-customer mules caught at the rules' budget rise or stay level in every fold (e.g. fold 3: witting 5/8 -> 6/8,
unwitting 0/4 -> 2/4). **roll4 is confirmed on fresh accounts.** Seed 43's look for roll4 is now used.
