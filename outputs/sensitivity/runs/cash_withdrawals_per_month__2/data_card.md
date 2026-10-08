# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, normal.cash_withdrawals_per_month=4.0. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             26.5 |                 66.6 |                 5286 |                  3927 |          0.75 |
| fake           |             26.6 |                 63.3 |                 4511 |                  3449 |          0.77 |
| normal         |             26.5 |                 62.9 |                 4221 |                  3319 |          0.79 |
| unwitting      |             26.6 |                 59.9 |                 3641 |                  3030 |          0.81 |
| witting        |             27.6 |                 60.3 |                 3651 |                  2937 |          0.79 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32881829 |     28.005 |          106    |
| Normal_DirectDebit     | 32117014 |     27.354 |           32.9  |
| Normal_Card            | 19290006 |     16.429 |          260.66 |
| Normal_CashWithdrawal  | 17565138 |     14.96  |          140    |
| Normal_Salary          |  6379956 |      5.434 |         1942.63 |
| Normal_TransferIn      |  4388774 |      3.738 |          100.04 |
| Normal_StandingOrder   |  3521186 |      2.999 |           45.33 |
| Normal_CashDeposit     |   516564 |      0.44  |          150    |
| Normal_Cheque          |   440372 |      0.375 |          100.17 |
| Normal_Abroad          |   153826 |      0.131 |          448.44 |
| Normal_Bonus           |   104231 |      0.089 |         1243.09 |
| Normal_GroupCollection |    41114 |      0.035 |           19.93 |
| Structuring            |     5328 |      0.005 |          284.34 |
| Deposit-Send           |     1677 |      0.001 |          408.77 |
| Layered_Fan_Out        |      925 |      0.001 |          424.85 |
| Layered_Fan_In         |      791 |      0.001 |          718.58 |
| Normal_LargeCash       |      752 |      0.001 |        14804    |
| Cycle                  |      688 |      0.001 |         1418.72 |
| Behavioural_Change_1   |      639 |      0.001 |          205.27 |
| Behavioural_Change_2   |      563 |      0     |          227.71 |
| Gather-Scatter         |      553 |      0     |          567.84 |
| Fan_In                 |      451 |      0     |          557.51 |
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
|               0 |         0.15 |            0.02 |           2.52 |
|               1 |         1.39 |            0.5  |          23.91 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        4940 |         4484 |      3.04318e+06 |
| unwitting |        4419 |         3540 | 493017           |
| witting   |        4085 |         3578 | 474111           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 3,598; true 237 -> false alarm share 93.4% (target 90-95%)
- Launderers alerted after their start: 234 of 732 (32%); accounts closed: 187

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      752 |             1 |
| R2     |      775 |            11 |
| R3     |      916 |             7 |
| R4     |     1210 |           206 |
| R5     |        5 |             0 |
| R6     |     1092 |            22 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        434 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   32.4 |                33 |             85 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        46 |       38 |
| Deposit-Send         |          111 |        43 |       35 |
| Behavioural_Change_1 |           50 |         3 |        1 |
| Layered_Fan_Out      |           50 |        14 |       12 |
| Layered_Fan_In       |           46 |        22 |       18 |
| Behavioural_Change_2 |           44 |         7 |        5 |
| Gather-Scatter       |           43 |        16 |       12 |
| Cycle                |           40 |        31 |       25 |
| Fan_In               |           33 |        10 |        6 |
| Scatter-Gather       |           27 |        10 |        8 |
| Fan_Out              |           25 |        14 |       13 |
| Bipartite            |           24 |         7 |        5 |
| Stacked Bipartite    |           22 |         2 |        2 |
| Cash_Withdrawal      |           18 |         9 |        7 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.755 (average precision 0.185, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.469, money_in 0.484, money_out 0.482, max_in 0.586, n_senders 0.546, share_abroad 0.550, n_internal 0.596, spike 0.467
