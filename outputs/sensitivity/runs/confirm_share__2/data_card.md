# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, rules.confirm_share=1.0. Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| fake           |             24.5 |                 61.8 |                 4586 |                  3544 |          0.77 |
| normal         |             24.5 |                 60.9 |                 4238 |                  3278 |          0.78 |
| unwitting      |             24.6 |                 58.3 |                 3641 |                  3026 |          0.81 |
| witting        |             25.5 |                 57.7 |                 3501 |                  2892 |          0.79 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32882750 |     30.266 |          129.46 |
| Normal_DirectDebit     | 32117438 |     29.562 |           42.05 |
| Normal_Card            | 19290481 |     17.756 |          260.66 |
| Normal_CashWithdrawal  |  8784736 |      8.086 |          140    |
| Normal_Salary          |  6379806 |      5.872 |         1942.95 |
| Normal_TransferIn      |  4388889 |      4.04  |          100.04 |
| Normal_StandingOrder   |  3521257 |      3.241 |           54.18 |
| Normal_CashDeposit     |   525571 |      0.484 |          149.89 |
| Normal_Cheque          |   440380 |      0.405 |          100.17 |
| Normal_Abroad          |   153581 |      0.141 |          450.5  |
| Normal_Bonus           |   104230 |      0.096 |         1243.17 |
| Normal_GroupCollection |    40934 |      0.038 |           20.01 |
| Structuring            |     5398 |      0.005 |          286.2  |
| Deposit-Send           |     1669 |      0.002 |          410.45 |
| Layered_Fan_Out        |      934 |      0.001 |          418.44 |
| Layered_Fan_In         |      824 |      0.001 |          704.17 |
| Normal_LargeCash       |      781 |      0.001 |        14770    |
| Cycle                  |      673 |      0.001 |         1472.74 |
| Behavioural_Change_1   |      627 |      0.001 |          205.27 |
| Behavioural_Change_2   |      586 |      0.001 |          220.71 |
| Gather-Scatter         |      550 |      0.001 |          545.64 |
| Fan_In                 |      439 |      0     |          565.09 |
| Fan_Out                |      402 |      0     |          661.17 |
| Scatter-Gather         |      371 |      0     |          508.96 |
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
|               0 |         0.16 |            0.03 |           2.75 |
|               1 |         1.38 |            0.49 |          24.22 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5017 |         4495 |      3.06353e+06 |
| unwitting |        4419 |         3674 | 497434           |
| witting   |        4148 |         3835 | 481180           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 5,923; true 178 -> false alarm share 97.0% (target 90-95%)
- Launderers alerted after their start: 178 of 732 (24%); accounts closed: 178

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      781 |             2 |
| R2     |      806 |            15 |
| R3     |      329 |             1 |
| R4     |      667 |           158 |
| R5     |        5 |             0 |
| R6     |     4495 |            13 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                     10 |          1 |        426 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   54.3 |                28 |            170 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        30 |       31 |
| Deposit-Send         |          111 |        27 |       28 |
| Behavioural_Change_1 |           50 |         3 |        3 |
| Layered_Fan_Out      |           50 |        11 |       11 |
| Layered_Fan_In       |           46 |        17 |       17 |
| Behavioural_Change_2 |           44 |         4 |        4 |
| Gather-Scatter       |           43 |         9 |        9 |
| Cycle                |           40 |        28 |       29 |
| Fan_In               |           33 |        10 |       10 |
| Scatter-Gather       |           27 |         9 |        9 |
| Fan_Out              |           25 |        11 |       11 |
| Bipartite            |           24 |         7 |        7 |
| Stacked Bipartite    |           22 |         1 |        1 |
| Cash_Withdrawal      |           18 |         8 |        8 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.750 (average precision 0.166, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.474, money_in 0.489, money_out 0.489, max_in 0.587, n_senders 0.556, share_abroad 0.546, n_internal 0.612, spike 0.471
