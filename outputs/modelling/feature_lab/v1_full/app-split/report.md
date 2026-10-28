# Feature lab: app-split

data `v1_full`, groups app_split, views app, seed 42, decides `catch_rules`, commit dd63d9e-dirty

Hypothesis: The single app score is ~70% fake accounts and puts 0 of 32 real-customer mules in the top 1%; a separate real-customer score (label: mule by week 26 among accounts not mules at week 0) should let the trees use age and housing for recruited customers (PLAN.md trial 2)

## View `app`: baseline vs baseline + candidates (3 folds, months 0-4)

### catch_rules (decides)

| variant    |   n_features |   rules |   catch_rules |   d_catch_rules | d_catch_rules_folds      | catch_rules_verdict   |
|:-----------|-------------:|--------:|--------------:|----------------:|:-------------------------|:----------------------|
| baseline   |           38 |   0.141 |         0.457 |           0.000 | +0.000 / +0.000 / +0.000 |                       |
| +app_split |           39 |   0.141 |         0.449 |          -0.008 | -0.008 / -0.022 / +0.006 | no clear change       |

### weekly_recall

| variant    |   n_features |   weekly_recall_pooled |   weekly_recall |   d_weekly_recall | d_weekly_recall_folds    | weekly_recall_verdict   |
|:-----------|-------------:|-----------------------:|----------------:|------------------:|:-------------------------|:------------------------|
| baseline   |           38 |                  0.397 |           0.402 |             0.000 | +0.000 / +0.000 / +0.000 |                         |
| +app_split |           39 |                  0.359 |           0.361 |            -0.041 | -0.086 / -0.013 / -0.024 | worse                   |

### acc_pr_auc

| variant    |   n_features |   acc_pr_auc |   d_acc_pr_auc | d_acc_pr_auc_folds       | acc_pr_auc_verdict   |
|:-----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline   |           38 |        0.870 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +app_split |           39 |        0.811 |         -0.059 | -0.087 / -0.064 / -0.025 | worse                |

### caught_2wk

| variant    |   n_features |   caught_2wk |   d_caught_2wk | d_caught_2wk_folds       | caught_2wk_verdict   |
|:-----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline   |           38 |        0.890 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +app_split |           39 |        0.844 |         -0.046 | -0.094 / -0.043 / +0.000 | no clear change      |

### catch_0.1pct

| variant    |   n_features |   rules |   catch_0.1pct |   d_catch_0.1pct | d_catch_0.1pct_folds     | catch_0.1pct_verdict   |
|:-----------|-------------:|--------:|---------------:|-----------------:|:-------------------------|:-----------------------|
| baseline   |           38 |   0.141 |          0.554 |            0.000 | +0.000 / +0.000 / +0.000 |                        |
| +app_split |           39 |   0.141 |          0.528 |           -0.026 | -0.034 / -0.039 / -0.005 | worse                  |

### Where the gain comes from (no verdict)

| variant    |   pre_start_recall | d_pre_start_recall_folds   |   start_recall | d_start_recall_folds     |   later_recall | d_later_recall_folds     |   first_caught_2wk | d_first_caught_2wk_folds   |
|:-----------|-------------------:|:---------------------------|---------------:|:-------------------------|---------------:|:-------------------------|-------------------:|:---------------------------|
| baseline   |              0.124 | +0.000 / +0.000 / +0.000   |          0.777 | +0.000 / +0.000 / +0.000 |          0.601 | +0.000 / +0.000 / +0.000 |              0.962 | +0.000 / +0.000 / +0.000   |
| +app_split |              0.114 | -0.022 / +0.000 / -0.007   |          0.733 | -0.102 / -0.043 / +0.013 |          0.532 | -0.142 / -0.019 / -0.047 |              0.942 | -0.031 / -0.029 / +0.000   |

Share of mule weeks in the weekly top 1%, by weeks since the account's laundering start: pre_start (fake accounts before they launder), start (start week and the next), later (2+ weeks after). first_caught_2wk: as caught_2wk, but a flag is permanent (decision 9 Oct 2026), so a mule flagged earlier counts as caught and later re-flags count for nothing.

### Catch curve at the rules' budget (mean of 3 folds)

Share of the accounts that are mules at week w already flagged by week w; flags are permanent and the model gets as many flags each week as the rules raised alerts.

| variant        |     0 |     2 |     4 |     8 |    12 |    17 |    26 |
|:---------------|------:|------:|------:|------:|------:|------:|------:|
| +app_split     | 0.000 | 0.010 | 0.054 | 0.092 | 0.383 | 0.777 | 0.841 |
| baseline       | 0.000 | 0.006 | 0.054 | 0.098 | 0.378 | 0.793 | 0.860 |
| rules (alerts) | 0.000 | 0.000 | 0.000 | 0.026 | 0.140 | 0.241 | 0.277 |

- weekly_recall: share of each week's mules in that week's top 1% of open accounts, mean over weeks 0-26 (the tuning measure, decision 26 Oct 2026). `weekly_recall_pooled` pools the 3 validation months per week, as notebook 06 reports it; the per-fold column and the verdict use each fold alone.
- catch_rules (proposal 28 Oct 2026): flags are permanent and limited to the rules' alert count in each week since opening on the same month's accounts; per week w the share of mule accounts (closed ones included) flagged by week w, averaged over weeks 0-26. `rules` = the same for the rules' own alerts. catch_0.1pct: the same with 0.1% of open accounts per week. Real-customer mules caught at the rules' budget per fold (`rules_budget_witting` / `_unwitting`) are in folds.csv.
- acc_pr_auc: account-level PR-AUC (an account's best week). caught_2wk: launderers starting in weeks 0-25 flagged in their start week or the next.
- verdict 'better' = all 3 folds improve and the mean gain is at least the noise level: weekly_recall 0.02, acc_pr_auc 0.04, caught_2wk 0.05, catch_rules 0.012, catch_0.1pct 0.005 (PR-AUC: team rule; the others: assumptions or placebo measurements, see the comments in feature_lab.py).
- Real-customer mules in the account-level top 1% per fold (witting / unwitting) are in folds.csv.

## Screen: AUC vs started launderers (95% interval over launderers)

| feature        | week 8            | week 12           | week 26           |
|:---------------|:------------------|:------------------|:------------------|
| app_score_fake | 0.623 (0.50-0.74) | 0.807 (0.77-0.84) | 0.794 (0.76-0.82) |
| app_score_real | 0.624 (0.53-0.71) | 0.473 (0.43-0.51) | 0.476 (0.44-0.51) |

