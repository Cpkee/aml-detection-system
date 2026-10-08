# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, normal.transfers_in_per_month=2.0. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             25.5 |                 65.8 |                 5490 |                  3866 |          0.72 |
| fake           |             25.5 |                 62.1 |                 4672 |                  3388 |          0.75 |
| normal         |             25.5 |                 61.9 |                 4402 |                  3279 |          0.75 |
| unwitting      |             25.2 |                 58.3 |                 4057 |                  3008 |          0.79 |
| witting        |             26.4 |                 59.9 |                 3706 |                  2856 |          0.76 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32881788 |     29.09  |          129.46 |
| Normal_DirectDebit     | 32116652 |     28.413 |           42.05 |
| Normal_Card            | 19290001 |     17.065 |          260.66 |
| Normal_CashWithdrawal  |  8784252 |      7.771 |          140    |
| Normal_TransferIn      |  8778350 |      7.766 |           99.98 |
| Normal_Salary          |  6379743 |      5.644 |         1942.8  |
| Normal_StandingOrder   |  3521193 |      3.115 |           54.18 |
| Normal_CashDeposit     |   528339 |      0.467 |          150.11 |
| Normal_Cheque          |   440115 |      0.389 |           99.94 |
| Normal_Abroad          |   155031 |      0.137 |          449.23 |
| Normal_Bonus           |   104232 |      0.092 |         1243.05 |
| Normal_GroupCollection |    42239 |      0.037 |           20.02 |
| Structuring            |     5374 |      0.005 |          283.86 |
| Deposit-Send           |     1678 |      0.001 |          411.49 |
| Layered_Fan_Out        |      925 |      0.001 |          424.85 |
| Layered_Fan_In         |      794 |      0.001 |          715.49 |
| Normal_LargeCash       |      726 |      0.001 |        14914    |
| Cycle                  |      658 |      0.001 |         1418.72 |
| Behavioural_Change_1   |      627 |      0.001 |          205.27 |
| Behavioural_Change_2   |      563 |      0     |          227.71 |
| Gather-Scatter         |      556 |      0     |          557.01 |
| Fan_In                 |      439 |      0     |          565.09 |
| Fan_Out                |      390 |      0     |          678.69 |
| Scatter-Gather         |      376 |      0     |          505.16 |
| Cash_Withdrawal        |      325 |      0     |          270.87 |
| Bipartite              |      279 |      0     |          682    |
| Stacked Bipartite      |      240 |      0     |          465.5  |
| Smurfing               |      162 |      0     |          139.44 |

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
|               1 |         1.39 |            0.5  |          23.91 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        4958 |         4426 |      3.04252e+06 |
| unwitting |        4353 |         3512 | 489746           |
| witting   |        4085 |         3524 | 467319           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 3,842; true 233 -> false alarm share 93.9% (target 90-95%)
- Launderers alerted after their start: 229 of 732 (31%); accounts closed: 188

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      725 |             1 |
| R2     |      751 |            13 |
| R3     |      981 |             5 |
| R4     |     1485 |           210 |
| R5     |        3 |             0 |
| R6     |      987 |            16 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        412 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   34.9 |                37 |             85 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        48 |       42 |
| Deposit-Send         |          111 |        41 |       33 |
| Behavioural_Change_1 |           50 |         4 |        2 |
| Layered_Fan_Out      |           50 |        11 |       12 |
| Layered_Fan_In       |           46 |        22 |       18 |
| Behavioural_Change_2 |           44 |         6 |        4 |
| Gather-Scatter       |           43 |        16 |       13 |
| Cycle                |           40 |        28 |       23 |
| Fan_In               |           33 |        10 |        7 |
| Scatter-Gather       |           27 |        11 |        8 |
| Fan_Out              |           25 |        13 |       12 |
| Bipartite            |           24 |         6 |        5 |
| Stacked Bipartite    |           22 |         2 |        2 |
| Cash_Withdrawal      |           18 |         9 |        7 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.784 (average precision 0.243, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.466, money_in 0.480, money_out 0.484, max_in 0.585, n_senders 0.528, share_abroad 0.555, n_internal 0.596, spike 0.490
