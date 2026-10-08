# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, normal.cash_withdrawals_per_month=1.0. Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             23.6 |                 63.7 |                 5325 |                  3853 |          0.73 |
| fake           |             23.8 |                 61.5 |                 4778 |                  3644 |          0.76 |
| normal         |             23.6 |                 59.9 |                 4247 |                  3260 |          0.77 |
| unwitting      |             24.1 |                 57.8 |                 3946 |                  3104 |          0.8  |
| witting        |             24.5 |                 56.7 |                 3445 |                  2828 |          0.8  |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32886452 |     31.542 |          141.39 |
| Normal_DirectDebit     | 32120314 |     30.807 |           46.6  |
| Normal_Card            | 19292298 |     18.504 |          260.66 |
| Normal_Salary          |  6380579 |      6.12  |         1942.8  |
| Normal_CashWithdrawal  |  4393829 |      4.214 |          140    |
| Normal_TransferIn      |  4389302 |      4.21  |          100.04 |
| Normal_StandingOrder   |  3521581 |      3.378 |           58.6  |
| Normal_CashDeposit     |   523697 |      0.502 |          149.77 |
| Normal_Cheque          |   440423 |      0.422 |          100.17 |
| Normal_Abroad          |   153038 |      0.147 |          449.55 |
| Normal_Bonus           |   104240 |      0.1   |         1243.09 |
| Normal_GroupCollection |    42209 |      0.04  |           20.02 |
| Structuring            |     5519 |      0.005 |          285.31 |
| Deposit-Send           |     1684 |      0.002 |          410.9  |
| Layered_Fan_Out        |      949 |      0.001 |          415.76 |
| Layered_Fan_In         |      851 |      0.001 |          709.51 |
| Normal_LargeCash       |      725 |      0.001 |        15173.1  |
| Cycle                  |      694 |      0.001 |         1468.21 |
| Behavioural_Change_1   |      627 |      0.001 |          205.27 |
| Behavioural_Change_2   |      596 |      0.001 |          223.69 |
| Gather-Scatter         |      577 |      0.001 |          552.25 |
| Fan_In                 |      439 |      0     |          565.09 |
| Fan_Out                |      402 |      0     |          661.17 |
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
|               0 |         0.17 |            0.03 |           2.88 |
|               1 |         1.36 |            0.48 |          24.7  |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5106 |         4605 |      3.09607e+06 |
| unwitting |        4419 |         3706 | 499427           |
| witting   |        4148 |         3913 | 490693           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 5,968; true 182 -> false alarm share 97.0% (target 90-95%)
- Launderers alerted after their start: 179 of 732 (24%); accounts closed: 145

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      725 |             2 |
| R2     |      747 |            15 |
| R3     |      319 |             1 |
| R4     |      701 |           161 |
| R5     |        3 |             0 |
| R6     |     4534 |            13 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          1 |        445 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   54.3 |                26 |            175 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        31 |       26 |
| Deposit-Send         |          111 |        29 |       25 |
| Behavioural_Change_1 |           50 |         4 |        3 |
| Layered_Fan_Out      |           50 |        10 |       10 |
| Layered_Fan_In       |           46 |        19 |       15 |
| Behavioural_Change_2 |           44 |         4 |        2 |
| Gather-Scatter       |           43 |        11 |       10 |
| Cycle                |           40 |        29 |       24 |
| Fan_In               |           33 |         9 |        6 |
| Scatter-Gather       |           27 |         4 |        2 |
| Fan_Out              |           25 |        10 |       10 |
| Bipartite            |           24 |         7 |        5 |
| Stacked Bipartite    |           22 |         1 |        1 |
| Cash_Withdrawal      |           18 |         8 |        6 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.765 (average precision 0.165, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.496, money_in 0.509, money_out 0.512, max_in 0.587, n_senders 0.584, share_abroad 0.539, n_internal 0.644, spike 0.482
