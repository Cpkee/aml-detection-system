# Feature lab: graph

data `v1_full`, groups graph_struct, graph_nb, views app, seed 42, decides `catch_rules`, commit dd63d9e-dirty

Hypothesis: Later chain members pay a member who started ~7 weeks earlier (153 of 163 launderer links); directed, money-weighted internal flows and neighbours already scored as suspicious should strengthen catching at the start (PLAN.md trial 3)

## View `app`: baseline vs baseline + candidates (3 folds, months 0-4)

### catch_rules (decides)

| variant       |   n_features |   rules |   catch_rules |   d_catch_rules | d_catch_rules_folds      | catch_rules_verdict   |
|:--------------|-------------:|--------:|--------------:|----------------:|:-------------------------|:----------------------|
| baseline      |           38 |   0.141 |         0.457 |           0.000 | +0.000 / +0.000 / +0.000 |                       |
| +graph_struct |           44 |   0.141 |         0.452 |          -0.005 | -0.011 / -0.004 / -0.001 | worse                 |
| +graph_nb     |           41 |   0.141 |         0.469 |           0.012 | -0.008 / +0.006 / +0.038 | no clear change       |
| +all          |           47 |   0.141 |         0.469 |           0.011 | +0.001 / +0.004 / +0.029 | no clear change       |

### weekly_recall

| variant       |   n_features |   weekly_recall_pooled |   weekly_recall |   d_weekly_recall | d_weekly_recall_folds    | weekly_recall_verdict   |
|:--------------|-------------:|-----------------------:|----------------:|------------------:|:-------------------------|:------------------------|
| baseline      |           38 |                  0.397 |           0.402 |             0.000 | +0.000 / +0.000 / +0.000 |                         |
| +graph_struct |           44 |                  0.402 |           0.405 |             0.002 | -0.015 / +0.009 / +0.014 | no clear change         |
| +graph_nb     |           41 |                  0.411 |           0.413 |             0.011 | -0.003 / +0.019 / +0.016 | no clear change         |
| +all          |           47 |                  0.411 |           0.415 |             0.013 | +0.008 / +0.013 / +0.018 | no clear change         |

### acc_pr_auc

| variant       |   n_features |   acc_pr_auc |   d_acc_pr_auc | d_acc_pr_auc_folds       | acc_pr_auc_verdict   |
|:--------------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline      |           38 |        0.870 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +graph_struct |           44 |        0.882 |          0.012 | +0.002 / +0.016 / +0.017 | no clear change      |
| +graph_nb     |           41 |        0.895 |          0.026 | +0.031 / +0.006 / +0.040 | no clear change      |
| +all          |           47 |        0.893 |          0.023 | +0.014 / +0.021 / +0.035 | no clear change      |

### caught_2wk

| variant       |   n_features |   caught_2wk |   d_caught_2wk | d_caught_2wk_folds       | caught_2wk_verdict   |
|:--------------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline      |           38 |        0.890 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| +graph_struct |           44 |        0.904 |          0.014 | +0.016 / +0.014 / +0.013 | no clear change      |
| +graph_nb     |           41 |        0.899 |          0.010 | +0.000 / +0.029 / +0.000 | no clear change      |
| +all          |           47 |        0.915 |          0.025 | +0.047 / +0.029 / +0.000 | no clear change      |

### catch_0.1pct

| variant       |   n_features |   rules |   catch_0.1pct |   d_catch_0.1pct | d_catch_0.1pct_folds     | catch_0.1pct_verdict   |
|:--------------|-------------:|--------:|---------------:|-----------------:|:-------------------------|:-----------------------|
| baseline      |           38 |   0.141 |          0.554 |            0.000 | +0.000 / +0.000 / +0.000 |                        |
| +graph_struct |           44 |   0.141 |          0.561 |            0.007 | +0.016 / -0.005 / +0.012 | no clear change        |
| +graph_nb     |           41 |   0.141 |          0.563 |            0.009 | +0.019 / -0.004 / +0.012 | no clear change        |
| +all          |           47 |   0.141 |          0.562 |            0.008 | +0.004 / -0.006 / +0.026 | no clear change        |

### Where the gain comes from (no verdict)

| variant       |   pre_start_recall | d_pre_start_recall_folds   |   start_recall | d_start_recall_folds     |   later_recall | d_later_recall_folds     |   first_caught_2wk | d_first_caught_2wk_folds   |
|:--------------|-------------------:|:---------------------------|---------------:|:-------------------------|---------------:|:-------------------------|-------------------:|:---------------------------|
| baseline      |              0.124 | +0.000 / +0.000 / +0.000   |          0.777 | +0.000 / +0.000 / +0.000 |          0.601 | +0.000 / +0.000 / +0.000 |              0.962 | +0.000 / +0.000 / +0.000   |
| +graph_struct |              0.120 | -0.008 / -0.017 / +0.016   |          0.798 | +0.016 / +0.014 / +0.033 |          0.605 | -0.027 / +0.030 / +0.008 |              0.957 | +0.000 / -0.014 / +0.000   |
| +graph_nb     |              0.120 | +0.006 / -0.023 / +0.007   |          0.808 | +0.024 / +0.043 / +0.026 |          0.622 | -0.014 / +0.051 / +0.023 |              0.957 | +0.000 / -0.029 / +0.013   |
| +all          |              0.115 | +0.000 / -0.026 / +0.000   |          0.806 | +0.031 / +0.036 / +0.020 |          0.632 | +0.013 / +0.043 / +0.036 |              0.961 | +0.000 / -0.014 / +0.013   |

Share of mule weeks in the weekly top 1%, by weeks since the account's laundering start: pre_start (fake accounts before they launder), start (start week and the next), later (2+ weeks after). first_caught_2wk: as caught_2wk, but a flag is permanent (decision 9 Oct 2026), so a mule flagged earlier counts as caught and later re-flags count for nothing.

### Catch curve at the rules' budget (mean of 3 folds)

Share of the accounts that are mules at week w already flagged by week w; flags are permanent and the model gets as many flags each week as the rules raised alerts.

| variant        |     0 |     2 |     4 |     8 |    12 |    17 |    26 |
|:---------------|------:|------:|------:|------:|------:|------:|------:|
| +all           | 0.000 | 0.000 | 0.044 | 0.103 | 0.398 | 0.801 | 0.891 |
| +graph_nb      | 0.000 | 0.005 | 0.054 | 0.096 | 0.397 | 0.806 | 0.892 |
| +graph_struct  | 0.000 | 0.000 | 0.049 | 0.088 | 0.373 | 0.782 | 0.864 |
| baseline       | 0.000 | 0.006 | 0.054 | 0.098 | 0.378 | 0.793 | 0.860 |
| rules (alerts) | 0.000 | 0.000 | 0.000 | 0.026 | 0.140 | 0.241 | 0.277 |

- weekly_recall: share of each week's mules in that week's top 1% of open accounts, mean over weeks 0-26 (the tuning measure, decision 26 Oct 2026). `weekly_recall_pooled` pools the 3 validation months per week, as notebook 06 reports it; the per-fold column and the verdict use each fold alone.
- catch_rules (proposal 28 Oct 2026): flags are permanent and limited to the rules' alert count in each week since opening on the same month's accounts; per week w the share of mule accounts (closed ones included) flagged by week w, averaged over weeks 0-26. `rules` = the same for the rules' own alerts. catch_0.1pct: the same with 0.1% of open accounts per week. Real-customer mules caught at the rules' budget per fold (`rules_budget_witting` / `_unwitting`) are in folds.csv.
- acc_pr_auc: account-level PR-AUC (an account's best week). caught_2wk: launderers starting in weeks 0-25 flagged in their start week or the next.
- verdict 'better' = all 3 folds improve and the mean gain is at least the noise level: weekly_recall 0.02, acc_pr_auc 0.04, caught_2wk 0.05, catch_rules 0.012, catch_0.1pct 0.005 (PR-AUC: team rule; the others: assumptions or placebo measurements, see the comments in feature_lab.py).
- Real-customer mules in the account-level top 1% per fold (witting / unwitting) are in folds.csv.

## Screen: AUC vs started launderers (95% interval over launderers)

| feature                | week 8            | week 12           | week 26           |
|:-----------------------|:------------------|:------------------|:------------------|
| g_int_fwd24h_share_4wk | 0.558 (0.47-0.65) | 0.549 (0.51-0.59) | 0.581 (0.55-0.61) |
| g_int_in_money_4wk     | 0.574 (0.48-0.67) | 0.548 (0.51-0.59) | 0.579 (0.55-0.61) |
| g_int_out_money_4wk    | 0.545 (0.45-0.64) | 0.607 (0.56-0.65) | 0.516 (0.48-0.55) |
| g_n_int_payers_4wk     | 0.552 (0.47-0.64) | 0.536 (0.50-0.57) | 0.556 (0.53-0.59) |
| g_n_nb_cum             | 0.558 (0.47-0.64) | 0.565 (0.52-0.61) | 0.586 (0.55-0.62) |
| g_n_nb_silent          | 0.516 (0.50-0.55) | 0.503 (0.50-0.51) | 0.553 (0.54-0.57) |
| g_nb_max_score         | 0.675 (0.55-0.78) | 0.664 (0.62-0.71) | 0.731 (0.70-0.76) |
| g_nb_max_score_4wk     | 0.634 (0.51-0.75) | 0.643 (0.60-0.69) | 0.588 (0.55-0.63) |
| g_nb_n_hot             | 0.623 (0.56-0.70) | 0.634 (0.60-0.67) | 0.685 (0.66-0.71) |

