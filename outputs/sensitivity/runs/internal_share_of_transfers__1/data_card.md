# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, normal.internal_share_of_transfers=0.05. Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             24.3 |                 64.5 |                 5276 |                  3875 |          0.75 |
| fake           |             24.7 |                 62.3 |                 4768 |                  3676 |          0.77 |
| normal         |             24.3 |                 60.6 |                 4187 |                  3278 |          0.79 |
| unwitting      |             25   |                 58.8 |                 3659 |                  3174 |          0.83 |
| witting        |             25.3 |                 57.1 |                 3429 |                  2781 |          0.82 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_DirectDebit     | 32120157 |     29.92  |           42.05 |
| Normal_Transfer        | 31585046 |     29.421 |          129.47 |
| Normal_Card            | 19292128 |     17.97  |          260.66 |
| Normal_CashWithdrawal  |  8783991 |      8.182 |          140    |
| Normal_Salary          |  6380552 |      5.943 |         1942.75 |
| Normal_TransferIn      |  4390747 |      4.09  |          100.05 |
| Normal_StandingOrder   |  3521526 |      3.28  |           54.18 |
| Normal_CashDeposit     |   526616 |      0.491 |          150.13 |
| Normal_Cheque          |   439893 |      0.41  |          100.13 |
| Normal_Abroad          |   154565 |      0.144 |          450.48 |
| Normal_Bonus           |   104239 |      0.097 |         1243.16 |
| Normal_GroupCollection |    41097 |      0.038 |           20.09 |
| Structuring            |     5495 |      0.005 |          285.73 |
| Deposit-Send           |     1684 |      0.002 |          410.9  |
| Layered_Fan_Out        |      931 |      0.001 |          420.06 |
| Layered_Fan_In         |      851 |      0.001 |          709.51 |
| Normal_LargeCash       |      768 |      0.001 |        14839.2  |
| Cycle                  |      715 |      0.001 |         1465.6  |
| Behavioural_Change_1   |      618 |      0.001 |          203.15 |
| Behavioural_Change_2   |      599 |      0.001 |          222.19 |
| Gather-Scatter         |      582 |      0.001 |          542.39 |
| Fan_In                 |      439 |      0     |          565.09 |
| Fan_Out                |      390 |      0     |          661.17 |
| Scatter-Gather         |      376 |      0     |          505.16 |
| Cash_Withdrawal        |      325 |      0     |          270.87 |
| Stacked Bipartite      |      291 |      0     |          483.86 |
| Bipartite              |      285 |      0     |          687.69 |
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
|               0 |         0.16 |            0.03 |           1.37 |
|               1 |         1.35 |            0.47 |          24.63 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5069 |         4597 |      3.08679e+06 |
| unwitting |        4419 |         3706 | 499475           |
| witting   |        4111 |         3913 | 500814           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 5,325; true 186 -> false alarm share 96.5% (target 90-95%)
- Launderers alerted after their start: 183 of 732 (25%); accounts closed: 150

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      767 |             1 |
| R2     |      800 |            16 |
| R3     |      300 |             3 |
| R4     |      657 |           161 |
| R5     |        3 |             0 |
| R6     |     3938 |            14 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                     10 |          1 |        459 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   48.4 |                26 |            150 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        32 |       27 |
| Deposit-Send         |          111 |        31 |       26 |
| Behavioural_Change_1 |           50 |         4 |        2 |
| Layered_Fan_Out      |           50 |        11 |       11 |
| Layered_Fan_In       |           46 |        21 |       17 |
| Behavioural_Change_2 |           44 |         4 |        2 |
| Gather-Scatter       |           43 |         8 |        8 |
| Cycle                |           40 |        31 |       26 |
| Fan_In               |           33 |         9 |        6 |
| Scatter-Gather       |           27 |         4 |        4 |
| Fan_Out              |           25 |        10 |        9 |
| Bipartite            |           24 |         7 |        5 |
| Stacked Bipartite    |           22 |         1 |        1 |
| Cash_Withdrawal      |           18 |         8 |        6 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.781 (average precision 0.160, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.501, money_in 0.511, money_out 0.514, max_in 0.587, n_senders 0.602, share_abroad 0.554, n_internal 0.723, spike 0.542
