# LightGBM baseline (untuned), 3 temporal folds

Settings: `{"data": "data/v1_full", "weeks": [0, 26], "folds": ["(0, 1) -> 2", "(0, 1, 2) -> 3", "(0, 1, 2, 3) -> 4"], "dropped_features": [], "model": "LGBMClassifier(class_weight='balanced'), defaults otherwise", "seed": 42, "lightgbm": "4.7.0"}`

## Account level, mean of 3 folds (min to max)

| view | ROC-AUC | PR-AUC | P @0.5 | R @0.5 | F1 @0.5 | P @best | R @best | F1 @best | P top 1% | R top 1% | F1 top 1% |
|---|---|---|---|---|---|---|---|---|---|---|---|
| application | 0.743 (0.71-0.76) | 0.016 (0.01-0.03) | 0.017 (0.01-0.02) | 0.138 (0.03-0.20) | 0.028 (0.02-0.04) | 0.090 (0.02-0.23) | 0.138 (0.04-0.19) | 0.046 (0.03-0.07) | 0.021 (0.01-0.04) | 0.098 (0.07-0.14) | 0.035 (0.02-0.06) |
| activity | 0.990 (0.98-1.00) | 0.733 (0.70-0.79) | 0.002 (0.00-0.00) | 0.996 (0.99-1.00) | 0.005 (0.00-0.01) | 0.889 (0.80-0.95) | 0.632 (0.59-0.67) | 0.737 (0.71-0.77) | 0.182 (0.16-0.22) | 0.870 (0.86-0.89) | 0.300 (0.27-0.35) |
| combined | 0.954 (0.95-0.96) | 0.216 (0.17-0.31) | 0.039 (0.02-0.07) | 0.732 (0.53-0.91) | 0.073 (0.04-0.12) | 0.282 (0.24-0.32) | 0.331 (0.23-0.51) | 0.294 (0.23-0.37) | 0.109 (0.08-0.16) | 0.514 (0.43-0.64) | 0.180 (0.14-0.25) |

- **@0.5**: flag accounts whose highest weekly score is at least 0.5. With class weights this flags far more accounts than a bank could review.
- **@best**: the threshold with the highest F1 on that fold's own validation month (optimistic: the threshold is chosen on the data it is scored on).
- **top 1%**: flag the 1% highest-scoring accounts, the review-budget view the project uses.

## Each fold

|   fold | train_months   |   valid_month | view        |   accounts |   account_mules |   acc_pr_auc |   acc_top_1%_precision |   acc_top_1%_recall |   acc_top_1%_f1 | top_1%_fake   | top_1%_witting   | top_1%_unwitting   |
|-------:|:---------------|--------------:|:------------|-----------:|----------------:|-------------:|-----------------------:|--------------------:|----------------:|:--------------|:-----------------|:-------------------|
|      1 | 0-1            |             2 | application |      33523 |              64 |        0.007 |                  0.015 |               0.078 |           0.025 | 5/56          | 0/3              | 0/5                |
|      1 | 0-1            |             2 | activity    |      33523 |              64 |        0.702 |                  0.164 |               0.859 |           0.276 | 49/56         | 2/3              | 4/5                |
|      1 | 0-1            |             2 | combined    |      33523 |              64 |        0.166 |                  0.090 |               0.469 |           0.150 | 25/56         | 2/3              | 3/5                |
|      2 | 0-1-2          |             3 | application |      36724 |              70 |        0.008 |                  0.014 |               0.071 |           0.023 | 5/57          | 0/7              | 0/6                |
|      2 | 0-1-2          |             3 | activity    |      36724 |              70 |        0.711 |                  0.163 |               0.857 |           0.275 | 49/57         | 5/7              | 6/6                |
|      2 | 0-1-2          |             3 | combined    |      36724 |              70 |        0.167 |                  0.082 |               0.429 |           0.137 | 26/57         | 2/7              | 2/6                |
|      3 | 0-1-2-3        |             4 | application |      31279 |              76 |        0.032 |                  0.035 |               0.145 |           0.057 | 11/65         | 0/4              | 0/7                |
|      3 | 0-1-2-3        |             4 | activity    |      31279 |              76 |        0.787 |                  0.217 |               0.895 |           0.350 | 59/65         | 3/4              | 6/7                |
|      3 | 0-1-2-3        |             4 | combined    |      31279 |              76 |        0.315 |                  0.157 |               0.645 |           0.252 | 44/65         | 0/4              | 5/7                |

top_1%_<type> = mules of that hidden type in the top 1% / all mules of that type.

![01_pr_curve.png](01_pr_curve.png)

![02_roc_curve.png](02_roc_curve.png)

![03_metrics_by_fold.png](03_metrics_by_fold.png)

![04_by_week.png](04_by_week.png)

![05_importance.png](05_importance.png)

## By week since opening (pooled out-of-fold)

| view        |   week |   mules |   pr_auc |   precision_top_1pct |   recall_top_1pct |   f1_top_1pct |
|:------------|-------:|--------:|---------:|---------------------:|------------------:|--------------:|
| activity    |      0 |     178 |    0.002 |                0.005 |             0.028 |         0.008 |
| activity    |      1 |     179 |    0.004 |                0.004 |             0.022 |         0.007 |
| activity    |      4 |     187 |    0.029 |                0.009 |             0.048 |         0.015 |
| activity    |      8 |     194 |    0.022 |                0.013 |             0.067 |         0.022 |
| activity    |     12 |     187 |    0.190 |                0.060 |             0.326 |         0.101 |
| activity    |     17 |     171 |    0.298 |                0.087 |             0.515 |         0.148 |
| activity    |     26 |     167 |    0.187 |                0.067 |             0.407 |         0.115 |
| application |      0 |     178 |    0.010 |                0.021 |             0.118 |         0.035 |
| application |      1 |     179 |    0.010 |                0.021 |             0.117 |         0.035 |
| application |      4 |     187 |    0.010 |                0.021 |             0.112 |         0.035 |
| application |      8 |     194 |    0.010 |                0.021 |             0.108 |         0.035 |
| application |     12 |     187 |    0.010 |                0.021 |             0.112 |         0.035 |
| application |     17 |     171 |    0.009 |                0.020 |             0.117 |         0.034 |
| application |     26 |     167 |    0.008 |                0.019 |             0.114 |         0.032 |
| combined    |      0 |     178 |    0.010 |                0.021 |             0.118 |         0.035 |
| combined    |      1 |     179 |    0.010 |                0.021 |             0.117 |         0.035 |
| combined    |      4 |     187 |    0.011 |                0.021 |             0.112 |         0.035 |
| combined    |      8 |     194 |    0.012 |                0.025 |             0.129 |         0.041 |
| combined    |     12 |     187 |    0.038 |                0.034 |             0.187 |         0.058 |
| combined    |     17 |     171 |    0.092 |                0.051 |             0.304 |         0.088 |
| combined    |     26 |     167 |    0.041 |                0.038 |             0.234 |         0.066 |

## Top 15 features by gain: application

| feature                          |   share |
|:---------------------------------|--------:|
| housing_status                   |   0.090 |
| device_os                        |   0.067 |
| velocity_24h                     |   0.062 |
| credit_risk_score                |   0.060 |
| name_email_similarity            |   0.057 |
| session_length_in_minutes        |   0.055 |
| velocity_4w                      |   0.052 |
| bank_months_count                |   0.050 |
| current_address_months_count     |   0.048 |
| days_since_request               |   0.045 |
| date_of_birth_distinct_emails_4w |   0.045 |
| zip_count_4w                     |   0.043 |
| prev_address_months_count        |   0.042 |
| intended_balcon_amount           |   0.042 |
| velocity_6h                      |   0.041 |

## Top 15 features by gain: activity

| feature                |   share |
|:-----------------------|--------:|
| n_payers_cum           |   0.164 |
| internal_out_share_cum |   0.100 |
| out_1h_share_wk        |   0.088 |
| weeks_since_open       |   0.086 |
| money_in_cum           |   0.082 |
| money_out_cum          |   0.081 |
| max_in_wk              |   0.052 |
| n_rows_cum             |   0.044 |
| cash_in_share_cum      |   0.041 |
| max_out_wk             |   0.036 |
| money_out_wk           |   0.030 |
| self_vs_past_money_in  |   0.026 |
| n_payees_cum           |   0.025 |
| abroad_out_share_cum   |   0.020 |
| peer_ratio_money_in    |   0.019 |

## Top 15 features by gain: combined

| feature                          |   share |
|:---------------------------------|--------:|
| housing_status                   |   0.088 |
| device_os                        |   0.067 |
| velocity_24h                     |   0.051 |
| credit_risk_score                |   0.050 |
| name_email_similarity            |   0.049 |
| n_payers_cum                     |   0.047 |
| current_address_months_count     |   0.046 |
| bank_months_count                |   0.045 |
| session_length_in_minutes        |   0.042 |
| velocity_4w                      |   0.042 |
| prev_address_months_count        |   0.039 |
| days_since_request               |   0.039 |
| intended_balcon_amount           |   0.037 |
| date_of_birth_distinct_emails_4w |   0.037 |
| bank_branch_count_8w             |   0.037 |

