# Harness, final test: cohort opened in month(s) 6, 7

Settings: `{"data": "data/sensitivity/fake_age_rule__1", "cohort_months": [6, 7], "horizons": [26, 77], "model": "robust_avg5", "model_params_source": "file", "model_git_commit": "56cfa2a227cf076499654c1d6b943fc8fe2ffe8e", "model_machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "cohort_accounts": 50061, "launderers": 198, "budget_per_horizon": {"26": 277, "77": 725}, "score_source": "model:robust_avg5", "scores_sha256": null, "run_manifest_sha256": "1edfcdbab4f6b2f03a09163792ec73a97c53a2534714e3c2aa9610bb590c8643", "git_commit": "56cfa2a227cf076499654c1d6b943fc8fe2ffe8e", "git_uncommitted_changes": true, "retest_reason": null, "seconds": 24}`

Model vs rules on the same accounts. Each week since opening the model may flag as many accounts as the rules raised alerts on this cohort that week; a flag is permanent. `model_anytime`: a secondary policy, one score threshold over the horizon (on each account's highest score) flagging the same total number of accounts.

- The weekly budget counts the rules' alerts: an account alerted twice counts twice, so the model can flag slightly more distinct accounts than the rules (e.g. 124 vs 119 over weeks 0-26 in the month-5 dry run).
- The model is trained on weeks 0-26 only (models.train WEEKS); weeks 27-77 are outside its training range, so its running-total features drift there and late scores are not comparable across weeks.

## Weeks 0-26 (main): launderers who are mules by the end of week 26

|                        | model   | rules   | model_anytime   |
|:-----------------------|:--------|:--------|:----------------|
| flagged                | 277     | 261     | 277             |
| caught                 | 128     | 47      | 137             |
| mules                  | 163     | 163     | 163             |
| recall                 | 0.785   | 0.288   | 0.840           |
| recall_final_label     | 0.646   | 0.237   | 0.692           |
| precision              | 0.462   | 0.180   | 0.495           |
| false_alarm_share      | 0.538   | 0.820   | 0.505           |
| precision_final_label  | 0.462   | 0.180   | 0.495           |
| catch_mean             | 0.404   | 0.151   | 0.444           |
| median_days_from_start | 7       | 6       | 6               |
| flagged_before_start   | 5       | 0       | 4               |
| caught_fake            | 124/157 | 44/157  | 133/157         |
| caught_witting         | 1/3     | 2/3     | 1/3             |
| caught_unwitting       | 3/3     | 1/3     | 3/3             |

Ties at the cut line (decided by account id): 0 of 27 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   163.0 |
| both                                |    42.0 |
| model_only                          |    86.0 |
| rules_only                          |     5.0 |
| either                              |   133.0 |
| neither                             |    30.0 |
| median_days_model_earlier_when_both |     1.0 |
| model_first_when_both               |    23.0 |
| rules_first_when_both               |    18.0 |
| median_min_days_earlier_model_only  |    84.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy        | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:--------------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model         | under 30 |      12526 |      68 |       53 |   0.7794 |               43 |                0.0035 |      0.5521 |
| model         | 30-49    |      29335 |      77 |       61 |   0.7922 |               87 |                0.003  |      0.4122 |
| model         | 50+      |       8200 |      18 |       14 |   0.7778 |               19 |                0.0023 |      0.4242 |
| rules         | under 30 |      12526 |      68 |       23 |   0.3382 |               52 |                0.0042 |      0.3067 |
| rules         | 30-49    |      29335 |      77 |       19 |   0.2468 |              126 |                0.0043 |      0.131  |
| rules         | 50+      |       8200 |      18 |        5 |   0.2778 |               36 |                0.0044 |      0.122  |
| model_anytime | under 30 |      12526 |      68 |       58 |   0.8529 |               41 |                0.0033 |      0.5859 |
| model_anytime | 30-49    |      29335 |      77 |       64 |   0.8312 |               83 |                0.0028 |      0.4354 |
| model_anytime | 50+      |       8200 |      18 |       15 |   0.8333 |               16 |                0.002  |      0.4839 |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy        |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:--------------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model         |            6 |      26529 |      87 |       69 |   0.7931 |       162 |      0.4259 |           0.5299 |        0.5337 |        0.5848 |
| model         |            7 |      23532 |      76 |       59 |   0.7763 |       115 |      0.513  |           0.4701 |        0.4663 |        0.4152 |
| rules         |            6 |      26529 |      87 |       26 |   0.2989 |       133 |      0.1955 |           0.5299 |        0.5337 |        0.5096 |
| rules         |            7 |      23532 |      76 |       21 |   0.2763 |       128 |      0.1641 |           0.4701 |        0.4663 |        0.4904 |
| model_anytime |            6 |      26529 |      87 |       74 |   0.8506 |       158 |      0.4684 |           0.5299 |        0.5337 |        0.5704 |
| model_anytime |            7 |      23532 |      76 |       63 |   0.8289 |       119 |      0.5294 |           0.4701 |        0.4663 |        0.4296 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   flagged_model_anytime |   catch_model_anytime |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|------------------------:|----------------------:|---------:|--------------:|
|      0 |           50061 |     157 |         0 |               5 |         0     |               5 |         0     |                       4 |                 0     |        5 |             0 |
|      2 |           50061 |     160 |         3 |              21 |         0.012 |              21 |         0.006 |                       8 |                 0.006 |        8 |             0 |
|      4 |           50061 |     161 |         4 |              40 |         0.043 |              39 |         0.006 |                      16 |                 0.019 |       10 |             0 |
|      8 |           50059 |     161 |        13 |              72 |         0.099 |              70 |         0.019 |                      40 |                 0.081 |       13 |             0 |
|     12 |           50053 |     161 |        75 |             118 |         0.335 |             115 |         0.137 |                     102 |                 0.36  |       10 |             0 |
|     17 |           50036 |     161 |       161 |             176 |         0.696 |             171 |         0.273 |                     200 |                 0.82  |       14 |             0 |
|     26 |           50025 |     163 |       163 |             277 |         0.785 |             261 |         0.288 |                     277 |                 0.84  |       12 |             0 |

## Weeks 0-77: launderers who are mules by the end of week 77

|                        | model   | rules   |
|:-----------------------|:--------|:--------|
| flagged                | 725     | 656     |
| caught                 | 152     | 57      |
| mules                  | 198     | 198     |
| recall                 | 0.768   | 0.288   |
| recall_final_label     | 0.768   | 0.288   |
| precision              | 0.210   | 0.087   |
| false_alarm_share      | 0.790   | 0.913   |
| precision_final_label  | 0.210   | 0.087   |
| catch_mean             | 0.650   | 0.240   |
| median_days_from_start | 7       | 6       |
| flagged_before_start   | 5       | 0       |
| caught_fake            | 127/157 | 49/157  |
| caught_witting         | 11/20   | 4/20    |
| caught_unwitting       | 14/21   | 4/21    |

`model_anytime`: not meaningful (model trained on weeks 0-26).

Ties at the cut line (decided by account id): 0 of 78 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   198.0 |
| both                                |    51.0 |
| model_only                          |   101.0 |
| rules_only                          |     6.0 |
| either                              |   158.0 |
| neither                             |    40.0 |
| median_days_model_earlier_when_both |     2.0 |
| model_first_when_both               |    30.0 |
| rules_first_when_both               |    19.0 |
| median_min_days_earlier_model_only  |   434.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy   | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:---------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model    | under 30 |      12526 |      89 |       68 |   0.764  |              248 |                0.0199 |      0.2152 |
| model    | 30-49    |      29335 |      88 |       67 |   0.7614 |              272 |                0.0093 |      0.1976 |
| model    | 50+      |       8200 |      21 |       17 |   0.8095 |               53 |                0.0065 |      0.2429 |
| rules    | under 30 |      12526 |      89 |       27 |   0.3034 |              155 |                0.0125 |      0.1484 |
| rules    | 30-49    |      29335 |      88 |       24 |   0.2727 |              347 |                0.0119 |      0.0647 |
| rules    | 50+      |       8200 |      21 |        6 |   0.2857 |               97 |                0.0119 |      0.0583 |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy   |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:---------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model    |            6 |      26529 |     105 |       87 |   0.8286 |       438 |      0.1986 |           0.5299 |        0.5303 |        0.6041 |
| model    |            7 |      23532 |      93 |       65 |   0.6989 |       287 |      0.2265 |           0.4701 |        0.4697 |        0.3959 |
| rules    |            6 |      26529 |     105 |       32 |   0.3048 |       351 |      0.0912 |           0.5299 |        0.5303 |        0.5351 |
| rules    |            7 |      23532 |      93 |       25 |   0.2688 |       305 |      0.082  |           0.4701 |        0.4697 |        0.4649 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|---------:|--------------:|
|      0 |           50061 |     157 |         0 |               5 |         0     |               5 |         0     |        5 |             0 |
|      2 |           50061 |     160 |         3 |              21 |         0.012 |              21 |         0.006 |        8 |             0 |
|      4 |           50061 |     161 |         4 |              40 |         0.043 |              39 |         0.006 |       10 |             0 |
|      8 |           50059 |     161 |        13 |              72 |         0.099 |              70 |         0.019 |       13 |             0 |
|     12 |           50053 |     161 |        75 |             118 |         0.335 |             115 |         0.137 |       10 |             0 |
|     17 |           50036 |     161 |       161 |             176 |         0.696 |             171 |         0.273 |       14 |             0 |
|     26 |           50025 |     163 |       163 |             277 |         0.785 |             261 |         0.288 |       12 |             0 |
|     52 |           50021 |     177 |       177 |             497 |         0.791 |             455 |         0.294 |       14 |             0 |
|     77 |           50016 |     198 |       198 |             725 |         0.768 |             656 |         0.288 |       10 |             0 |

- recall / precision: against mule accounts by the end of the horizon (fake accounts from opening, real customers from their start). recall_final_label / precision_final_label: against launderers at any time in the 18 months (label maturity).
- median_min_days_earlier_model_only: launderers caught by the model but not by the rules within the horizon; days from the model's flag to the end of the horizon, so the model is at least this many days earlier (the count is model_only).
- median_days_from_start: days from laundering start to the first flag, caught launderers only (negative = flagged before it started). A model flag is dated at the end of its week.
- catch_mean: per week the share of that week's mules already flagged, averaged over the weeks.
- Accounts closed by the bank stay in the cohort (caught by the rules); `open_accounts` counts the ones still open at the end of each week.
