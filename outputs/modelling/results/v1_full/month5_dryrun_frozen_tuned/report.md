# Harness, dry run: cohort opened in month(s) 5

Settings: `{"data": "data/v1_full", "cohort_months": [5], "horizons": [26, 77], "model": "frozen_tuned", "model_params_source": "file", "model_git_commit": "fb47487555177750503c4da8dfdd840dd1aad524", "cohort_accounts": 29120, "launderers": 97, "budget_per_horizon": {"26": 124, "77": 382}, "seconds": 28}`

Model vs rules on the same accounts. Each week since opening the model may flag as many accounts as the rules raised alerts on this cohort that week; a flag is permanent. `model_anytime`: the same total number of flags, spent whenever the model likes (an upper bound on the head start).

## Weeks 0-26 (main): launderers who are mules by the end of week 26

|                        | model   | rules   | model_anytime   |
|:-----------------------|:--------|:--------|:----------------|
| flagged                | 124     | 119     | 124             |
| caught                 | 63      | 16      | 72              |
| mules                  | 78      | 78      | 78              |
| recall                 | 0.808   | 0.205   | 0.923           |
| precision              | 0.508   | 0.134   | 0.581           |
| false_alarm_share      | 0.492   | 0.866   | 0.419           |
| precision_final_label  | 0.508   | 0.134   | 0.581           |
| catch_mean             | 0.382   | 0.095   | 0.462           |
| median_days_from_start | 8       | 8.500   | 6.500           |
| flagged_before_start   | 0       | 0       | 0               |
| caught_fake            | 59/70   | 13/70   | 66/70           |
| caught_witting         | 3/5     | 3/5     | 3/5             |
| caught_unwitting       | 1/3     | 0/3     | 3/3             |

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |    78.0 |
| both                                |    14.0 |
| model_only                          |    49.0 |
| rules_only                          |     2.0 |
| either                              |    65.0 |
| neither                             |    13.0 |
| median_days_model_earlier_when_both |     1.5 |
| model_first_when_both               |     8.0 |
| rules_first_when_both               |     4.0 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   flagged_model_anytime |   catch_model_anytime |   budget |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|------------------------:|----------------------:|---------:|
|      0 |           29120 |      71 |         1 |               0 |         0     |               0 |         0     |                       1 |                 0     |        0 |
|      2 |           29120 |      71 |         1 |               6 |         0     |               6 |         0     |                       1 |                 0     |        3 |
|      4 |           29120 |      71 |         1 |              14 |         0     |              14 |         0     |                       1 |                 0     |        1 |
|      8 |           29120 |      71 |         2 |              26 |         0.014 |              26 |         0     |                       9 |                 0.014 |        2 |
|     12 |           29119 |      72 |        34 |              49 |         0.306 |              48 |         0.083 |                      36 |                 0.347 |        5 |
|     17 |           29113 |      74 |        74 |              75 |         0.649 |              73 |         0.162 |                      85 |                 0.892 |        5 |
|     26 |           29108 |      78 |        78 |             124 |         0.808 |             119 |         0.205 |                     124 |                 0.923 |        2 |

## Weeks 0-77: launderers who are mules by the end of week 77

|                        | model   | rules   | model_anytime   |
|:-----------------------|:--------|:--------|:----------------|
| flagged                | 382     | 350     | 382             |
| caught                 | 76      | 29      | 52              |
| mules                  | 97      | 97      | 97              |
| recall                 | 0.784   | 0.299   | 0.536           |
| precision              | 0.199   | 0.083   | 0.136           |
| false_alarm_share      | 0.801   | 0.917   | 0.864           |
| precision_final_label  | 0.199   | 0.083   | 0.136           |
| catch_mean             | 0.655   | 0.198   | 0.404           |
| median_days_from_start | 9       | 9       | 10              |
| flagged_before_start   | 1       | 0       | 0               |
| caught_fake            | 61/70   | 16/70   | 42/70           |
| caught_witting         | 6/12    | 6/12    | 3/12            |
| caught_unwitting       | 9/15    | 7/15    | 7/15            |

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |    97.0 |
| both                                |    24.0 |
| model_only                          |    52.0 |
| rules_only                          |     5.0 |
| either                              |    81.0 |
| neither                             |    16.0 |
| median_days_model_earlier_when_both |     1.5 |
| model_first_when_both               |    14.0 |
| rules_first_when_both               |     6.0 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   flagged_model_anytime |   catch_model_anytime |   budget |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|------------------------:|----------------------:|---------:|
|      0 |           29120 |      71 |         1 |               0 |         0     |               0 |         0     |                       0 |                 0     |        0 |
|      2 |           29120 |      71 |         1 |               6 |         0     |               6 |         0     |                       0 |                 0     |        3 |
|      4 |           29120 |      71 |         1 |              14 |         0     |              14 |         0     |                       0 |                 0     |        1 |
|      8 |           29120 |      71 |         2 |              26 |         0.014 |              26 |         0     |                       0 |                 0     |        2 |
|     12 |           29119 |      72 |        34 |              49 |         0.306 |              48 |         0.083 |                      12 |                 0.167 |        5 |
|     17 |           29113 |      74 |        74 |              75 |         0.649 |              73 |         0.162 |                      35 |                 0.473 |        5 |
|     26 |           29108 |      78 |        78 |             124 |         0.808 |             119 |         0.205 |                      37 |                 0.474 |        2 |
|     52 |           29102 |      86 |        86 |             248 |         0.791 |             230 |         0.256 |                      65 |                 0.477 |        1 |
|     77 |           29098 |      97 |        97 |             382 |         0.784 |             350 |         0.299 |                     382 |                 0.536 |        6 |

- recall / precision: against mule accounts by the end of the horizon (fake accounts from opening, real customers from their start). precision_final_label: against launderers at any time in the 18 months.
- median_days_from_start: days from laundering start to the first flag, caught launderers only (negative = flagged before it started). A model flag is dated at the end of its week.
- catch_mean: per week the share of that week's mules already flagged, averaged over the weeks.
- Accounts closed by the bank stay in the cohort (caught by the rules); `open_accounts` counts the ones still open at the end of each week.
