# Harness, dry run: cohort opened in month(s) 5

Settings: `{"data": "data/v1_full", "cohort_months": [5], "horizons": [26, 77], "model": "frozen_tuned", "model_params_source": "file", "model_git_commit": "fb47487555177750503c4da8dfdd840dd1aad524", "model_machine": null, "machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "cohort_accounts": 29120, "launderers": 97, "budget_per_horizon": {"26": 124, "77": 382}, "score_source": "model:frozen_tuned", "scores_sha256": null, "run_manifest_sha256": "4ce1c4fb593a8ae5f40e9acb082f1969655095c5a4977dc81f58c9026c62d7ba", "git_commit": "222ad8066f8bb6a3d99c764a590aec81e116c4f0", "git_uncommitted_changes": false, "seconds": 6}`

Model vs rules on the same accounts. Each week since opening the model may flag as many accounts as the rules raised alerts on this cohort that week; a flag is permanent. `model_anytime`: a secondary policy, one score threshold over the horizon (on each account's highest score) flagging the same total number of accounts.

- The weekly budget counts the rules' alerts: an account alerted twice counts twice, so the model can flag slightly more distinct accounts than the rules (e.g. 124 vs 119 over weeks 0-26 in the month-5 dry run).
- The model is trained on weeks 0-26 only (models.train WEEKS); weeks 27-77 are outside its training range, so its running-total features drift there and late scores are not comparable across weeks.
- Scores: model:frozen_tuned. `model_anytime` is shown for horizons up to week 26 only; for longer horizons it is not meaningful (its rows stay in the CSV files).

## Weeks 0-26 (main): launderers who are mules by the end of week 26

|                        | model   | rules   | model_anytime   |
|:-----------------------|:--------|:--------|:----------------|
| flagged                | 124     | 119     | 124             |
| caught                 | 63      | 16      | 72              |
| mules                  | 78      | 78      | 78              |
| recall                 | 0.808   | 0.205   | 0.923           |
| recall_final_label     | 0.649   | 0.165   | 0.742           |
| precision              | 0.508   | 0.134   | 0.581           |
| false_alarm_share      | 0.492   | 0.866   | 0.419           |
| precision_final_label  | 0.508   | 0.134   | 0.581           |
| catch_mean             | 0.382   | 0.095   | 0.462           |
| median_days_from_start | 8       | 8.500   | 6.500           |
| flagged_before_start   | 0       | 0       | 0               |
| caught_fake            | 59/70   | 13/70   | 66/70           |
| caught_witting         | 3/5     | 3/5     | 3/5             |
| caught_unwitting       | 1/3     | 0/3     | 3/3             |

Ties at the cut line (decided by account id): 0 of 27 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |    78.0 |
| both                                |    14.0 |
| model_only                          |    49.0 |
| rules_only                          |     2.0 |
| either                              |    65.0 |
| neither                             |    13.0 |
| median_days_model_earlier_when_both |     1.5 |
| model_first_when_both               |     8.0 |
| rules_first_when_both               |     4.0 |
| median_min_days_earlier_model_only  |    84.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy        | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:--------------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model         | under 30 |       7990 |      14 |       12 |   0.8571 |                5 |                0.0006 |      0.7059 |
| model         | 30-49    |      16034 |      36 |       29 |   0.8056 |               39 |                0.0024 |      0.4265 |
| model         | 50+      |       5096 |      28 |       22 |   0.7857 |               17 |                0.0034 |      0.5641 |
| rules         | under 30 |       7990 |      14 |        4 |   0.2857 |               30 |                0.0038 |      0.1176 |
| rules         | 30-49    |      16034 |      36 |        7 |   0.1944 |               57 |                0.0036 |      0.1094 |
| rules         | 50+      |       5096 |      28 |        5 |   0.1786 |               16 |                0.0032 |      0.2381 |
| model_anytime | under 30 |       7990 |      14 |       13 |   0.9286 |                5 |                0.0006 |      0.7222 |
| model_anytime | 30-49    |      16034 |      36 |       33 |   0.9167 |               34 |                0.0021 |      0.4925 |
| model_anytime | 50+      |       5096 |      28 |       26 |   0.9286 |               13 |                0.0026 |      0.6667 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   flagged_model_anytime |   catch_model_anytime |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|------------------------:|----------------------:|---------:|--------------:|
|      0 |           29120 |      71 |         1 |               0 |         0     |               0 |         0     |                       1 |                 0     |        0 |             0 |
|      2 |           29120 |      71 |         1 |               6 |         0     |               6 |         0     |                       1 |                 0     |        3 |             0 |
|      4 |           29120 |      71 |         1 |              14 |         0     |              14 |         0     |                       1 |                 0     |        1 |             0 |
|      8 |           29120 |      71 |         2 |              26 |         0.014 |              26 |         0     |                       9 |                 0.014 |        2 |             0 |
|     12 |           29119 |      72 |        34 |              49 |         0.306 |              48 |         0.083 |                      36 |                 0.347 |        5 |             0 |
|     17 |           29113 |      74 |        74 |              75 |         0.649 |              73 |         0.162 |                      85 |                 0.892 |        5 |             0 |
|     26 |           29108 |      78 |        78 |             124 |         0.808 |             119 |         0.205 |                     124 |                 0.923 |        2 |             0 |

## Weeks 0-77: launderers who are mules by the end of week 77

|                        | model   | rules   |
|:-----------------------|:--------|:--------|
| flagged                | 382     | 350     |
| caught                 | 76      | 29      |
| mules                  | 97      | 97      |
| recall                 | 0.784   | 0.299   |
| recall_final_label     | 0.784   | 0.299   |
| precision              | 0.199   | 0.083   |
| false_alarm_share      | 0.801   | 0.917   |
| precision_final_label  | 0.199   | 0.083   |
| catch_mean             | 0.655   | 0.198   |
| median_days_from_start | 9       | 9       |
| flagged_before_start   | 1       | 0       |
| caught_fake            | 61/70   | 16/70   |
| caught_witting         | 6/12    | 6/12    |
| caught_unwitting       | 9/15    | 7/15    |

`model_anytime`: not meaningful (model trained on weeks 0-26).

Ties at the cut line (decided by account id): 0 of 78 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |    97.0 |
| both                                |    24.0 |
| model_only                          |    52.0 |
| rules_only                          |     5.0 |
| either                              |    81.0 |
| neither                             |    16.0 |
| median_days_model_earlier_when_both |     1.5 |
| model_first_when_both               |    14.0 |
| rules_first_when_both               |     6.0 |
| median_min_days_earlier_model_only  |   437.5 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy   | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:---------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model    | under 30 |       7990 |      24 |       16 |   0.6667 |               92 |                0.0115 |      0.1481 |
| model    | 30-49    |      16034 |      43 |       34 |   0.7907 |              148 |                0.0093 |      0.1868 |
| model    | 50+      |       5096 |      30 |       26 |   0.8667 |               66 |                0.013  |      0.2826 |
| rules    | under 30 |       7990 |      24 |        8 |   0.3333 |               88 |                0.011  |      0.0833 |
| rules    | 30-49    |      16034 |      43 |       13 |   0.3023 |              179 |                0.0112 |      0.0677 |
| rules    | 50+      |       5096 |      30 |        8 |   0.2667 |               54 |                0.0107 |      0.129  |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|---------:|--------------:|
|      0 |           29120 |      71 |         1 |               0 |         0     |               0 |         0     |        0 |             0 |
|      2 |           29120 |      71 |         1 |               6 |         0     |               6 |         0     |        3 |             0 |
|      4 |           29120 |      71 |         1 |              14 |         0     |              14 |         0     |        1 |             0 |
|      8 |           29120 |      71 |         2 |              26 |         0.014 |              26 |         0     |        2 |             0 |
|     12 |           29119 |      72 |        34 |              49 |         0.306 |              48 |         0.083 |        5 |             0 |
|     17 |           29113 |      74 |        74 |              75 |         0.649 |              73 |         0.162 |        5 |             0 |
|     26 |           29108 |      78 |        78 |             124 |         0.808 |             119 |         0.205 |        2 |             0 |
|     52 |           29102 |      86 |        86 |             248 |         0.791 |             230 |         0.256 |        1 |             0 |
|     77 |           29098 |      97 |        97 |             382 |         0.784 |             350 |         0.299 |        6 |             0 |

- recall / precision: against mule accounts by the end of the horizon (fake accounts from opening, real customers from their start). recall_final_label / precision_final_label: against launderers at any time in the 18 months (label maturity).
- median_min_days_earlier_model_only: launderers caught by the model but not by the rules within the horizon; days from the model's flag to the end of the horizon, so the model is at least this many days earlier (the count is model_only).
- median_days_from_start: days from laundering start to the first flag, caught launderers only (negative = flagged before it started). A model flag is dated at the end of its week.
- catch_mean: per week the share of that week's mules already flagged, averaged over the weeks.
- Accounts closed by the bank stay in the cohort (caught by the rules); `open_accounts` counts the ones still open at the end of each week.
