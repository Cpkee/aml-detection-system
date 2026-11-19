# Harness, final test: cohort opened in month(s) 6, 7

Settings: `{"data": "data/sensitivity/seed__44", "cohort_months": [6, 7], "horizons": [26, 77], "model": "robust_avg5", "model_params_source": "file", "model_git_commit": "8cd3539420ab132d0839083945efc131126b2deb", "model_machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "cohort_accounts": 49737, "launderers": 176, "budget_per_horizon": {"26": 241, "77": 678}, "score_source": "model:robust_avg5", "scores_sha256": null, "run_manifest_sha256": "854bbb57b1eaf9302d090f05a0310ee35e0d632451653625537bd2d0ddaf4c30", "git_commit": "8cd3539420ab132d0839083945efc131126b2deb", "git_uncommitted_changes": true, "retest_reason": null, "seconds": 22}`

Model vs rules on the same accounts. Each week since opening the model may flag as many accounts as the rules raised alerts on this cohort that week; a flag is permanent. `model_anytime`: a secondary policy, one score threshold over the horizon (on each account's highest score) flagging the same total number of accounts.

- The weekly budget counts the rules' alerts: an account alerted twice counts twice, so the model can flag slightly more distinct accounts than the rules (e.g. 124 vs 119 over weeks 0-26 in the month-5 dry run).
- The model is trained on weeks 0-26 only (models.train WEEKS); weeks 27-77 are outside its training range, so its running-total features drift there and late scores are not comparable across weeks.

## Weeks 0-26 (main): launderers who are mules by the end of week 26

|                        | model   | rules   | model_anytime   |
|:-----------------------|:--------|:--------|:----------------|
| flagged                | 241     | 232     | 241             |
| caught                 | 114     | 35      | 128             |
| mules                  | 145     | 145     | 145             |
| recall                 | 0.786   | 0.241   | 0.883           |
| recall_final_label     | 0.648   | 0.199   | 0.727           |
| precision              | 0.473   | 0.151   | 0.531           |
| false_alarm_share      | 0.527   | 0.849   | 0.469           |
| precision_final_label  | 0.473   | 0.151   | 0.531           |
| catch_mean             | 0.394   | 0.118   | 0.474           |
| median_days_from_start | 9       | 9       | 6               |
| flagged_before_start   | 0       | 0       | 1               |
| caught_fake            | 104/132 | 32/132  | 118/132         |
| caught_witting         | 8/10    | 2/10    | 7/10            |
| caught_unwitting       | 2/3     | 1/3     | 3/3             |

Ties at the cut line (decided by account id): 0 of 27 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   145.0 |
| both                                |    35.0 |
| model_only                          |    79.0 |
| rules_only                          |     0.0 |
| either                              |   114.0 |
| neither                             |    31.0 |
| median_days_model_earlier_when_both |     1.0 |
| model_first_when_both               |    19.0 |
| rules_first_when_both               |    14.0 |
| median_min_days_earlier_model_only  |    84.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy        | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:--------------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model         | under 30 |      12477 |      23 |       16 |   0.6957 |               11 |                0.0009 |      0.5926 |
| model         | 30-49    |      29023 |      72 |       59 |   0.8194 |               72 |                0.0025 |      0.4504 |
| model         | 50+      |       8237 |      50 |       39 |   0.78   |               44 |                0.0054 |      0.4699 |
| rules         | under 30 |      12477 |      23 |        4 |   0.1739 |               42 |                0.0034 |      0.087  |
| rules         | 30-49    |      29023 |      72 |       15 |   0.2083 |              120 |                0.0041 |      0.1111 |
| rules         | 50+      |       8237 |      50 |       16 |   0.32   |               35 |                0.0043 |      0.3137 |
| model_anytime | under 30 |      12477 |      23 |       19 |   0.8261 |               11 |                0.0009 |      0.6333 |
| model_anytime | 30-49    |      29023 |      72 |       66 |   0.9167 |               64 |                0.0022 |      0.5077 |
| model_anytime | 50+      |       8237 |      50 |       43 |   0.86   |               38 |                0.0046 |      0.5309 |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy        |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:--------------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model         |            6 |      26281 |      69 |       63 |   0.913  |       145 |      0.4345 |           0.5284 |        0.4759 |        0.6017 |
| model         |            7 |      23456 |      76 |       51 |   0.6711 |        96 |      0.5312 |           0.4716 |        0.5241 |        0.3983 |
| rules         |            6 |      26281 |      69 |       24 |   0.3478 |       121 |      0.1983 |           0.5284 |        0.4759 |        0.5216 |
| rules         |            7 |      23456 |      76 |       11 |   0.1447 |       111 |      0.0991 |           0.4716 |        0.5241 |        0.4784 |
| model_anytime |            6 |      26281 |      69 |       65 |   0.942  |       137 |      0.4745 |           0.5284 |        0.4759 |        0.5685 |
| model_anytime |            7 |      23456 |      76 |       63 |   0.8289 |       104 |      0.6058 |           0.4716 |        0.5241 |        0.4315 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   flagged_model_anytime |   catch_model_anytime |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|------------------------:|----------------------:|---------:|--------------:|
|      0 |           49737 |     132 |         0 |               1 |         0     |               1 |         0     |                       1 |                 0     |        1 |             0 |
|      2 |           49737 |     133 |         1 |              20 |         0.008 |              20 |         0     |                       5 |                 0.008 |       13 |             0 |
|      4 |           49737 |     135 |         3 |              28 |         0.007 |              28 |         0.007 |                       9 |                 0.007 |        4 |             0 |
|      8 |           49736 |     138 |        10 |              61 |         0.043 |              60 |         0.014 |                      28 |                 0.043 |       12 |             0 |
|     12 |           49734 |     138 |        79 |             103 |         0.348 |             100 |         0.072 |                     106 |                 0.457 |       12 |             0 |
|     17 |           49720 |     141 |       141 |             157 |         0.695 |             153 |         0.206 |                     189 |                 0.858 |       13 |             0 |
|     26 |           49710 |     145 |       145 |             241 |         0.786 |             232 |         0.241 |                     241 |                 0.883 |       11 |             0 |

## Weeks 0-77: launderers who are mules by the end of week 77

|                        | model   | rules   |
|:-----------------------|:--------|:--------|
| flagged                | 678     | 630     |
| caught                 | 136     | 46      |
| mules                  | 176     | 176     |
| recall                 | 0.773   | 0.261   |
| recall_final_label     | 0.773   | 0.261   |
| precision              | 0.201   | 0.073   |
| false_alarm_share      | 0.799   | 0.927   |
| precision_final_label  | 0.201   | 0.073   |
| catch_mean             | 0.644   | 0.208   |
| median_days_from_start | 10      | 10      |
| flagged_before_start   | 0       | 0       |
| caught_fake            | 110/132 | 37/132  |
| caught_witting         | 15/24   | 5/24    |
| caught_unwitting       | 11/20   | 4/20    |

`model_anytime`: not meaningful (model trained on weeks 0-26).

Ties at the cut line (decided by account id): 0 of 78 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   176.0 |
| both                                |    45.0 |
| model_only                          |    91.0 |
| rules_only                          |     1.0 |
| either                              |   137.0 |
| neither                             |    39.0 |
| median_days_model_earlier_when_both |     1.0 |
| model_first_when_both               |    24.0 |
| rules_first_when_both               |    18.0 |
| median_min_days_earlier_model_only  |   427.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy   | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:---------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model    | under 30 |      12477 |      39 |       28 |   0.7179 |               81 |                0.0065 |      0.2569 |
| model    | 30-49    |      29023 |      86 |       66 |   0.7674 |              287 |                0.0099 |      0.187  |
| model    | 50+      |       8237 |      51 |       42 |   0.8235 |              174 |                0.0213 |      0.1944 |
| rules    | under 30 |      12477 |      39 |        7 |   0.1795 |              129 |                0.0104 |      0.0515 |
| rules    | 30-49    |      29023 |      86 |       21 |   0.2442 |              351 |                0.0121 |      0.0565 |
| rules    | 50+      |       8237 |      51 |       18 |   0.3529 |              104 |                0.0127 |      0.1475 |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy   |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:---------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model    |            6 |      26281 |      87 |       72 |   0.8276 |       415 |      0.1735 |           0.5284 |        0.4943 |        0.6121 |
| model    |            7 |      23456 |      89 |       64 |   0.7191 |       263 |      0.2433 |           0.4716 |        0.5057 |        0.3879 |
| rules    |            6 |      26281 |      87 |       28 |   0.3218 |       317 |      0.0883 |           0.5284 |        0.4943 |        0.5032 |
| rules    |            7 |      23456 |      89 |       18 |   0.2022 |       313 |      0.0575 |           0.4716 |        0.5057 |        0.4968 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|---------:|--------------:|
|      0 |           49737 |     132 |         0 |               1 |         0     |               1 |         0     |        1 |             0 |
|      2 |           49737 |     133 |         1 |              20 |         0.008 |              20 |         0     |       13 |             0 |
|      4 |           49737 |     135 |         3 |              28 |         0.007 |              28 |         0.007 |        4 |             0 |
|      8 |           49736 |     138 |        10 |              61 |         0.043 |              60 |         0.014 |       12 |             0 |
|     12 |           49734 |     138 |        79 |             103 |         0.348 |             100 |         0.072 |       12 |             0 |
|     17 |           49720 |     141 |       141 |             157 |         0.695 |             153 |         0.206 |       13 |             0 |
|     26 |           49710 |     145 |       145 |             241 |         0.786 |             232 |         0.241 |       11 |             0 |
|     52 |           49704 |     163 |       163 |             455 |         0.761 |             428 |         0.264 |        5 |             0 |
|     77 |           49701 |     176 |       176 |             678 |         0.773 |             630 |         0.261 |       12 |             0 |

- recall / precision: against mule accounts by the end of the horizon (fake accounts from opening, real customers from their start). recall_final_label / precision_final_label: against launderers at any time in the 18 months (label maturity).
- median_min_days_earlier_model_only: launderers caught by the model but not by the rules within the horizon; days from the model's flag to the end of the horizon, so the model is at least this many days earlier (the count is model_only).
- median_days_from_start: days from laundering start to the first flag, caught launderers only (negative = flagged before it started). A model flag is dated at the end of its week.
- catch_mean: per week the share of that week's mules already flagged, averaged over the weeks.
- Accounts closed by the bank stay in the cohort (caught by the rules); `open_accounts` counts the ones still open at the end of each week.
