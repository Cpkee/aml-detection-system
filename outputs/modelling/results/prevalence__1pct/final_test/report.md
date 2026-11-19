# Harness, final test: cohort opened in month(s) 6, 7

Settings: `{"data": "/Users/cheepheng/aml-detection-system/data/sensitivity/prevalence__1pct", "cohort_months": [6, 7], "horizons": [26, 77], "model": "robust_avg5", "model_params_source": "file", "model_git_commit": "9ab7838ff1f8d6b4450e525f2a7db285f80be8a9", "model_machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "cohort_accounts": 50061, "launderers": 611, "budget_per_horizon": {"26": 369, "77": 834}, "score_source": "model:robust_avg5", "scores_sha256": null, "run_manifest_sha256": "b9924a67fdc210e653993df06e1e99cec6e4a30d26fbc9b91d5e116e65568c23", "git_commit": "9ab7838ff1f8d6b4450e525f2a7db285f80be8a9", "git_uncommitted_changes": false, "retest_reason": null, "seconds": 25}`

Model vs rules on the same accounts. Each week since opening the model may flag as many accounts as the rules raised alerts on this cohort that week; a flag is permanent. `model_anytime`: a secondary policy, one score threshold over the horizon (on each account's highest score) flagging the same total number of accounts.

- The weekly budget counts the rules' alerts: an account alerted twice counts twice, so the model can flag slightly more distinct accounts than the rules (e.g. 124 vs 119 over weeks 0-26 in the month-5 dry run).
- The model is trained on weeks 0-26 only (models.train WEEKS); weeks 27-77 are outside its training range, so its running-total features drift there and late scores are not comparable across weeks.

## Weeks 0-26 (main): launderers who are mules by the end of week 26

|                        | model   | rules   | model_anytime   |
|:-----------------------|:--------|:--------|:----------------|
| flagged                | 369     | 352     | 369             |
| caught                 | 297     | 138     | 367             |
| mules                  | 524     | 524     | 524             |
| recall                 | 0.567   | 0.263   | 0.700           |
| recall_final_label     | 0.486   | 0.226   | 0.601           |
| precision              | 0.805   | 0.392   | 0.995           |
| false_alarm_share      | 0.195   | 0.608   | 0.005           |
| precision_final_label  | 0.805   | 0.392   | 0.995           |
| catch_mean             | 0.258   | 0.133   | 0.370           |
| median_days_from_start | 11      | 7       | 8               |
| flagged_before_start   | 4       | 0       | 0               |
| caught_fake            | 273/477 | 123/477 | 347/477         |
| caught_witting         | 6/17    | 5/17    | 6/17            |
| caught_unwitting       | 18/30   | 10/30   | 14/30           |

Ties at the cut line (decided by account id): 0 of 27 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   524.0 |
| both                                |    90.0 |
| model_only                          |   207.0 |
| rules_only                          |    48.0 |
| either                              |   345.0 |
| neither                             |   179.0 |
| median_days_model_earlier_when_both |     0.0 |
| model_first_when_both               |    39.0 |
| rules_first_when_both               |    36.0 |
| median_min_days_earlier_model_only  |    70.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy        | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:--------------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model         | under 30 |      12526 |      85 |       42 |   0.4941 |               11 |                0.0009 |      0.7925 |
| model         | 30-49    |      29335 |     283 |      159 |   0.5618 |               39 |                0.0013 |      0.803  |
| model         | 50+      |       8200 |     156 |       96 |   0.6154 |               22 |                0.0027 |      0.8136 |
| rules         | under 30 |      12526 |      85 |       23 |   0.2706 |               52 |                0.0042 |      0.3067 |
| rules         | 30-49    |      29335 |     283 |       70 |   0.2473 |              126 |                0.0043 |      0.3571 |
| rules         | 50+      |       8200 |     156 |       45 |   0.2885 |               36 |                0.0045 |      0.5556 |
| model_anytime | under 30 |      12526 |      85 |       55 |   0.6471 |                0 |                0      |      1      |
| model_anytime | 30-49    |      29335 |     283 |      199 |   0.7032 |                2 |                0.0001 |      0.99   |
| model_anytime | 50+      |       8200 |     156 |      113 |   0.7244 |                0 |                0      |      1      |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy        |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:--------------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model         |            6 |      26529 |     258 |      146 |   0.5659 |       192 |      0.7604 |           0.5299 |        0.4924 |        0.5203 |
| model         |            7 |      23532 |     266 |      151 |   0.5677 |       177 |      0.8531 |           0.4701 |        0.5076 |        0.4797 |
| rules         |            6 |      26529 |     258 |       71 |   0.2752 |       178 |      0.3989 |           0.5299 |        0.4924 |        0.5057 |
| rules         |            7 |      23532 |     266 |       67 |   0.2519 |       174 |      0.3851 |           0.4701 |        0.5076 |        0.4943 |
| model_anytime |            6 |      26529 |     258 |      179 |   0.6938 |       181 |      0.989  |           0.5299 |        0.4924 |        0.4905 |
| model_anytime |            7 |      23532 |     266 |      188 |   0.7068 |       188 |      1      |           0.4701 |        0.5076 |        0.5095 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   flagged_model_anytime |   catch_model_anytime |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|------------------------:|----------------------:|---------:|--------------:|
|      0 |           50061 |     477 |         0 |               5 |         0     |               5 |         0     |                       0 |                 0     |        5 |             0 |
|      2 |           50061 |     483 |         6 |              21 |         0.012 |              21 |         0.002 |                       2 |                 0.004 |        8 |             0 |
|      4 |           50060 |     487 |        10 |              41 |         0.025 |              40 |         0.004 |                       4 |                 0.008 |       10 |             0 |
|      8 |           50058 |     495 |        38 |              74 |         0.053 |              72 |         0.01  |                       9 |                 0.018 |       13 |             0 |
|     12 |           50048 |     505 |       279 |             148 |         0.198 |             145 |         0.103 |                     161 |                 0.319 |       27 |             0 |
|     17 |           49978 |     513 |       513 |             259 |         0.411 |             254 |         0.248 |                     354 |                 0.688 |       18 |             0 |
|     26 |           49943 |     524 |       524 |             369 |         0.567 |             352 |         0.263 |                     369 |                 0.7   |       12 |             0 |

## Weeks 0-77: launderers who are mules by the end of week 77

|                        | model   | rules   |
|:-----------------------|:--------|:--------|
| flagged                | 834     | 765     |
| caught                 | 377     | 170     |
| mules                  | 611     | 611     |
| recall                 | 0.617   | 0.278   |
| recall_final_label     | 0.617   | 0.278   |
| precision              | 0.452   | 0.222   |
| false_alarm_share      | 0.548   | 0.778   |
| precision_final_label  | 0.452   | 0.222   |
| catch_mean             | 0.486   | 0.222   |
| median_days_from_start | 12      | 7.500   |
| flagged_before_start   | 4       | 0       |
| caught_fake            | 312/477 | 135/477 |
| caught_witting         | 36/67   | 17/67   |
| caught_unwitting       | 29/67   | 18/67   |

`model_anytime`: not meaningful (model trained on weeks 0-26).

Ties at the cut line (decided by account id): 0 of 78 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   611.0 |
| both                                |   109.0 |
| model_only                          |   268.0 |
| rules_only                          |    61.0 |
| either                              |   438.0 |
| neither                             |   173.0 |
| median_days_model_earlier_when_both |     0.0 |
| model_first_when_both               |    48.0 |
| rules_first_when_both               |    43.0 |
| median_min_days_earlier_model_only  |   413.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy   | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:---------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model    | under 30 |      12526 |     130 |       64 |   0.4923 |               74 |                0.006  |      0.4638 |
| model    | 30-49    |      29335 |     319 |      199 |   0.6238 |              264 |                0.0091 |      0.4298 |
| model    | 50+      |       8200 |     162 |      114 |   0.7037 |              119 |                0.0148 |      0.4893 |
| rules    | under 30 |      12526 |     130 |       34 |   0.2615 |              155 |                0.0125 |      0.1799 |
| rules    | 30-49    |      29335 |     319 |       86 |   0.2696 |              345 |                0.0119 |      0.1995 |
| rules    | 50+      |       8200 |     162 |       50 |   0.3086 |               95 |                0.0118 |      0.3448 |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy   |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:---------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model    |            6 |      26529 |     297 |      187 |   0.6296 |       487 |      0.384  |           0.5299 |        0.4861 |        0.5839 |
| model    |            7 |      23532 |     314 |      190 |   0.6051 |       347 |      0.5476 |           0.4701 |        0.5139 |        0.4161 |
| rules    |            6 |      26529 |     297 |       86 |   0.2896 |       404 |      0.2129 |           0.5299 |        0.4861 |        0.5281 |
| rules    |            7 |      23532 |     314 |       84 |   0.2675 |       361 |      0.2327 |           0.4701 |        0.5139 |        0.4719 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|---------:|--------------:|
|      0 |           50061 |     477 |         0 |               5 |         0     |               5 |         0     |        5 |             0 |
|      2 |           50061 |     483 |         6 |              21 |         0.012 |              21 |         0.002 |        8 |             0 |
|      4 |           50060 |     487 |        10 |              41 |         0.025 |              40 |         0.004 |       10 |             0 |
|      8 |           50058 |     495 |        38 |              74 |         0.053 |              72 |         0.01  |       13 |             0 |
|     12 |           50048 |     505 |       279 |             148 |         0.198 |             145 |         0.103 |       27 |             0 |
|     17 |           49978 |     513 |       513 |             259 |         0.411 |             254 |         0.248 |       18 |             0 |
|     26 |           49943 |     524 |       524 |             369 |         0.567 |             352 |         0.263 |       12 |             0 |
|     52 |           49935 |     564 |       564 |             596 |         0.61  |             554 |         0.27  |       15 |             0 |
|     77 |           49918 |     611 |       611 |             834 |         0.617 |             765 |         0.278 |       10 |             0 |

- recall / precision: against mule accounts by the end of the horizon (fake accounts from opening, real customers from their start). recall_final_label / precision_final_label: against launderers at any time in the 18 months (label maturity).
- median_min_days_earlier_model_only: launderers caught by the model but not by the rules within the horizon; days from the model's flag to the end of the horizon, so the model is at least this many days earlier (the count is model_only).
- median_days_from_start: days from laundering start to the first flag, caught launderers only (negative = flagged before it started). A model flag is dated at the end of its week.
- catch_mean: per week the share of that week's mules already flagged, averaged over the weeks.
- Accounts closed by the bank stay in the cohort (caught by the rules); `open_accounts` counts the ones still open at the end of each week.
