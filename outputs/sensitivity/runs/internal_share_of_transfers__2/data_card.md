# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, normal.internal_share_of_transfers=0.2. Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| fake           |             25.4 |                 63.1 |                 4889 |                  3662 |          0.76 |
| normal         |             25.2 |                 61.5 |                 4338 |                  3278 |          0.76 |
| unwitting      |             25.5 |                 59   |                 3748 |                  3029 |          0.79 |
| witting        |             26.3 |                 59   |                 3478 |                  2852 |          0.77 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 35486634 |     31.898 |          129.45 |
| Normal_DirectDebit     | 32120428 |     28.872 |           42.05 |
| Normal_Card            | 19292239 |     17.341 |          260.66 |
| Normal_CashWithdrawal  |  8783352 |      7.895 |          140    |
| Normal_Salary          |  6380741 |      5.735 |         1942.63 |
| Normal_TransferIn      |  4387722 |      3.944 |          100.05 |
| Normal_StandingOrder   |  3521573 |      3.165 |           54.18 |
| Normal_CashDeposit     |   524010 |      0.471 |          150.35 |
| Normal_Cheque          |   439162 |      0.395 |          100.07 |
| Normal_Abroad          |   155035 |      0.139 |          450.13 |
| Normal_Bonus           |   104243 |      0.094 |         1243.09 |
| Normal_GroupCollection |    41817 |      0.038 |           20.06 |
| Structuring            |     5532 |      0.005 |          285.03 |
| Deposit-Send           |     1678 |      0.002 |          411.49 |
| Layered_Fan_Out        |      937 |      0.001 |          423.8  |
| Layered_Fan_In         |      851 |      0.001 |          709.51 |
| Normal_LargeCash       |      715 |      0.001 |        14823    |
| Cycle                  |      688 |      0.001 |         1448.57 |
| Behavioural_Change_1   |      618 |      0.001 |          203.15 |
| Behavioural_Change_2   |      614 |      0.001 |          223.69 |
| Gather-Scatter         |      573 |      0.001 |          556.45 |
| Fan_In                 |      451 |      0     |          557.51 |
| Fan_Out                |      390 |      0     |          661.17 |
| Scatter-Gather         |      376 |      0     |          505.16 |
| Cash_Withdrawal        |      325 |      0     |          270.87 |
| Stacked Bipartite      |      291 |      0     |          483.86 |
| Bipartite              |      285 |      0     |          687.69 |
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
|               1 |         1.33 |            0.47 |          24.67 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5106 |         4602 |      3.09249e+06 |
| unwitting |        4419 |         3706 | 500692           |
| witting   |        4111 |         3835 | 485396           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 7,081; true 184 -> false alarm share 97.4% (target 90-95%)
- Launderers alerted after their start: 182 of 732 (25%); accounts closed: 147

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      713 |             1 |
| R2     |      741 |            14 |
| R3     |      378 |             2 |
| R4     |      669 |           164 |
| R5     |        3 |             0 |
| R6     |     5643 |            12 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                     10 |          1 |        412 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   64.4 |                24 |            240 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        35 |       29 |
| Deposit-Send         |          111 |        30 |       25 |
| Behavioural_Change_1 |           50 |         3 |        2 |
| Layered_Fan_Out      |           50 |        12 |       12 |
| Layered_Fan_In       |           46 |        20 |       16 |
| Behavioural_Change_2 |           44 |         3 |        3 |
| Gather-Scatter       |           43 |        10 |        8 |
| Cycle                |           40 |        29 |       24 |
| Fan_In               |           33 |         9 |        6 |
| Scatter-Gather       |           27 |         5 |        4 |
| Fan_Out              |           25 |         8 |        8 |
| Bipartite            |           24 |         6 |        4 |
| Stacked Bipartite    |           22 |         1 |        1 |
| Cash_Withdrawal      |           18 |         7 |        5 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.759 (average precision 0.201, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.498, money_in 0.507, money_out 0.510, max_in 0.588, n_senders 0.574, share_abroad 0.555, n_internal 0.578, spike 0.481
