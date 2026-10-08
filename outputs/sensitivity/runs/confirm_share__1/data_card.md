# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, rules.confirm_share=0.6. Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| fake           |             25.2 |                 63   |                 4971 |                  3818 |          0.77 |
| normal         |             24.5 |                 60.9 |                 4238 |                  3278 |          0.78 |
| unwitting      |             25   |                 59.1 |                 3961 |                  3164 |          0.81 |
| witting        |             25.7 |                 58.5 |                 3751 |                  2956 |          0.79 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32889895 |     30.267 |          129.47 |
| Normal_DirectDebit     | 32123105 |     29.561 |           42.06 |
| Normal_Card            | 19294045 |     17.755 |          260.67 |
| Normal_CashWithdrawal  |  8786340 |      8.086 |          140    |
| Normal_Salary          |  6381056 |      5.872 |         1942.98 |
| Normal_TransferIn      |  4389696 |      4.04  |          100.04 |
| Normal_StandingOrder   |  3521897 |      3.241 |           54.18 |
| Normal_CashDeposit     |   525709 |      0.484 |          149.89 |
| Normal_Cheque          |   440451 |      0.405 |          100.17 |
| Normal_Abroad          |   153623 |      0.141 |          450.51 |
| Normal_Bonus           |   104250 |      0.096 |         1243.2  |
| Normal_GroupCollection |    40934 |      0.038 |           20.01 |
| Structuring            |     5574 |      0.005 |          285.23 |
| Deposit-Send           |     1690 |      0.002 |          410.62 |
| Layered_Fan_Out        |      949 |      0.001 |          415.76 |
| Layered_Fan_In         |      851 |      0.001 |          709.51 |
| Normal_LargeCash       |      781 |      0.001 |        14770    |
| Cycle                  |      724 |      0.001 |         1448.57 |
| Behavioural_Change_1   |      639 |      0.001 |          205.27 |
| Behavioural_Change_2   |      599 |      0.001 |          222.19 |
| Gather-Scatter         |      577 |      0.001 |          552.25 |
| Fan_In                 |      439 |      0     |          565.09 |
| Fan_Out                |      420 |      0     |          668.74 |
| Scatter-Gather         |      394 |      0     |          512.94 |
| Stacked Bipartite      |      333 |      0     |          478.07 |
| Cash_Withdrawal        |      325 |      0     |          270.87 |
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
|               1 |         1.33 |            0.47 |          25.08 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5106 |         4656 |      3.12537e+06 |
| unwitting |        4419 |         3706 | 502386           |
| witting   |        4148 |         3934 | 501919           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 5,937; true 191 -> false alarm share 96.8% (target 90-95%)
- Launderers alerted after their start: 187 of 732 (26%); accounts closed: 114

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      781 |             2 |
| R2     |      806 |            15 |
| R3     |      329 |             1 |
| R4     |      678 |           169 |
| R5     |        5 |             0 |
| R6     |     4498 |            15 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          1 |        426 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   54.5 |                28 |            171 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        31 |       20 |
| Deposit-Send         |          111 |        27 |       16 |
| Behavioural_Change_1 |           50 |         3 |        2 |
| Layered_Fan_Out      |           50 |        11 |        8 |
| Layered_Fan_In       |           46 |        19 |       13 |
| Behavioural_Change_2 |           44 |         4 |        0 |
| Gather-Scatter       |           43 |        10 |        9 |
| Cycle                |           40 |        31 |       21 |
| Fan_In               |           33 |        10 |        4 |
| Scatter-Gather       |           27 |         9 |        3 |
| Fan_Out              |           25 |        12 |       10 |
| Bipartite            |           24 |         7 |        3 |
| Stacked Bipartite    |           22 |         2 |        2 |
| Cash_Withdrawal      |           18 |         8 |        3 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.753 (average precision 0.114, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.526, money_in 0.533, money_out 0.537, max_in 0.588, n_senders 0.609, share_abroad 0.547, n_internal 0.675, spike 0.480
