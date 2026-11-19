# Harness, final test: cohort opened in month(s) 6, 7

Settings: `{"data": "data/sensitivity/out_transfer_mean__1", "cohort_months": [6, 7], "horizons": [26, 77], "model": "robust_avg5", "model_params_source": "file", "model_git_commit": "56cfa2a227cf076499654c1d6b943fc8fe2ffe8e", "model_machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "cohort_accounts": 50061, "launderers": 180, "budget_per_horizon": {"26": 354, "77": 808}, "score_source": "model:robust_avg5", "scores_sha256": null, "run_manifest_sha256": "068ee6768e7d9b74fe17c45271ac27f91e480eb9802acd04f2409a212d430de9", "git_commit": "56cfa2a227cf076499654c1d6b943fc8fe2ffe8e", "git_uncommitted_changes": true, "retest_reason": null, "seconds": 23}`

Model vs rules on the same accounts. Each week since opening the model may flag as many accounts as the rules raised alerts on this cohort that week; a flag is permanent. `model_anytime`: a secondary policy, one score threshold over the horizon (on each account's highest score) flagging the same total number of accounts.

- The weekly budget counts the rules' alerts: an account alerted twice counts twice, so the model can flag slightly more distinct accounts than the rules (e.g. 124 vs 119 over weeks 0-26 in the month-5 dry run).
- The model is trained on weeks 0-26 only (models.train WEEKS); weeks 27-77 are outside its training range, so its running-total features drift there and late scores are not comparable across weeks.

## Weeks 0-26 (main): launderers who are mules by the end of week 26

|                        | model   | rules   | model_anytime   |
|:-----------------------|:--------|:--------|:----------------|
| flagged                | 354     | 334     | 354             |
| caught                 | 148     | 120     | 148             |
| mules                  | 163     | 163     | 163             |
| recall                 | 0.908   | 0.736   | 0.908           |
| recall_final_label     | 0.822   | 0.667   | 0.822           |
| precision              | 0.418   | 0.359   | 0.418           |
| false_alarm_share      | 0.582   | 0.641   | 0.582           |
| precision_final_label  | 0.418   | 0.359   | 0.418           |
| catch_mean             | 0.501   | 0.379   | 0.516           |
| median_days_from_start | 4       | 6       | 4               |
| flagged_before_start   | 5       | 0       | 9               |
| caught_fake            | 134/147 | 109/147 | 134/147         |
| caught_witting         | 9/11    | 6/11    | 9/11            |
| caught_unwitting       | 5/5     | 5/5     | 5/5             |

Ties at the cut line (decided by account id): 0 of 27 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   163.0 |
| both                                |   118.0 |
| model_only                          |    30.0 |
| rules_only                          |     2.0 |
| either                              |   150.0 |
| neither                             |    13.0 |
| median_days_model_earlier_when_both |     3.0 |
| model_first_when_both               |    77.0 |
| rules_first_when_both               |    32.0 |
| median_min_days_earlier_model_only  |    91.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy        | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:--------------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model         | under 30 |      12526 |      26 |       24 |   0.9231 |               27 |                0.0022 |      0.4706 |
| model         | 30-49    |      29335 |      80 |       72 |   0.9    |              106 |                0.0036 |      0.4045 |
| model         | 50+      |       8200 |      57 |       52 |   0.9123 |               73 |                0.009  |      0.416  |
| rules         | under 30 |      12526 |      26 |       16 |   0.6154 |               52 |                0.0042 |      0.2353 |
| rules         | 30-49    |      29335 |      80 |       59 |   0.7375 |              126 |                0.0043 |      0.3189 |
| rules         | 50+      |       8200 |      57 |       45 |   0.7895 |               36 |                0.0044 |      0.5556 |
| model_anytime | under 30 |      12526 |      26 |       24 |   0.9231 |               26 |                0.0021 |      0.48   |
| model_anytime | 30-49    |      29335 |      80 |       72 |   0.9    |              102 |                0.0035 |      0.4138 |
| model_anytime | 50+      |       8200 |      57 |       52 |   0.9123 |               78 |                0.0096 |      0.4    |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy        |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:--------------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model         |            6 |      26529 |      93 |       83 |   0.8925 |       212 |      0.3915 |           0.5299 |        0.5706 |        0.5989 |
| model         |            7 |      23532 |      70 |       65 |   0.9286 |       142 |      0.4577 |           0.4701 |        0.4294 |        0.4011 |
| rules         |            6 |      26529 |      93 |       71 |   0.7634 |       178 |      0.3989 |           0.5299 |        0.5706 |        0.5329 |
| rules         |            7 |      23532 |      70 |       49 |   0.7    |       156 |      0.3141 |           0.4701 |        0.4294 |        0.4671 |
| model_anytime |            6 |      26529 |      93 |       83 |   0.8925 |       211 |      0.3934 |           0.5299 |        0.5706 |        0.596  |
| model_anytime |            7 |      23532 |      70 |       65 |   0.9286 |       143 |      0.4545 |           0.4701 |        0.4294 |        0.404  |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   flagged_model_anytime |   catch_model_anytime |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|------------------------:|----------------------:|---------:|--------------:|
|      0 |           50061 |     147 |         0 |               5 |         0     |               5 |         0     |                      49 |                 0.034 |        5 |             0 |
|      2 |           50061 |     149 |         2 |              20 |         0.013 |              20 |         0     |                      66 |                 0.047 |        7 |             0 |
|      4 |           50060 |     150 |         3 |              42 |         0.02  |              41 |         0.02  |                      78 |                 0.06  |       12 |             0 |
|      8 |           50059 |     151 |        13 |              73 |         0.093 |              71 |         0.026 |                     112 |                 0.126 |       13 |             0 |
|     12 |           50048 |     155 |        77 |             145 |         0.458 |             142 |         0.316 |                     182 |                 0.477 |       18 |             0 |
|     17 |           49996 |     158 |       158 |             243 |         0.899 |             237 |         0.696 |                     272 |                 0.899 |       21 |             0 |
|     26 |           49961 |     163 |       163 |             354 |         0.908 |             334 |         0.736 |                     354 |                 0.908 |       13 |             0 |

## Weeks 0-77: launderers who are mules by the end of week 77

|                        | model   | rules   |
|:-----------------------|:--------|:--------|
| flagged                | 808     | 732     |
| caught                 | 159     | 135     |
| mules                  | 180     | 180     |
| recall                 | 0.883   | 0.750   |
| recall_final_label     | 0.883   | 0.750   |
| precision              | 0.197   | 0.184   |
| false_alarm_share      | 0.803   | 0.816   |
| precision_final_label  | 0.197   | 0.184   |
| catch_mean             | 0.760   | 0.618   |
| median_days_from_start | 4       | 6       |
| flagged_before_start   | 5       | 0       |
| caught_fake            | 136/147 | 113/147 |
| caught_witting         | 13/20   | 10/20   |
| caught_unwitting       | 10/13   | 12/13   |

`model_anytime`: not meaningful (model trained on weeks 0-26).

Ties at the cut line (decided by account id): 0 of 78 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   180.0 |
| both                                |   131.0 |
| model_only                          |    28.0 |
| rules_only                          |     4.0 |
| either                              |   163.0 |
| neither                             |    17.0 |
| median_days_model_earlier_when_both |     2.0 |
| model_first_when_both               |    83.0 |
| rules_first_when_both               |    39.0 |
| median_min_days_earlier_model_only  |   448.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy   | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:---------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model    | under 30 |      12526 |      35 |       30 |   0.8571 |              120 |                0.0096 |      0.2    |
| model    | 30-49    |      29335 |      86 |       76 |   0.8837 |              330 |                0.0113 |      0.1872 |
| model    | 50+      |       8200 |      59 |       53 |   0.8983 |              199 |                0.0244 |      0.2103 |
| rules    | under 30 |      12526 |      35 |       23 |   0.6571 |              155 |                0.0124 |      0.1292 |
| rules    | 30-49    |      29335 |      86 |       65 |   0.7558 |              347 |                0.0119 |      0.1578 |
| rules    | 50+      |       8200 |      59 |       47 |   0.7966 |               95 |                0.0117 |      0.331  |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy   |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:---------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model    |            6 |      26529 |     103 |       90 |   0.8738 |       477 |      0.1887 |           0.5299 |        0.5722 |        0.5903 |
| model    |            7 |      23532 |      77 |       69 |   0.8961 |       331 |      0.2085 |           0.4701 |        0.4278 |        0.4097 |
| rules    |            6 |      26529 |     103 |       80 |   0.7767 |       398 |      0.201  |           0.5299 |        0.5722 |        0.5437 |
| rules    |            7 |      23532 |      77 |       55 |   0.7143 |       334 |      0.1647 |           0.4701 |        0.4278 |        0.4563 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|---------:|--------------:|
|      0 |           50061 |     147 |         0 |               5 |         0     |               5 |         0     |        5 |             0 |
|      2 |           50061 |     149 |         2 |              20 |         0.013 |              20 |         0     |        7 |             0 |
|      4 |           50060 |     150 |         3 |              42 |         0.02  |              41 |         0.02  |       12 |             0 |
|      8 |           50059 |     151 |        13 |              73 |         0.093 |              71 |         0.026 |       13 |             0 |
|     12 |           50048 |     155 |        77 |             145 |         0.458 |             142 |         0.316 |       18 |             0 |
|     17 |           49996 |     158 |       158 |             243 |         0.899 |             237 |         0.696 |       21 |             0 |
|     26 |           49961 |     163 |       163 |             354 |         0.908 |             334 |         0.736 |       13 |             0 |
|     52 |           49954 |     169 |       169 |             577 |         0.893 |             529 |         0.746 |       15 |             0 |
|     77 |           49948 |     180 |       180 |             808 |         0.883 |             732 |         0.75  |       10 |             0 |

- recall / precision: against mule accounts by the end of the horizon (fake accounts from opening, real customers from their start). recall_final_label / precision_final_label: against launderers at any time in the 18 months (label maturity).
- median_min_days_earlier_model_only: launderers caught by the model but not by the rules within the horizon; days from the model's flag to the end of the horizon, so the model is at least this many days earlier (the count is model_only).
- median_days_from_start: days from laundering start to the first flag, caught launderers only (negative = flagged before it started). A model flag is dated at the end of its week.
- catch_mean: per week the share of that week's mules already flagged, averaged over the weeks.
- Accounts closed by the bank stay in the cohort (caught by the rules); `open_accounts` counts the ones still open at the end of each week.
