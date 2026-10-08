# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, profiles.in_window_mix={"fake": 0.53, "witting": 0.235, "unwitting": 0.235}. Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

## Accounts by profile

| profile        |      n |   fraud_rows |
|:---------------|-------:|-------------:|
| normal         | 240899 |            0 |
| app_fraud_only |   2369 |         2369 |
| fake           |    388 |          388 |
| unwitting      |    172 |            0 |
| witting        |    172 |            0 |

## Activity per account (medians)

| profile        |   rows_per_month |   payments_per_month |   money_in_per_month |   money_out_per_month |   out_over_in |
|:---------------|-----------------:|---------------------:|---------------------:|----------------------:|--------------:|
| app_fraud_only |             24.5 |                 64.7 |                 5294 |                  3868 |          0.74 |
| fake           |             24.6 |                 62.4 |                 4759 |                  3588 |          0.75 |
| normal         |             24.5 |                 60.9 |                 4238 |                  3278 |          0.78 |
| unwitting      |             25   |                 58.9 |                 3821 |                  3144 |          0.81 |
| witting        |             24.9 |                 59.2 |                 3846 |                  3298 |          0.82 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32888758 |     30.267 |          129.47 |
| Normal_DirectDebit     | 32122137 |     29.561 |           42.05 |
| Normal_Card            | 19293390 |     17.755 |          260.67 |
| Normal_CashWithdrawal  |  8786130 |      8.086 |          140    |
| Normal_Salary          |  6380966 |      5.872 |         1942.83 |
| Normal_TransferIn      |  4389555 |      4.04  |          100.04 |
| Normal_StandingOrder   |  3521751 |      3.241 |           54.18 |
| Normal_CashDeposit     |   525674 |      0.484 |          149.89 |
| Normal_Cheque          |   440432 |      0.405 |          100.16 |
| Normal_Abroad          |   153619 |      0.141 |          450.51 |
| Normal_Bonus           |   104245 |      0.096 |         1243.05 |
| Normal_GroupCollection |    40934 |      0.038 |           20.01 |
| Structuring            |     5809 |      0.005 |          296.45 |
| Deposit-Send           |     1272 |      0.001 |          410.07 |
| Layered_Fan_In         |     1042 |      0.001 |          695.99 |
| Layered_Fan_Out        |      967 |      0.001 |          427.26 |
| Normal_LargeCash       |      781 |      0.001 |        14770    |
| Fan_In                 |      585 |      0.001 |          571.53 |
| Cycle                  |      568 |      0.001 |         1253.54 |
| Behavioural_Change_2   |      557 |      0.001 |          212.19 |
| Stacked Bipartite      |      548 |      0.001 |          463.4  |
| Gather-Scatter         |      530 |      0     |          559.6  |
| Behavioural_Change_1   |      470 |      0     |          217.5  |
| Scatter-Gather         |      417 |      0     |          502.31 |
| Bipartite              |      349 |      0     |          583.44 |
| Fan_Out                |      253 |      0     |          635.77 |
| Cash_Withdrawal        |      212 |      0     |          277.29 |
| Smurfing               |      142 |      0     |          171.37 |

## Laundering start (days after opening)

| profile   |   n |   min_rel |   median_rel |   max_rel |   pct_year1 |
|:----------|----:|----------:|-------------:|----------:|------------:|
| fake      | 388 |        60 |           92 |       120 |       100   |
| unwitting | 172 |         0 |          297 |       526 |        59.3 |
| witting   | 172 |         7 |          307 |       519 |        59.3 |

## Launderer networks

| net         |   n |
|:------------|----:|
| big network | 183 |
| chain       | 549 |

## Outgoing rows: abroad, high-risk, internal (%)

|   is_laundering |   pct_abroad |   pct_high_risk |   pct_internal |
|----------------:|-------------:|----------------:|---------------:|
|               0 |         0.16 |            0.03 |           2.75 |
|               1 |         1.56 |            0.39 |          24.94 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5204 |         4687 |      2.23571e+06 |
| unwitting |        4728 |         4184 | 888359           |
| witting   |        4692 |         4297 | 885933           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 5,912; true 162 -> false alarm share 97.3% (target 90-95%)
- Launderers alerted after their start: 162 of 732 (22%); accounts closed: 137

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      781 |             0 |
| R2     |      802 |             9 |
| R3     |      328 |             1 |
| R4     |      651 |           141 |
| R5     |        5 |             0 |
| R6     |     4506 |            20 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                     10 |          0 |        427 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   54.2 |                28 |            167 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          199 |        35 |       32 |
| Deposit-Send         |           95 |        18 |       17 |
| Layered_Fan_In       |           60 |        17 |       14 |
| Layered_Fan_Out      |           58 |         5 |        5 |
| Fan_In               |           46 |        13 |       10 |
| Behavioural_Change_2 |           41 |         0 |        0 |
| Gather-Scatter       |           38 |        11 |        8 |
| Behavioural_Change_1 |           34 |         6 |        6 |
| Cycle                |           34 |        25 |       22 |
| Stacked Bipartite    |           31 |         7 |        4 |
| Scatter-Gather       |           29 |         5 |        4 |
| Bipartite            |           28 |         6 |        6 |
| Fan_Out              |           17 |         8 |        6 |
| Cash_Withdrawal      |           14 |         5 |        3 |
| Smurfing             |            8 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.753 (average precision 0.107, base rate 0.0030)
- Application-only logistic AUC: 0.662
- Single-feature AUC: n_rows 0.492, money_in 0.501, money_out 0.507, max_in 0.584, n_senders 0.606, share_abroad 0.556, n_internal 0.654, spike 0.504
