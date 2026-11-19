# Harness, final test: cohort opened in month(s) 6, 7

Settings: `{"data": "/Users/cheepheng/aml-detection-system/data/variant_II", "cohort_months": [6, 7], "horizons": [26, 77], "model": "robust_avg5", "model_params_source": "file", "model_git_commit": "8e37e746b1721047ffe36a9585799e7db2a3c0a3", "model_machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "machine": {"os": "macOS-26.5.1-arm64-arm-64bit", "processor": "arm", "cpu_count": 15, "python": "3.12.15"}, "cohort_accounts": 50061, "launderers": 169, "budget_per_horizon": {"26": 265, "77": 716}, "score_source": "model:robust_avg5", "scores_sha256": null, "run_manifest_sha256": "994539a119411f70226522464122f071349c00e025727d6261553180cae20ad2", "git_commit": "e12b0d0223ea9cea8b27380f663deb82e2de3f52", "git_uncommitted_changes": false, "retest_reason": null, "seconds": 52}`

Model vs rules on the same accounts. Each week since opening the model may flag as many accounts as the rules raised alerts on this cohort that week; a flag is permanent. `model_anytime`: a secondary policy, one score threshold over the horizon (on each account's highest score) flagging the same total number of accounts.

- The weekly budget counts the rules' alerts: an account alerted twice counts twice, so the model can flag slightly more distinct accounts than the rules (e.g. 124 vs 119 over weeks 0-26 in the month-5 dry run).
- The model is trained on weeks 0-26 only (models.train WEEKS); weeks 27-77 are outside its training range, so its running-total features drift there and late scores are not comparable across weeks.

## Weeks 0-26 (main): launderers who are mules by the end of week 26

|                        | model   | rules   | model_anytime   |
|:-----------------------|:--------|:--------|:----------------|
| flagged                | 265     | 257     | 265             |
| caught                 | 134     | 57      | 139             |
| mules                  | 152     | 152     | 152             |
| recall                 | 0.882   | 0.375   | 0.914           |
| recall_final_label     | 0.793   | 0.337   | 0.822           |
| precision              | 0.506   | 0.222   | 0.525           |
| false_alarm_share      | 0.494   | 0.778   | 0.475           |
| precision_final_label  | 0.506   | 0.222   | 0.525           |
| catch_mean             | 0.460   | 0.190   | 0.477           |
| median_days_from_start | 7       | 9       | 6               |
| flagged_before_start   | 4       | 0       | 3               |
| caught_fake            | 126/138 | 53/138  | 130/138         |
| caught_witting         | 6/10    | 3/10    | 7/10            |
| caught_unwitting       | 2/4     | 1/4     | 2/4             |

Ties at the cut line (decided by account id): 0 of 27 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   152.0 |
| both                                |    55.0 |
| model_only                          |    79.0 |
| rules_only                          |     2.0 |
| either                              |   136.0 |
| neither                             |    16.0 |
| median_days_model_earlier_when_both |     3.0 |
| model_first_when_both               |    38.0 |
| rules_first_when_both               |    11.0 |
| median_min_days_earlier_model_only  |    84.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy        | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:--------------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model         | under 30 |       7532 |      14 |        9 |   0.6429 |                5 |                0.0007 |      0.6429 |
| model         | 30-49    |      17225 |      21 |       19 |   0.9048 |               39 |                0.0023 |      0.3276 |
| model         | 50+      |      25304 |     117 |      106 |   0.906  |               87 |                0.0035 |      0.5492 |
| rules         | under 30 |       7532 |      14 |        5 |   0.3571 |               17 |                0.0023 |      0.2273 |
| rules         | 30-49    |      17225 |      21 |        8 |   0.381  |               64 |                0.0037 |      0.1111 |
| rules         | 50+      |      25304 |     117 |       44 |   0.3761 |              119 |                0.0047 |      0.2699 |
| model_anytime | under 30 |       7532 |      14 |       10 |   0.7143 |                6 |                0.0008 |      0.625  |
| model_anytime | 30-49    |      17225 |      21 |       19 |   0.9048 |               41 |                0.0024 |      0.3167 |
| model_anytime | 50+      |      25304 |     117 |      110 |   0.9402 |               79 |                0.0031 |      0.582  |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy        |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:--------------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model         |            6 |      26529 |      78 |       70 |   0.8974 |       148 |      0.473  |           0.5299 |        0.5132 |        0.5585 |
| model         |            7 |      23532 |      74 |       64 |   0.8649 |       117 |      0.547  |           0.4701 |        0.4868 |        0.4415 |
| rules         |            6 |      26529 |      78 |       28 |   0.359  |       131 |      0.2137 |           0.5299 |        0.5132 |        0.5097 |
| rules         |            7 |      23532 |      74 |       29 |   0.3919 |       126 |      0.2302 |           0.4701 |        0.4868 |        0.4903 |
| model_anytime |            6 |      26529 |      78 |       74 |   0.9487 |       144 |      0.5139 |           0.5299 |        0.5132 |        0.5434 |
| model_anytime |            7 |      23532 |      74 |       65 |   0.8784 |       121 |      0.5372 |           0.4701 |        0.4868 |        0.4566 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   flagged_model_anytime |   catch_model_anytime |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|------------------------:|----------------------:|---------:|--------------:|
|      0 |           50061 |     138 |         0 |               1 |         0     |               1 |         0     |                       1 |                 0     |        1 |             0 |
|      2 |           50061 |     140 |         2 |              12 |         0.029 |              12 |         0.007 |                       2 |                 0.007 |        6 |             0 |
|      4 |           50061 |     141 |         3 |              28 |         0.043 |              28 |         0.007 |                      14 |                 0.028 |        9 |             0 |
|      8 |           50060 |     141 |        12 |              48 |         0.05  |              47 |         0.014 |                      31 |                 0.05  |        3 |             0 |
|     12 |           50051 |     144 |        72 |              99 |         0.354 |              96 |         0.139 |                     100 |                 0.389 |       12 |             0 |
|     17 |           50031 |     147 |       147 |             179 |         0.83  |             174 |         0.354 |                     197 |                 0.871 |       15 |             0 |
|     26 |           50018 |     152 |       152 |             265 |         0.882 |             257 |         0.375 |                     265 |                 0.914 |        8 |             0 |

## Weeks 0-77: launderers who are mules by the end of week 77

|                        | model   | rules   |
|:-----------------------|:--------|:--------|
| flagged                | 716     | 653     |
| caught                 | 147     | 63      |
| mules                  | 169     | 169     |
| recall                 | 0.870   | 0.373   |
| recall_final_label     | 0.870   | 0.373   |
| precision              | 0.205   | 0.096   |
| false_alarm_share      | 0.795   | 0.904   |
| precision_final_label  | 0.205   | 0.096   |
| catch_mean             | 0.729   | 0.309   |
| median_days_from_start | 7       | 9       |
| flagged_before_start   | 4       | 0       |
| caught_fake            | 128/138 | 55/138  |
| caught_witting         | 12/19   | 4/19    |
| caught_unwitting       | 7/12    | 4/12    |

`model_anytime`: not meaningful (model trained on weeks 0-26).

Ties at the cut line (decided by account id): 0 of 78 weeks, 0 tied accounts in all (weekly column `tied_at_cut`).

### Head to head (permanent model flags vs the rules' first alerts)

|                                     |   value |
|:------------------------------------|--------:|
| mules                               |   169.0 |
| both                                |    59.0 |
| model_only                          |    88.0 |
| rules_only                          |     4.0 |
| either                              |   151.0 |
| neither                             |    18.0 |
| median_days_model_earlier_when_both |     3.0 |
| model_first_when_both               |    42.0 |
| rules_first_when_both               |    11.0 |
| median_min_days_earlier_model_only  |   434.0 |

### By age band (recall; false_positive_rate = share of normal accounts flagged)

| policy   | age      |   accounts |   mules |   caught |   recall |   normal_flagged |   false_positive_rate |   precision |
|:---------|:---------|-----------:|--------:|---------:|---------:|-----------------:|----------------------:|------------:|
| model    | under 30 |       7532 |      23 |       14 |   0.6087 |               52 |                0.0069 |      0.2121 |
| model    | 30-49    |      17225 |      26 |       23 |   0.8846 |              158 |                0.0092 |      0.1271 |
| model    | 50+      |      25304 |     120 |      110 |   0.9167 |              359 |                0.0143 |      0.2345 |
| rules    | under 30 |       7532 |      23 |        8 |   0.3478 |               69 |                0.0092 |      0.1039 |
| rules    | 30-49    |      17225 |      26 |       10 |   0.3846 |              200 |                0.0116 |      0.0476 |
| rules    | 50+      |      25304 |     120 |       45 |   0.375  |              321 |                0.0127 |      0.123  |

### By opening month (calendar drift: share_flags far below share_mules = month under-ranked)

| policy   |   open_month |   accounts |   mules |   caught |   recall |   flagged |   precision |   share_accounts |   share_mules |   share_flags |
|:---------|-------------:|-----------:|--------:|---------:|---------:|----------:|------------:|-----------------:|--------------:|--------------:|
| model    |            6 |      26529 |      89 |       79 |   0.8876 |       436 |      0.1812 |           0.5299 |        0.5266 |        0.6089 |
| model    |            7 |      23532 |      80 |       68 |   0.85   |       280 |      0.2429 |           0.4701 |        0.4734 |        0.3911 |
| rules    |            6 |      26529 |      89 |       34 |   0.382  |       353 |      0.0963 |           0.5299 |        0.5266 |        0.5406 |
| rules    |            7 |      23532 |      80 |       29 |   0.3625 |       300 |      0.0967 |           0.4701 |        0.4734 |        0.4594 |

### By week since opening

|   week |   open_accounts |   mules |   started |   flagged_model |   catch_model |   flagged_rules |   catch_rules |   budget |   tied_at_cut |
|-------:|----------------:|--------:|----------:|----------------:|--------------:|----------------:|--------------:|---------:|--------------:|
|      0 |           50061 |     138 |         0 |               1 |         0     |               1 |         0     |        1 |             0 |
|      2 |           50061 |     140 |         2 |              12 |         0.029 |              12 |         0.007 |        6 |             0 |
|      4 |           50061 |     141 |         3 |              28 |         0.043 |              28 |         0.007 |        9 |             0 |
|      8 |           50060 |     141 |        12 |              48 |         0.05  |              47 |         0.014 |        3 |             0 |
|     12 |           50051 |     144 |        72 |              99 |         0.354 |              96 |         0.139 |       12 |             0 |
|     17 |           50031 |     147 |       147 |             179 |         0.83  |             174 |         0.354 |       15 |             0 |
|     26 |           50018 |     152 |       152 |             265 |         0.882 |             257 |         0.375 |        8 |             0 |
|     52 |           50016 |     158 |       158 |             494 |         0.861 |             459 |         0.367 |       12 |             0 |
|     77 |           50011 |     169 |       169 |             716 |         0.87  |             653 |         0.373 |        7 |             0 |

- recall / precision: against mule accounts by the end of the horizon (fake accounts from opening, real customers from their start). recall_final_label / precision_final_label: against launderers at any time in the 18 months (label maturity).
- median_min_days_earlier_model_only: launderers caught by the model but not by the rules within the horizon; days from the model's flag to the end of the horizon, so the model is at least this many days earlier (the count is model_only).
- median_days_from_start: days from laundering start to the first flag, caught launderers only (negative = flagged before it started). A model flag is dated at the end of its week.
- catch_mean: per week the share of that week's mules already flagged, averaged over the weeks.
- Accounts closed by the bank stay in the cohort (caught by the rules); `open_accounts` counts the ones still open at the end of each week.
