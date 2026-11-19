# Harness, dry run: cohort opened in month(s) 0, 1, 2, 3, 4

Settings: `{"data": "data/v1_full", "cohort_months": [0, 1, 2, 3, 4], "horizons": [26], "model": null, "model_params_source": null, "model_git_commit": null, "model_machine": null, "machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "cohort_accounts": 164819, "launderers": 455, "budget_per_horizon": {"26": 828}, "score_source": "file:data/v1_full/scores/scorecard_tune_1.41.parquet", "scores_sha256": "ff40eb4488f763d51608adecb348f024c160dc5920b93d364d3d484639453f83", "run_manifest_sha256": "4ce1c4fb593a8ae5f40e9acb082f1969655095c5a4977dc81f58c9026c62d7ba", "git_commit": "d23cf7e05daa7532c7abf29b7d4129c43805d09f", "git_uncommitted_changes": false, "retest_reason": null, "seconds": 3}`

Model vs rules on the same accounts. Each week since opening the model may flag as many accounts as the rules raised alerts on this cohort that week; a flag is permanent. `model_anytime`: a secondary policy, one score threshold over the horizon (on each account's highest score) flagging the same total number of accounts.

- The weekly budget counts the rules' alerts: an account alerted twice counts twice, so the model can flag slightly more distinct accounts than the rules (e.g. 124 vs 119 over weeks 0-26 in the month-5 dry run).
- The model is trained on weeks 0-26 only (models.train WEEKS); weeks 27-77 are outside its training range, so its running-total features drift there and late scores are not comparable across weeks.

## Weeks 0-26 (main): launderers who are mules by the end of week 26

|                        | model   | rules   | model_anytime   |
|:-----------------------|:--------|:--------|:----------------|
| flagged                | 828     | 780     | 828             |
| caught                 | 155     | 109     | 154             |
| mules                  | 361     | 361     | 361             |
| recall                 | 0.429   | 0.302   | 0.427           |
| recall_final_label     | 0.341   | 0.240   | 0.338           |
| precision              | 0.187   | 0.140   | 0.186           |
| false_alarm_share      | 0.813   | 0.860   | 0.814           |
| precision_final_label  | 0.187   | 0.141   | 0.186           |
| catch_mean             | 0.218   | 0.155   | 0.215           |
| median_days_from_start | 8       | 6       | 9               |
| flagged_before_start   | 0       | 0       | 0               |
| caught_fake            | 138/320 | 97/320  | 137/320         |
| caught_witting         | 6/16    | 2/16    | 6/16            |
| caught_unwitting       | 11/25   | 10/25   | 11/25           |

Ties at the cut line (decided by account id): 15 of 27 weeks, 94 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   361.0 |
| both                                |    74.0 |
| model_only                          |    81.0 |
| rules_only                          |    35.0 |
| either                              |   190.0 |
| neither                             |   171.0 |
| median_days_model_earlier_when_both |     0.0 |
| model_first_when_both               |    32.0 |
| rules_first_when_both               |    34.0 |
| median_min_days_earlier_model_only  |    91.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy        | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:--------------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model         | under 30 |      44463 |      70 |       28 |   0.4    |              174 |                0.0039 |      0.1386 |
| model         | 30-49    |      89206 |     155 |       66 |   0.4258 |              373 |                0.0042 |      0.1503 |
| model         | 50+      |      31150 |     136 |       61 |   0.4485 |              126 |                0.0041 |      0.3262 |
| rules         | under 30 |      44463 |      70 |       24 |   0.3429 |              164 |                0.0037 |      0.1277 |
| rules         | 30-49    |      89206 |     155 |       47 |   0.3032 |              378 |                0.0042 |      0.1106 |
| rules         | 50+      |      31150 |     136 |       38 |   0.2794 |              129 |                0.0042 |      0.2275 |
| model_anytime | under 30 |      44463 |      70 |       28 |   0.4    |              175 |                0.0039 |      0.1379 |
| model_anytime | 30-49    |      89206 |     155 |       64 |   0.4129 |              372 |                0.0042 |      0.1468 |
| model_anytime | 50+      |      31150 |     136 |       62 |   0.4559 |              127 |                0.0041 |      0.328  |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy        |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:--------------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model         |            0 |      32217 |      83 |       34 |   0.4096 |       155 |      0.2194 |           0.1955 |        0.2299 |        0.1872 |
| model         |            1 |      31076 |      68 |       29 |   0.4265 |       159 |      0.1824 |           0.1885 |        0.1884 |        0.192  |
| model         |            2 |      33523 |      64 |       30 |   0.4688 |       170 |      0.1765 |           0.2034 |        0.1773 |        0.2053 |
| model         |            3 |      36724 |      70 |       28 |   0.4    |       185 |      0.1514 |           0.2228 |        0.1939 |        0.2234 |
| model         |            4 |      31279 |      76 |       34 |   0.4474 |       159 |      0.2138 |           0.1898 |        0.2105 |        0.192  |
| rules         |            0 |      32217 |      83 |       26 |   0.3133 |       164 |      0.1585 |           0.1955 |        0.2299 |        0.2103 |
| rules         |            1 |      31076 |      68 |       25 |   0.3676 |       149 |      0.1678 |           0.1885 |        0.1884 |        0.191  |
| rules         |            2 |      33523 |      64 |       19 |   0.2969 |       165 |      0.1152 |           0.2034 |        0.1773 |        0.2115 |
| rules         |            3 |      36724 |      70 |       18 |   0.2571 |       150 |      0.12   |           0.2228 |        0.1939 |        0.1923 |
| rules         |            4 |      31279 |      76 |       21 |   0.2763 |       152 |      0.1382 |           0.1898 |        0.2105 |        0.1949 |
| model_anytime |            0 |      32217 |      83 |       33 |   0.3976 |       152 |      0.2171 |           0.1955 |        0.2299 |        0.1836 |
| model_anytime |            1 |      31076 |      68 |       32 |   0.4706 |       160 |      0.2    |           0.1885 |        0.1884 |        0.1932 |
| model_anytime |            2 |      33523 |      64 |       29 |   0.4531 |       170 |      0.1706 |           0.2034 |        0.1773 |        0.2053 |
| model_anytime |            3 |      36724 |      70 |       28 |   0.4    |       200 |      0.14   |           0.2228 |        0.1939 |        0.2415 |
| model_anytime |            4 |      31279 |      76 |       32 |   0.4211 |       146 |      0.2192 |           0.1898 |        0.2105 |        0.1763 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   flagged_model_anytime |   catch_model_anytime |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|------------------------:|----------------------:|---------:|--------------:|
|      0 |          164819 |     320 |         0 |               8 |         0     |               8 |         0     |                      17 |                 0     |        8 |             5 |
|      2 |          164819 |     325 |         5 |              43 |         0     |              43 |         0     |                      69 |                 0     |       10 |             4 |
|      4 |          164819 |     332 |        12 |              92 |         0.006 |              91 |         0.003 |                     122 |                 0.006 |       30 |             8 |
|      8 |          164818 |     340 |        32 |             209 |         0.026 |             202 |         0.026 |                     240 |                 0.024 |       40 |             0 |
|     12 |          164800 |     344 |       176 |             360 |         0.201 |             349 |         0.142 |                     375 |                 0.18  |       41 |             8 |
|     17 |          164763 |     348 |       348 |             533 |         0.382 |             511 |         0.264 |                     581 |                 0.388 |       27 |             5 |
|     26 |          164735 |     361 |       361 |             828 |         0.429 |             780 |         0.302 |                     828 |                 0.427 |       24 |             0 |

- recall / precision: against mule accounts by the end of the horizon (fake accounts from opening, real customers from their start). recall_final_label / precision_final_label: against launderers at any time in the 18 months (label maturity).
- median_min_days_earlier_model_only: launderers caught by the model but not by the rules within the horizon; days from the model's flag to the end of the horizon, so the model is at least this many days earlier (the count is model_only).
- median_days_from_start: days from laundering start to the first flag, caught launderers only (negative = flagged before it started). A model flag is dated at the end of its week.
- catch_mean: per week the share of that week's mules already flagged, averaged over the weeks.
- Accounts closed by the bank stay in the cohort (caught by the rules); `open_accounts` counts the ones still open at the end of each week.
