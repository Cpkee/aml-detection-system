# Harness, dry run: cohort opened in month(s) 0, 1, 2, 3, 4

Settings: `{"data": "data/v1_full", "cohort_months": [0, 1, 2, 3, 4], "horizons": [26], "model": null, "model_params_source": null, "model_git_commit": null, "model_machine": null, "machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "cohort_accounts": 164819, "launderers": 455, "budget_per_horizon": {"26": 828}, "score_source": "file:data/v1_full/scores/scorecard_tune_0.71.parquet", "scores_sha256": "a4396c4d1d0eea3ddb992256c0085fac70a88fd5777616b32e583e2d47fb4f3f", "run_manifest_sha256": "4ce1c4fb593a8ae5f40e9acb082f1969655095c5a4977dc81f58c9026c62d7ba", "git_commit": "d23cf7e05daa7532c7abf29b7d4129c43805d09f", "git_uncommitted_changes": false, "retest_reason": null, "seconds": 3}`

Model vs rules on the same accounts. Each week since opening the model may flag as many accounts as the rules raised alerts on this cohort that week; a flag is permanent. `model_anytime`: a secondary policy, one score threshold over the horizon (on each account's highest score) flagging the same total number of accounts.

- The weekly budget counts the rules' alerts: an account alerted twice counts twice, so the model can flag slightly more distinct accounts than the rules (e.g. 124 vs 119 over weeks 0-26 in the month-5 dry run).
- The model is trained on weeks 0-26 only (models.train WEEKS); weeks 27-77 are outside its training range, so its running-total features drift there and late scores are not comparable across weeks.

## Weeks 0-26 (main): launderers who are mules by the end of week 26

|                        | model   | rules   | model_anytime   |
|:-----------------------|:--------|:--------|:----------------|
| flagged                | 828     | 780     | 828             |
| caught                 | 143     | 109     | 130             |
| mules                  | 361     | 361     | 361             |
| recall                 | 0.396   | 0.302   | 0.360           |
| recall_final_label     | 0.314   | 0.240   | 0.286           |
| precision              | 0.173   | 0.140   | 0.157           |
| false_alarm_share      | 0.827   | 0.860   | 0.843           |
| precision_final_label  | 0.173   | 0.141   | 0.157           |
| catch_mean             | 0.199   | 0.155   | 0.183           |
| median_days_from_start | 8       | 6       | 9               |
| flagged_before_start   | 0       | 0       | 0               |
| caught_fake            | 126/320 | 97/320  | 116/320         |
| caught_witting         | 6/16    | 2/16    | 5/16            |
| caught_unwitting       | 11/25   | 10/25   | 9/25            |

Ties at the cut line (decided by account id): 8 of 27 weeks, 81 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   361.0 |
| both                                |    47.0 |
| model_only                          |    96.0 |
| rules_only                          |    62.0 |
| either                              |   205.0 |
| neither                             |   156.0 |
| median_days_model_earlier_when_both |     0.0 |
| model_first_when_both               |    22.0 |
| rules_first_when_both               |    22.0 |
| median_min_days_earlier_model_only  |    87.5 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy        | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:--------------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model         | under 30 |      44463 |      70 |       30 |   0.4286 |              176 |                0.004  |      0.1456 |
| model         | 30-49    |      89206 |     155 |       57 |   0.3677 |              384 |                0.0043 |      0.1293 |
| model         | 50+      |      31150 |     136 |       56 |   0.4118 |              125 |                0.004  |      0.3094 |
| rules         | under 30 |      44463 |      70 |       24 |   0.3429 |              164 |                0.0037 |      0.1277 |
| rules         | 30-49    |      89206 |     155 |       47 |   0.3032 |              378 |                0.0042 |      0.1106 |
| rules         | 50+      |      31150 |     136 |       38 |   0.2794 |              129 |                0.0042 |      0.2275 |
| model_anytime | under 30 |      44463 |      70 |       27 |   0.3857 |              175 |                0.0039 |      0.1337 |
| model_anytime | 30-49    |      89206 |     155 |       48 |   0.3097 |              388 |                0.0044 |      0.1101 |
| model_anytime | 50+      |      31150 |     136 |       55 |   0.4044 |              135 |                0.0044 |      0.2895 |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy        |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:--------------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model         |            0 |      32217 |      83 |       31 |   0.3735 |       150 |      0.2067 |           0.1955 |        0.2299 |        0.1812 |
| model         |            1 |      31076 |      68 |       25 |   0.3676 |       155 |      0.1613 |           0.1885 |        0.1884 |        0.1872 |
| model         |            2 |      33523 |      64 |       30 |   0.4688 |       184 |      0.163  |           0.2034 |        0.1773 |        0.2222 |
| model         |            3 |      36724 |      70 |       28 |   0.4    |       182 |      0.1538 |           0.2228 |        0.1939 |        0.2198 |
| model         |            4 |      31279 |      76 |       29 |   0.3816 |       157 |      0.1847 |           0.1898 |        0.2105 |        0.1896 |
| rules         |            0 |      32217 |      83 |       26 |   0.3133 |       164 |      0.1585 |           0.1955 |        0.2299 |        0.2103 |
| rules         |            1 |      31076 |      68 |       25 |   0.3676 |       149 |      0.1678 |           0.1885 |        0.1884 |        0.191  |
| rules         |            2 |      33523 |      64 |       19 |   0.2969 |       165 |      0.1152 |           0.2034 |        0.1773 |        0.2115 |
| rules         |            3 |      36724 |      70 |       18 |   0.2571 |       150 |      0.12   |           0.2228 |        0.1939 |        0.1923 |
| rules         |            4 |      31279 |      76 |       21 |   0.2763 |       152 |      0.1382 |           0.1898 |        0.2105 |        0.1949 |
| model_anytime |            0 |      32217 |      83 |       29 |   0.3494 |       160 |      0.1812 |           0.1955 |        0.2299 |        0.1932 |
| model_anytime |            1 |      31076 |      68 |       23 |   0.3382 |       161 |      0.1429 |           0.1885 |        0.1884 |        0.1944 |
| model_anytime |            2 |      33523 |      64 |       26 |   0.4062 |       164 |      0.1585 |           0.2034 |        0.1773 |        0.1981 |
| model_anytime |            3 |      36724 |      70 |       25 |   0.3571 |       188 |      0.133  |           0.2228 |        0.1939 |        0.2271 |
| model_anytime |            4 |      31279 |      76 |       27 |   0.3553 |       155 |      0.1742 |           0.1898 |        0.2105 |        0.1872 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   flagged_model_anytime |   catch_model_anytime |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|------------------------:|----------------------:|---------:|--------------:|
|      0 |          164819 |     320 |         0 |               8 |         0     |               8 |         0     |                      18 |                 0     |        8 |            10 |
|      2 |          164819 |     325 |         5 |              43 |         0     |              43 |         0     |                      74 |                 0     |       10 |            16 |
|      4 |          164819 |     332 |        12 |              92 |         0.012 |              91 |         0.003 |                     124 |                 0.009 |       30 |             0 |
|      8 |          164818 |     340 |        32 |             209 |         0.029 |             202 |         0.026 |                     241 |                 0.024 |       40 |             0 |
|     12 |          164800 |     344 |       176 |             360 |         0.177 |             349 |         0.142 |                     369 |                 0.142 |       41 |             0 |
|     17 |          164763 |     348 |       348 |             533 |         0.351 |             511 |         0.264 |                     574 |                 0.339 |       27 |            14 |
|     26 |          164735 |     361 |       361 |             828 |         0.396 |             780 |         0.302 |                     828 |                 0.36  |       24 |             0 |

- recall / precision: against mule accounts by the end of the horizon (fake accounts from opening, real customers from their start). recall_final_label / precision_final_label: against launderers at any time in the 18 months (label maturity).
- median_min_days_earlier_model_only: launderers caught by the model but not by the rules within the horizon; days from the model's flag to the end of the horizon, so the model is at least this many days earlier (the count is model_only).
- median_days_from_start: days from laundering start to the first flag, caught launderers only (negative = flagged before it started). A model flag is dated at the end of its week.
- catch_mean: per week the share of that week's mules already flagged, averaged over the weeks.
- Accounts closed by the bank stay in the cohort (caught by the rules); `open_accounts` counts the ones still open at the end of each week.
