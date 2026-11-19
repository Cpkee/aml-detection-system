# Feature lab: drop-weak-tuned-v1_full

data `v1_full`, groups added (none), left out out_1h_share_wk, self_vs_past_rows, money_out_wk, passthrough_wk, max_out_wk, n_payees_wk, n_out_wk, out_24h_share_wk, card_items_wk, med_in_out_minutes_wk, new_payer_share_wk, passthrough_4wk, n_rows_wk, high_risk_out_share_cum, views app, seed 42, decides `weekly_recall`, LightGBM settings `outputs/modelling/models/v1_full/lgbm_tuning_step2/tuned_params.json`, commit 00d136e-dirty

Hypothesis: 14 inputs labelled weak by notebook 10 (tuned settings) add nothing measurable

Variants starting with `-` leave inputs out. For them, 'better' = the model improved without them, 'no clear change' = they can go without a measurable loss, 'worse' = the model needs them.

## View `app`: baseline vs each variant (3 folds, months 0-4)

### weekly_recall (decides)

| variant   |   n_features |   weekly_recall_pooled |   weekly_recall |   d_weekly_recall | d_weekly_recall_folds    | weekly_recall_verdict   |
|:----------|-------------:|-----------------------:|----------------:|------------------:|:-------------------------|:------------------------|
| baseline  |           38 |                  0.426 |           0.431 |             0.000 | +0.000 / +0.000 / +0.000 |                         |
| -set      |           24 |                  0.431 |           0.436 |             0.005 | +0.009 / +0.005 / -0.000 | no clear change         |

### acc_pr_auc

| variant   |   n_features |   acc_pr_auc |   d_acc_pr_auc | d_acc_pr_auc_folds       | acc_pr_auc_verdict   |
|:----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline  |           38 |        0.876 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| -set      |           24 |        0.838 |         -0.038 | -0.041 / -0.039 / -0.034 | worse                |

### caught_2wk

| variant   |   n_features |   caught_2wk |   d_caught_2wk | d_caught_2wk_folds       | caught_2wk_verdict   |
|:----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline  |           38 |        0.904 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| -set      |           24 |        0.899 |         -0.004 | +0.000 / +0.000 / -0.013 | no clear change      |

### catch_rules

| variant   |   n_features |   rules |   catch_rules |   d_catch_rules | d_catch_rules_folds      | catch_rules_verdict   |
|:----------|-------------:|--------:|--------------:|----------------:|:-------------------------|:----------------------|
| baseline  |           38 |   0.141 |         0.452 |           0.000 | +0.000 / +0.000 / +0.000 |                       |
| -set      |           24 |   0.141 |         0.452 |           0.000 | +0.009 / +0.002 / -0.010 | no clear change       |

### catch_0.1pct

| variant   |   n_features |   rules |   catch_0.1pct |   d_catch_0.1pct | d_catch_0.1pct_folds     | catch_0.1pct_verdict   |
|:----------|-------------:|--------:|---------------:|-----------------:|:-------------------------|:-----------------------|
| baseline  |           38 |   0.141 |          0.560 |            0.000 | +0.000 / +0.000 / +0.000 |                        |
| -set      |           24 |   0.141 |          0.554 |           -0.006 | -0.014 / -0.007 / +0.003 | no clear change        |

### Where the gain comes from (no verdict)

| variant   |   pre_start_recall | d_pre_start_recall_folds   |   start_recall | d_start_recall_folds     |   later_recall | d_later_recall_folds     |   first_caught_2wk | d_first_caught_2wk_folds   |
|:----------|-------------------:|:---------------------------|---------------:|:-------------------------|---------------:|:-------------------------|-------------------:|:---------------------------|
| baseline  |              0.141 | +0.000 / +0.000 / +0.000   |          0.800 | +0.000 / +0.000 / +0.000 |          0.642 | +0.000 / +0.000 / +0.000 |              0.966 | +0.000 / +0.000 / +0.000   |
| -set      |              0.151 | +0.018 / +0.007 / +0.004   |          0.790 | -0.016 / -0.007 / -0.007 |          0.645 | +0.005 / +0.005 / -0.003 |              0.966 | +0.000 / +0.000 / +0.000   |

Share of mule weeks in the weekly top 1%, by weeks since the account's laundering start: pre_start (fake accounts before they launder), start (start week and the next), later (2+ weeks after). first_caught_2wk: as caught_2wk, but a flag is permanent (decision 9 Oct 2026), so a mule flagged earlier counts as caught and later re-flags count for nothing.

### Catch curve at the rules' budget (mean of 3 folds)

Share of the accounts that are mules at week w already flagged by week w; flags are permanent and the model gets as many flags each week as the rules raised alerts.

| variant        |     0 |     2 |     4 |     8 |    12 |    17 |    26 |
|:---------------|------:|------:|------:|------:|------:|------:|------:|
| -set           | 0.000 | 0.000 | 0.049 | 0.093 | 0.388 | 0.788 | 0.854 |
| baseline       | 0.000 | 0.000 | 0.049 | 0.087 | 0.382 | 0.796 | 0.864 |
| rules (alerts) | 0.000 | 0.000 | 0.000 | 0.026 | 0.140 | 0.241 | 0.277 |

- weekly_recall: share of each week's mules in that week's top 1% of open accounts, mean over weeks 0-26 (the tuning measure, decision 26 Oct 2026). `weekly_recall_pooled` pools the 3 validation months per week, as notebook 06 reports it; the per-fold column and the verdict use each fold alone.
- catch_rules (proposal 28 Oct 2026): flags are permanent and limited to the rules' alert count in each week since opening on the same month's accounts; per week w the share of mule accounts (closed ones included) flagged by week w, averaged over weeks 0-26. `rules` = the same for the rules' own alerts. catch_0.1pct: the same with 0.1% of open accounts per week. Real-customer mules caught at the rules' budget per fold (`rules_budget_witting` / `_unwitting`) are in folds.csv.
- acc_pr_auc: account-level PR-AUC (an account's best week). caught_2wk: launderers starting in weeks 0-25 flagged in their start week or the next.
- verdict 'better' = all 3 folds improve and the mean gain is at least the noise level: weekly_recall 0.02, acc_pr_auc 0.04, caught_2wk 0.05, catch_rules 0.012, catch_0.1pct 0.005 (PR-AUC: team rule; the others: assumptions or placebo measurements, see the comments in feature_lab.py).
- Real-customer mules in the account-level top 1% per fold (witting / unwitting) are in folds.csv.

