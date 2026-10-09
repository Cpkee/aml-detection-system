# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, income.money_in_source="hmrc_individual". Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| fake           |             24.1 |                 59.5 |                 3654 |                  3182 |          0.86 |
| normal         |             24.5 |                 59.8 |                 3523 |                  3118 |          0.86 |
| unwitting      |             23.8 |                 54.9 |                 2977 |                  2800 |          0.87 |
| witting        |             23.9 |                 54.3 |                 2983 |                  2542 |          0.86 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32895857 |     30.276 |          118.54 |
| Normal_DirectDebit     | 32117215 |     29.56  |           37.63 |
| Normal_Card            | 19283198 |     17.748 |          243.35 |
| Normal_CashWithdrawal  |  8784657 |      8.085 |          140    |
| Normal_Salary          |  6379620 |      5.872 |         1614.22 |
| Normal_TransferIn      |  4392954 |      4.043 |          100.05 |
| Normal_StandingOrder   |  3523086 |      3.243 |           51.02 |
| Normal_CashDeposit     |   522646 |      0.481 |          149.8  |
| Normal_Cheque          |   439427 |      0.404 |          100.1  |
| Normal_Abroad          |   153066 |      0.141 |          450.68 |
| Normal_Bonus           |   104224 |      0.096 |         1259.78 |
| Normal_GroupCollection |    42083 |      0.039 |           19.97 |
| Structuring            |     5345 |      0.005 |          284.72 |
| Deposit-Send           |     1638 |      0.002 |          411.88 |
| Layered_Fan_Out        |      925 |      0.001 |          424.85 |
| Layered_Fan_In         |      791 |      0.001 |          718.58 |
| Normal_LargeCash       |      766 |      0.001 |        14902.2  |
| Cycle                  |      676 |      0.001 |         1435.05 |
| Behavioural_Change_1   |      627 |      0.001 |          205.27 |
| Behavioural_Change_2   |      563 |      0.001 |          227.71 |
| Gather-Scatter         |      538 |      0     |          568.51 |
| Fan_In                 |      439 |      0     |          565.09 |
| Fan_Out                |      384 |      0     |          678.69 |
| Scatter-Gather         |      376 |      0     |          505.16 |
| Cash_Withdrawal        |      325 |      0     |          270.87 |
| Bipartite              |      267 |      0     |          682    |
| Stacked Bipartite      |      240 |      0     |          465.5  |
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
|               1 |         1.39 |            0.5  |          23.68 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        4914 |         4371 |      3.01124e+06 |
| unwitting |        4387 |         3512 | 491905           |
| witting   |        4111 |         3611 | 493903           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 4,209; true 241 -> false alarm share 94.3% (target 90-95%)
- Launderers alerted after their start: 239 of 732 (33%); accounts closed: 188

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      766 |             0 |
| R2     |      790 |            10 |
| R3     |      884 |             5 |
| R4     |     1328 |           214 |
| R5     |        7 |             0 |
| R6     |     1657 |            24 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        412 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   38.3 |                38 |            143 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        47 |       40 |
| Deposit-Send         |          111 |        43 |       32 |
| Behavioural_Change_1 |           50 |         4 |        2 |
| Layered_Fan_Out      |           50 |        13 |       11 |
| Layered_Fan_In       |           46 |        25 |       21 |
| Behavioural_Change_2 |           44 |         5 |        3 |
| Gather-Scatter       |           43 |        14 |       11 |
| Cycle                |           40 |        32 |       24 |
| Fan_In               |           33 |        13 |        8 |
| Scatter-Gather       |           27 |         9 |        7 |
| Fan_Out              |           25 |        13 |       12 |
| Bipartite            |           24 |         8 |        6 |
| Stacked Bipartite    |           22 |         3 |        3 |
| Cash_Withdrawal      |           18 |         9 |        8 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.768 (average precision 0.229, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.444, money_in 0.485, money_out 0.484, max_in 0.603, n_senders 0.543, share_abroad 0.554, n_internal 0.590, spike 0.477
