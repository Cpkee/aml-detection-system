# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, normal.cash_deposits_per_month=4.0. Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             24.5 |                 64.8 |                 5335 |                  3884 |          0.74 |
| fake           |             24.7 |                 62   |                 4742 |                  3667 |          0.76 |
| normal         |             24.7 |                 61   |                 4258 |                  3279 |          0.78 |
| unwitting      |             24.9 |                 58.3 |                 3641 |                  3026 |          0.81 |
| witting        |             25.6 |                 57.7 |                 3572 |                  2906 |          0.77 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32885560 |     30.121 |          129.46 |
| Normal_DirectDebit     | 32119723 |     29.42  |           42.05 |
| Normal_Card            | 19291861 |     17.67  |          260.66 |
| Normal_CashWithdrawal  |  8785342 |      8.047 |          140    |
| Normal_Salary          |  6380375 |      5.844 |         1942.84 |
| Normal_TransferIn      |  4389191 |      4.02  |          100.04 |
| Normal_StandingOrder   |  3521533 |      3.226 |           54.18 |
| Normal_CashDeposit     |  1051688 |      0.963 |          150.06 |
| Normal_Cheque          |   440413 |      0.403 |          100.17 |
| Normal_Abroad          |   151425 |      0.139 |          449.7  |
| Normal_Bonus           |   104242 |      0.095 |         1243.13 |
| Normal_GroupCollection |    41381 |      0.038 |           19.98 |
| Structuring            |     5504 |      0.005 |          285.03 |
| Deposit-Send           |     1681 |      0.002 |          410.45 |
| Layered_Fan_Out        |      949 |      0.001 |          415.76 |
| Layered_Fan_In         |      851 |      0.001 |          709.51 |
| Normal_LargeCash       |      723 |      0.001 |        14708.5  |
| Cycle                  |      694 |      0.001 |         1468.21 |
| Behavioural_Change_1   |      627 |      0.001 |          205.27 |
| Behavioural_Change_2   |      596 |      0.001 |          223.69 |
| Gather-Scatter         |      568 |      0.001 |          555.61 |
| Fan_In                 |      439 |      0     |          565.09 |
| Fan_Out                |      390 |      0     |          678.69 |
| Scatter-Gather         |      376 |      0     |          505.16 |
| Cash_Withdrawal        |      325 |      0     |          270.87 |
| Stacked Bipartite      |      291 |      0     |          483.86 |
| Bipartite              |      276 |      0     |          685.84 |
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
|               1 |         1.35 |            0.48 |          24.59 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5087 |         4602 |      3.08919e+06 |
| unwitting |        4419 |         3706 | 499427           |
| witting   |        4148 |         3835 | 488693           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 18,105; true 201 -> false alarm share 98.9% (target 90-95%)
- Launderers alerted after their start: 197 of 732 (27%); accounts closed: 160

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      721 |             1 |
| R2     |    12783 |            31 |
| R3     |      318 |             3 |
| R4     |      658 |           162 |
| R5     |        5 |             0 |
| R6     |     4666 |            14 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                     10 |          1 |        412 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                  163.1 |               154 |            353 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        34 |       30 |
| Deposit-Send         |          111 |        29 |       26 |
| Behavioural_Change_1 |           50 |         7 |        5 |
| Layered_Fan_Out      |           50 |        14 |       13 |
| Layered_Fan_In       |           46 |        19 |       15 |
| Behavioural_Change_2 |           44 |         6 |        4 |
| Gather-Scatter       |           43 |        10 |        9 |
| Cycle                |           40 |        27 |       24 |
| Fan_In               |           33 |        11 |        6 |
| Scatter-Gather       |           27 |         7 |        5 |
| Fan_Out              |           25 |        11 |       10 |
| Bipartite            |           24 |         6 |        5 |
| Stacked Bipartite    |           22 |         1 |        1 |
| Cash_Withdrawal      |           18 |         9 |        7 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.773 (average precision 0.151, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.485, money_in 0.506, money_out 0.506, max_in 0.589, n_senders 0.574, share_abroad 0.549, n_internal 0.634, spike 0.476
