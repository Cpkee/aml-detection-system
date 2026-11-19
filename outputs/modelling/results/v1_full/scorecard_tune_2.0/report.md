# Harness, dry run: cohort opened in month(s) 0, 1, 2, 3, 4

Settings: `{"data": "data/v1_full", "cohort_months": [0, 1, 2, 3, 4], "horizons": [26], "model": null, "model_params_source": null, "model_git_commit": null, "model_machine": null, "machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "cohort_accounts": 164819, "launderers": 455, "budget_per_horizon": {"26": 828}, "score_source": "file:data/v1_full/scores/scorecard_tune_2.0.parquet", "scores_sha256": "23d40d4a9319e96606c50aaba4aac47d22806977b7ee7367b2392f685fbdba64", "run_manifest_sha256": "4ce1c4fb593a8ae5f40e9acb082f1969655095c5a4977dc81f58c9026c62d7ba", "git_commit": "d23cf7e05daa7532c7abf29b7d4129c43805d09f", "git_uncommitted_changes": false, "retest_reason": null, "seconds": 3}`

Model vs rules on the same accounts. Each week since opening the model may flag as many accounts as the rules raised alerts on this cohort that week; a flag is permanent. `model_anytime`: a secondary policy, one score threshold over the horizon (on each account's highest score) flagging the same total number of accounts.

- The weekly budget counts the rules' alerts: an account alerted twice counts twice, so the model can flag slightly more distinct accounts than the rules (e.g. 124 vs 119 over weeks 0-26 in the month-5 dry run).
- The model is trained on weeks 0-26 only (models.train WEEKS); weeks 27-77 are outside its training range, so its running-total features drift there and late scores are not comparable across weeks.

## Weeks 0-26 (main): launderers who are mules by the end of week 26

|                        | model   | rules   | model_anytime   |
|:-----------------------|:--------|:--------|:----------------|
| flagged                | 828     | 780     | 828             |
| caught                 | 164     | 109     | 168             |
| mules                  | 361     | 361     | 361             |
| recall                 | 0.454   | 0.302   | 0.465           |
| recall_final_label     | 0.360   | 0.240   | 0.369           |
| precision              | 0.198   | 0.140   | 0.203           |
| false_alarm_share      | 0.802   | 0.860   | 0.797           |
| precision_final_label  | 0.198   | 0.141   | 0.203           |
| catch_mean             | 0.238   | 0.155   | 0.472           |
| median_days_from_start | 8       | 6       | -84             |
| flagged_before_start   | 0       | 0       | 168             |
| caught_fake            | 148/320 | 97/320  | 152/320         |
| caught_witting         | 4/16    | 2/16    | 4/16            |
| caught_unwitting       | 12/25   | 10/25   | 12/25           |

Ties at the cut line (decided by account id): 23 of 27 weeks, 2958658 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   361.0 |
| both                                |    88.0 |
| model_only                          |    76.0 |
| rules_only                          |    21.0 |
| either                              |   185.0 |
| neither                             |   176.0 |
| median_days_model_earlier_when_both |     0.0 |
| model_first_when_both               |    40.0 |
| rules_first_when_both               |    39.0 |
| median_min_days_earlier_model_only  |    84.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy        | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:--------------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model         | under 30 |      44463 |      70 |       29 |   0.4143 |              169 |                0.0038 |      0.1465 |
| model         | 30-49    |      89206 |     155 |       71 |   0.4581 |              357 |                0.004  |      0.1659 |
| model         | 50+      |      31150 |     136 |       64 |   0.4706 |              138 |                0.0044 |      0.3168 |
| rules         | under 30 |      44463 |      70 |       24 |   0.3429 |              164 |                0.0037 |      0.1277 |
| rules         | 30-49    |      89206 |     155 |       47 |   0.3032 |              378 |                0.0042 |      0.1106 |
| rules         | 50+      |      31150 |     136 |       38 |   0.2794 |              129 |                0.0042 |      0.2275 |
| model_anytime | under 30 |      44463 |      70 |       30 |   0.4286 |              163 |                0.0037 |      0.1554 |
| model_anytime | 30-49    |      89206 |     155 |       73 |   0.471  |              363 |                0.0041 |      0.1674 |
| model_anytime | 50+      |      31150 |     136 |       65 |   0.4779 |              134 |                0.0043 |      0.3266 |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy        |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:--------------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model         |            0 |      32217 |      83 |       32 |   0.3855 |       259 |      0.1236 |           0.1955 |        0.2299 |        0.3128 |
| model         |            1 |      31076 |      68 |       34 |   0.5    |       135 |      0.2519 |           0.1885 |        0.1884 |        0.163  |
| model         |            2 |      33523 |      64 |       32 |   0.5    |       143 |      0.2238 |           0.2034 |        0.1773 |        0.1727 |
| model         |            3 |      36724 |      70 |       34 |   0.4857 |       157 |      0.2166 |           0.2228 |        0.1939 |        0.1896 |
| model         |            4 |      31279 |      76 |       32 |   0.4211 |       134 |      0.2388 |           0.1898 |        0.2105 |        0.1618 |
| rules         |            0 |      32217 |      83 |       26 |   0.3133 |       164 |      0.1585 |           0.1955 |        0.2299 |        0.2103 |
| rules         |            1 |      31076 |      68 |       25 |   0.3676 |       149 |      0.1678 |           0.1885 |        0.1884 |        0.191  |
| rules         |            2 |      33523 |      64 |       19 |   0.2969 |       165 |      0.1152 |           0.2034 |        0.1773 |        0.2115 |
| rules         |            3 |      36724 |      70 |       18 |   0.2571 |       150 |      0.12   |           0.2228 |        0.1939 |        0.1923 |
| rules         |            4 |      31279 |      76 |       21 |   0.2763 |       152 |      0.1382 |           0.1898 |        0.2105 |        0.1949 |
| model_anytime |            0 |      32217 |      83 |       33 |   0.3976 |       213 |      0.1549 |           0.1955 |        0.2299 |        0.2572 |
| model_anytime |            1 |      31076 |      68 |       35 |   0.5147 |       143 |      0.2448 |           0.1885 |        0.1884 |        0.1727 |
| model_anytime |            2 |      33523 |      64 |       33 |   0.5156 |       153 |      0.2157 |           0.2034 |        0.1773 |        0.1848 |
| model_anytime |            3 |      36724 |      70 |       34 |   0.4857 |       170 |      0.2    |           0.2228 |        0.1939 |        0.2053 |
| model_anytime |            4 |      31279 |      76 |       33 |   0.4342 |       149 |      0.2215 |           0.1898 |        0.2105 |        0.18   |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   flagged_model_anytime |   catch_model_anytime |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|------------------------:|----------------------:|---------:|--------------:|
|      0 |          164819 |     320 |         0 |               8 |         0     |               8 |         0     |                     828 |                 0.475 |        8 |             5 |
|      2 |          164819 |     325 |         5 |              43 |         0     |              43 |         0     |                     828 |                 0.474 |       10 |             4 |
|      4 |          164819 |     332 |        12 |              92 |         0.012 |              91 |         0.003 |                     828 |                 0.473 |       30 |        164733 |
|      8 |          164818 |     340 |        32 |             209 |         0.032 |             202 |         0.026 |                     828 |                 0.474 |       40 |        164622 |
|     12 |          164800 |     344 |       176 |             360 |         0.212 |             349 |         0.142 |                     828 |                 0.474 |       41 |        164466 |
|     17 |          164763 |     348 |       348 |             533 |         0.428 |             511 |         0.264 |                     828 |                 0.474 |       27 |             0 |
|     26 |          164735 |     361 |       361 |             828 |         0.454 |             780 |         0.302 |                     828 |                 0.465 |       24 |        163981 |

- recall / precision: against mule accounts by the end of the horizon (fake accounts from opening, real customers from their start). recall_final_label / precision_final_label: against launderers at any time in the 18 months (label maturity).
- median_min_days_earlier_model_only: launderers caught by the model but not by the rules within the horizon; days from the model's flag to the end of the horizon, so the model is at least this many days earlier (the count is model_only).
- median_days_from_start: days from laundering start to the first flag, caught launderers only (negative = flagged before it started). A model flag is dated at the end of its week.
- catch_mean: per week the share of that week's mules already flagged, averaged over the weeks.
- Accounts closed by the bank stay in the cohort (caught by the rules); `open_accounts` counts the ones still open at the end of each week.
