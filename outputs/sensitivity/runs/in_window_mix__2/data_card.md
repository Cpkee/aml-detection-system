# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, profiles.in_window_mix={"fake": 0.56, "witting": 0.22, "unwitting": 0.22}. Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

## Accounts by profile

| profile        |      n |   fraud_rows |
|:---------------|-------:|-------------:|
| normal         | 240921 |            0 |
| app_fraud_only |   2347 |         2347 |
| fake           |    410 |          410 |
| unwitting      |    161 |            0 |
| witting        |    161 |            0 |

## Activity per account (medians)

| profile        |   rows_per_month |   payments_per_month |   money_in_per_month |   money_out_per_month |   out_over_in |
|:---------------|-----------------:|---------------------:|---------------------:|----------------------:|--------------:|
| app_fraud_only |             24.5 |                 64.7 |                 5287 |                  3868 |          0.74 |
| fake           |             24.2 |                 61.8 |                 4834 |                  3701 |          0.77 |
| normal         |             24.5 |                 60.9 |                 4238 |                  3278 |          0.78 |
| unwitting      |             25.2 |                 59.3 |                 3760 |                  3007 |          0.81 |
| witting        |             24.9 |                 57.2 |                 3395 |                  2923 |          0.81 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32886695 |     30.267 |          129.47 |
| Normal_DirectDebit     | 32120489 |     29.562 |           42.06 |
| Normal_Card            | 19292458 |     17.756 |          260.66 |
| Normal_CashWithdrawal  |  8785743 |      8.086 |          140    |
| Normal_Salary          |  6380368 |      5.872 |         1942.98 |
| Normal_TransferIn      |  4389359 |      4.04  |          100.04 |
| Normal_StandingOrder   |  3521618 |      3.241 |           54.18 |
| Normal_CashDeposit     |   525744 |      0.484 |          149.89 |
| Normal_Cheque          |   440427 |      0.405 |          100.16 |
| Normal_Abroad          |   153622 |      0.141 |          450.51 |
| Normal_Bonus           |   104234 |      0.096 |         1243.01 |
| Normal_GroupCollection |    40906 |      0.038 |           20.02 |
| Structuring            |     5543 |      0.005 |          284.05 |
| Deposit-Send           |     1377 |      0.001 |          449.15 |
| Layered_Fan_Out        |     1163 |      0.001 |          462.85 |
| Layered_Fan_In         |      883 |      0.001 |          729.09 |
| Normal_LargeCash       |      781 |      0.001 |        14770    |
| Gather-Scatter         |      668 |      0.001 |          579.55 |
| Cycle                  |      641 |      0.001 |         1525.33 |
| Behavioural_Change_2   |      640 |      0.001 |          238.21 |
| Behavioural_Change_1   |      489 |      0     |          223.99 |
| Stacked Bipartite      |      465 |      0     |          593.14 |
| Fan_Out                |      449 |      0     |          615.87 |
| Bipartite              |      370 |      0     |          572.13 |
| Scatter-Gather         |      340 |      0     |          535.97 |
| Fan_In                 |      302 |      0     |          568.32 |
| Cash_Withdrawal        |      213 |      0     |          267.03 |
| Smurfing               |      152 |      0     |          166.49 |

## Laundering start (days after opening)

| profile   |   n |   min_rel |   median_rel |   max_rel |   pct_year1 |
|:----------|----:|----------:|-------------:|----------:|------------:|
| fake      | 410 |        60 |           92 |       120 |       100   |
| unwitting | 161 |         0 |          303 |       525 |        57.8 |
| witting   | 161 |         7 |          308 |       526 |        59   |

## Launderer networks

| net         |   n |
|:------------|----:|
| big network | 183 |
| chain       | 549 |

## Outgoing rows: abroad, high-risk, internal (%)

|   is_laundering |   pct_abroad |   pct_high_risk |   pct_internal |
|----------------:|-------------:|----------------:|---------------:|
|               0 |         0.16 |            0.03 |           2.75 |
|               1 |         1.63 |            0.47 |          24.41 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5547 |         5240 |      2.50627e+06 |
| unwitting |        4525 |         3959 | 836773           |
| witting   |        4034 |         3608 | 810164           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 5,923; true 176 -> false alarm share 97.0% (target 90-95%)
- Launderers alerted after their start: 176 of 732 (24%); accounts closed: 148

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      781 |             0 |
| R2     |      803 |            10 |
| R3     |      329 |             1 |
| R4     |      667 |           159 |
| R5     |        5 |             0 |
| R6     |     4500 |            16 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        403 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   54.3 |                27 |            170 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          192 |        30 |       28 |
| Deposit-Send         |          102 |        26 |       20 |
| Layered_Fan_Out      |           64 |        13 |       11 |
| Layered_Fan_In       |           53 |        15 |       13 |
| Gather-Scatter       |           47 |        10 |        8 |
| Behavioural_Change_2 |           46 |         5 |        4 |
| Cycle                |           38 |        25 |       22 |
| Behavioural_Change_1 |           35 |         2 |        3 |
| Fan_Out              |           34 |        10 |       10 |
| Stacked Bipartite    |           28 |         8 |        6 |
| Bipartite            |           25 |         9 |        7 |
| Scatter-Gather       |           24 |        11 |        9 |
| Fan_In               |           23 |         5 |        5 |
| Cash_Withdrawal      |           13 |         1 |        2 |
| Smurfing             |            8 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.781 (average precision 0.138, base rate 0.0030)
- Application-only logistic AUC: 0.664
- Single-feature AUC: n_rows 0.481, money_in 0.493, money_out 0.497, max_in 0.580, n_senders 0.585, share_abroad 0.558, n_internal 0.641, spike 0.497
