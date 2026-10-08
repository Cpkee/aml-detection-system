# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, laundering.out_transfer_mean=1500. Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

## Accounts by profile

| profile        |      n |   fraud_rows |
|:---------------|-------:|-------------:|
| normal         | 241048 |            0 |
| app_fraud_only |   2220 |         2220 |
| fake           |    537 |          537 |
| witting        |     98 |            0 |
| unwitting      |     97 |            0 |

## Activity per account (medians)

| profile        |   rows_per_month |   payments_per_month |   money_in_per_month |   money_out_per_month |   out_over_in |
|:---------------|-----------------:|---------------------:|---------------------:|----------------------:|--------------:|
| app_fraud_only |             24.5 |                 64.7 |                 5311 |                  3889 |          0.74 |
| fake           |              7.9 |                 19   |                 2511 |                  2019 |          0.79 |
| normal         |             24.5 |                 60.9 |                 4238 |                  3278 |          0.78 |
| unwitting      |             22.2 |                 50.8 |                 3494 |                  2828 |          0.8  |
| witting        |             23.2 |                 51.7 |                 3237 |                  2756 |          0.8  |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32854034 |     30.264 |          129.45 |
| Normal_DirectDebit     | 32092798 |     29.563 |           42.05 |
| Normal_Card            | 19276022 |     17.757 |          260.64 |
| Normal_CashWithdrawal  |  8777962 |      8.086 |          140    |
| Normal_Salary          |  6375177 |      5.873 |         1942.61 |
| Normal_TransferIn      |  4385601 |      4.04  |          100.04 |
| Normal_StandingOrder   |  3518666 |      3.241 |           54.17 |
| Normal_CashDeposit     |   525061 |      0.484 |          149.89 |
| Normal_Cheque          |   440015 |      0.405 |          100.16 |
| Normal_Abroad          |   153431 |      0.141 |          450.53 |
| Normal_Bonus           |   104156 |      0.096 |         1242.99 |
| Normal_GroupCollection |    40909 |      0.038 |           20.02 |
| Structuring            |     4505 |      0.004 |          817.69 |
| Deposit-Send           |     1458 |      0.001 |         1229    |
| Normal_LargeCash       |      779 |      0.001 |        14753.6  |
| Cash_Withdrawal        |      730 |      0.001 |          289.43 |
| Layered_Fan_In         |      691 |      0.001 |         2012.64 |
| Fan_In                 |      684 |      0.001 |         1674.15 |
| Behavioural_Change_1   |      614 |      0.001 |          537.64 |
| Behavioural_Change_2   |      577 |      0.001 |          677.07 |
| Layered_Fan_Out        |      500 |      0     |         1233.72 |
| Cycle                  |      460 |      0     |         3836.96 |
| Gather-Scatter         |      378 |      0     |         1774.85 |
| Fan_Out                |      321 |      0     |         1638.11 |
| Scatter-Gather         |      309 |      0     |         1579.39 |
| Stacked Bipartite      |      289 |      0     |         1569.27 |
| Smurfing               |      181 |      0     |          380.45 |
| Bipartite              |      145 |      0     |         1701.03 |

## Laundering start (days after opening)

| profile   |   n |   min_rel |   median_rel |   max_rel |   pct_year1 |
|:----------|----:|----------:|-------------:|----------:|------------:|
| fake      | 537 |        60 |           92 |       120 |       100   |
| unwitting |  97 |        10 |          299 |       521 |        58.8 |
| witting   |  98 |         1 |          297 |       526 |        61.2 |

## Launderer networks

| net         |   n |
|:------------|----:|
| big network | 183 |
| chain       | 549 |

## Outgoing rows: abroad, high-risk, internal (%)

|   is_laundering |   pct_abroad |   pct_high_risk |   pct_internal |
|----------------:|-------------:|----------------:|---------------:|
|               0 |         0.16 |            0.03 |           2.75 |
|               1 |         1.4  |            0.36 |          18.82 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |    total_in |
|:----------|------------:|-------------:|------------:|
| fake      |       12465 |        10013 | 7.5876e+06  |
| unwitting |       10916 |         9238 | 1.24029e+06 |
| witting   |       10492 |         7619 | 1.21937e+06 |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 6,282; true 538 -> false alarm share 91.4% (target 90-95%)
- Launderers alerted after their start: 520 of 732 (71%); accounts closed: 433

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      780 |             1 |
| R2     |      836 |            45 |
| R3     |      328 |             0 |
| R4     |      978 |           469 |
| R5     |        5 |             0 |
| R6     |     4552 |            71 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      7 |          0 |        397 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   57.6 |                30 |            181 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          180 |       140 |      119 |
| Deposit-Send         |          114 |        83 |       70 |
| Layered_Fan_In       |           53 |        35 |       32 |
| Fan_In               |           50 |        38 |       32 |
| Behavioural_Change_1 |           49 |        18 |       18 |
| Behavioural_Change_2 |           47 |        25 |       22 |
| Layered_Fan_Out      |           39 |        23 |       20 |
| Gather-Scatter       |           37 |        29 |       25 |
| Cycle                |           36 |        28 |       23 |
| Stacked Bipartite    |           29 |        18 |       12 |
| Scatter-Gather       |           28 |        20 |       18 |
| Fan_Out              |           26 |        20 |       17 |
| Cash_Withdrawal      |           20 |        17 |       14 |
| Bipartite            |           14 |         9 |        7 |
| Smurfing             |           10 |         6 |        4 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.859 (average precision 0.479, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.255, money_in 0.371, money_out 0.357, max_in 0.724, n_senders 0.317, share_abroad 0.548, n_internal 0.346, spike 0.495
