# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, normal.internal_share_of_transfers=0.2. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             25.1 |                 65.3 |                 5407 |                  3889 |          0.73 |
| fake           |             24.9 |                 61.6 |                 4566 |                  3375 |          0.76 |
| normal         |             25.2 |                 61.5 |                 4338 |                  3278 |          0.76 |
| unwitting      |             25.2 |                 58.6 |                 3703 |                  2930 |          0.79 |
| witting        |             26.5 |                 58.5 |                 3571 |                  2831 |          0.77 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 35481296 |     31.897 |          129.45 |
| Normal_DirectDebit     | 32116908 |     28.872 |           42.05 |
| Normal_Card            | 19290062 |     17.341 |          260.66 |
| Normal_CashWithdrawal  |  8782375 |      7.895 |          140    |
| Normal_Salary          |  6380007 |      5.735 |         1942.61 |
| Normal_TransferIn      |  4387218 |      3.944 |          100.05 |
| Normal_StandingOrder   |  3521205 |      3.165 |           54.18 |
| Normal_CashDeposit     |   523911 |      0.471 |          150.35 |
| Normal_Cheque          |   439100 |      0.395 |          100.07 |
| Normal_Abroad          |   155005 |      0.139 |          450.13 |
| Normal_Bonus           |   104232 |      0.094 |         1243.01 |
| Normal_GroupCollection |    41807 |      0.038 |           20.06 |
| Structuring            |     5426 |      0.005 |          284.39 |
| Deposit-Send           |     1662 |      0.001 |          412.77 |
| Layered_Fan_Out        |      907 |      0.001 |          428.57 |
| Layered_Fan_In         |      794 |      0.001 |          715.49 |
| Normal_LargeCash       |      715 |      0.001 |        14823    |
| Cycle                  |      709 |      0.001 |         1436.55 |
| Behavioural_Change_1   |      627 |      0.001 |          205.27 |
| Behavioural_Change_2   |      581 |      0.001 |          227.71 |
| Gather-Scatter         |      550 |      0     |          568.51 |
| Fan_In                 |      451 |      0     |          557.51 |
| Fan_Out                |      378 |      0     |          678.69 |
| Scatter-Gather         |      376 |      0     |          505.16 |
| Cash_Withdrawal        |      325 |      0     |          270.87 |
| Bipartite              |      279 |      0     |          682    |
| Stacked Bipartite      |      240 |      0     |          465.5  |
| Smurfing               |      165 |      0     |          141.66 |

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
|               0 |         0.16 |            0.03 |           5.5  |
|               1 |         1.36 |            0.48 |          24.04 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        4965 |         4484 |      3.04834e+06 |
| unwitting |        4419 |         3561 | 493017           |
| witting   |        4111 |         3611 | 489469           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 3,605; true 235 -> false alarm share 93.5% (target 90-95%)
- Launderers alerted after their start: 232 of 732 (32%); accounts closed: 187

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      714 |             1 |
| R2     |      741 |            13 |
| R3     |      940 |             6 |
| R4     |     1380 |           213 |
| R5     |        7 |             0 |
| R6     |      925 |            16 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        412 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   32.8 |                36 |             79 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        47 |       39 |
| Deposit-Send         |          111 |        43 |       35 |
| Behavioural_Change_1 |           50 |         5 |        3 |
| Layered_Fan_Out      |           50 |        13 |       13 |
| Layered_Fan_In       |           46 |        22 |       18 |
| Behavioural_Change_2 |           44 |         7 |        5 |
| Gather-Scatter       |           43 |        17 |       13 |
| Cycle                |           40 |        31 |       25 |
| Fan_In               |           33 |        10 |        7 |
| Scatter-Gather       |           27 |        10 |        8 |
| Fan_Out              |           25 |        11 |        9 |
| Bipartite            |           24 |         6 |        4 |
| Stacked Bipartite    |           22 |         2 |        2 |
| Cash_Withdrawal      |           18 |         8 |        6 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.747 (average precision 0.218, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.466, money_in 0.481, money_out 0.483, max_in 0.586, n_senders 0.535, share_abroad 0.554, n_internal 0.535, spike 0.479
