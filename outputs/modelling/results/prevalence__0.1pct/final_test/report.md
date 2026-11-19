# Harness, final test: cohort opened in month(s) 6, 7

Settings: `{"data": "/Users/cheepheng/aml-detection-system/data/sensitivity/prevalence__0.1pct", "cohort_months": [6, 7], "horizons": [26, 77], "model": "robust_avg5", "model_params_source": "file", "model_git_commit": "813eedc22d890bc4ee591cdb5d4356249708b655", "model_machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "cohort_accounts": 149992, "launderers": 192, "budget_per_horizon": {"26": 740, "77": 2165}, "score_source": "model:robust_avg5", "scores_sha256": null, "run_manifest_sha256": "c7a6ed658c51d50d78fe805887fd379f58a0928da3eeba94f9961bbb7dcde432", "git_commit": "813eedc22d890bc4ee591cdb5d4356249708b655", "git_uncommitted_changes": false, "retest_reason": null, "seconds": 83}`

Model vs rules on the same accounts. Each week since opening the model may flag as many accounts as the rules raised alerts on this cohort that week; a flag is permanent. `model_anytime`: a secondary policy, one score threshold over the horizon (on each account's highest score) flagging the same total number of accounts.

- The weekly budget counts the rules' alerts: an account alerted twice counts twice, so the model can flag slightly more distinct accounts than the rules (e.g. 124 vs 119 over weeks 0-26 in the month-5 dry run).
- The model is trained on weeks 0-26 only (models.train WEEKS); weeks 27-77 are outside its training range, so its running-total features drift there and late scores are not comparable across weeks.

## Weeks 0-26 (main): launderers who are mules by the end of week 26

|                        | model   | rules   | model_anytime   |
|:-----------------------|:--------|:--------|:----------------|
| flagged                | 740     | 665     | 740             |
| caught                 | 151     | 40      | 151             |
| mules                  | 172     | 172     | 172             |
| recall                 | 0.878   | 0.233   | 0.878           |
| recall_final_label     | 0.786   | 0.208   | 0.786           |
| precision              | 0.204   | 0.060   | 0.204           |
| false_alarm_share      | 0.796   | 0.940   | 0.796           |
| precision_final_label  | 0.204   | 0.060   | 0.204           |
| catch_mean             | 0.467   | 0.117   | 0.469           |
| median_days_from_start | 6       | 8.500   | 6               |
| flagged_before_start   | 3       | 1       | 2               |
| caught_fake            | 139/154 | 33/154  | 139/154         |
| caught_witting         | 4/9     | 4/9     | 4/9             |
| caught_unwitting       | 8/9     | 3/9     | 8/9             |

Ties at the cut line (decided by account id): 0 of 27 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   172.0 |
| both                                |    37.0 |
| model_only                          |   114.0 |
| rules_only                          |     3.0 |
| either                              |   154.0 |
| neither                             |    18.0 |
| median_days_model_earlier_when_both |     3.0 |
| model_first_when_both               |    26.0 |
| rules_first_when_both               |     7.0 |
| median_min_days_earlier_model_only  |    84.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy        | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:--------------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model         | under 30 |      37546 |      25 |       18 |   0.72   |               83 |                0.0022 |      0.1782 |
| model         | 30-49    |      87753 |      93 |       83 |   0.8925 |              329 |                0.0038 |      0.2015 |
| model         | 50+      |      24693 |      54 |       50 |   0.9259 |              177 |                0.0072 |      0.2203 |
| rules         | under 30 |      37546 |      25 |        5 |   0.2    |              137 |                0.0037 |      0.0352 |
| rules         | 30-49    |      87753 |      93 |       24 |   0.2581 |              384 |                0.0044 |      0.0588 |
| rules         | 50+      |      24693 |      54 |       11 |   0.2037 |              104 |                0.0042 |      0.0957 |
| model_anytime | under 30 |      37546 |      25 |       18 |   0.72   |               89 |                0.0024 |      0.1682 |
| model_anytime | 30-49    |      87753 |      93 |       83 |   0.8925 |              321 |                0.0037 |      0.2054 |
| model_anytime | 50+      |      24693 |      54 |       50 |   0.9259 |              179 |                0.0073 |      0.2183 |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy        |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:--------------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model         |            6 |      79192 |      85 |       75 |   0.8824 |       440 |      0.1705 |            0.528 |        0.4942 |        0.5946 |
| model         |            7 |      70800 |      87 |       76 |   0.8736 |       300 |      0.2533 |            0.472 |        0.5058 |        0.4054 |
| rules         |            6 |      79192 |      85 |       14 |   0.1647 |       330 |      0.0424 |            0.528 |        0.4942 |        0.4962 |
| rules         |            7 |      70800 |      87 |       26 |   0.2989 |       335 |      0.0776 |            0.472 |        0.5058 |        0.5038 |
| model_anytime |            6 |      79192 |      85 |       75 |   0.8824 |       440 |      0.1705 |            0.528 |        0.4942 |        0.5946 |
| model_anytime |            7 |      70800 |      87 |       76 |   0.8736 |       300 |      0.2533 |            0.472 |        0.5058 |        0.4054 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   flagged_model_anytime |   catch_model_anytime |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|------------------------:|----------------------:|---------:|--------------:|
|      0 |          149992 |     156 |         2 |               8 |         0     |               8 |         0     |                      19 |                 0.006 |        8 |             0 |
|      2 |          149992 |     157 |         3 |              67 |         0.032 |              67 |         0.006 |                      42 |                 0.025 |       29 |             0 |
|      4 |          149991 |     159 |         5 |             119 |         0.031 |             118 |         0.013 |                      77 |                 0.025 |       22 |             0 |
|      8 |          149990 |     159 |        10 |             212 |         0.05  |             199 |         0.019 |                     147 |                 0.044 |       23 |             0 |
|     12 |          149987 |     162 |        75 |             329 |         0.37  |             304 |         0.074 |                     301 |                 0.377 |       27 |             0 |
|     17 |          149974 |     165 |       165 |             483 |         0.855 |             438 |         0.206 |                     536 |                 0.873 |       24 |             0 |
|     26 |          149962 |     172 |       172 |             740 |         0.878 |             665 |         0.233 |                     740 |                 0.878 |       28 |             0 |

## Weeks 0-77: launderers who are mules by the end of week 77

|                        | model   | rules   |
|:-----------------------|:--------|:--------|
| flagged                | 2165    | 1847    |
| caught                 | 161     | 49      |
| mules                  | 192     | 192     |
| recall                 | 0.839   | 0.255   |
| recall_final_label     | 0.839   | 0.255   |
| precision              | 0.074   | 0.027   |
| false_alarm_share      | 0.926   | 0.973   |
| precision_final_label  | 0.074   | 0.027   |
| catch_mean             | 0.724   | 0.204   |
| median_days_from_start | 6       | 9       |
| flagged_before_start   | 3       | 1       |
| caught_fake            | 141/154 | 36/154  |
| caught_witting         | 8/19    | 6/19    |
| caught_unwitting       | 12/19   | 7/19    |

`model_anytime`: not meaningful (model trained on weeks 0-26).

Ties at the cut line (decided by account id): 0 of 78 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   192.0 |
| both                                |    45.0 |
| model_only                          |   116.0 |
| rules_only                          |     4.0 |
| either                              |   165.0 |
| neither                             |    27.0 |
| median_days_model_earlier_when_both |     4.0 |
| model_first_when_both               |    32.0 |
| rules_first_when_both               |     9.0 |
| median_min_days_earlier_model_only  |   441.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy   | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:---------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model    | under 30 |      37546 |      39 |       23 |   0.5897 |              373 |                0.0099 |      0.0581 |
| model    | 30-49    |      87753 |      99 |       88 |   0.8889 |             1074 |                0.0123 |      0.0757 |
| model    | 50+      |      24693 |      54 |       50 |   0.9259 |              557 |                0.0226 |      0.0824 |
| rules    | under 30 |      37546 |      39 |        8 |   0.2051 |              430 |                0.0115 |      0.0183 |
| rules    | 30-49    |      87753 |      99 |       29 |   0.2929 |             1070 |                0.0122 |      0.0264 |
| rules    | 50+      |      24693 |      54 |       12 |   0.2222 |              298 |                0.0121 |      0.0387 |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy   |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:---------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model    |            6 |      79192 |      95 |       82 |   0.8632 |      1271 |      0.0645 |            0.528 |        0.4948 |        0.5871 |
| model    |            7 |      70800 |      97 |       79 |   0.8144 |       894 |      0.0884 |            0.472 |        0.5052 |        0.4129 |
| rules    |            6 |      79192 |      95 |       19 |   0.2    |       962 |      0.0198 |            0.528 |        0.4948 |        0.5208 |
| rules    |            7 |      70800 |      97 |       30 |   0.3093 |       885 |      0.0339 |            0.472 |        0.5052 |        0.4792 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|---------:|--------------:|
|      0 |          149992 |     156 |         2 |               8 |         0     |               8 |         0     |        8 |             0 |
|      2 |          149992 |     157 |         3 |              67 |         0.032 |              67 |         0.006 |       29 |             0 |
|      4 |          149991 |     159 |         5 |             119 |         0.031 |             118 |         0.013 |       22 |             0 |
|      8 |          149990 |     159 |        10 |             212 |         0.05  |             199 |         0.019 |       23 |             0 |
|     12 |          149987 |     162 |        75 |             329 |         0.37  |             304 |         0.074 |       27 |             0 |
|     17 |          149974 |     165 |       165 |             483 |         0.855 |             438 |         0.206 |       24 |             0 |
|     26 |          149962 |     172 |       172 |             740 |         0.878 |             665 |         0.233 |       28 |             0 |
|     52 |          149958 |     183 |       183 |            1433 |         0.869 |            1243 |         0.246 |       29 |             0 |
|     77 |          149955 |     192 |       192 |            2165 |         0.839 |            1847 |         0.255 |       24 |             0 |

- recall / precision: against mule accounts by the end of the horizon (fake accounts from opening, real customers from their start). recall_final_label / precision_final_label: against launderers at any time in the 18 months (label maturity).
- median_min_days_earlier_model_only: launderers caught by the model but not by the rules within the horizon; days from the model's flag to the end of the horizon, so the model is at least this many days earlier (the count is model_only).
- median_days_from_start: days from laundering start to the first flag, caught launderers only (negative = flagged before it started). A model flag is dated at the end of its week.
- catch_mean: per week the share of that week's mules already flagged, averaged over the weeks.
- Accounts closed by the bank stay in the cohort (caught by the rules); `open_accounts` counts the ones still open at the end of each week.
