# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, normal.transfers_in_per_month=0.5. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| fake           |             24   |                 60.7 |                 4414 |                  3379 |          0.78 |
| normal         |             24.1 |                 60.4 |                 4154 |                  3280 |          0.8  |
| unwitting      |             24.2 |                 56.9 |                 3565 |                  3076 |          0.83 |
| witting        |             25.1 |                 56.3 |                 3426 |                  2790 |          0.81 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32881646 |     30.89  |          129.46 |
| Normal_DirectDebit     | 32116395 |     30.172 |           42.05 |
| Normal_Card            | 19289907 |     18.122 |          260.66 |
| Normal_CashWithdrawal  |  8782793 |      8.251 |          140    |
| Normal_Salary          |  6379761 |      5.993 |         1942.82 |
| Normal_StandingOrder   |  3521176 |      3.308 |           54.18 |
| Normal_TransferIn      |  2195099 |      2.062 |           99.92 |
| Normal_CashDeposit     |   527897 |      0.496 |          150.12 |
| Normal_Cheque          |   438636 |      0.412 |           99.99 |
| Normal_Abroad          |   151506 |      0.142 |          447.62 |
| Normal_Bonus           |   104231 |      0.098 |         1243.01 |
| Normal_GroupCollection |    42671 |      0.04  |           20.07 |
| Structuring            |     5359 |      0.005 |          284.58 |
| Deposit-Send           |     1695 |      0.002 |          408.77 |
| Layered_Fan_Out        |      901 |      0.001 |          427.81 |
| Layered_Fan_In         |      791 |      0.001 |          718.58 |
| Normal_LargeCash       |      763 |      0.001 |        14932.6  |
| Cycle                  |      694 |      0.001 |         1448.57 |
| Behavioural_Change_1   |      624 |      0.001 |          206.02 |
| Behavioural_Change_2   |      578 |      0.001 |          227.56 |
| Gather-Scatter         |      547 |      0.001 |          567.84 |
| Fan_In                 |      433 |      0     |          571.35 |
| Fan_Out                |      378 |      0     |          678.69 |
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
|               1 |         1.38 |            0.48 |          23.88 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        4914 |         4389 |      3.02783e+06 |
| unwitting |        4419 |         3479 | 493017           |
| witting   |        4111 |         3690 | 493903           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 3,703; true 240 -> false alarm share 93.5% (target 90-95%)
- Launderers alerted after their start: 237 of 732 (32%); accounts closed: 189

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      763 |             3 |
| R2     |      792 |            14 |
| R3     |      906 |             6 |
| R4     |     1277 |           205 |
| R5     |        4 |             0 |
| R6     |     1132 |            26 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        412 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   33.4 |                35 |             95 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        50 |       42 |
| Deposit-Send         |          111 |        43 |       34 |
| Behavioural_Change_1 |           50 |         3 |        1 |
| Layered_Fan_Out      |           50 |        14 |       14 |
| Layered_Fan_In       |           46 |        22 |       18 |
| Behavioural_Change_2 |           44 |         6 |        4 |
| Gather-Scatter       |           43 |        17 |       13 |
| Cycle                |           40 |        33 |       27 |
| Fan_In               |           33 |        10 |        7 |
| Scatter-Gather       |           27 |         8 |        5 |
| Fan_Out              |           25 |        12 |       10 |
| Bipartite            |           24 |         7 |        4 |
| Stacked Bipartite    |           22 |         3 |        3 |
| Cash_Withdrawal      |           18 |         9 |        7 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.771 (average precision 0.194, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.464, money_in 0.484, money_out 0.482, max_in 0.588, n_senders 0.589, share_abroad 0.551, n_internal 0.596, spike 0.568
