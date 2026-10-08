# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, normal.transfers_in_per_month=2.0. Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| fake           |             25.9 |                 63.4 |                 4834 |                  3681 |          0.74 |
| normal         |             25.5 |                 61.9 |                 4402 |                  3279 |          0.75 |
| unwitting      |             25.9 |                 60.3 |                 4100 |                  3084 |          0.79 |
| witting        |             26.3 |                 58.7 |                 3600 |                  2811 |          0.76 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32885961 |     29.09  |          129.46 |
| Normal_DirectDebit     | 32120149 |     28.413 |           42.05 |
| Normal_Card            | 19292051 |     17.065 |          260.66 |
| Normal_CashWithdrawal  |  8785171 |      7.771 |          140    |
| Normal_TransferIn      |  8779322 |      7.766 |           99.98 |
| Normal_Salary          |  6380453 |      5.644 |         1942.81 |
| Normal_StandingOrder   |  3521543 |      3.115 |           54.18 |
| Normal_CashDeposit     |   528340 |      0.467 |          150.11 |
| Normal_Cheque          |   440168 |      0.389 |           99.94 |
| Normal_Abroad          |   155047 |      0.137 |          449.25 |
| Normal_Bonus           |   104239 |      0.092 |         1243.09 |
| Normal_GroupCollection |    42254 |      0.037 |           20.02 |
| Structuring            |     5474 |      0.005 |          285.03 |
| Deposit-Send           |     1684 |      0.001 |          410.9  |
| Layered_Fan_Out        |      958 |      0.001 |          412.96 |
| Layered_Fan_In         |      851 |      0.001 |          709.51 |
| Normal_LargeCash       |      726 |      0.001 |        14914    |
| Cycle                  |      721 |      0.001 |         1438.04 |
| Behavioural_Change_1   |      618 |      0.001 |          203.15 |
| Behavioural_Change_2   |      596 |      0.001 |          223.69 |
| Gather-Scatter         |      582 |      0.001 |          542.39 |
| Fan_In                 |      439 |      0     |          565.09 |
| Fan_Out                |      402 |      0     |          661.17 |
| Scatter-Gather         |      376 |      0     |          505.16 |
| Cash_Withdrawal        |      325 |      0     |          270.87 |
| Bipartite              |      285 |      0     |          687.69 |
| Stacked Bipartite      |      276 |      0     |          479.95 |
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
|               1 |         1.36 |            0.48 |          24.63 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5087 |         4602 |      3.10144e+06 |
| unwitting |        4419 |         3803 | 499711           |
| witting   |        4111 |         3809 | 487228           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 8,915; true 186 -> false alarm share 97.9% (target 90-95%)
- Launderers alerted after their start: 183 of 732 (25%); accounts closed: 152

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      726 |             1 |
| R2     |      753 |            14 |
| R3     |      405 |             3 |
| R4     |      723 |           166 |
| R5     |        2 |             0 |
| R6     |     7353 |             9 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                     10 |          1 |        412 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   82.5 |                27 |            286 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        29 |       27 |
| Deposit-Send         |          111 |        29 |       27 |
| Behavioural_Change_1 |           50 |         4 |        3 |
| Layered_Fan_Out      |           50 |        10 |       11 |
| Layered_Fan_In       |           46 |        20 |       16 |
| Behavioural_Change_2 |           44 |         4 |        2 |
| Gather-Scatter       |           43 |         9 |        8 |
| Cycle                |           40 |        29 |       26 |
| Fan_In               |           33 |         9 |        6 |
| Scatter-Gather       |           27 |         5 |        4 |
| Fan_Out              |           25 |        10 |       11 |
| Bipartite            |           24 |         6 |        5 |
| Stacked Bipartite    |           22 |         1 |        1 |
| Cash_Withdrawal      |           18 |         7 |        5 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.793 (average precision 0.186, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.497, money_in 0.504, money_out 0.509, max_in 0.585, n_senders 0.565, share_abroad 0.556, n_internal 0.640, spike 0.492
