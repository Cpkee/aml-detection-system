# Feature lab: roll4-confirm-seed43

data `seed__43`, groups roll4, views app, seed 42, decides `catch_rules`, commit 68f0322-dirty

Hypothesis: One look (PLAN.md): does the adopted roll4 hold on fresh accounts (seed 43, never used by a trial) at the rules' budget?

## View `app`: baseline vs baseline + candidates (3 folds, months 0-4)

### catch_rules (decides)

| variant   |   n_features |   rules |   catch_rules |   d_catch_rules | d_catch_rules_folds      | catch_rules_verdict   |
|:----------|-------------:|--------:|--------------:|----------------:|:-------------------------|:----------------------|
| baseline  |           30 |   0.162 |         0.382 |           0.000 | +0.000 / +0.000 / +0.000 |                       |
| +roll4    |           38 |   0.162 |         0.452 |           0.070 | +0.076 / +0.079 / +0.055 | better                |

### weekly_recall

| variant   |   n_features |   weekly_recall_pooled |   weekly_recall |   d_weekly_recall | d_weekly_recall_folds    | weekly_recall_verdict   |
|:----------|-------------:|-----------------------:|----------------:|------------------:|:-------------------------|:------------------------|
| baseline  |           30 |                  0.347 |           0.359 |             0.000 | +0.000 / +0.000 / +0.000 |                         |
| +roll4    |           38 |                  0.400 |           0.406 |             0.047 | +0.047 / +0.048 / +0.045 | better                  |

### acc_pr_auc

| variant   |   n_features |   acc_pr_auc |   d_acc_pr_auc | d_acc_pr_auc_folds       | acc_pr_auc_verdict   |
|:----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline  |           30 |        0.691 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +roll4    |           38 |        0.859 |          0.168 | +0.167 / +0.195 / +0.142 | better               |

### caught_2wk

| variant   |   n_features |   caught_2wk |   d_caught_2wk | d_caught_2wk_folds       | caught_2wk_verdict   |
|:----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline  |           30 |        0.849 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +roll4    |           38 |        0.870 |          0.022 | -0.014 / +0.043 / +0.036 | no clear change      |

### catch_0.1pct

| variant   |   n_features |   rules |   catch_0.1pct |   d_catch_0.1pct | d_catch_0.1pct_folds     | catch_0.1pct_verdict   |
|:----------|-------------:|--------:|---------------:|-----------------:|:-------------------------|:-----------------------|
| baseline  |           30 |   0.162 |          0.501 |            0.000 | +0.000 / +0.000 / +0.000 |                        |
| +roll4    |           38 |   0.162 |          0.531 |            0.029 | +0.015 / +0.049 / +0.024 | better                 |

### Where the gain comes from (no verdict)

| variant   |   pre_start_recall | d_pre_start_recall_folds   |   start_recall | d_start_recall_folds     |   later_recall | d_later_recall_folds     |   first_caught_2wk | d_first_caught_2wk_folds   |
|:----------|-------------------:|:---------------------------|---------------:|:-------------------------|---------------:|:-------------------------|-------------------:|:---------------------------|
| baseline  |              0.126 | +0.000 / +0.000 / +0.000   |          0.697 | +0.000 / +0.000 / +0.000 |          0.536 | +0.000 / +0.000 / +0.000 |              0.941 | +0.000 / +0.000 / +0.000   |
| +roll4    |              0.109 | -0.053 / +0.005 / -0.003   |          0.772 | +0.069 / +0.051 / +0.104 |          0.645 | +0.143 / +0.098 / +0.088 |              0.963 | +0.000 / +0.043 / +0.024   |

Share of mule weeks in the weekly top 1%, by weeks since the account's laundering start: pre_start (fake accounts before they launder), start (start week and the next), later (2+ weeks after). first_caught_2wk: as caught_2wk, but a flag is permanent (decision 9 Oct 2026), so a mule flagged earlier counts as caught and later re-flags count for nothing.

### Catch curve at the rules' budget (mean of 3 folds)

Share of the accounts that are mules at week w already flagged by week w; flags are permanent and the model gets as many flags each week as the rules raised alerts.

| variant        |     0 |     2 |     4 |     8 |    12 |    17 |    26 |
|:---------------|------:|------:|------:|------:|------:|------:|------:|
| +roll4         | 0.000 | 0.010 | 0.014 | 0.033 | 0.408 | 0.837 | 0.872 |
| baseline       | 0.000 | 0.010 | 0.015 | 0.038 | 0.353 | 0.681 | 0.746 |
| rules (alerts) | 0.000 | 0.000 | 0.000 | 0.005 | 0.128 | 0.309 | 0.326 |

- weekly_recall: share of each week's mules in that week's top 1% of open accounts, mean over weeks 0-26 (the tuning measure, decision 26 Oct 2026). `weekly_recall_pooled` pools the 3 validation months per week, as notebook 06 reports it; the per-fold column and the verdict use each fold alone.
- catch_rules (proposal 28 Oct 2026): flags are permanent and limited to the rules' alert count in each week since opening on the same month's accounts; per week w the share of mule accounts (closed ones included) flagged by week w, averaged over weeks 0-26. `rules` = the same for the rules' own alerts. catch_0.1pct: the same with 0.1% of open accounts per week. Real-customer mules caught at the rules' budget per fold (`rules_budget_witting` / `_unwitting`) are in folds.csv.
- acc_pr_auc: account-level PR-AUC (an account's best week). caught_2wk: launderers starting in weeks 0-25 flagged in their start week or the next.
- verdict 'better' = all 3 folds improve and the mean gain is at least the noise level: weekly_recall 0.02, acc_pr_auc 0.04, caught_2wk 0.05, catch_rules 0.012, catch_0.1pct 0.005 (PR-AUC: team rule; the others: assumptions or placebo measurements, see the comments in feature_lab.py).
- Real-customer mules in the account-level top 1% per fold (witting / unwitting) are in folds.csv.

## Screen: AUC vs started launderers (95% interval over launderers)

| feature           | week 8            | week 12           | week 26           |
|:------------------|:------------------|:------------------|:------------------|
| money_in_4wk      | 0.624 (0.51-0.72) | 0.850 (0.82-0.88) | 0.641 (0.61-0.67) |
| money_out_4wk     | 0.680 (0.58-0.77) | 0.872 (0.84-0.90) | 0.642 (0.61-0.67) |
| n_in_4wk          | 0.691 (0.59-0.78) | 0.863 (0.84-0.89) | 0.581 (0.55-0.62) |
| n_payers_4wk      | 0.663 (0.57-0.75) | 0.821 (0.79-0.85) | 0.547 (0.52-0.58) |
| n_rows_4wk        | 0.665 (0.56-0.76) | 0.891 (0.86-0.92) | 0.583 (0.55-0.62) |
| out_1h_share_4wk  | 0.818 (0.73-0.91) | 0.947 (0.92-0.97) | 0.592 (0.57-0.62) |
| out_24h_share_4wk | 0.814 (0.72-0.89) | 0.917 (0.89-0.94) | 0.569 (0.54-0.60) |
| passthrough_4wk   | 0.565 (0.45-0.66) | 0.578 (0.55-0.61) | 0.474 (0.44-0.51) |

