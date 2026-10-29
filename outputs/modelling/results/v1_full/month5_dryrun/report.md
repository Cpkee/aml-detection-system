# Harness, dry run: cohort opened in month(s) 5

Settings: `{"data": "data/v1_full", "cohort_months": [5], "horizons": [26, 77], "model": "frozen", "model_params_source": "default", "model_git_commit": "8871f4dbdee5862dac61e9e969653a53f7f4a5e6", "cohort_accounts": 29120, "launderers": 97, "budget_per_horizon": {"26": 124, "77": 382}, "seconds": 6}`

Model vs rules on the same accounts. Each week since opening the model may flag as many accounts as the rules raised alerts on this cohort that week; a flag is permanent. `model_anytime`: the same total number of flags, spent whenever the model likes (an upper bound on the head start).

## Weeks 0-26 (main): launderers who are mules by the end of week 26

|                        | model   | rules   | model_anytime   |
|:-----------------------|:--------|:--------|:----------------|
| flagged                | 124     | 119     | 124             |
| caught                 | 62      | 16      | 71              |
| mules                  | 78      | 78      | 78              |
| recall                 | 0.795   | 0.205   | 0.910           |
| precision              | 0.500   | 0.134   | 0.573           |
| false_alarm_share      | 0.500   | 0.866   | 0.427           |
| precision_final_label  | 0.508   | 0.134   | 0.581           |
| catch_mean             | 0.371   | 0.095   | 0.454           |
| median_days_from_start | 9       | 8.500   | 6               |
| flagged_before_start   | 0       | 0       | 0               |
| caught_fake            | 57/70   | 13/70   | 66/70           |
| caught_witting         | 3/5     | 3/5     | 3/5             |
| caught_unwitting       | 2/3     | 0/3     | 2/3             |

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |    78.0 |
| both                                |    13.0 |
| model_only                          |    49.0 |
| rules_only                          |     3.0 |
| either                              |    65.0 |
| neither                             |    13.0 |
| median_days_model_earlier_when_both |     0.0 |
| model_first_when_both               |     6.0 |
| rules_first_when_both               |     5.0 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   flagged_model_anytime |   catch_model_anytime |   budget |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|------------------------:|----------------------:|---------:|
|      0 |           29120 |      71 |         1 |               0 |         0     |               0 |         0     |                       1 |                 0     |        0 |
|      2 |           29120 |      71 |         1 |               6 |         0     |               6 |         0     |                       1 |                 0     |        3 |
|      4 |           29120 |      71 |         1 |              14 |         0     |              14 |         0     |                       2 |                 0     |        1 |
|      8 |           29120 |      71 |         2 |              26 |         0.014 |              26 |         0     |                       8 |                 0.014 |        2 |
|     12 |           29119 |      72 |        34 |              49 |         0.278 |              48 |         0.083 |                      36 |                 0.347 |        5 |
|     17 |           29113 |      74 |        74 |              75 |         0.622 |              73 |         0.162 |                      84 |                 0.851 |        5 |
|     26 |           29108 |      78 |        78 |             124 |         0.795 |             119 |         0.205 |                     124 |                 0.91  |        2 |

## Weeks 0-77: launderers who are mules by the end of week 77

|                        | model   | rules   | model_anytime   |
|:-----------------------|:--------|:--------|:----------------|
| flagged                | 382     | 350     | 382             |
| caught                 | 75      | 29      | 54              |
| mules                  | 97      | 97      | 97              |
| recall                 | 0.773   | 0.299   | 0.557           |
| precision              | 0.196   | 0.083   | 0.141           |
| false_alarm_share      | 0.804   | 0.917   | 0.859           |
| precision_final_label  | 0.196   | 0.083   | 0.141           |
| catch_mean             | 0.651   | 0.198   | 0.453           |
| median_days_from_start | 10      | 9       | 12              |
| flagged_before_start   | 1       | 0       | 0               |
| caught_fake            | 60/70   | 16/70   | 45/70           |
| caught_witting         | 8/12    | 6/12    | 4/12            |
| caught_unwitting       | 7/15    | 7/15    | 5/15            |

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |    97.0 |
| both                                |    23.0 |
| model_only                          |    52.0 |
| rules_only                          |     6.0 |
| either                              |    81.0 |
| neither                             |    16.0 |
| median_days_model_earlier_when_both |     0.0 |
| model_first_when_both               |    11.0 |
| rules_first_when_both               |     9.0 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   flagged_model_anytime |   catch_model_anytime |   budget |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|------------------------:|----------------------:|---------:|
|      0 |           29120 |      71 |         1 |               0 |         0     |               0 |         0     |                       0 |                 0     |        0 |
|      2 |           29120 |      71 |         1 |               6 |         0     |               6 |         0     |                       0 |                 0     |        3 |
|      4 |           29120 |      71 |         1 |              14 |         0     |              14 |         0     |                       0 |                 0     |        1 |
|      8 |           29120 |      71 |         2 |              26 |         0.014 |              26 |         0     |                       0 |                 0     |        2 |
|     12 |           29119 |      72 |        34 |              49 |         0.278 |              48 |         0.083 |                      13 |                 0.181 |        5 |
|     17 |           29113 |      74 |        74 |              75 |         0.622 |              73 |         0.162 |                      39 |                 0.527 |        5 |
|     26 |           29108 |      78 |        78 |             124 |         0.795 |             119 |         0.205 |                      41 |                 0.526 |        2 |
|     52 |           29102 |      86 |        86 |             248 |         0.802 |             230 |         0.256 |                      85 |                 0.547 |        1 |
|     77 |           29098 |      97 |        97 |             382 |         0.773 |             350 |         0.299 |                     382 |                 0.557 |        6 |

- recall / precision: against mule accounts by the end of the horizon (fake accounts from opening, real customers from their start). precision_final_label: against launderers at any time in the 18 months.
- median_days_from_start: days from laundering start to the first flag, caught launderers only (negative = flagged before it started). A model flag is dated at the end of its week.
- catch_mean: per week the share of that week's mules already flagged, averaged over the weeks.
- Accounts closed by the bank stay in the cohort (caught by the rules); `open_accounts` counts the ones still open at the end of each week.
