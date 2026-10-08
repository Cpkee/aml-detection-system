# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, timing.bursts_per_launderer="repeat_until_closed". Code: 136967e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| fake           |             20.1 |                 45.1 |                 4307 |                  3498 |          0.79 |
| normal         |             24.5 |                 60.9 |                 4238 |                  3278 |          0.78 |
| unwitting      |             25.7 |                 56.2 |                 4082 |                  3255 |          0.8  |
| witting        |             26.7 |                 55.7 |                 3882 |                  3017 |          0.79 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32865644 |     30.25  |          129.45 |
| Normal_DirectDebit     | 32103255 |     29.549 |           42.05 |
| Normal_Card            | 19281698 |     17.747 |          260.64 |
| Normal_CashWithdrawal  |  8780713 |      8.082 |          140    |
| Normal_Salary          |  6376764 |      5.869 |         1942.71 |
| Normal_TransferIn      |  4386913 |      4.038 |          100.04 |
| Normal_StandingOrder   |  3519706 |      3.24  |           54.17 |
| Normal_CashDeposit     |   525255 |      0.483 |          149.9  |
| Normal_Cheque          |   440144 |      0.405 |          100.17 |
| Normal_Abroad          |   153517 |      0.141 |          450.55 |
| Normal_Bonus           |   104183 |      0.096 |         1242.79 |
| Normal_GroupCollection |    40912 |      0.038 |           20.02 |
| Structuring            |    30575 |      0.028 |          290.3  |
| Deposit-Send           |     5601 |      0.005 |          443.53 |
| Layered_Fan_Out        |     4620 |      0.004 |          467.77 |
| Behavioural_Change_1   |     4516 |      0.004 |          210.4  |
| Behavioural_Change_2   |     4117 |      0.004 |          236.44 |
| Fan_In                 |     2585 |      0.002 |          564.93 |
| Layered_Fan_In         |     1995 |      0.002 |          681.25 |
| Gather-Scatter         |     1986 |      0.002 |          575.18 |
| Bipartite              |     1923 |      0.002 |          602.35 |
| Stacked Bipartite      |     1687 |      0.002 |          571.81 |
| Scatter-Gather         |     1657 |      0.002 |          540.26 |
| Smurfing               |     1618 |      0.001 |          156.14 |
| Cash_Withdrawal        |     1159 |      0.001 |          276.16 |
| Fan_Out                |     1090 |      0.001 |          622.63 |
| Normal_LargeCash       |      780 |      0.001 |        14761.8  |
| Cycle                  |      709 |      0.001 |         1546.66 |

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
|               1 |         1.7  |            0.47 |          17.56 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |    total_in |
|:----------|------------:|-------------:|------------:|
| fake      |       24536 |        19544 | 1.48923e+07 |
| unwitting |       13674 |        10254 | 1.68755e+06 |
| witting   |       13313 |         9788 | 1.69787e+06 |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 6,317; true 572 -> false alarm share 90.9% (target 90-95%)
- Launderers alerted after their start: 493 of 732 (67%); accounts closed: 457

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      780 |             1 |
| R2     |      874 |            83 |
| R3     |      331 |             3 |
| R4     |     1001 |           492 |
| R5     |        5 |             0 |
| R6     |     4487 |             5 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                     96 |          0 |        452 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                     58 |                31 |            175 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          188 |       107 |       98 |
| Deposit-Send         |          108 |        95 |       94 |
| Layered_Fan_Out      |           65 |        35 |       31 |
| Behavioural_Change_1 |           45 |         7 |        5 |
| Layered_Fan_In       |           45 |        39 |       38 |
| Behavioural_Change_2 |           44 |        12 |       11 |
| Fan_In               |           42 |        34 |       34 |
| Gather-Scatter       |           36 |        27 |       22 |
| Bipartite            |           33 |        24 |       25 |
| Stacked Bipartite    |           33 |        24 |       25 |
| Fan_Out              |           24 |        22 |       21 |
| Scatter-Gather       |           24 |        18 |       19 |
| Cycle                |           22 |        19 |       16 |
| Cash_Withdrawal      |           12 |        12 |       11 |
| Smurfing             |           11 |        10 |        7 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.900 (average precision 0.695, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.452, money_in 0.511, money_out 0.507, max_in 0.606, n_senders 0.585, share_abroad 0.675, n_internal 0.644, spike 0.244
