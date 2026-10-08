# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, normal.transfers_in_per_month=0.5. Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             24.1 |                 64.2 |                 5247 |                  3879 |          0.75 |
| fake           |             24.3 |                 62   |                 4754 |                  3663 |          0.77 |
| normal         |             24.1 |                 60.4 |                 4154 |                  3280 |          0.8  |
| unwitting      |             24.5 |                 57.9 |                 3842 |                  3227 |          0.85 |
| witting        |             25.2 |                 57.1 |                 3372 |                  2809 |          0.82 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32886464 |     30.891 |          129.46 |
| Normal_DirectDebit     | 32120329 |     30.171 |           42.05 |
| Normal_Card            | 19292310 |     18.122 |          260.66 |
| Normal_CashWithdrawal  |  8783923 |      8.251 |          140    |
| Normal_Salary          |  6380577 |      5.993 |         1942.82 |
| Normal_StandingOrder   |  3521581 |      3.308 |           54.18 |
| Normal_TransferIn      |  2195358 |      2.062 |           99.93 |
| Normal_CashDeposit     |   527899 |      0.496 |          150.12 |
| Normal_Cheque          |   438687 |      0.412 |           99.99 |
| Normal_Abroad          |   151522 |      0.142 |          447.61 |
| Normal_Bonus           |   104241 |      0.098 |         1243.1  |
| Normal_GroupCollection |    42671 |      0.04  |           20.07 |
| Structuring            |     5485 |      0.005 |          285.34 |
| Deposit-Send           |     1687 |      0.002 |          411.46 |
| Layered_Fan_Out        |      934 |      0.001 |          418.44 |
| Layered_Fan_In         |      851 |      0.001 |          709.51 |
| Normal_LargeCash       |      763 |      0.001 |        14932.6  |
| Cycle                  |      715 |      0.001 |         1465.6  |
| Behavioural_Change_1   |      618 |      0.001 |          203.15 |
| Behavioural_Change_2   |      611 |      0.001 |          222.19 |
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
|               0 |         0.16 |            0.03 |           2.75 |
|               1 |         1.35 |            0.47 |          24.64 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5051 |         4593 |      3.08676e+06 |
| unwitting |        4419 |         3706 | 499711           |
| witting   |        4111 |         3913 | 501055           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 4,532; true 183 -> false alarm share 96.0% (target 90-95%)
- Launderers alerted after their start: 180 of 732 (25%); accounts closed: 146

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      763 |             3 |
| R2     |      794 |            16 |
| R3     |      348 |             3 |
| R4     |      647 |           155 |
| R5     |        2 |             0 |
| R6     |     3116 |            19 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        412 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   40.8 |                27 |            129 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        32 |       26 |
| Deposit-Send         |          111 |        29 |       25 |
| Behavioural_Change_1 |           50 |         3 |        2 |
| Layered_Fan_Out      |           50 |        11 |       12 |
| Layered_Fan_In       |           46 |        20 |       16 |
| Behavioural_Change_2 |           44 |         4 |        2 |
| Gather-Scatter       |           43 |         9 |        8 |
| Cycle                |           40 |        31 |       26 |
| Fan_In               |           33 |        10 |        7 |
| Scatter-Gather       |           27 |         4 |        2 |
| Fan_Out              |           25 |        10 |        9 |
| Bipartite            |           24 |         6 |        4 |
| Stacked Bipartite    |           22 |         2 |        2 |
| Cash_Withdrawal      |           18 |         7 |        5 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.762 (average precision 0.158, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.498, money_in 0.513, money_out 0.513, max_in 0.589, n_senders 0.622, share_abroad 0.552, n_internal 0.645, spike 0.577
