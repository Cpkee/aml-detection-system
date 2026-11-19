# Harness, dry run: cohort opened in month(s) 0, 1, 2, 3, 4

Settings: `{"data": "data/v1_full", "cohort_months": [0, 1, 2, 3, 4], "horizons": [26], "model": null, "model_params_source": null, "model_git_commit": null, "model_machine": null, "machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "cohort_accounts": 164819, "launderers": 455, "budget_per_horizon": {"26": 828}, "score_source": "file:data/v1_full/scores/scorecard_tune_0.5.parquet", "scores_sha256": "5b462f7f1fda6439f0b4b5e9fd304a12ce91fc9a040fcb59ba72ed216ba3c507", "run_manifest_sha256": "4ce1c4fb593a8ae5f40e9acb082f1969655095c5a4977dc81f58c9026c62d7ba", "git_commit": "d23cf7e05daa7532c7abf29b7d4129c43805d09f", "git_uncommitted_changes": false, "retest_reason": null, "seconds": 3}`

Model vs rules on the same accounts. Each week since opening the model may flag as many accounts as the rules raised alerts on this cohort that week; a flag is permanent. `model_anytime`: a secondary policy, one score threshold over the horizon (on each account's highest score) flagging the same total number of accounts.

- The weekly budget counts the rules' alerts: an account alerted twice counts twice, so the model can flag slightly more distinct accounts than the rules (e.g. 124 vs 119 over weeks 0-26 in the month-5 dry run).
- The model is trained on weeks 0-26 only (models.train WEEKS); weeks 27-77 are outside its training range, so its running-total features drift there and late scores are not comparable across weeks.

## Weeks 0-26 (main): launderers who are mules by the end of week 26

|                        | model   | rules   | model_anytime   |
|:-----------------------|:--------|:--------|:----------------|
| flagged                | 828     | 780     | 828             |
| caught                 | 119     | 109     | 120             |
| mules                  | 361     | 361     | 361             |
| recall                 | 0.330   | 0.302   | 0.332           |
| recall_final_label     | 0.262   | 0.240   | 0.264           |
| precision              | 0.144   | 0.140   | 0.145           |
| false_alarm_share      | 0.856   | 0.860   | 0.855           |
| precision_final_label  | 0.144   | 0.141   | 0.145           |
| catch_mean             | 0.173   | 0.155   | 0.174           |
| median_days_from_start | 7       | 6       | 7               |
| flagged_before_start   | 1       | 0       | 1               |
| caught_fake            | 105/320 | 97/320  | 106/320         |
| caught_witting         | 5/16    | 2/16    | 5/16            |
| caught_unwitting       | 9/25    | 10/25   | 9/25            |

Ties at the cut line (decided by account id): 21 of 27 weeks, 595 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   361.0 |
| both                                |    32.0 |
| model_only                          |    87.0 |
| rules_only                          |    77.0 |
| either                              |   196.0 |
| neither                             |   165.0 |
| median_days_model_earlier_when_both |     1.0 |
| model_first_when_both               |    17.0 |
| rules_first_when_both               |    13.0 |
| median_min_days_earlier_model_only  |    91.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy        | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:--------------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model         | under 30 |      44463 |      70 |       26 |   0.3714 |              171 |                0.0039 |      0.132  |
| model         | 30-49    |      89206 |     155 |       48 |   0.3097 |              386 |                0.0043 |      0.1106 |
| model         | 50+      |      31150 |     136 |       45 |   0.3309 |              152 |                0.0049 |      0.2284 |
| rules         | under 30 |      44463 |      70 |       24 |   0.3429 |              164 |                0.0037 |      0.1277 |
| rules         | 30-49    |      89206 |     155 |       47 |   0.3032 |              378 |                0.0042 |      0.1106 |
| rules         | 50+      |      31150 |     136 |       38 |   0.2794 |              129 |                0.0042 |      0.2275 |
| model_anytime | under 30 |      44463 |      70 |       26 |   0.3714 |              175 |                0.0039 |      0.1294 |
| model_anytime | 30-49    |      89206 |     155 |       48 |   0.3097 |              386 |                0.0043 |      0.1106 |
| model_anytime | 50+      |      31150 |     136 |       46 |   0.3382 |              147 |                0.0047 |      0.2383 |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy        |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:--------------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model         |            0 |      32217 |      83 |       26 |   0.3133 |       188 |      0.1383 |           0.1955 |        0.2299 |        0.2271 |
| model         |            1 |      31076 |      68 |       17 |   0.25   |       155 |      0.1097 |           0.1885 |        0.1884 |        0.1872 |
| model         |            2 |      33523 |      64 |       25 |   0.3906 |       173 |      0.1445 |           0.2034 |        0.1773 |        0.2089 |
| model         |            3 |      36724 |      70 |       24 |   0.3429 |       167 |      0.1437 |           0.2228 |        0.1939 |        0.2017 |
| model         |            4 |      31279 |      76 |       27 |   0.3553 |       145 |      0.1862 |           0.1898 |        0.2105 |        0.1751 |
| rules         |            0 |      32217 |      83 |       26 |   0.3133 |       164 |      0.1585 |           0.1955 |        0.2299 |        0.2103 |
| rules         |            1 |      31076 |      68 |       25 |   0.3676 |       149 |      0.1678 |           0.1885 |        0.1884 |        0.191  |
| rules         |            2 |      33523 |      64 |       19 |   0.2969 |       165 |      0.1152 |           0.2034 |        0.1773 |        0.2115 |
| rules         |            3 |      36724 |      70 |       18 |   0.2571 |       150 |      0.12   |           0.2228 |        0.1939 |        0.1923 |
| rules         |            4 |      31279 |      76 |       21 |   0.2763 |       152 |      0.1382 |           0.1898 |        0.2105 |        0.1949 |
| model_anytime |            0 |      32217 |      83 |       26 |   0.3133 |       212 |      0.1226 |           0.1955 |        0.2299 |        0.256  |
| model_anytime |            1 |      31076 |      68 |       19 |   0.2794 |       220 |      0.0864 |           0.1885 |        0.1884 |        0.2657 |
| model_anytime |            2 |      33523 |      64 |       24 |   0.375  |       114 |      0.2105 |           0.2034 |        0.1773 |        0.1377 |
| model_anytime |            3 |      36724 |      70 |       24 |   0.3429 |       139 |      0.1727 |           0.2228 |        0.1939 |        0.1679 |
| model_anytime |            4 |      31279 |      76 |       27 |   0.3553 |       143 |      0.1888 |           0.1898 |        0.2105 |        0.1727 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   flagged_model_anytime |   catch_model_anytime |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|------------------------:|----------------------:|---------:|--------------:|
|      0 |          164819 |     320 |         0 |               8 |         0     |               8 |         0     |                      33 |                 0     |        8 |             0 |
|      2 |          164819 |     325 |         5 |              43 |         0     |              43 |         0     |                      68 |                 0     |       10 |            35 |
|      4 |          164819 |     332 |        12 |              92 |         0.012 |              91 |         0.003 |                     108 |                 0.012 |       30 |             0 |
|      8 |          164818 |     340 |        32 |             209 |         0.026 |             202 |         0.026 |                     219 |                 0.026 |       40 |            31 |
|     12 |          164800 |     344 |       176 |             360 |         0.16  |             349 |         0.142 |                     342 |                 0.157 |       41 |            23 |
|     17 |          164763 |     348 |       348 |             533 |         0.313 |             511 |         0.264 |                     554 |                 0.319 |       27 |             0 |
|     26 |          164735 |     361 |       361 |             828 |         0.33  |             780 |         0.302 |                     828 |                 0.332 |       24 |            22 |

- recall / precision: against mule accounts by the end of the horizon (fake accounts from opening, real customers from their start). recall_final_label / precision_final_label: against launderers at any time in the 18 months (label maturity).
- median_min_days_earlier_model_only: launderers caught by the model but not by the rules within the horizon; days from the model's flag to the end of the horizon, so the model is at least this many days earlier (the count is model_only).
- median_days_from_start: days from laundering start to the first flag, caught launderers only (negative = flagged before it started). A model flag is dated at the end of its week.
- catch_mean: per week the share of that week's mules already flagged, averaged over the weeks.
- Accounts closed by the bank stay in the cohort (caught by the rules); `open_accounts` counts the ones still open at the end of each week.
