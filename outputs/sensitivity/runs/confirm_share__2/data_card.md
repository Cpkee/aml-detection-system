# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, rules.confirm_share=1.0. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             24.5 |                 64.7 |                 5311 |                  3890 |          0.74 |
| fake           |             24.2 |                 59.9 |                 4187 |                  3181 |          0.77 |
| normal         |             24.5 |                 60.9 |                 4238 |                  3278 |          0.78 |
| unwitting      |             23.8 |                 57.2 |                 3565 |                  2944 |          0.8  |
| witting        |             25.3 |                 56.5 |                 3501 |                  2801 |          0.79 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32877181 |     30.266 |          129.46 |
| Normal_DirectDebit     | 32113240 |     29.563 |           42.05 |
| Normal_Card            | 19287669 |     17.756 |          260.66 |
| Normal_CashWithdrawal  |  8783462 |      8.086 |          140    |
| Normal_Salary          |  6378994 |      5.872 |         1942.81 |
| Normal_TransferIn      |  4388255 |      4.04  |          100.04 |
| Normal_StandingOrder   |  3520738 |      3.241 |           54.18 |
| Normal_CashDeposit     |   525507 |      0.484 |          149.89 |
| Normal_Cheque          |   440307 |      0.405 |          100.17 |
| Normal_Abroad          |   153541 |      0.141 |          450.51 |
| Normal_Bonus           |   104222 |      0.096 |         1243.09 |
| Normal_GroupCollection |    40934 |      0.038 |           20.01 |
| Structuring            |     5191 |      0.005 |          285.69 |
| Deposit-Send           |     1669 |      0.002 |          411.51 |
| Layered_Fan_Out        |      907 |      0.001 |          424.85 |
| Normal_LargeCash       |      780 |      0.001 |        14761.8  |
| Layered_Fan_In         |      767 |      0.001 |          707.97 |
| Cycle                  |      624 |      0.001 |         1465.6  |
| Behavioural_Change_1   |      621 |      0.001 |          205.27 |
| Behavioural_Change_2   |      553 |      0.001 |          227.4  |
| Gather-Scatter         |      535 |      0     |          557.57 |
| Fan_In                 |      439 |      0     |          565.09 |
| Fan_Out                |      384 |      0     |          668.74 |
| Scatter-Gather         |      371 |      0     |          508.96 |
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
|               1 |         1.42 |            0.51 |          23.17 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        4901 |         4349 |      2.99133e+06 |
| unwitting |        4419 |         3453 | 490905           |
| witting   |        4085 |         3467 | 457990           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 3,606; true 232 -> false alarm share 93.6% (target 90-95%)
- Launderers alerted after their start: 232 of 732 (32%); accounts closed: 232

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      780 |             1 |
| R2     |      804 |            13 |
| R3     |      810 |             4 |
| R4     |     1302 |           205 |
| R5     |        8 |             0 |
| R6     |     1102 |            23 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        426 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   33.1 |                34 |             95 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        46 |       46 |
| Deposit-Send         |          111 |        42 |       42 |
| Behavioural_Change_1 |           50 |         3 |        3 |
| Layered_Fan_Out      |           50 |        13 |       13 |
| Layered_Fan_In       |           46 |        20 |       20 |
| Behavioural_Change_2 |           44 |         7 |        7 |
| Gather-Scatter       |           43 |        15 |       15 |
| Cycle                |           40 |        29 |       30 |
| Fan_In               |           33 |        11 |       11 |
| Scatter-Gather       |           27 |        13 |       13 |
| Fan_Out              |           25 |        14 |       14 |
| Bipartite            |           24 |         7 |        7 |
| Stacked Bipartite    |           22 |         2 |        2 |
| Cash_Withdrawal      |           18 |         9 |        9 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.775 (average precision 0.205, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.436, money_in 0.456, money_out 0.453, max_in 0.585, n_senders 0.512, share_abroad 0.543, n_internal 0.555, spike 0.463
