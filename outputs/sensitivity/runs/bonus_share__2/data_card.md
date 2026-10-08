# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, normal.bonus_share=0.6. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             24.5 |                 64.5 |                 5388 |                  3878 |          0.73 |
| fake           |             24.2 |                 60.2 |                 4516 |                  3399 |          0.76 |
| normal         |             24.5 |                 60.9 |                 4273 |                  3279 |          0.77 |
| unwitting      |             24   |                 56.2 |                 3620 |                  2987 |          0.8  |
| witting        |             24.5 |                 56.1 |                 3427 |                  2838 |          0.79 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32896943 |     30.254 |          129.46 |
| Normal_DirectDebit     | 32104542 |     29.526 |           42.14 |
| Normal_Card            | 19289497 |     17.74  |          260.59 |
| Normal_CashWithdrawal  |  8775418 |      8.07  |          140    |
| Normal_Salary          |  6379743 |      5.867 |         1942.65 |
| Normal_TransferIn      |  4392175 |      4.039 |          100.11 |
| Normal_StandingOrder   |  3519780 |      3.237 |           54.22 |
| Normal_CashDeposit     |   519911 |      0.478 |          149.99 |
| Normal_Cheque          |   440622 |      0.405 |           99.96 |
| Normal_Bonus           |   208783 |      0.192 |         1248.58 |
| Normal_Abroad          |   151378 |      0.139 |          449.61 |
| Normal_GroupCollection |    41723 |      0.038 |           20.1  |
| Structuring            |     5337 |      0.005 |          284.49 |
| Deposit-Send           |     1636 |      0.002 |          413.05 |
| Layered_Fan_Out        |      901 |      0.001 |          427.81 |
| Layered_Fan_In         |      786 |      0.001 |          720.17 |
| Normal_LargeCash       |      759 |      0.001 |        15057.8  |
| Behavioural_Change_1   |      639 |      0.001 |          205.27 |
| Cycle                  |      622 |      0.001 |         1473.45 |
| Gather-Scatter         |      562 |      0.001 |          565.41 |
| Behavioural_Change_2   |      554 |      0.001 |          229.96 |
| Fan_In                 |      433 |      0     |          571.35 |
| Fan_Out                |      390 |      0     |          678.69 |
| Scatter-Gather         |      377 |      0     |          507.01 |
| Cash_Withdrawal        |      325 |      0     |          270.87 |
| Bipartite              |      279 |      0     |          682    |
| Stacked Bipartite      |      252 |      0     |          475.09 |
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
|               1 |         1.4  |            0.5  |          23.52 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        4914 |         4375 |      3.01488e+06 |
| unwitting |        4387 |         3512 | 491192           |
| witting   |        4111 |         3567 | 475594           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 4,017; true 245 -> false alarm share 93.9% (target 90-95%)
- Launderers alerted after their start: 243 of 732 (33%); accounts closed: 192

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      759 |             2 |
| R2     |      791 |            13 |
| R3     |      892 |             5 |
| R4     |     1385 |           218 |
| R5     |        2 |             0 |
| R6     |     1355 |            21 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        472 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   36.5 |                36 |            125 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        45 |       38 |
| Deposit-Send         |          111 |        41 |       30 |
| Behavioural_Change_1 |           50 |         4 |        2 |
| Layered_Fan_Out      |           50 |        17 |       15 |
| Layered_Fan_In       |           46 |        25 |       21 |
| Behavioural_Change_2 |           44 |         6 |        4 |
| Gather-Scatter       |           43 |        16 |       13 |
| Cycle                |           40 |        28 |       22 |
| Fan_In               |           33 |        11 |        7 |
| Scatter-Gather       |           27 |        12 |        9 |
| Fan_Out              |           25 |        16 |       15 |
| Bipartite            |           24 |         8 |        5 |
| Stacked Bipartite    |           22 |         3 |        3 |
| Cash_Withdrawal      |           18 |        10 |        8 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.742 (average precision 0.171, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.431, money_in 0.480, money_out 0.478, max_in 0.586, n_senders 0.549, share_abroad 0.551, n_internal 0.570, spike 0.475
