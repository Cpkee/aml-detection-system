# Harness, final test: cohort opened in month(s) 6, 7

Settings: `{"data": "data/sensitivity/fake_start_days__1", "cohort_months": [6, 7], "horizons": [26, 77], "model": "robust_avg5", "model_params_source": "file", "model_git_commit": "56cfa2a227cf076499654c1d6b943fc8fe2ffe8e", "model_machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "cohort_accounts": 50061, "launderers": 180, "budget_per_horizon": {"26": 284, "77": 726}, "score_source": "model:robust_avg5", "scores_sha256": null, "run_manifest_sha256": "a08dd7fe4f37edd558b8d1d5bac19e2605ae8e6bde4711358fe4d3f0e2e34af1", "git_commit": "56cfa2a227cf076499654c1d6b943fc8fe2ffe8e", "git_uncommitted_changes": true, "retest_reason": null, "seconds": 23}`

Model vs rules on the same accounts. Each week since opening the model may flag as many accounts as the rules raised alerts on this cohort that week; a flag is permanent. `model_anytime`: a secondary policy, one score threshold over the horizon (on each account's highest score) flagging the same total number of accounts.

- The weekly budget counts the rules' alerts: an account alerted twice counts twice, so the model can flag slightly more distinct accounts than the rules (e.g. 124 vs 119 over weeks 0-26 in the month-5 dry run).
- The model is trained on weeks 0-26 only (models.train WEEKS); weeks 27-77 are outside its training range, so its running-total features drift there and late scores are not comparable across weeks.

## Weeks 0-26 (main): launderers who are mules by the end of week 26

|                        | model   | rules   | model_anytime   |
|:-----------------------|:--------|:--------|:----------------|
| flagged                | 284     | 268     | 284             |
| caught                 | 118     | 54      | 144             |
| mules                  | 163     | 163     | 163             |
| recall                 | 0.724   | 0.331   | 0.883           |
| recall_final_label     | 0.656   | 0.300   | 0.800           |
| precision              | 0.415   | 0.201   | 0.507           |
| false_alarm_share      | 0.585   | 0.799   | 0.493           |
| precision_final_label  | 0.415   | 0.201   | 0.507           |
| catch_mean             | 0.570   | 0.262   | 0.748           |
| median_days_from_start | 11      | 7       | 6               |
| flagged_before_start   | 0       | 0       | 0               |
| caught_fake            | 110/147 | 51/147  | 135/147         |
| caught_witting         | 5/11    | 1/11    | 6/11            |
| caught_unwitting       | 3/5     | 2/5     | 3/5             |

Ties at the cut line (decided by account id): 0 of 27 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   163.0 |
| both                                |    46.0 |
| model_only                          |    72.0 |
| rules_only                          |     8.0 |
| either                              |   126.0 |
| neither                             |    37.0 |
| median_days_model_earlier_when_both |    -0.5 |
| model_first_when_both               |    17.0 |
| rules_first_when_both               |    23.0 |
| median_min_days_earlier_model_only  |   136.5 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy        | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:--------------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model         | under 30 |      12526 |      26 |       16 |   0.6154 |               28 |                0.0022 |      0.3636 |
| model         | 30-49    |      29335 |      80 |       58 |   0.725  |               86 |                0.0029 |      0.4028 |
| model         | 50+      |       8200 |      57 |       44 |   0.7719 |               52 |                0.0064 |      0.4583 |
| rules         | under 30 |      12526 |      26 |        5 |   0.1923 |               52 |                0.0042 |      0.0877 |
| rules         | 30-49    |      29335 |      80 |       29 |   0.3625 |              126 |                0.0043 |      0.1871 |
| rules         | 50+      |       8200 |      57 |       20 |   0.3509 |               36 |                0.0044 |      0.3571 |
| model_anytime | under 30 |      12526 |      26 |       20 |   0.7692 |               26 |                0.0021 |      0.4348 |
| model_anytime | 30-49    |      29335 |      80 |       72 |   0.9    |               76 |                0.0026 |      0.4865 |
| model_anytime | 50+      |       8200 |      57 |       52 |   0.9123 |               38 |                0.0047 |      0.5778 |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy        |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:--------------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model         |            6 |      26529 |      93 |       68 |   0.7312 |       172 |      0.3953 |           0.5299 |        0.5706 |        0.6056 |
| model         |            7 |      23532 |      70 |       50 |   0.7143 |       112 |      0.4464 |           0.4701 |        0.4294 |        0.3944 |
| rules         |            6 |      26529 |      93 |       33 |   0.3548 |       140 |      0.2357 |           0.5299 |        0.5706 |        0.5224 |
| rules         |            7 |      23532 |      70 |       21 |   0.3    |       128 |      0.1641 |           0.4701 |        0.4294 |        0.4776 |
| model_anytime |            6 |      26529 |      93 |       82 |   0.8817 |       164 |      0.5    |           0.5299 |        0.5706 |        0.5775 |
| model_anytime |            7 |      23532 |      70 |       62 |   0.8857 |       120 |      0.5167 |           0.4701 |        0.4294 |        0.4225 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   flagged_model_anytime |   catch_model_anytime |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|------------------------:|----------------------:|---------:|--------------:|
|      0 |           50061 |     147 |         0 |               5 |         0     |               5 |         0     |                       0 |                 0     |        5 |             0 |
|      2 |           50061 |     149 |        36 |              20 |         0.047 |              20 |         0     |                      21 |                 0.128 |        7 |             0 |
|      4 |           50061 |     150 |        99 |              57 |         0.293 |              56 |         0.12  |                      80 |                 0.487 |       22 |             0 |
|      8 |           50034 |     151 |       151 |             118 |         0.682 |             116 |         0.325 |                     159 |                 0.907 |       14 |             0 |
|     12 |           50018 |     155 |       155 |             147 |         0.69  |             144 |         0.329 |                     185 |                 0.89  |        5 |             0 |
|     17 |           50018 |     158 |       158 |             183 |         0.715 |             178 |         0.323 |                     214 |                 0.886 |        8 |             0 |
|     26 |           50017 |     163 |       163 |             284 |         0.724 |             268 |         0.331 |                     284 |                 0.883 |       13 |             0 |

## Weeks 0-77: launderers who are mules by the end of week 77

|                        | model   | rules   |
|:-----------------------|:--------|:--------|
| flagged                | 726     | 657     |
| caught                 | 132     | 60      |
| mules                  | 180     | 180     |
| recall                 | 0.733   | 0.333   |
| recall_final_label     | 0.733   | 0.333   |
| precision              | 0.182   | 0.091   |
| false_alarm_share      | 0.818   | 0.909   |
| precision_final_label  | 0.182   | 0.091   |
| catch_mean             | 0.680   | 0.306   |
| median_days_from_start | 11      | 8       |
| flagged_before_start   | 0       | 0       |
| caught_fake            | 115/147 | 54/147  |
| caught_witting         | 10/20   | 3/20    |
| caught_unwitting       | 7/13    | 3/13    |

`model_anytime`: not meaningful (model trained on weeks 0-26).

Ties at the cut line (decided by account id): 0 of 78 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   180.0 |
| both                                |    52.0 |
| model_only                          |    80.0 |
| rules_only                          |     8.0 |
| either                              |   140.0 |
| neither                             |    40.0 |
| median_days_model_earlier_when_both |     0.0 |
| model_first_when_both               |    22.0 |
| rules_first_when_both               |    24.0 |
| median_min_days_earlier_model_only  |   490.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy   | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:---------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model    | under 30 |      12526 |      35 |       22 |   0.6286 |               95 |                0.0076 |      0.188  |
| model    | 30-49    |      29335 |      86 |       62 |   0.7209 |              296 |                0.0101 |      0.1732 |
| model    | 50+      |       8200 |      59 |       48 |   0.8136 |              203 |                0.0249 |      0.1912 |
| rules    | under 30 |      12526 |      35 |        7 |   0.2    |              155 |                0.0124 |      0.0432 |
| rules    | 30-49    |      29335 |      86 |       31 |   0.3605 |              347 |                0.0119 |      0.082  |
| rules    | 50+      |       8200 |      59 |       22 |   0.3729 |               95 |                0.0117 |      0.188  |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy   |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:---------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model    |            6 |      26529 |     103 |       78 |   0.7573 |       449 |      0.1737 |           0.5299 |        0.5722 |        0.6185 |
| model    |            7 |      23532 |      77 |       54 |   0.7013 |       277 |      0.1949 |           0.4701 |        0.4278 |        0.3815 |
| rules    |            6 |      26529 |     103 |       37 |   0.3592 |       355 |      0.1042 |           0.5299 |        0.5722 |        0.5403 |
| rules    |            7 |      23532 |      77 |       23 |   0.2987 |       302 |      0.0762 |           0.4701 |        0.4278 |        0.4597 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|---------:|--------------:|
|      0 |           50061 |     147 |         0 |               5 |         0     |               5 |         0     |        5 |             0 |
|      2 |           50061 |     149 |        36 |              20 |         0.047 |              20 |         0     |        7 |             0 |
|      4 |           50061 |     150 |        99 |              57 |         0.293 |              56 |         0.12  |       22 |             0 |
|      8 |           50034 |     151 |       151 |             118 |         0.682 |             116 |         0.325 |       14 |             0 |
|     12 |           50018 |     155 |       155 |             147 |         0.69  |             144 |         0.329 |        5 |             0 |
|     17 |           50018 |     158 |       158 |             183 |         0.715 |             178 |         0.323 |        8 |             0 |
|     26 |           50017 |     163 |       163 |             284 |         0.724 |             268 |         0.331 |       13 |             0 |
|     52 |           50015 |     169 |       169 |             499 |         0.74  |             457 |         0.32  |       14 |             0 |
|     77 |           50010 |     180 |       180 |             726 |         0.733 |             657 |         0.333 |       10 |             0 |

- recall / precision: against mule accounts by the end of the horizon (fake accounts from opening, real customers from their start). recall_final_label / precision_final_label: against launderers at any time in the 18 months (label maturity).
- median_min_days_earlier_model_only: launderers caught by the model but not by the rules within the horizon; days from the model's flag to the end of the horizon, so the model is at least this many days earlier (the count is model_only).
- median_days_from_start: days from laundering start to the first flag, caught launderers only (negative = flagged before it started). A model flag is dated at the end of its week.
- catch_mean: per week the share of that week's mules already flagged, averaged over the weeks.
- Accounts closed by the bank stay in the cohort (caught by the rules); `open_accounts` counts the ones still open at the end of each week.
