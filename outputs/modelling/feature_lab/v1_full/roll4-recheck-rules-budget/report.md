# Feature lab: roll4-recheck-rules-budget

data `v1_full`, groups roll4, views app, seed 42, decides `catch_rules`, commit dd63d9e-dirty

Hypothesis: Re-check the adopted 4-week windows at the rules budget with permanent flags (PLAN.md trial 1)

## View `app`: baseline vs baseline + candidates (3 folds, months 0-4)

### catch_rules (decides)

| variant   |   n_features |   rules |   catch_rules |   d_catch_rules | d_catch_rules_folds      | catch_rules_verdict   |
|:----------|-------------:|--------:|--------------:|----------------:|:-------------------------|:----------------------|
| baseline  |           30 |   0.141 |         0.381 |           0.000 | +0.000 / +0.000 / +0.000 |                       |
| +roll4    |           38 |   0.141 |         0.457 |           0.076 | +0.128 / +0.072 / +0.027 | better                |

### weekly_recall

| variant   |   n_features |   weekly_recall_pooled |   weekly_recall |   d_weekly_recall | d_weekly_recall_folds    | weekly_recall_verdict   |
|:----------|-------------:|-----------------------:|----------------:|------------------:|:-------------------------|:------------------------|
| baseline  |           30 |                  0.340 |           0.348 |             0.000 | +0.000 / +0.000 / +0.000 |                         |
| +roll4    |           38 |                  0.397 |           0.402 |             0.054 | +0.083 / +0.029 / +0.051 | better                  |

### acc_pr_auc

| variant   |   n_features |   acc_pr_auc |   d_acc_pr_auc | d_acc_pr_auc_folds       | acc_pr_auc_verdict   |
|:----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline  |           30 |        0.701 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +roll4    |           38 |        0.870 |          0.168 | +0.273 / +0.145 / +0.088 | better               |

### caught_2wk

| variant   |   n_features |   caught_2wk |   d_caught_2wk | d_caught_2wk_folds       | caught_2wk_verdict   |
|:----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline  |           30 |        0.874 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +roll4    |           38 |        0.890 |          0.016 | +0.062 / -0.029 / +0.013 | no clear change      |

### catch_0.1pct

| variant   |   n_features |   rules |   catch_0.1pct |   d_catch_0.1pct | d_catch_0.1pct_folds     | catch_0.1pct_verdict   |
|:----------|-------------:|--------:|---------------:|-----------------:|:-------------------------|:-----------------------|
| baseline  |           30 |   0.141 |          0.543 |            0.000 | +0.000 / +0.000 / +0.000 |                        |
| +roll4    |           38 |   0.141 |          0.554 |            0.011 | +0.030 / +0.000 / +0.003 | better                 |

### Where the gain comes from (no verdict)

| variant   |   pre_start_recall | d_pre_start_recall_folds   |   start_recall | d_start_recall_folds     |   later_recall | d_later_recall_folds     |   first_caught_2wk | d_first_caught_2wk_folds   |
|:----------|-------------------:|:---------------------------|---------------:|:-------------------------|---------------:|:-------------------------|-------------------:|:---------------------------|
| baseline  |              0.145 | +0.000 / +0.000 / +0.000   |          0.694 | +0.000 / +0.000 / +0.000 |          0.479 | +0.000 / +0.000 / +0.000 |              0.958 | +0.000 / +0.000 / +0.000   |
| +roll4    |              0.124 | +0.001 / -0.051 / -0.016   |          0.777 | +0.165 / +0.058 / +0.026 |          0.601 | +0.152 / +0.093 / +0.123 |              0.962 | -0.016 / +0.014 / +0.013   |

Share of mule weeks in the weekly top 1%, by weeks since the account's laundering start: pre_start (fake accounts before they launder), start (start week and the next), later (2+ weeks after). first_caught_2wk: as caught_2wk, but a flag is permanent (decision 9 Oct 2026), so a mule flagged earlier counts as caught and later re-flags count for nothing.

### Catch curve at the rules' budget (mean of 3 folds)

Share of the accounts that are mules at week w already flagged by week w; flags are permanent and the model gets as many flags each week as the rules raised alerts.

| variant        |     0 |     2 |     4 |     8 |    12 |    17 |    26 |
|:---------------|------:|------:|------:|------:|------:|------:|------:|
| +roll4         | 0.000 | 0.006 | 0.054 | 0.098 | 0.378 | 0.793 | 0.860 |
| baseline       | 0.000 | 0.011 | 0.032 | 0.066 | 0.334 | 0.682 | 0.708 |
| rules (alerts) | 0.000 | 0.000 | 0.000 | 0.026 | 0.140 | 0.241 | 0.277 |

- weekly_recall: share of each week's mules in that week's top 1% of open accounts, mean over weeks 0-26 (the tuning measure, decision 26 Oct 2026). `weekly_recall_pooled` pools the 3 validation months per week, as notebook 06 reports it; the per-fold column and the verdict use each fold alone.
- catch_rules (proposal 28 Oct 2026): flags are permanent and limited to the rules' alert count in each week since opening on the same month's accounts; per week w the share of mule accounts (closed ones included) flagged by week w, averaged over weeks 0-26. `rules` = the same for the rules' own alerts. catch_0.1pct: the same with 0.1% of open accounts per week. Real-customer mules caught at the rules' budget per fold (`rules_budget_witting` / `_unwitting`) are in folds.csv.
- acc_pr_auc: account-level PR-AUC (an account's best week). caught_2wk: launderers starting in weeks 0-25 flagged in their start week or the next.
- verdict 'better' = all 3 folds improve and the mean gain is at least the noise level: weekly_recall 0.02, acc_pr_auc 0.04, caught_2wk 0.05, catch_rules 0.012, catch_0.1pct 0.005 (PR-AUC: team rule; the others: assumptions or placebo measurements, see the comments in feature_lab.py).
- Real-customer mules in the account-level top 1% per fold (witting / unwitting) are in folds.csv.

## Screen: AUC vs started launderers (95% interval over launderers)

| feature           | week 8            | week 12           | week 26           |
|:------------------|:------------------|:------------------|:------------------|
| money_in_4wk      | 0.714 (0.61-0.80) | 0.830 (0.80-0.86) | 0.596 (0.56-0.63) |
| money_out_4wk     | 0.758 (0.66-0.84) | 0.855 (0.82-0.89) | 0.595 (0.56-0.63) |
| n_in_4wk          | 0.842 (0.77-0.90) | 0.886 (0.86-0.91) | 0.590 (0.56-0.62) |
| n_payers_4wk      | 0.811 (0.73-0.88) | 0.830 (0.80-0.86) | 0.572 (0.54-0.60) |
| n_rows_4wk        | 0.822 (0.73-0.90) | 0.880 (0.85-0.91) | 0.566 (0.53-0.60) |
| out_1h_share_4wk  | 0.901 (0.83-0.96) | 0.934 (0.91-0.96) | 0.572 (0.55-0.60) |
| out_24h_share_4wk | 0.882 (0.82-0.93) | 0.908 (0.88-0.93) | 0.585 (0.55-0.62) |
| passthrough_4wk   | 0.602 (0.52-0.68) | 0.541 (0.51-0.58) | 0.484 (0.45-0.52) |

