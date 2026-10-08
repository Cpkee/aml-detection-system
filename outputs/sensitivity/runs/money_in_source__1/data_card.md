# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, income.money_in_source="hmrc_individual". Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             24.5 |                 64.6 |                 4606 |                  3853 |          0.84 |
| fake           |             24.5 |                 60.8 |                 3940 |                  3466 |          0.86 |
| normal         |             24.5 |                 59.8 |                 3523 |                  3118 |          0.86 |
| unwitting      |             24   |                 55.2 |                 3140 |                  2863 |          0.88 |
| witting        |             24   |                 54.4 |                 2776 |                  2490 |          0.87 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32900099 |     30.277 |          118.54 |
| Normal_DirectDebit     | 32120786 |     29.559 |           37.63 |
| Normal_Card            | 19285352 |     17.748 |          243.35 |
| Normal_CashWithdrawal  |  8785689 |      8.085 |          140    |
| Normal_Salary          |  6380262 |      5.871 |         1614.27 |
| Normal_TransferIn      |  4393448 |      4.043 |          100.05 |
| Normal_StandingOrder   |  3523459 |      3.242 |           51.02 |
| Normal_CashDeposit     |   522696 |      0.481 |          149.8  |
| Normal_Cheque          |   439477 |      0.404 |          100.1  |
| Normal_Abroad          |   153080 |      0.141 |          450.69 |
| Normal_Bonus           |   104236 |      0.096 |         1259.82 |
| Normal_GroupCollection |    42083 |      0.039 |           19.97 |
| Structuring            |     5486 |      0.005 |          285.71 |
| Deposit-Send           |     1675 |      0.002 |          408.77 |
| Layered_Fan_Out        |      949 |      0.001 |          415.76 |
| Layered_Fan_In         |      851 |      0.001 |          709.51 |
| Normal_LargeCash       |      767 |      0.001 |        14903.9  |
| Cycle                  |      703 |      0.001 |         1413.35 |
| Behavioural_Change_1   |      618 |      0.001 |          203.15 |
| Behavioural_Change_2   |      587 |      0.001 |          226.43 |
| Gather-Scatter         |      553 |      0.001 |          557.57 |
| Fan_In                 |      439 |      0     |          565.09 |
| Fan_Out                |      396 |      0     |          661.17 |
| Scatter-Gather         |      376 |      0     |          505.16 |
| Cash_Withdrawal        |      325 |      0     |          270.87 |
| Stacked Bipartite      |      276 |      0     |          479.95 |
| Bipartite              |      273 |      0     |          687.69 |
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
|               0 |         0.16 |            0.03 |           2.75 |
|               1 |         1.36 |            0.48 |          24.48 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5062 |         4574 |      3.06762e+06 |
| unwitting |        4419 |         3706 | 500456           |
| witting   |        4111 |         3868 | 498454           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 5,626; true 192 -> false alarm share 96.6% (target 90-95%)
- Launderers alerted after their start: 190 of 732 (26%); accounts closed: 150

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      767 |             1 |
| R2     |      792 |            12 |
| R3     |      340 |             1 |
| R4     |      722 |           168 |
| R5     |        6 |             0 |
| R6     |     4186 |            23 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        412 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   51.6 |                28 |            161 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        30 |       25 |
| Deposit-Send         |          111 |        31 |       25 |
| Behavioural_Change_1 |           50 |         4 |        2 |
| Layered_Fan_Out      |           50 |        11 |       11 |
| Layered_Fan_In       |           46 |        21 |       18 |
| Behavioural_Change_2 |           44 |         4 |        2 |
| Gather-Scatter       |           43 |        10 |        9 |
| Cycle                |           40 |        31 |       24 |
| Fan_In               |           33 |        10 |        6 |
| Scatter-Gather       |           27 |         5 |        3 |
| Fan_Out              |           25 |        12 |       12 |
| Bipartite            |           24 |         6 |        4 |
| Stacked Bipartite    |           22 |         3 |        3 |
| Cash_Withdrawal      |           18 |         7 |        6 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.776 (average precision 0.163, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.477, money_in 0.512, money_out 0.510, max_in 0.604, n_senders 0.581, share_abroad 0.555, n_internal 0.635, spike 0.481
