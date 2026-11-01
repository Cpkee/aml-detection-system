# Harness, dry run: cohort opened in month(s) 5

Settings: `{"data": "data/v1_full", "cohort_months": [5], "horizons": [26], "model": null, "model_params_source": null, "model_git_commit": null, "model_machine": null, "machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "cohort_accounts": 29120, "launderers": 97, "budget_per_horizon": {"26": 124}, "score_source": "file:data/v1_full/scores/outlier_look/outlier_rarity_m5.parquet", "scores_sha256": "888044b05174416e31b7fb2ddf20a6a88315587f5202268f446e73500aed185a", "run_manifest_sha256": "4ce1c4fb593a8ae5f40e9acb082f1969655095c5a4977dc81f58c9026c62d7ba", "git_commit": "39119ede45a10873ac1ff3ef7a5918a7ad5583b1", "git_uncommitted_changes": false, "seconds": 1}`

Model vs rules on the same accounts. Each week since opening the model may flag as many accounts as the rules raised alerts on this cohort that week; a flag is permanent. `model_anytime`: a secondary policy, one score threshold over the horizon (on each account's highest score) flagging the same total number of accounts.

- The weekly budget counts the rules' alerts: an account alerted twice counts twice, so the model can flag slightly more distinct accounts than the rules (e.g. 124 vs 119 over weeks 0-26 in the month-5 dry run).
- The model is trained on weeks 0-26 only (models.train WEEKS); weeks 27-77 are outside its training range, so its running-total features drift there and late scores are not comparable across weeks.

## Weeks 0-26 (main): launderers who are mules by the end of week 26

|                        | model   | rules   | model_anytime   |
|:-----------------------|:--------|:--------|:----------------|
| flagged                | 124     | 119     | 124             |
| caught                 | 16      | 16      | 17              |
| mules                  | 78      | 78      | 78              |
| recall                 | 0.205   | 0.205   | 0.218           |
| recall_final_label     | 0.165   | 0.165   | 0.175           |
| precision              | 0.129   | 0.134   | 0.137           |
| false_alarm_share      | 0.871   | 0.866   | 0.863           |
| precision_final_label  | 0.129   | 0.134   | 0.137           |
| catch_mean             | 0.097   | 0.095   | 0.096           |
| median_days_from_start | 9       | 8.500   | 9               |
| flagged_before_start   | 0       | 0       | 0               |
| caught_fake            | 14/70   | 13/70   | 14/70           |
| caught_witting         | 2/5     | 3/5     | 2/5             |
| caught_unwitting       | 0/3     | 0/3     | 1/3             |

Ties at the cut line (decided by account id): 0 of 27 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |    78.0 |
| both                                |     4.0 |
| model_only                          |    12.0 |
| rules_only                          |    12.0 |
| either                              |    28.0 |
| neither                             |    50.0 |
| median_days_model_earlier_when_both |     1.0 |
| model_first_when_both               |     2.0 |
| rules_first_when_both               |     1.0 |
| median_min_days_earlier_model_only  |    84.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy        | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:--------------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model         | under 30 |       7990 |      14 |        4 |   0.2857 |               30 |                0.0038 |      0.1176 |
| model         | 30-49    |      16034 |      36 |       10 |   0.2778 |               67 |                0.0042 |      0.1299 |
| model         | 50+      |       5096 |      28 |        2 |   0.0714 |               11 |                0.0022 |      0.1538 |
| rules         | under 30 |       7990 |      14 |        4 |   0.2857 |               30 |                0.0038 |      0.1176 |
| rules         | 30-49    |      16034 |      36 |        7 |   0.1944 |               57 |                0.0036 |      0.1094 |
| rules         | 50+      |       5096 |      28 |        5 |   0.1786 |               16 |                0.0032 |      0.2381 |
| model_anytime | under 30 |       7990 |      14 |        6 |   0.4286 |               25 |                0.0031 |      0.1935 |
| model_anytime | 30-49    |      16034 |      36 |        9 |   0.25   |               67 |                0.0042 |      0.1184 |
| model_anytime | 50+      |       5096 |      28 |        2 |   0.0714 |               15 |                0.003  |      0.1176 |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy        |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:--------------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model         |            5 |      29120 |      78 |       16 |   0.2051 |       124 |      0.129  |                1 |             1 |             1 |
| rules         |            5 |      29120 |      78 |       16 |   0.2051 |       119 |      0.1345 |                1 |             1 |             1 |
| model_anytime |            5 |      29120 |      78 |       17 |   0.2179 |       124 |      0.1371 |                1 |             1 |             1 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   flagged_model_anytime |   catch_model_anytime |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|------------------------:|----------------------:|---------:|--------------:|
|      0 |           29120 |      71 |         1 |               0 |         0     |               0 |         0     |                       3 |                 0     |        0 |             0 |
|      2 |           29120 |      71 |         1 |               6 |         0     |               6 |         0     |                       7 |                 0     |        3 |             0 |
|      4 |           29120 |      71 |         1 |              14 |         0     |              14 |         0     |                      16 |                 0     |        1 |             0 |
|      8 |           29120 |      71 |         2 |              26 |         0     |              26 |         0     |                      36 |                 0     |        2 |             0 |
|     12 |           29119 |      72 |        34 |              49 |         0.069 |              48 |         0.083 |                      57 |                 0.056 |        5 |             0 |
|     17 |           29113 |      74 |        74 |              75 |         0.176 |              73 |         0.162 |                      85 |                 0.176 |        5 |             0 |
|     26 |           29108 |      78 |        78 |             124 |         0.205 |             119 |         0.205 |                     124 |                 0.218 |        2 |             0 |

- recall / precision: against mule accounts by the end of the horizon (fake accounts from opening, real customers from their start). recall_final_label / precision_final_label: against launderers at any time in the 18 months (label maturity).
- median_min_days_earlier_model_only: launderers caught by the model but not by the rules within the horizon; days from the model's flag to the end of the horizon, so the model is at least this many days earlier (the count is model_only).
- median_days_from_start: days from laundering start to the first flag, caught launderers only (negative = flagged before it started). A model flag is dated at the end of its week.
- catch_mean: per week the share of that week's mules already flagged, averaged over the weeks.
- Accounts closed by the bank stay in the cohort (caught by the rules); `open_accounts` counts the ones still open at the end of each week.
