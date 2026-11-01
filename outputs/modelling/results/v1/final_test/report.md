# Harness, final test: cohort opened in month(s) 6, 7

Settings: `{"data": "data/v1", "cohort_months": [6, 7], "horizons": [26, 77], "model": "rehearsal_tuned", "model_params_source": "file", "model_git_commit": "f08190c7e12cbb8b9c01f28ec2624d1530f867dc", "model_machine": {"os": "macOS-26.5.2-arm64-arm-64bit", "processor": "arm", "cpu_count": 8, "python": "3.12.3"}, "machine": {"os": "macOS-26.5.2-arm64-arm-64bit", "processor": "arm", "cpu_count": 8, "python": "3.12.3"}, "cohort_accounts": 10183, "launderers": 32, "budget_per_horizon": {"26": 53, "77": 157}, "score_source": "model:rehearsal_tuned", "scores_sha256": null, "run_manifest_sha256": "abe179ada692126714499f487d9783110633d8863ef183adfcf2a06900a12926", "git_commit": "f08190c7e12cbb8b9c01f28ec2624d1530f867dc", "git_uncommitted_changes": true, "seconds": 5}`

Model vs rules on the same accounts. Each week since opening the model may flag as many accounts as the rules raised alerts on this cohort that week; a flag is permanent. `model_anytime`: a secondary policy, one score threshold over the horizon (on each account's highest score) flagging the same total number of accounts.

- The weekly budget counts the rules' alerts: an account alerted twice counts twice, so the model can flag slightly more distinct accounts than the rules (e.g. 124 vs 119 over weeks 0-26 in the month-5 dry run).
- The model is trained on weeks 0-26 only (models.train WEEKS); weeks 27-77 are outside its training range, so its running-total features drift there and late scores are not comparable across weeks.

## Weeks 0-26 (main): launderers who are mules by the end of week 26

|                        | model   | rules   | model_anytime   |
|:-----------------------|:--------|:--------|:----------------|
| flagged                | 53      | 52      | 53              |
| caught                 | 16      | 7       | 17              |
| mules                  | 22      | 22      | 22              |
| recall                 | 0.727   | 0.318   | 0.773           |
| recall_final_label     | 0.500   | 0.219   | 0.531           |
| precision              | 0.302   | 0.135   | 0.321           |
| false_alarm_share      | 0.698   | 0.865   | 0.679           |
| precision_final_label  | 0.302   | 0.135   | 0.321           |
| catch_mean             | 0.390   | 0.171   | 0.422           |
| median_days_from_start | 9       | 5       | 6               |
| flagged_before_start   | 0       | 0       | 0               |
| caught_fake            | 15/20   | 6/20    | 16/20           |
| caught_witting         | 1/1     | 1/1     | 1/1             |
| caught_unwitting       | 0/1     | 0/1     | 0/1             |

Ties at the cut line (decided by account id): 0 of 27 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |    22.0 |
| both                                |     6.0 |
| model_only                          |    10.0 |
| rules_only                          |     1.0 |
| either                              |    17.0 |
| neither                             |     5.0 |
| median_days_model_earlier_when_both |    -2.5 |
| model_first_when_both               |     1.0 |
| rules_first_when_both               |     5.0 |
| median_min_days_earlier_model_only  |    91.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy        | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:--------------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model         | under 30 |       2531 |       4 |        2 |    0.5   |                6 |                0.0024 |      0.25   |
| model         | 30-49    |       5963 |       8 |        7 |    0.875 |               20 |                0.0034 |      0.2593 |
| model         | 50+      |       1689 |      10 |        7 |    0.7   |               11 |                0.0066 |      0.3889 |
| rules         | under 30 |       2531 |       4 |        1 |    0.25  |               10 |                0.004  |      0.0909 |
| rules         | 30-49    |       5963 |       8 |        2 |    0.25  |               26 |                0.0044 |      0.0714 |
| rules         | 50+      |       1689 |      10 |        4 |    0.4   |                9 |                0.0054 |      0.3077 |
| model_anytime | under 30 |       2531 |       4 |        3 |    0.75  |                8 |                0.0032 |      0.2727 |
| model_anytime | 30-49    |       5963 |       8 |        8 |    1     |               22 |                0.0037 |      0.2667 |
| model_anytime | 50+      |       1689 |      10 |        6 |    0.6   |                6 |                0.0036 |      0.5    |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy        |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:--------------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model         |            6 |       5267 |      10 |        8 |   0.8    |        26 |      0.3077 |           0.5172 |        0.4545 |        0.4906 |
| model         |            7 |       4916 |      12 |        8 |   0.6667 |        27 |      0.2963 |           0.4828 |        0.5455 |        0.5094 |
| rules         |            6 |       5267 |      10 |        3 |   0.3    |        27 |      0.1111 |           0.5172 |        0.4545 |        0.5192 |
| rules         |            7 |       4916 |      12 |        4 |   0.3333 |        25 |      0.16   |           0.4828 |        0.5455 |        0.4808 |
| model_anytime |            6 |       5267 |      10 |        8 |   0.8    |        31 |      0.2581 |           0.5172 |        0.4545 |        0.5849 |
| model_anytime |            7 |       4916 |      12 |        9 |   0.75   |        22 |      0.4091 |           0.4828 |        0.5455 |        0.4151 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   flagged_model_anytime |   catch_model_anytime |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|------------------------:|----------------------:|---------:|--------------:|
|      0 |           10183 |      20 |         0 |               2 |         0     |               2 |         0     |                       0 |                 0     |        2 |             0 |
|      2 |           10183 |      20 |         0 |               2 |         0     |               2 |         0     |                       0 |                 0     |        0 |             0 |
|      4 |           10183 |      20 |         0 |               4 |         0     |               4 |         0     |                       0 |                 0     |        0 |             0 |
|      8 |           10183 |      20 |         0 |               8 |         0     |               8 |         0     |                       7 |                 0     |        0 |             0 |
|     12 |           10182 |      20 |        11 |              20 |         0.4   |              20 |         0.15  |                      19 |                 0.4   |        5 |             0 |
|     17 |           10179 |      21 |        21 |              34 |         0.714 |              34 |         0.333 |                      36 |                 0.762 |        3 |             0 |
|     26 |           10177 |      22 |        22 |              53 |         0.727 |              52 |         0.318 |                      53 |                 0.773 |        1 |             0 |

## Weeks 0-77: launderers who are mules by the end of week 77

|                        | model   | rules   |
|:-----------------------|:--------|:--------|
| flagged                | 157     | 149     |
| caught                 | 22      | 12      |
| mules                  | 32      | 32      |
| recall                 | 0.688   | 0.375   |
| recall_final_label     | 0.688   | 0.375   |
| precision              | 0.140   | 0.081   |
| false_alarm_share      | 0.860   | 0.919   |
| precision_final_label  | 0.140   | 0.081   |
| catch_mean             | 0.598   | 0.278   |
| median_days_from_start | 11      | 7       |
| flagged_before_start   | 0       | 0       |
| caught_fake            | 15/20   | 7/20    |
| caught_witting         | 4/7     | 3/7     |
| caught_unwitting       | 3/5     | 2/5     |

`model_anytime`: not meaningful (model trained on weeks 0-26).

Ties at the cut line (decided by account id): 0 of 78 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |    32.0 |
| both                                |     9.0 |
| model_only                          |    13.0 |
| rules_only                          |     3.0 |
| either                              |    25.0 |
| neither                             |     7.0 |
| median_days_model_earlier_when_both |    -2.0 |
| model_first_when_both               |     2.0 |
| rules_first_when_both               |     7.0 |
| median_min_days_earlier_model_only  |   434.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy   | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:---------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model    | under 30 |       2531 |      11 |        6 |   0.5455 |               41 |                0.0163 |      0.1277 |
| model    | 30-49    |       5963 |      10 |        8 |   0.8    |               63 |                0.0106 |      0.1127 |
| model    | 50+      |       1689 |      11 |        8 |   0.7273 |               31 |                0.0185 |      0.2051 |
| rules    | under 30 |       2531 |      11 |        4 |   0.3636 |               31 |                0.0123 |      0.1143 |
| rules    | 30-49    |       5963 |      10 |        3 |   0.3    |               77 |                0.0129 |      0.0375 |
| rules    | 50+      |       1689 |      11 |        5 |   0.4545 |               29 |                0.0173 |      0.1471 |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy   |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:---------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model    |            6 |       5267 |      14 |       11 |   0.7857 |        76 |      0.1447 |           0.5172 |        0.4375 |        0.4841 |
| model    |            7 |       4916 |      18 |       11 |   0.6111 |        81 |      0.1358 |           0.4828 |        0.5625 |        0.5159 |
| rules    |            6 |       5267 |      14 |        5 |   0.3571 |        68 |      0.0735 |           0.5172 |        0.4375 |        0.4564 |
| rules    |            7 |       4916 |      18 |        7 |   0.3889 |        81 |      0.0864 |           0.4828 |        0.5625 |        0.5436 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|---------:|--------------:|
|      0 |           10183 |      20 |         0 |               2 |         0     |               2 |         0     |        2 |             0 |
|      2 |           10183 |      20 |         0 |               2 |         0     |               2 |         0     |        0 |             0 |
|      4 |           10183 |      20 |         0 |               4 |         0     |               4 |         0     |        0 |             0 |
|      8 |           10183 |      20 |         0 |               8 |         0     |               8 |         0     |        0 |             0 |
|     12 |           10182 |      20 |        11 |              20 |         0.4   |              20 |         0.15  |        5 |             0 |
|     17 |           10179 |      21 |        21 |              34 |         0.714 |              34 |         0.333 |        3 |             0 |
|     26 |           10177 |      22 |        22 |              53 |         0.727 |              52 |         0.318 |        1 |             0 |
|     52 |           10176 |      28 |        28 |             101 |         0.714 |              97 |         0.321 |        2 |             0 |
|     77 |           10172 |      32 |        32 |             157 |         0.688 |             149 |         0.375 |        1 |             0 |

- recall / precision: against mule accounts by the end of the horizon (fake accounts from opening, real customers from their start). recall_final_label / precision_final_label: against launderers at any time in the 18 months (label maturity).
- median_min_days_earlier_model_only: launderers caught by the model but not by the rules within the horizon; days from the model's flag to the end of the horizon, so the model is at least this many days earlier (the count is model_only).
- median_days_from_start: days from laundering start to the first flag, caught launderers only (negative = flagged before it started). A model flag is dated at the end of its week.
- catch_mean: per week the share of that week's mules already flagged, averaged over the weeks.
- Accounts closed by the bank stay in the cohort (caught by the rules); `open_accounts` counts the ones still open at the end of each week.
