# Harness, final test: cohort opened in month(s) 6, 7

Settings: `{"data": "data/sensitivity/fake_start_days__2", "cohort_months": [6, 7], "horizons": [26, 77], "model": "robust_avg5", "model_params_source": "file", "model_git_commit": "56cfa2a227cf076499654c1d6b943fc8fe2ffe8e", "model_machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "cohort_accounts": 50061, "launderers": 180, "budget_per_horizon": {"26": 260, "77": 722}, "score_source": "model:robust_avg5", "scores_sha256": null, "run_manifest_sha256": "619ef05ea98ac4f5499dd11ed7acf9e55ccaf97b98cfe26bb718ccb94e6fd9b3", "git_commit": "56cfa2a227cf076499654c1d6b943fc8fe2ffe8e", "git_uncommitted_changes": true, "retest_reason": null, "seconds": 23}`

Model vs rules on the same accounts. Each week since opening the model may flag as many accounts as the rules raised alerts on this cohort that week; a flag is permanent. `model_anytime`: a secondary policy, one score threshold over the horizon (on each account's highest score) flagging the same total number of accounts.

- The weekly budget counts the rules' alerts: an account alerted twice counts twice, so the model can flag slightly more distinct accounts than the rules (e.g. 124 vs 119 over weeks 0-26 in the month-5 dry run).
- The model is trained on weeks 0-26 only (models.train WEEKS); weeks 27-77 are outside its training range, so its running-total features drift there and late scores are not comparable across weeks.

## Weeks 0-26 (main): launderers who are mules by the end of week 26

|                        | model   | rules   | model_anytime   |
|:-----------------------|:--------|:--------|:----------------|
| flagged                | 260     | 244     | 260             |
| caught                 | 91      | 30      | 92              |
| mules                  | 163     | 163     | 163             |
| recall                 | 0.558   | 0.184   | 0.564           |
| recall_final_label     | 0.506   | 0.167   | 0.511           |
| precision              | 0.350   | 0.123   | 0.354           |
| false_alarm_share      | 0.650   | 0.877   | 0.646           |
| precision_final_label  | 0.350   | 0.123   | 0.354           |
| catch_mean             | 0.133   | 0.031   | 0.157           |
| median_days_from_start | 4       | 6       | 4               |
| flagged_before_start   | 13      | 0       | 13              |
| caught_fake            | 78/147  | 24/147  | 79/147          |
| caught_witting         | 10/11   | 4/11    | 10/11           |
| caught_unwitting       | 3/5     | 2/5     | 3/5             |

Ties at the cut line (decided by account id): 0 of 27 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   163.0 |
| both                                |    29.0 |
| model_only                          |    62.0 |
| rules_only                          |     1.0 |
| either                              |    92.0 |
| neither                             |    71.0 |
| median_days_model_earlier_when_both |     1.0 |
| model_first_when_both               |    16.0 |
| rules_first_when_both               |     9.0 |
| median_min_days_earlier_model_only  |    21.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy        | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:--------------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model         | under 30 |      12526 |      26 |       15 |   0.5769 |               21 |                0.0017 |      0.4167 |
| model         | 30-49    |      29335 |      80 |       44 |   0.55   |               81 |                0.0028 |      0.352  |
| model         | 50+      |       8200 |      57 |       32 |   0.5614 |               67 |                0.0082 |      0.3232 |
| rules         | under 30 |      12526 |      26 |        4 |   0.1538 |               52 |                0.0042 |      0.0714 |
| rules         | 30-49    |      29335 |      80 |       14 |   0.175  |              126 |                0.0043 |      0.1    |
| rules         | 50+      |       8200 |      57 |       12 |   0.2105 |               36 |                0.0044 |      0.25   |
| model_anytime | under 30 |      12526 |      26 |       15 |   0.5769 |               20 |                0.0016 |      0.4286 |
| model_anytime | 30-49    |      29335 |      80 |       43 |   0.5375 |               80 |                0.0027 |      0.3496 |
| model_anytime | 50+      |       8200 |      57 |       34 |   0.5965 |               68 |                0.0084 |      0.3333 |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy        |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:--------------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model         |            6 |      26529 |      93 |       52 |   0.5591 |       168 |      0.3095 |           0.5299 |        0.5706 |        0.6462 |
| model         |            7 |      23532 |      70 |       39 |   0.5571 |        92 |      0.4239 |           0.4701 |        0.4294 |        0.3538 |
| rules         |            6 |      26529 |      93 |       17 |   0.1828 |       124 |      0.1371 |           0.5299 |        0.5706 |        0.5082 |
| rules         |            7 |      23532 |      70 |       13 |   0.1857 |       120 |      0.1083 |           0.4701 |        0.4294 |        0.4918 |
| model_anytime |            6 |      26529 |      93 |       52 |   0.5591 |       169 |      0.3077 |           0.5299 |        0.5706 |        0.65   |
| model_anytime |            7 |      23532 |      70 |       40 |   0.5714 |        91 |      0.4396 |           0.4701 |        0.4294 |        0.35   |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   flagged_model_anytime |   catch_model_anytime |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|------------------------:|----------------------:|---------:|--------------:|
|      0 |           50061 |     147 |         0 |               5 |         0     |               5 |         0     |                      72 |                 0.061 |        5 |             0 |
|      2 |           50061 |     149 |         2 |              20 |         0.007 |              20 |         0     |                      85 |                 0.067 |        7 |             0 |
|      4 |           50061 |     150 |         3 |              39 |         0.04  |              38 |         0     |                      99 |                 0.08  |       10 |             0 |
|      8 |           50061 |     151 |         4 |              69 |         0.053 |              67 |         0     |                     121 |                 0.086 |       12 |             0 |
|     12 |           50060 |     155 |         8 |              97 |         0.084 |              94 |         0.006 |                     136 |                 0.103 |        5 |             0 |
|     17 |           50060 |     158 |        11 |             134 |         0.108 |             129 |         0.013 |                     154 |                 0.12  |        8 |             0 |
|     26 |           50043 |     163 |       111 |             260 |         0.558 |             244 |         0.184 |                     260 |                 0.564 |       15 |             0 |

## Weeks 0-77: launderers who are mules by the end of week 77

|                        | model   | rules   |
|:-----------------------|:--------|:--------|
| flagged                | 722     | 653     |
| caught                 | 154     | 56      |
| mules                  | 180     | 180     |
| recall                 | 0.856   | 0.311   |
| recall_final_label     | 0.856   | 0.311   |
| precision              | 0.213   | 0.086   |
| false_alarm_share      | 0.787   | 0.914   |
| precision_final_label  | 0.213   | 0.086   |
| catch_mean             | 0.601   | 0.213   |
| median_days_from_start | 6       | 6       |
| flagged_before_start   | 13      | 0       |
| caught_fake            | 128/147 | 48/147  |
| caught_witting         | 15/20   | 5/20    |
| caught_unwitting       | 11/13   | 3/13    |

`model_anytime`: not meaningful (model trained on weeks 0-26).

Ties at the cut line (decided by account id): 0 of 78 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   180.0 |
| both                                |    53.0 |
| model_only                          |   101.0 |
| rules_only                          |     3.0 |
| either                              |   157.0 |
| neither                             |    23.0 |
| median_days_model_earlier_when_both |     2.0 |
| model_first_when_both               |    35.0 |
| rules_first_when_both               |    13.0 |
| median_min_days_earlier_model_only  |   350.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy   | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:---------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model    | under 30 |      12526 |      35 |       29 |   0.8286 |              102 |                0.0082 |      0.2214 |
| model    | 30-49    |      29335 |      86 |       73 |   0.8488 |              289 |                0.0099 |      0.2017 |
| model    | 50+      |       8200 |      59 |       52 |   0.8814 |              177 |                0.0217 |      0.2271 |
| rules    | under 30 |      12526 |      35 |        5 |   0.1429 |              155 |                0.0124 |      0.0312 |
| rules    | 30-49    |      29335 |      86 |       30 |   0.3488 |              347 |                0.0119 |      0.0796 |
| rules    | 50+      |       8200 |      59 |       21 |   0.3559 |               95 |                0.0117 |      0.181  |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy   |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:---------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model    |            6 |      26529 |     103 |       90 |   0.8738 |       443 |      0.2032 |           0.5299 |        0.5722 |        0.6136 |
| model    |            7 |      23532 |      77 |       64 |   0.8312 |       279 |      0.2294 |           0.4701 |        0.4278 |        0.3864 |
| rules    |            6 |      26529 |     103 |       33 |   0.3204 |       351 |      0.094  |           0.5299 |        0.5722 |        0.5375 |
| rules    |            7 |      23532 |      77 |       23 |   0.2987 |       302 |      0.0762 |           0.4701 |        0.4278 |        0.4625 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|---------:|--------------:|
|      0 |           50061 |     147 |         0 |               5 |         0     |               5 |         0     |        5 |             0 |
|      2 |           50061 |     149 |         2 |              20 |         0.007 |              20 |         0     |        7 |             0 |
|      4 |           50061 |     150 |         3 |              39 |         0.04  |              38 |         0     |       10 |             0 |
|      8 |           50061 |     151 |         4 |              69 |         0.053 |              67 |         0     |       12 |             0 |
|     12 |           50060 |     155 |         8 |              97 |         0.084 |              94 |         0.006 |        5 |             0 |
|     17 |           50060 |     158 |        11 |             134 |         0.108 |             129 |         0.013 |        8 |             0 |
|     26 |           50043 |     163 |       111 |             260 |         0.558 |             244 |         0.184 |       15 |             0 |
|     52 |           50023 |     169 |       169 |             498 |         0.858 |             456 |         0.314 |       14 |             0 |
|     77 |           50020 |     180 |       180 |             722 |         0.856 |             653 |         0.311 |       10 |             0 |

- recall / precision: against mule accounts by the end of the horizon (fake accounts from opening, real customers from their start). recall_final_label / precision_final_label: against launderers at any time in the 18 months (label maturity).
- median_min_days_earlier_model_only: launderers caught by the model but not by the rules within the horizon; days from the model's flag to the end of the horizon, so the model is at least this many days earlier (the count is model_only).
- median_days_from_start: days from laundering start to the first flag, caught launderers only (negative = flagged before it started). A model flag is dated at the end of its week.
- catch_mean: per week the share of that week's mules already flagged, averaged over the weeks.
- Accounts closed by the bank stay in the cohort (caught by the rules); `open_accounts` counts the ones still open at the end of each week.
