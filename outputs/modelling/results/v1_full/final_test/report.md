# Harness, final test: cohort opened in month(s) 6, 7

Settings: `{"data": "data/v1_full", "cohort_months": [6, 7], "horizons": [26, 77], "model": "frozen_tuned_avg5", "model_params_source": "file", "model_git_commit": "bc707f30c22dd8f662c5b83584f5e54c85dc7819", "model_machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "cohort_accounts": 50061, "launderers": 180, "budget_per_horizon": {"26": 280, "77": 725}, "score_source": "model:frozen_tuned_avg5", "scores_sha256": null, "run_manifest_sha256": "4ce1c4fb593a8ae5f40e9acb082f1969655095c5a4977dc81f58c9026c62d7ba", "git_commit": "9e748c851ffb5d2082e8d68217247b3b57c1daf9", "git_uncommitted_changes": false, "seconds": 24}`

Model vs rules on the same accounts. Each week since opening the model may flag as many accounts as the rules raised alerts on this cohort that week; a flag is permanent. `model_anytime`: a secondary policy, one score threshold over the horizon (on each account's highest score) flagging the same total number of accounts.

- The weekly budget counts the rules' alerts: an account alerted twice counts twice, so the model can flag slightly more distinct accounts than the rules (e.g. 124 vs 119 over weeks 0-26 in the month-5 dry run).
- The model is trained on weeks 0-26 only (models.train WEEKS); weeks 27-77 are outside its training range, so its running-total features drift there and late scores are not comparable across weeks.

## Weeks 0-26 (main): launderers who are mules by the end of week 26

|                        | model   | rules   | model_anytime   |
|:-----------------------|:--------|:--------|:----------------|
| flagged                | 280     | 264     | 280             |
| caught                 | 120     | 50      | 139             |
| mules                  | 163     | 163     | 163             |
| recall                 | 0.736   | 0.307   | 0.853           |
| recall_final_label     | 0.667   | 0.278   | 0.772           |
| precision              | 0.429   | 0.189   | 0.496           |
| false_alarm_share      | 0.571   | 0.811   | 0.504           |
| precision_final_label  | 0.429   | 0.189   | 0.496           |
| catch_mean             | 0.379   | 0.145   | 0.449           |
| median_days_from_start | 8       | 9       | 6               |
| flagged_before_start   | 2       | 0       | 2               |
| caught_fake            | 109/147 | 46/147  | 128/147         |
| caught_witting         | 8/11    | 3/11    | 8/11            |
| caught_unwitting       | 3/5     | 1/5     | 3/5             |

Ties at the cut line (decided by account id): 0 of 27 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   163.0 |
| both                                |    43.0 |
| model_only                          |    77.0 |
| rules_only                          |     7.0 |
| either                              |   127.0 |
| neither                             |    36.0 |
| median_days_model_earlier_when_both |     2.0 |
| model_first_when_both               |    26.0 |
| rules_first_when_both               |    13.0 |
| median_min_days_earlier_model_only  |    91.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy        | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:--------------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model         | under 30 |      12526 |      26 |       21 |   0.8077 |               24 |                0.0019 |      0.4667 |
| model         | 30-49    |      29335 |      80 |       62 |   0.775  |               86 |                0.0029 |      0.4189 |
| model         | 50+      |       8200 |      57 |       37 |   0.6491 |               50 |                0.0061 |      0.4253 |
| rules         | under 30 |      12526 |      26 |        8 |   0.3077 |               52 |                0.0042 |      0.1333 |
| rules         | 30-49    |      29335 |      80 |       25 |   0.3125 |              126 |                0.0043 |      0.1656 |
| rules         | 50+      |       8200 |      57 |       17 |   0.2982 |               36 |                0.0044 |      0.3208 |
| model_anytime | under 30 |      12526 |      26 |       23 |   0.8846 |               26 |                0.0021 |      0.4694 |
| model_anytime | 30-49    |      29335 |      80 |       70 |   0.875  |               77 |                0.0026 |      0.4762 |
| model_anytime | 50+      |       8200 |      57 |       46 |   0.807  |               38 |                0.0047 |      0.5476 |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy        |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:--------------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model         |            6 |      26529 |      93 |       72 |   0.7742 |       176 |      0.4091 |           0.5299 |        0.5706 |        0.6286 |
| model         |            7 |      23532 |      70 |       48 |   0.6857 |       104 |      0.4615 |           0.4701 |        0.4294 |        0.3714 |
| rules         |            6 |      26529 |      93 |       30 |   0.3226 |       137 |      0.219  |           0.5299 |        0.5706 |        0.5189 |
| rules         |            7 |      23532 |      70 |       20 |   0.2857 |       127 |      0.1575 |           0.4701 |        0.4294 |        0.4811 |
| model_anytime |            6 |      26529 |      93 |       79 |   0.8495 |       165 |      0.4788 |           0.5299 |        0.5706 |        0.5893 |
| model_anytime |            7 |      23532 |      70 |       60 |   0.8571 |       115 |      0.5217 |           0.4701 |        0.4294 |        0.4107 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   flagged_model_anytime |   catch_model_anytime |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|------------------------:|----------------------:|---------:|--------------:|
|      0 |           50061 |     147 |         0 |               5 |         0     |               5 |         0     |                       0 |                 0     |        5 |             0 |
|      2 |           50061 |     149 |         2 |              20 |         0.007 |              20 |         0     |                       0 |                 0     |        7 |             0 |
|      4 |           50061 |     150 |         3 |              39 |         0.013 |              38 |         0     |                       6 |                 0.007 |       10 |             0 |
|      8 |           50061 |     151 |        13 |              70 |         0.06  |              68 |         0.007 |                      19 |                 0.046 |       12 |             0 |
|     12 |           50056 |     155 |        77 |             111 |         0.316 |             108 |         0.097 |                      87 |                 0.381 |        7 |             0 |
|     17 |           50038 |     158 |       158 |             174 |         0.671 |             169 |         0.266 |                     184 |                 0.797 |       14 |             0 |
|     26 |           50019 |     163 |       163 |             280 |         0.736 |             264 |         0.307 |                     280 |                 0.853 |       12 |             0 |

## Weeks 0-77: launderers who are mules by the end of week 77

|                        | model   | rules   |
|:-----------------------|:--------|:--------|
| flagged                | 725     | 656     |
| caught                 | 138     | 59      |
| mules                  | 180     | 180     |
| recall                 | 0.767   | 0.328   |
| recall_final_label     | 0.767   | 0.328   |
| precision              | 0.190   | 0.090   |
| false_alarm_share      | 0.810   | 0.910   |
| precision_final_label  | 0.190   | 0.090   |
| catch_mean             | 0.626   | 0.257   |
| median_days_from_start | 8.500   | 9       |
| flagged_before_start   | 3       | 0       |
| caught_fake            | 115/147 | 52/147  |
| caught_witting         | 13/20   | 5/20    |
| caught_unwitting       | 10/13   | 2/13    |

`model_anytime`: not meaningful (model trained on weeks 0-26).

Ties at the cut line (decided by account id): 0 of 78 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   180.0 |
| both                                |    51.0 |
| model_only                          |    87.0 |
| rules_only                          |     8.0 |
| either                              |   146.0 |
| neither                             |    34.0 |
| median_days_model_earlier_when_both |     3.0 |
| model_first_when_both               |    33.0 |
| rules_first_when_both               |    14.0 |
| median_min_days_earlier_model_only  |   441.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy   | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:---------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model    | under 30 |      12526 |      35 |       29 |   0.8286 |              124 |                0.0099 |      0.1895 |
| model    | 30-49    |      29335 |      86 |       66 |   0.7674 |              306 |                0.0105 |      0.1774 |
| model    | 50+      |       8200 |      59 |       43 |   0.7288 |              157 |                0.0193 |      0.215  |
| rules    | under 30 |      12526 |      35 |        8 |   0.2286 |              155 |                0.0124 |      0.0491 |
| rules    | 30-49    |      29335 |      86 |       29 |   0.3372 |              347 |                0.0119 |      0.0771 |
| rules    | 50+      |       8200 |      59 |       22 |   0.3729 |               95 |                0.0117 |      0.188  |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy   |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:---------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model    |            6 |      26529 |     103 |       85 |   0.8252 |       442 |      0.1923 |           0.5299 |        0.5722 |        0.6097 |
| model    |            7 |      23532 |      77 |       53 |   0.6883 |       283 |      0.1873 |           0.4701 |        0.4278 |        0.3903 |
| rules    |            6 |      26529 |     103 |       37 |   0.3592 |       355 |      0.1042 |           0.5299 |        0.5722 |        0.5412 |
| rules    |            7 |      23532 |      77 |       22 |   0.2857 |       301 |      0.0731 |           0.4701 |        0.4278 |        0.4588 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|---------:|--------------:|
|      0 |           50061 |     147 |         0 |               5 |         0     |               5 |         0     |        5 |             0 |
|      2 |           50061 |     149 |         2 |              20 |         0.007 |              20 |         0     |        7 |             0 |
|      4 |           50061 |     150 |         3 |              39 |         0.013 |              38 |         0     |       10 |             0 |
|      8 |           50061 |     151 |        13 |              70 |         0.06  |              68 |         0.007 |       12 |             0 |
|     12 |           50056 |     155 |        77 |             111 |         0.316 |             108 |         0.097 |        7 |             0 |
|     17 |           50038 |     158 |       158 |             174 |         0.671 |             169 |         0.266 |       14 |             0 |
|     26 |           50019 |     163 |       163 |             280 |         0.736 |             264 |         0.307 |       12 |             0 |
|     52 |           50018 |     169 |       169 |             500 |         0.763 |             458 |         0.325 |       14 |             0 |
|     77 |           50013 |     180 |       180 |             725 |         0.767 |             656 |         0.328 |       10 |             0 |

- recall / precision: against mule accounts by the end of the horizon (fake accounts from opening, real customers from their start). recall_final_label / precision_final_label: against launderers at any time in the 18 months (label maturity).
- median_min_days_earlier_model_only: launderers caught by the model but not by the rules within the horizon; days from the model's flag to the end of the horizon, so the model is at least this many days earlier (the count is model_only).
- median_days_from_start: days from laundering start to the first flag, caught launderers only (negative = flagged before it started). A model flag is dated at the end of its week.
- catch_mean: per week the share of that week's mules already flagged, averaged over the weeks.
- Accounts closed by the bank stay in the cohort (caught by the rules); `open_accounts` counts the ones still open at the end of each week.
