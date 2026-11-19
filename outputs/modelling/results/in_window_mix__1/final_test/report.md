# Harness, final test: cohort opened in month(s) 6, 7

Settings: `{"data": "data/sensitivity/in_window_mix__1", "cohort_months": [6, 7], "horizons": [26, 77], "model": "robust_avg5", "model_params_source": "file", "model_git_commit": "7f2b8e510d8650bd8b5362fdfe8a2bc54a0362e9", "model_machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "cohort_accounts": 50061, "launderers": 164, "budget_per_horizon": {"26": 260, "77": 711}, "score_source": "model:robust_avg5", "scores_sha256": null, "run_manifest_sha256": "cf4e12681fcfb78ba330d0c693597ddc3752b3fbae26a30a7825926471a0135b", "git_commit": "7f2b8e510d8650bd8b5362fdfe8a2bc54a0362e9", "git_uncommitted_changes": true, "retest_reason": null, "seconds": 27}`

Model vs rules on the same accounts. Each week since opening the model may flag as many accounts as the rules raised alerts on this cohort that week; a flag is permanent. `model_anytime`: a secondary policy, one score threshold over the horizon (on each account's highest score) flagging the same total number of accounts.

- The weekly budget counts the rules' alerts: an account alerted twice counts twice, so the model can flag slightly more distinct accounts than the rules (e.g. 124 vs 119 over weeks 0-26 in the month-5 dry run).
- The model is trained on weeks 0-26 only (models.train WEEKS); weeks 27-77 are outside its training range, so its running-total features drift there and late scores are not comparable across weeks.

## Weeks 0-26 (main): launderers who are mules by the end of week 26

|                        | model   | rules   | model_anytime   |
|:-----------------------|:--------|:--------|:----------------|
| flagged                | 260     | 244     | 260             |
| caught                 | 99      | 30      | 106             |
| mules                  | 124     | 124     | 124             |
| recall                 | 0.798   | 0.242   | 0.855           |
| recall_final_label     | 0.604   | 0.183   | 0.646           |
| precision              | 0.381   | 0.123   | 0.408           |
| false_alarm_share      | 0.619   | 0.877   | 0.592           |
| precision_final_label  | 0.381   | 0.123   | 0.408           |
| catch_mean             | 0.410   | 0.119   | 0.451           |
| median_days_from_start | 7       | 9       | 6               |
| flagged_before_start   | 1       | 0       | 1               |
| caught_fake            | 81/103  | 24/103  | 87/103          |
| caught_witting         | 9/11    | 4/11    | 9/11            |
| caught_unwitting       | 9/10    | 2/10    | 10/10           |

Ties at the cut line (decided by account id): 0 of 27 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   124.0 |
| both                                |    24.0 |
| model_only                          |    75.0 |
| rules_only                          |     6.0 |
| either                              |   105.0 |
| neither                             |    19.0 |
| median_days_model_earlier_when_both |     2.0 |
| model_first_when_both               |    16.0 |
| rules_first_when_both               |     4.0 |
| median_min_days_earlier_model_only  |    84.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy        | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:--------------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model         | under 30 |      12526 |      30 |       25 |   0.8333 |               37 |                0.003  |      0.4032 |
| model         | 30-49    |      29335 |      66 |       54 |   0.8182 |               82 |                0.0028 |      0.3971 |
| model         | 50+      |       8200 |      28 |       20 |   0.7143 |               42 |                0.0051 |      0.3226 |
| rules         | under 30 |      12526 |      30 |        7 |   0.2333 |               52 |                0.0042 |      0.1186 |
| rules         | 30-49    |      29335 |      66 |       20 |   0.303  |              126 |                0.0043 |      0.137  |
| rules         | 50+      |       8200 |      28 |        3 |   0.1071 |               36 |                0.0044 |      0.0769 |
| model_anytime | under 30 |      12526 |      30 |       27 |   0.9    |               33 |                0.0026 |      0.45   |
| model_anytime | 30-49    |      29335 |      66 |       55 |   0.8333 |               82 |                0.0028 |      0.4015 |
| model_anytime | 50+      |       8200 |      28 |       24 |   0.8571 |               39 |                0.0048 |      0.381  |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy        |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:--------------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model         |            6 |      26529 |      66 |       56 |   0.8485 |       171 |      0.3275 |           0.5299 |        0.5323 |        0.6577 |
| model         |            7 |      23532 |      58 |       43 |   0.7414 |        89 |      0.4831 |           0.4701 |        0.4677 |        0.3423 |
| rules         |            6 |      26529 |      66 |       12 |   0.1818 |       119 |      0.1008 |           0.5299 |        0.5323 |        0.4877 |
| rules         |            7 |      23532 |      58 |       18 |   0.3103 |       125 |      0.144  |           0.4701 |        0.4677 |        0.5123 |
| model_anytime |            6 |      26529 |      66 |       60 |   0.9091 |       160 |      0.375  |           0.5299 |        0.5323 |        0.6154 |
| model_anytime |            7 |      23532 |      58 |       46 |   0.7931 |       100 |      0.46   |           0.4701 |        0.4677 |        0.3846 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   flagged_model_anytime |   catch_model_anytime |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|------------------------:|----------------------:|---------:|--------------:|
|      0 |           50061 |     103 |         0 |               5 |         0     |               5 |         0     |                       4 |                 0     |        5 |             0 |
|      2 |           50061 |     104 |         1 |              21 |         0.01  |              21 |         0.01  |                       7 |                 0.01  |        8 |             0 |
|      4 |           50061 |     104 |         1 |              40 |         0.019 |              39 |         0.01  |                      18 |                 0.019 |       10 |             0 |
|      8 |           50060 |     107 |         7 |              71 |         0.056 |              69 |         0.019 |                      40 |                 0.056 |       12 |             0 |
|     12 |           50054 |     111 |        58 |             107 |         0.342 |             104 |         0.099 |                      99 |                 0.405 |        6 |             0 |
|     17 |           50044 |     115 |       115 |             156 |         0.713 |             151 |         0.209 |                     185 |                 0.817 |        9 |             0 |
|     26 |           50038 |     124 |       124 |             260 |         0.798 |             244 |         0.242 |                     260 |                 0.855 |       14 |             0 |

## Weeks 0-77: launderers who are mules by the end of week 77

|                        | model   | rules   |
|:-----------------------|:--------|:--------|
| flagged                | 711     | 642     |
| caught                 | 136     | 43      |
| mules                  | 164     | 164     |
| recall                 | 0.829   | 0.262   |
| recall_final_label     | 0.829   | 0.262   |
| precision              | 0.191   | 0.067   |
| false_alarm_share      | 0.809   | 0.933   |
| precision_final_label  | 0.191   | 0.067   |
| catch_mean             | 0.678   | 0.214   |
| median_days_from_start | 7       | 9       |
| flagged_before_start   | 1       | 0       |
| caught_fake            | 88/103  | 28/103  |
| caught_witting         | 27/34   | 8/34    |
| caught_unwitting       | 21/27   | 7/27    |

`model_anytime`: not meaningful (model trained on weeks 0-26).

Ties at the cut line (decided by account id): 0 of 78 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   164.0 |
| both                                |    37.0 |
| model_only                          |    99.0 |
| rules_only                          |     6.0 |
| either                              |   142.0 |
| neither                             |    22.0 |
| median_days_model_earlier_when_both |     2.0 |
| model_first_when_both               |    25.0 |
| rules_first_when_both               |     7.0 |
| median_min_days_earlier_model_only  |   427.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy   | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:---------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model    | under 30 |      12526 |      53 |       45 |   0.8491 |              164 |                0.0131 |      0.2153 |
| model    | 30-49    |      29335 |      81 |       68 |   0.8395 |              278 |                0.0095 |      0.1965 |
| model    | 50+      |       8200 |      30 |       23 |   0.7667 |              133 |                0.0163 |      0.1474 |
| rules    | under 30 |      12526 |      53 |       14 |   0.2642 |              155 |                0.0124 |      0.0828 |
| rules    | 30-49    |      29335 |      81 |       23 |   0.284  |              347 |                0.0119 |      0.0622 |
| rules    | 50+      |       8200 |      30 |        6 |   0.2    |               97 |                0.0119 |      0.0583 |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy   |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:---------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model    |            6 |      26529 |      91 |       75 |   0.8242 |       453 |      0.1656 |           0.5299 |        0.5549 |        0.6371 |
| model    |            7 |      23532 |      73 |       61 |   0.8356 |       258 |      0.2364 |           0.4701 |        0.4451 |        0.3629 |
| rules    |            6 |      26529 |      91 |       21 |   0.2308 |       340 |      0.0618 |           0.5299 |        0.5549 |        0.5296 |
| rules    |            7 |      23532 |      73 |       22 |   0.3014 |       302 |      0.0728 |           0.4701 |        0.4451 |        0.4704 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|---------:|--------------:|
|      0 |           50061 |     103 |         0 |               5 |         0     |               5 |         0     |        5 |             0 |
|      2 |           50061 |     104 |         1 |              21 |         0.01  |              21 |         0.01  |        8 |             0 |
|      4 |           50061 |     104 |         1 |              40 |         0.019 |              39 |         0.01  |       10 |             0 |
|      8 |           50060 |     107 |         7 |              71 |         0.056 |              69 |         0.019 |       12 |             0 |
|     12 |           50054 |     111 |        58 |             107 |         0.342 |             104 |         0.099 |        6 |             0 |
|     17 |           50044 |     115 |       115 |             156 |         0.713 |             151 |         0.209 |        9 |             0 |
|     26 |           50038 |     124 |       124 |             260 |         0.798 |             244 |         0.242 |       14 |             0 |
|     52 |           50027 |     143 |       143 |             484 |         0.818 |             442 |         0.273 |       14 |             0 |
|     77 |           50024 |     164 |       164 |             711 |         0.829 |             642 |         0.262 |       10 |             0 |

- recall / precision: against mule accounts by the end of the horizon (fake accounts from opening, real customers from their start). recall_final_label / precision_final_label: against launderers at any time in the 18 months (label maturity).
- median_min_days_earlier_model_only: launderers caught by the model but not by the rules within the horizon; days from the model's flag to the end of the horizon, so the model is at least this many days earlier (the count is model_only).
- median_days_from_start: days from laundering start to the first flag, caught launderers only (negative = flagged before it started). A model flag is dated at the end of its week.
- catch_mean: per week the share of that week's mules already flagged, averaged over the weeks.
- Accounts closed by the bank stay in the cohort (caught by the rules); `open_accounts` counts the ones still open at the end of each week.
