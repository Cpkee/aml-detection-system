# Feature lab: drop-weak-and-copies-v1_full

data `v1_full`, groups added (none), families dropped cash_in_share_cum, abroad_out_share_cum, self_vs_past_rows, new_payer_share_wk, med_in_out_minutes_wk, out_1h_share_wk, n_rows_wk, high_risk_out_share_cum, money_out_wk, card_items_wk, n_payees_wk, passthrough_wk, n_out_wk, out_24h_share_wk, passthrough_4wk, max_out_wk, n_in_wk, n_payers_wk, self_vs_past_money_in, self_vs_past_payers, peer_ratio_money_in, n_in_4wk, n_payees_cum, views app, seed 42, commit bf43eac-dirty

Hypothesis: weak inputs plus 7 spare near-copies (notebook 07) add nothing measurable

Variants starting with `-` leave a family out. For them, 'better' = the model improved without it, 'no clear change' = it can go without a measurable loss, 'worse' = the model needs it.

## View `app`: baseline vs each variant (3 folds, months 0-4)

### weekly_recall (decides)

| variant   |   n_features |   weekly_recall_pooled |   weekly_recall |   d_weekly_recall | d_weekly_recall_folds    | weekly_recall_verdict   |
|:----------|-------------:|-----------------------:|----------------:|------------------:|:-------------------------|:------------------------|
| baseline  |           38 |                  0.402 |           0.407 |             0.000 | +0.000 / +0.000 / +0.000 |                         |
| -set      |           15 |                  0.398 |           0.400 |            -0.007 | +0.001 / -0.016 / -0.007 | no clear change         |

### acc_pr_auc

| variant   |   n_features |   acc_pr_auc |   d_acc_pr_auc | d_acc_pr_auc_folds       | acc_pr_auc_verdict   |
|:----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline  |           38 |        0.867 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| -set      |           15 |        0.847 |         -0.020 | -0.034 / -0.032 / +0.005 | no clear change      |

### caught_2wk

| variant   |   n_features |   caught_2wk |   d_caught_2wk | d_caught_2wk_folds       | caught_2wk_verdict   |
|:----------|-------------:|-------------:|---------------:|:-------------------------|:---------------------|
| baseline  |           38 |        0.880 |          0.000 | +0.000 / +0.000 / +0.000 |                      |
| -set      |           15 |        0.870 |         -0.010 | -0.031 / +0.000 / +0.000 | no clear change      |

- weekly_recall: share of each week's mules in that week's top 1% of open accounts, mean over weeks 0-26 (the tuning measure, decision 26 Oct 2026). `weekly_recall_pooled` pools the 3 validation months per week, as notebook 06 reports it; the per-fold column and the verdict use each fold alone.
- acc_pr_auc: account-level PR-AUC (an account's best week). caught_2wk: launderers starting in weeks 0-25 flagged in their start week or the next.
- verdict 'better' = all 3 folds improve and the mean gain is at least the noise level: weekly_recall 0.02, acc_pr_auc 0.04, caught_2wk 0.05 (PR-AUC: team rule; the others: assumptions).
- Real-customer mules in the account-level top 1% per fold (witting / unwitting) are in folds.csv.

