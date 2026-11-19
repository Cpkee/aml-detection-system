# Harness, final test: cohort opened in month(s) 6, 7

Settings: `{"data": "data/sensitivity/bursts_per_launderer__1", "cohort_months": [6, 7], "horizons": [26, 77], "model": "robust_avg5", "model_params_source": "file", "model_git_commit": "56cfa2a227cf076499654c1d6b943fc8fe2ffe8e", "model_machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "cohort_accounts": 50061, "launderers": 180, "budget_per_horizon": {"26": 312, "77": 820}, "score_source": "model:robust_avg5", "scores_sha256": null, "run_manifest_sha256": "2868f3321cba22fcb85313a111620f3c15213c985fa1d2444fbebe58e5137701", "git_commit": "56cfa2a227cf076499654c1d6b943fc8fe2ffe8e", "git_uncommitted_changes": true, "retest_reason": null, "seconds": 27}`

Model vs rules on the same accounts. Each week since opening the model may flag as many accounts as the rules raised alerts on this cohort that week; a flag is permanent. `model_anytime`: a secondary policy, one score threshold over the horizon (on each account's highest score) flagging the same total number of accounts.

- The weekly budget counts the rules' alerts: an account alerted twice counts twice, so the model can flag slightly more distinct accounts than the rules (e.g. 124 vs 119 over weeks 0-26 in the month-5 dry run).
- The model is trained on weeks 0-26 only (models.train WEEKS); weeks 27-77 are outside its training range, so its running-total features drift there and late scores are not comparable across weeks.

## Weeks 0-26 (main): launderers who are mules by the end of week 26

|                        | model   | rules   | model_anytime   |
|:-----------------------|:--------|:--------|:----------------|
| flagged                | 312     | 289     | 312             |
| caught                 | 150     | 75      | 156             |
| mules                  | 163     | 163     | 163             |
| recall                 | 0.920   | 0.460   | 0.957           |
| recall_final_label     | 0.833   | 0.417   | 0.867           |
| precision              | 0.481   | 0.260   | 0.500           |
| false_alarm_share      | 0.519   | 0.740   | 0.500           |
| precision_final_label  | 0.481   | 0.260   | 0.500           |
| catch_mean             | 0.446   | 0.187   | 0.486           |
| median_days_from_start | 9       | 17      | 7               |
| flagged_before_start   | 2       | 0       | 1               |
| caught_fake            | 137/147 | 71/147  | 143/147         |
| caught_witting         | 9/11    | 3/11    | 9/11            |
| caught_unwitting       | 4/5     | 1/5     | 4/5             |

Ties at the cut line (decided by account id): 0 of 27 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   163.0 |
| both                                |    70.0 |
| model_only                          |    80.0 |
| rules_only                          |     5.0 |
| either                              |   155.0 |
| neither                             |     8.0 |
| median_days_model_earlier_when_both |     5.0 |
| model_first_when_both               |    56.0 |
| rules_first_when_both               |     8.0 |
| median_min_days_earlier_model_only  |    70.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy        | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:--------------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model         | under 30 |      12526 |      26 |       22 |   0.8462 |               27 |                0.0022 |      0.449  |
| model         | 30-49    |      29335 |      80 |       73 |   0.9125 |               88 |                0.003  |      0.4534 |
| model         | 50+      |       8200 |      57 |       55 |   0.9649 |               47 |                0.0058 |      0.5392 |
| rules         | under 30 |      12526 |      26 |       14 |   0.5385 |               52 |                0.0042 |      0.2121 |
| rules         | 30-49    |      29335 |      80 |       38 |   0.475  |              126 |                0.0043 |      0.2317 |
| rules         | 50+      |       8200 |      57 |       23 |   0.4035 |               36 |                0.0044 |      0.3898 |
| model_anytime | under 30 |      12526 |      26 |       23 |   0.8846 |               34 |                0.0027 |      0.4035 |
| model_anytime | 30-49    |      29335 |      80 |       77 |   0.9625 |               90 |                0.0031 |      0.4611 |
| model_anytime | 50+      |       8200 |      57 |       56 |   0.9825 |               32 |                0.0039 |      0.6364 |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy        |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:--------------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model         |            6 |      26529 |      93 |       88 |   0.9462 |       196 |      0.449  |           0.5299 |        0.5706 |        0.6282 |
| model         |            7 |      23532 |      70 |       62 |   0.8857 |       116 |      0.5345 |           0.4701 |        0.4294 |        0.3718 |
| rules         |            6 |      26529 |      93 |       48 |   0.5161 |       155 |      0.3097 |           0.5299 |        0.5706 |        0.5363 |
| rules         |            7 |      23532 |      70 |       27 |   0.3857 |       134 |      0.2015 |           0.4701 |        0.4294 |        0.4637 |
| model_anytime |            6 |      26529 |      93 |       90 |   0.9677 |       183 |      0.4918 |           0.5299 |        0.5706 |        0.5865 |
| model_anytime |            7 |      23532 |      70 |       66 |   0.9429 |       129 |      0.5116 |           0.4701 |        0.4294 |        0.4135 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   flagged_model_anytime |   catch_model_anytime |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|------------------------:|----------------------:|---------:|--------------:|
|      0 |           50061 |     147 |         0 |               5 |         0     |               5 |         0     |                       0 |                 0     |        5 |             0 |
|      2 |           50061 |     149 |         2 |              20 |         0.013 |              20 |         0     |                       0 |                 0     |        7 |             0 |
|      4 |           50061 |     150 |         3 |              39 |         0.02  |              38 |         0     |                       5 |                 0.007 |       10 |             0 |
|      8 |           50061 |     151 |        13 |              69 |         0.066 |              67 |         0     |                      24 |                 0.046 |       12 |             0 |
|     12 |           50055 |     155 |        77 |             117 |         0.348 |             114 |         0.135 |                      88 |                 0.387 |        9 |             0 |
|     17 |           50035 |     158 |       158 |             180 |         0.734 |             174 |         0.297 |                     209 |                 0.899 |       15 |             0 |
|     26 |           50000 |     163 |       163 |             312 |         0.92  |             289 |         0.46  |                     312 |                 0.957 |       13 |             0 |

## Weeks 0-77: launderers who are mules by the end of week 77

|                        | model   | rules   |
|:-----------------------|:--------|:--------|
| flagged                | 820     | 732     |
| caught                 | 172     | 135     |
| mules                  | 180     | 180     |
| recall                 | 0.956   | 0.750   |
| recall_final_label     | 0.956   | 0.750   |
| precision              | 0.210   | 0.184   |
| false_alarm_share      | 0.790   | 0.816   |
| precision_final_label  | 0.210   | 0.184   |
| catch_mean             | 0.773   | 0.477   |
| median_days_from_start | 9.500   | 58      |
| flagged_before_start   | 2       | 0       |
| caught_fake            | 142/147 | 117/147 |
| caught_witting         | 18/20   | 11/20   |
| caught_unwitting       | 12/13   | 7/13    |

`model_anytime`: not meaningful (model trained on weeks 0-26).

Ties at the cut line (decided by account id): 0 of 78 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   180.0 |
| both                                |   130.0 |
| model_only                          |    42.0 |
| rules_only                          |     5.0 |
| either                              |   177.0 |
| neither                             |     3.0 |
| median_days_model_earlier_when_both |    45.5 |
| model_first_when_both               |   113.0 |
| rules_first_when_both               |    10.0 |
| median_min_days_earlier_model_only  |   413.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy   | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:---------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model    | under 30 |      12526 |      35 |       33 |   0.9429 |              120 |                0.0096 |      0.2157 |
| model    | 30-49    |      29335 |      86 |       82 |   0.9535 |              345 |                0.0118 |      0.192  |
| model    | 50+      |       8200 |      59 |       57 |   0.9661 |              183 |                0.0225 |      0.2375 |
| rules    | under 30 |      12526 |      35 |       22 |   0.6286 |              155 |                0.0124 |      0.1243 |
| rules    | 30-49    |      29335 |      86 |       65 |   0.7558 |              347 |                0.0119 |      0.1578 |
| rules    | 50+      |       8200 |      59 |       48 |   0.8136 |               95 |                0.0117 |      0.3357 |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy   |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:---------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model    |            6 |      26529 |     103 |      100 |   0.9709 |       509 |      0.1965 |           0.5299 |        0.5722 |        0.6207 |
| model    |            7 |      23532 |      77 |       72 |   0.9351 |       311 |      0.2315 |           0.4701 |        0.4278 |        0.3793 |
| rules    |            6 |      26529 |     103 |       79 |   0.767  |       397 |      0.199  |           0.5299 |        0.5722 |        0.5423 |
| rules    |            7 |      23532 |      77 |       56 |   0.7273 |       335 |      0.1672 |           0.4701 |        0.4278 |        0.4577 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|---------:|--------------:|
|      0 |           50061 |     147 |         0 |               5 |         0     |               5 |         0     |        5 |             0 |
|      2 |           50061 |     149 |         2 |              20 |         0.013 |              20 |         0     |        7 |             0 |
|      4 |           50061 |     150 |         3 |              39 |         0.02  |              38 |         0     |       10 |             0 |
|      8 |           50061 |     151 |        13 |              69 |         0.066 |              67 |         0     |       12 |             0 |
|     12 |           50055 |     155 |        77 |             117 |         0.348 |             114 |         0.135 |        9 |             0 |
|     17 |           50035 |     158 |       158 |             180 |         0.734 |             174 |         0.297 |       15 |             0 |
|     26 |           50000 |     163 |       163 |             312 |         0.92  |             289 |         0.46  |       13 |             0 |
|     52 |           49966 |     169 |       169 |             563 |         0.947 |             508 |         0.621 |       14 |             0 |
|     77 |           49938 |     180 |       180 |             820 |         0.956 |             732 |         0.75  |       12 |             0 |

- recall / precision: against mule accounts by the end of the horizon (fake accounts from opening, real customers from their start). recall_final_label / precision_final_label: against launderers at any time in the 18 months (label maturity).
- median_min_days_earlier_model_only: launderers caught by the model but not by the rules within the horizon; days from the model's flag to the end of the horizon, so the model is at least this many days earlier (the count is model_only).
- median_days_from_start: days from laundering start to the first flag, caught launderers only (negative = flagged before it started). A model flag is dated at the end of its week.
- catch_mean: per week the share of that week's mules already flagged, averaged over the weeks.
- Accounts closed by the bank stay in the cohort (caught by the rules); `open_accounts` counts the ones still open at the end of each week.
