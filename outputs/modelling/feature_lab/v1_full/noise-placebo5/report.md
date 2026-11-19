# Feature lab: noise-placebo5

data `v1_full`, groups placebo1, placebo2, placebo3, placebo4, placebo5, views app, seed 42, decides `catch_rules`, commit dd63d9e-dirty

Hypothesis: Placebo trial: 5 groups of 8 store columns shuffled across accounts within each week carry no information; their gains measure refit noise for every measure (sets NOISE for catch_rules / catch_0.1pct)

## View `app`: baseline vs baseline + candidates (3 folds, months 0-4)

### catch_rules (decides)

| variant   |   n_features |   rules |   catch_rules |   d_catch_rules | d_catch_rules_folds      | catch_rules_verdict   |
|:----------|-------------:|--------:|--------------:|----------------:|:-------------------------|:----------------------|
| baseline  |           38 |   0.141 |         0.457 |           0.000 | +0.000 / +0.000 / +0.000 |                       |
| +placebo1 |           46 |   0.141 |         0.454 |          -0.004 | -0.001 / -0.011 / +0.001 | no noise level yet    |
| +placebo2 |           46 |   0.141 |         0.446 |          -0.011 | -0.013 / -0.018 / -0.002 | no noise level yet    |
| +placebo3 |           46 |   0.141 |         0.452 |          -0.005 | +0.000 / -0.019 / +0.003 | no noise level yet    |
| +placebo4 |           46 |   0.141 |         0.459 |           0.001 | +0.004 / -0.007 / +0.007 | no noise level yet    |
| +placebo5 |           46 |   0.141 |         0.462 |           0.005 | -0.002 / -0.005 / +0.022 | no noise level yet    |

### weekly_recall

| variant   |   n_features |   weekly_recall_pooled |   weekly_recall |   d_weekly_recall | d_weekly_recall_folds    | weekly_recall_verdict   |
|:----------|-------------:|-----------------------:|----------------:|------------------:|:-------------------------|:------------------------|
| baseline  |           38 |                  0.397 |           0.402 |             0.000 | +0.000 / +0.000 / +0.000 |                         |
| +placebo1 |           46 |                  0.396 |           0.402 |            -0.001 | -0.009 / -0.003 / +0.011 | no clear change         |
| +placebo2 |           46 |                  0.396 |           0.407 |             0.005 | +0.007 / -0.002 / +0.011 | no clear change         |
| +placebo3 |           46 |                  0.405 |           0.405 |             0.003 | +0.003 / -0.004 / +0.010 | no clear change         |
| +placebo4 |           46 |                  0.397 |           0.405 |             0.002 | -0.007 / -0.006 / +0.020 | no clear change         |
| +placebo5 |           46 |                  0.397 |           0.403 |             0.001 | -0.008 / -0.001 / +0.012 | no clear change         |

### acc_pr_auc

| variant   |   n_features |   acc_pr_auc |   d_acc_pr_auc | d_acc_pr_auc_folds       | acc_pr_auc_verdict   |
|:----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline  |           38 |        0.870 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +placebo1 |           46 |        0.866 |         -0.003 | -0.011 / +0.003 / -0.003 | no clear change      |
| +placebo2 |           46 |        0.865 |         -0.005 | -0.015 / -0.004 / +0.006 | no clear change      |
| +placebo3 |           46 |        0.864 |         -0.005 | -0.016 / -0.002 / +0.002 | no clear change      |
| +placebo4 |           46 |        0.872 |          0.003 | -0.002 / +0.005 / +0.005 | no clear change      |
| +placebo5 |           46 |        0.873 |          0.003 | -0.006 / +0.007 / +0.008 | no clear change      |

### caught_2wk

| variant   |   n_features |   caught_2wk |   d_caught_2wk | d_caught_2wk_folds       | caught_2wk_verdict   |
|:----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline  |           38 |        0.890 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +placebo1 |           46 |        0.889 |         -0.001 | -0.016 / +0.000 / +0.013 | no clear change      |
| +placebo2 |           46 |        0.910 |          0.020 | +0.047 / +0.000 / +0.013 | no clear change      |
| +placebo3 |           46 |        0.890 |          0.000 | +0.000 / +0.000 / +0.000 | no clear change      |
| +placebo4 |           46 |        0.894 |          0.004 | +0.000 / +0.000 / +0.013 | no clear change      |
| +placebo5 |           46 |        0.875 |         -0.015 | -0.031 / +0.000 / -0.013 | no clear change      |

### catch_0.1pct

| variant   |   n_features |   rules |   catch_0.1pct |   d_catch_0.1pct | d_catch_0.1pct_folds     | catch_0.1pct_verdict   |
|:----------|-------------:|--------:|---------------:|-----------------:|:-------------------------|:-----------------------|
| baseline  |           38 |   0.141 |          0.554 |            0.000 | +0.000 / +0.000 / +0.000 |                        |
| +placebo1 |           46 |   0.141 |          0.557 |            0.003 | +0.008 / +0.003 / -0.001 | no noise level yet     |
| +placebo2 |           46 |   0.141 |          0.552 |           -0.002 | -0.005 / +0.001 / -0.002 | no noise level yet     |
| +placebo3 |           46 |   0.141 |          0.551 |           -0.003 | +0.001 / -0.008 / -0.001 | no noise level yet     |
| +placebo4 |           46 |   0.141 |          0.553 |           -0.001 | -0.004 / -0.002 / +0.005 | no noise level yet     |
| +placebo5 |           46 |   0.141 |          0.555 |            0.002 | -0.012 / +0.011 / +0.006 | no noise level yet     |

### Where the gain comes from (no verdict)

| variant   |   pre_start_recall | d_pre_start_recall_folds   |   start_recall | d_start_recall_folds     |   later_recall | d_later_recall_folds     |   first_caught_2wk | d_first_caught_2wk_folds   |
|:----------|-------------------:|:---------------------------|---------------:|:-------------------------|---------------:|:-------------------------|-------------------:|:---------------------------|
| baseline  |              0.124 | +0.000 / +0.000 / +0.000   |          0.777 | +0.000 / +0.000 / +0.000 |          0.601 | +0.000 / +0.000 / +0.000 |              0.962 | +0.000 / +0.000 / +0.000   |
| +placebo1 |              0.124 | +0.000 / -0.001 / +0.004   |          0.774 | -0.016 / -0.007 / +0.013 |          0.600 | -0.016 / -0.004 / +0.017 |              0.947 | +0.000 / -0.043 / +0.000   |
| +placebo2 |              0.129 | +0.004 / -0.003 / +0.017   |          0.782 | +0.024 / -0.014 / +0.007 |          0.605 | +0.006 / +0.000 / +0.005 |              0.957 | +0.000 / -0.014 / +0.000   |
| +placebo3 |              0.133 | +0.021 / -0.012 / +0.019   |          0.781 | -0.008 / +0.007 / +0.013 |          0.598 | -0.010 / +0.000 / +0.000 |              0.952 | +0.000 / -0.029 / +0.000   |
| +placebo4 |              0.135 | +0.010 / +0.004 / +0.021   |          0.779 | +0.000 / -0.007 / +0.013 |          0.595 | -0.024 / -0.015 / +0.020 |              0.952 | +0.000 / -0.029 / +0.000   |
| +placebo5 |              0.124 | -0.006 / -0.001 / +0.007   |          0.770 | -0.016 / -0.007 / +0.000 |          0.605 | -0.008 / +0.000 / +0.018 |              0.952 | +0.000 / -0.029 / +0.000   |

Share of mule weeks in the weekly top 1%, by weeks since the account's laundering start: pre_start (fake accounts before they launder), start (start week and the next), later (2+ weeks after). first_caught_2wk: as caught_2wk, but a flag is permanent (decision 9 Oct 2026), so a mule flagged earlier counts as caught and later re-flags count for nothing.

### Catch curve at the rules' budget (mean of 3 folds)

Share of the accounts that are mules at week w already flagged by week w; flags are permanent and the model gets as many flags each week as the rules raised alerts.

| variant        |     0 |     2 |     4 |     8 |    12 |    17 |    26 |
|:---------------|------:|------:|------:|------:|------:|------:|------:|
| +placebo1      | 0.000 | 0.006 | 0.054 | 0.092 | 0.378 | 0.787 | 0.860 |
| +placebo2      | 0.000 | 0.000 | 0.049 | 0.082 | 0.378 | 0.782 | 0.845 |
| +placebo3      | 0.000 | 0.000 | 0.049 | 0.088 | 0.378 | 0.793 | 0.855 |
| +placebo4      | 0.000 | 0.000 | 0.049 | 0.103 | 0.388 | 0.798 | 0.868 |
| +placebo5      | 0.005 | 0.005 | 0.054 | 0.097 | 0.393 | 0.801 | 0.868 |
| baseline       | 0.000 | 0.006 | 0.054 | 0.098 | 0.378 | 0.793 | 0.860 |
| rules (alerts) | 0.000 | 0.000 | 0.000 | 0.026 | 0.140 | 0.241 | 0.277 |

## Noise from placebo groups

Each placebo group is 8 store columns shuffled across accounts within each week, so it carries no information about any account. The gain it brings is what refitting alone moves a measure by. proposed_noise = 2 x root mean square of the placebo gains (mean of 3 folds).

| measure          |   placebos |   mean_gain |   rms_gain |   max_abs_gain |   proposed_noise |   current_noise |   baseline_boot_sd_per_fold |
|:-----------------|-----------:|------------:|-----------:|---------------:|-----------------:|----------------:|----------------------------:|
| weekly_recall    |          5 |      0.0022 |     0.0029 |         0.0051 |           0.0058 |          0.0200 |                    nan      |
| acc_pr_auc       |          5 |     -0.0015 |     0.0039 |         0.0053 |           0.0078 |          0.0400 |                    nan      |
| caught_2wk       |          5 |      0.0018 |     0.0113 |         0.0201 |           0.0227 |          0.0500 |                    nan      |
| catch_rules      |          5 |     -0.0028 |     0.0062 |         0.0111 |           0.0123 |        nan      |                      0.0265 |
| catch_0.1pct     |          5 |     -0.0000 |     0.0023 |         0.0035 |           0.0046 |        nan      |                      0.0244 |
| pre_start_recall |          5 |      0.0056 |     0.0073 |         0.0119 |           0.0146 |        nan      |                    nan      |
| start_recall     |          5 |      0.0001 |     0.0049 |         0.0077 |           0.0097 |        nan      |                    nan      |
| later_recall     |          5 |     -0.0007 |     0.0039 |         0.0061 |           0.0077 |        nan      |                    nan      |
| first_caught_2wk |          5 |     -0.0095 |     0.0100 |         0.0143 |           0.0200 |        nan      |                    nan      |

- weekly_recall: share of each week's mules in that week's top 1% of open accounts, mean over weeks 0-26 (the tuning measure, decision 26 Oct 2026). `weekly_recall_pooled` pools the 3 validation months per week, as notebook 06 reports it; the per-fold column and the verdict use each fold alone.
- catch_rules (proposal 28 Oct 2026): flags are permanent and limited to the rules' alert count in each week since opening on the same month's accounts; per week w the share of mule accounts (closed ones included) flagged by week w, averaged over weeks 0-26. `rules` = the same for the rules' own alerts. catch_0.1pct: the same with 0.1% of open accounts per week. Real-customer mules caught at the rules' budget per fold (`rules_budget_witting` / `_unwitting`) are in folds.csv.
- acc_pr_auc: account-level PR-AUC (an account's best week). caught_2wk: launderers starting in weeks 0-25 flagged in their start week or the next.
- verdict 'better' = all 3 folds improve and the mean gain is at least the noise level: weekly_recall 0.02, acc_pr_auc 0.04, caught_2wk 0.05, catch_rules None, catch_0.1pct None (PR-AUC: team rule; the others: assumptions or placebo measurements, see the comments in feature_lab.py).
- Real-customer mules in the account-level top 1% per fold (witting / unwitting) are in folds.csv.

## Screen: AUC vs started launderers (95% interval over launderers)

| feature                   | week 8            | week 12           | week 26           |
|:--------------------------|:------------------|:------------------|:------------------|
| placebo1_money_in_wk      | 0.487 (0.39-0.58) | 0.546 (0.50-0.59) | 0.531 (0.50-0.57) |
| placebo1_money_out_wk     | 0.509 (0.41-0.60) | 0.500 (0.46-0.54) | 0.521 (0.49-0.56) |
| placebo1_n_in_wk          | 0.488 (0.40-0.57) | 0.506 (0.47-0.54) | 0.461 (0.43-0.49) |
| placebo1_n_payers_wk      | 0.454 (0.37-0.53) | 0.548 (0.50-0.59) | 0.516 (0.49-0.55) |
| placebo1_n_rows_wk        | 0.474 (0.37-0.58) | 0.536 (0.49-0.58) | 0.516 (0.48-0.55) |
| placebo1_out_1h_share_wk  | 0.456 (0.36-0.55) | 0.512 (0.48-0.55) | 0.529 (0.50-0.56) |
| placebo1_out_24h_share_wk | 0.657 (0.57-0.74) | 0.510 (0.47-0.55) | 0.509 (0.48-0.54) |
| placebo1_passthrough_wk   | 0.491 (0.39-0.59) | 0.482 (0.44-0.52) | 0.474 (0.44-0.51) |
| placebo2_money_in_wk      | 0.498 (0.40-0.60) | 0.547 (0.50-0.59) | 0.513 (0.48-0.54) |
| placebo2_money_out_wk     | 0.508 (0.40-0.61) | 0.512 (0.47-0.56) | 0.509 (0.48-0.54) |
| placebo2_n_in_wk          | 0.540 (0.45-0.63) | 0.516 (0.47-0.56) | 0.504 (0.47-0.53) |
| placebo2_n_payers_wk      | 0.531 (0.43-0.63) | 0.508 (0.47-0.55) | 0.476 (0.45-0.51) |
| placebo2_n_rows_wk        | 0.423 (0.33-0.51) | 0.470 (0.43-0.51) | 0.486 (0.45-0.52) |
| placebo2_out_1h_share_wk  | 0.533 (0.45-0.61) | 0.482 (0.44-0.52) | 0.499 (0.47-0.53) |
| placebo2_out_24h_share_wk | 0.521 (0.43-0.61) | 0.475 (0.44-0.51) | 0.504 (0.47-0.54) |
| placebo2_passthrough_wk   | 0.438 (0.36-0.52) | 0.497 (0.46-0.54) | 0.491 (0.46-0.52) |
| placebo3_money_in_wk      | 0.516 (0.41-0.62) | 0.499 (0.46-0.54) | 0.504 (0.47-0.54) |
| placebo3_money_out_wk     | 0.503 (0.40-0.60) | 0.496 (0.45-0.54) | 0.503 (0.47-0.54) |
| placebo3_n_in_wk          | 0.495 (0.39-0.60) | 0.518 (0.48-0.56) | 0.493 (0.46-0.52) |
| placebo3_n_payers_wk      | 0.395 (0.32-0.47) | 0.505 (0.47-0.54) | 0.504 (0.47-0.54) |
| placebo3_n_rows_wk        | 0.530 (0.45-0.61) | 0.502 (0.46-0.55) | 0.479 (0.45-0.51) |
| placebo3_out_1h_share_wk  | 0.558 (0.47-0.64) | 0.512 (0.48-0.55) | 0.502 (0.47-0.53) |
| placebo3_out_24h_share_wk | 0.457 (0.36-0.55) | 0.497 (0.46-0.54) | 0.501 (0.47-0.53) |
| placebo3_passthrough_wk   | 0.429 (0.34-0.52) | 0.492 (0.45-0.53) | 0.496 (0.46-0.53) |
| placebo4_money_in_wk      | 0.543 (0.44-0.65) | 0.502 (0.46-0.54) | 0.500 (0.47-0.53) |
| placebo4_money_out_wk     | 0.563 (0.47-0.65) | 0.437 (0.39-0.48) | 0.479 (0.44-0.51) |
| placebo4_n_in_wk          | 0.532 (0.45-0.61) | 0.484 (0.45-0.52) | 0.508 (0.48-0.54) |
| placebo4_n_payers_wk      | 0.432 (0.35-0.51) | 0.492 (0.45-0.53) | 0.480 (0.45-0.51) |
| placebo4_n_rows_wk        | 0.538 (0.43-0.64) | 0.523 (0.48-0.56) | 0.516 (0.48-0.55) |
| placebo4_out_1h_share_wk  | 0.454 (0.36-0.53) | 0.533 (0.49-0.57) | 0.493 (0.46-0.52) |
| placebo4_out_24h_share_wk | 0.478 (0.38-0.57) | 0.508 (0.47-0.55) | 0.530 (0.50-0.56) |
| placebo4_passthrough_wk   | 0.566 (0.47-0.66) | 0.559 (0.52-0.60) | 0.488 (0.46-0.52) |
| placebo5_money_in_wk      | 0.506 (0.40-0.61) | 0.472 (0.43-0.51) | 0.486 (0.45-0.52) |
| placebo5_money_out_wk     | 0.501 (0.39-0.61) | 0.506 (0.46-0.55) | 0.484 (0.45-0.52) |
| placebo5_n_in_wk          | 0.465 (0.39-0.54) | 0.504 (0.46-0.55) | 0.471 (0.44-0.50) |
| placebo5_n_payers_wk      | 0.518 (0.42-0.61) | 0.504 (0.46-0.55) | 0.473 (0.44-0.50) |
| placebo5_n_rows_wk        | 0.525 (0.42-0.62) | 0.495 (0.46-0.54) | 0.495 (0.46-0.53) |
| placebo5_out_1h_share_wk  | 0.517 (0.44-0.60) | 0.487 (0.45-0.52) | 0.522 (0.49-0.55) |
| placebo5_out_24h_share_wk | 0.569 (0.47-0.66) | 0.502 (0.46-0.54) | 0.505 (0.48-0.54) |
| placebo5_passthrough_wk   | 0.529 (0.43-0.62) | 0.527 (0.49-0.57) | 0.479 (0.45-0.51) |

