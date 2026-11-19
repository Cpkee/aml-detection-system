# Harness, final test: cohort opened in month(s) 6, 7

Settings: `{"data": "/Users/cheepheng/aml-detection-system/data/sensitivity/forward_delay_shares__1", "cohort_months": [6, 7], "horizons": [26, 77], "model": "robust_avg5", "model_params_source": "file", "model_git_commit": "c4e47d864781a9895070fe02716f2c3d6a352e8f", "model_machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "cohort_accounts": 50061, "launderers": 180, "budget_per_horizon": {"26": 268, "77": 711}, "score_source": "model:robust_avg5", "scores_sha256": null, "run_manifest_sha256": "99818711c1a3bfb908f0d3e94a2a0ad4360b155fd39de5695668cbb3037c0fb4", "git_commit": "6acdc391a172c125ff9dbfddefd3fa5ce0c2dacd", "git_uncommitted_changes": false, "retest_reason": null, "seconds": 28}`

Model vs rules on the same accounts. Each week since opening the model may flag as many accounts as the rules raised alerts on this cohort that week; a flag is permanent. `model_anytime`: a secondary policy, one score threshold over the horizon (on each account's highest score) flagging the same total number of accounts.

- The weekly budget counts the rules' alerts: an account alerted twice counts twice, so the model can flag slightly more distinct accounts than the rules (e.g. 124 vs 119 over weeks 0-26 in the month-5 dry run).
- The model is trained on weeks 0-26 only (models.train WEEKS); weeks 27-77 are outside its training range, so its running-total features drift there and late scores are not comparable across weeks.

## Weeks 0-26 (main): launderers who are mules by the end of week 26

|                        | model   | rules   | model_anytime   |
|:-----------------------|:--------|:--------|:----------------|
| flagged                | 268     | 252     | 268             |
| caught                 | 117     | 38      | 130             |
| mules                  | 163     | 163     | 163             |
| recall                 | 0.718   | 0.233   | 0.798           |
| recall_final_label     | 0.650   | 0.211   | 0.722           |
| precision              | 0.437   | 0.151   | 0.485           |
| false_alarm_share      | 0.563   | 0.849   | 0.515           |
| precision_final_label  | 0.437   | 0.151   | 0.485           |
| catch_mean             | 0.365   | 0.120   | 0.413           |
| median_days_from_start | 9       | 8       | 7               |
| flagged_before_start   | 3       | 0       | 3               |
| caught_fake            | 107/147 | 34/147  | 120/147         |
| caught_witting         | 8/11    | 4/11    | 9/11            |
| caught_unwitting       | 2/5     | 0/5     | 1/5             |

Ties at the cut line (decided by account id): 0 of 27 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   163.0 |
| both                                |    37.0 |
| model_only                          |    80.0 |
| rules_only                          |     1.0 |
| either                              |   118.0 |
| neither                             |    45.0 |
| median_days_model_earlier_when_both |     1.0 |
| model_first_when_both               |    19.0 |
| rules_first_when_both               |    16.0 |
| median_min_days_earlier_model_only  |    84.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy        | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:--------------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model         | under 30 |      12526 |      26 |       21 |   0.8077 |               28 |                0.0022 |      0.4286 |
| model         | 30-49    |      29335 |      80 |       55 |   0.6875 |               79 |                0.0027 |      0.4104 |
| model         | 50+      |       8200 |      57 |       41 |   0.7193 |               44 |                0.0054 |      0.4824 |
| rules         | under 30 |      12526 |      26 |        8 |   0.3077 |               52 |                0.0042 |      0.1333 |
| rules         | 30-49    |      29335 |      80 |       14 |   0.175  |              126 |                0.0043 |      0.1    |
| rules         | 50+      |       8200 |      57 |       16 |   0.2807 |               36 |                0.0044 |      0.3077 |
| model_anytime | under 30 |      12526 |      26 |       23 |   0.8846 |               26 |                0.0021 |      0.4694 |
| model_anytime | 30-49    |      29335 |      80 |       63 |   0.7875 |               82 |                0.0028 |      0.4345 |
| model_anytime | 50+      |       8200 |      57 |       44 |   0.7719 |               30 |                0.0037 |      0.5946 |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy        |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:--------------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model         |            6 |      26529 |      93 |       72 |   0.7742 |       163 |      0.4417 |           0.5299 |        0.5706 |        0.6082 |
| model         |            7 |      23532 |      70 |       45 |   0.6429 |       105 |      0.4286 |           0.4701 |        0.4294 |        0.3918 |
| rules         |            6 |      26529 |      93 |       23 |   0.2473 |       130 |      0.1769 |           0.5299 |        0.5706 |        0.5159 |
| rules         |            7 |      23532 |      70 |       15 |   0.2143 |       122 |      0.123  |           0.4701 |        0.4294 |        0.4841 |
| model_anytime |            6 |      26529 |      93 |       78 |   0.8387 |       154 |      0.5065 |           0.5299 |        0.5706 |        0.5746 |
| model_anytime |            7 |      23532 |      70 |       52 |   0.7429 |       114 |      0.4561 |           0.4701 |        0.4294 |        0.4254 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   flagged_model_anytime |   catch_model_anytime |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|------------------------:|----------------------:|---------:|--------------:|
|      0 |           50061 |     147 |         0 |               5 |         0     |               5 |         0     |                       0 |                 0     |        5 |             0 |
|      2 |           50061 |     149 |         2 |              20 |         0.013 |              20 |         0     |                       1 |                 0     |        7 |             0 |
|      4 |           50061 |     150 |         3 |              39 |         0.033 |              38 |         0     |                       4 |                 0.007 |       10 |             0 |
|      8 |           50061 |     151 |        13 |              69 |         0.06  |              67 |         0     |                      24 |                 0.033 |       12 |             0 |
|     12 |           50059 |     155 |        77 |             112 |         0.297 |             109 |         0.103 |                      91 |                 0.316 |       10 |             0 |
|     17 |           50035 |     158 |       158 |             166 |         0.627 |             161 |         0.215 |                     197 |                 0.753 |       11 |             0 |
|     26 |           50027 |     163 |       163 |             268 |         0.718 |             252 |         0.233 |                     268 |                 0.798 |       12 |             0 |

## Weeks 0-77: launderers who are mules by the end of week 77

|                        | model   | rules   |
|:-----------------------|:--------|:--------|
| flagged                | 711     | 642     |
| caught                 | 126     | 45      |
| mules                  | 180     | 180     |
| recall                 | 0.700   | 0.250   |
| recall_final_label     | 0.700   | 0.250   |
| precision              | 0.177   | 0.070   |
| false_alarm_share      | 0.823   | 0.930   |
| precision_final_label  | 0.177   | 0.070   |
| catch_mean             | 0.596   | 0.197   |
| median_days_from_start | 9       | 9       |
| flagged_before_start   | 4       | 0       |
| caught_fake            | 111/147 | 37/147  |
| caught_witting         | 11/20   | 6/20    |
| caught_unwitting       | 4/13    | 2/13    |

`model_anytime`: not meaningful (model trained on weeks 0-26).

Ties at the cut line (decided by account id): 0 of 78 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   180.0 |
| both                                |    42.0 |
| model_only                          |    84.0 |
| rules_only                          |     3.0 |
| either                              |   129.0 |
| neither                             |    51.0 |
| median_days_model_earlier_when_both |     1.0 |
| model_first_when_both               |    23.0 |
| rules_first_when_both               |    16.0 |
| median_min_days_earlier_model_only  |   434.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy   | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:---------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model    | under 30 |      12526 |      35 |       24 |   0.6857 |              125 |                0.01   |      0.1611 |
| model    | 30-49    |      29335 |      86 |       56 |   0.6512 |              288 |                0.0098 |      0.1628 |
| model    | 50+      |       8200 |      59 |       46 |   0.7797 |              172 |                0.0211 |      0.211  |
| rules    | under 30 |      12526 |      35 |       10 |   0.2857 |              155 |                0.0124 |      0.0606 |
| rules    | 30-49    |      29335 |      86 |       16 |   0.186  |              347 |                0.0119 |      0.0441 |
| rules    | 50+      |       8200 |      59 |       19 |   0.322  |               95 |                0.0117 |      0.1667 |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy   |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:---------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model    |            6 |      26529 |     103 |       79 |   0.767  |       437 |      0.1808 |           0.5299 |        0.5722 |        0.6146 |
| model    |            7 |      23532 |      77 |       47 |   0.6104 |       274 |      0.1715 |           0.4701 |        0.4278 |        0.3854 |
| rules    |            6 |      26529 |     103 |       27 |   0.2621 |       345 |      0.0783 |           0.5299 |        0.5722 |        0.5374 |
| rules    |            7 |      23532 |      77 |       18 |   0.2338 |       297 |      0.0606 |           0.4701 |        0.4278 |        0.4626 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|---------:|--------------:|
|      0 |           50061 |     147 |         0 |               5 |         0     |               5 |         0     |        5 |             0 |
|      2 |           50061 |     149 |         2 |              20 |         0.013 |              20 |         0     |        7 |             0 |
|      4 |           50061 |     150 |         3 |              39 |         0.033 |              38 |         0     |       10 |             0 |
|      8 |           50061 |     151 |        13 |              69 |         0.06  |              67 |         0     |       12 |             0 |
|     12 |           50059 |     155 |        77 |             112 |         0.297 |             109 |         0.103 |       10 |             0 |
|     17 |           50035 |     158 |       158 |             166 |         0.627 |             161 |         0.215 |       11 |             0 |
|     26 |           50027 |     163 |       163 |             268 |         0.718 |             252 |         0.233 |       12 |             0 |
|     52 |           50026 |     169 |       169 |             485 |         0.722 |             443 |         0.237 |       14 |             0 |
|     77 |           50022 |     180 |       180 |             711 |         0.7   |             642 |         0.25  |       10 |             0 |

- recall / precision: against mule accounts by the end of the horizon (fake accounts from opening, real customers from their start). recall_final_label / precision_final_label: against launderers at any time in the 18 months (label maturity).
- median_min_days_earlier_model_only: launderers caught by the model but not by the rules within the horizon; days from the model's flag to the end of the horizon, so the model is at least this many days earlier (the count is model_only).
- median_days_from_start: days from laundering start to the first flag, caught launderers only (negative = flagged before it started). A model flag is dated at the end of its week.
- catch_mean: per week the share of that week's mules already flagged, averaged over the weeks.
- Accounts closed by the bank stay in the cohort (caught by the rules); `open_accounts` counts the ones still open at the end of each week.
