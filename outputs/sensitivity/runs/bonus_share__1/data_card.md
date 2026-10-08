# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, normal.bonus_share=0.15. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             24.5 |                 64.4 |                 5303 |                  3891 |          0.74 |
| fake           |             24.1 |                 60.5 |                 4477 |                  3443 |          0.76 |
| normal         |             24.5 |                 60.9 |                 4216 |                  3281 |          0.78 |
| unwitting      |             23.9 |                 59.4 |                 3837 |                  2996 |          0.81 |
| witting        |             24.4 |                 56.2 |                 3493 |                  2753 |          0.81 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32897659 |     30.29  |          129.47 |
| Normal_DirectDebit     | 32123787 |     29.577 |           42.07 |
| Normal_Card            | 19289909 |     17.761 |          260.58 |
| Normal_CashWithdrawal  |  8780766 |      8.085 |          140    |
| Normal_Salary          |  6379791 |      5.874 |         1942.63 |
| Normal_TransferIn      |  4391034 |      4.043 |          100.05 |
| Normal_StandingOrder   |  3517695 |      3.239 |           54.24 |
| Normal_CashDeposit     |   525762 |      0.484 |          149.92 |
| Normal_Cheque          |   439852 |      0.405 |           99.96 |
| Normal_Abroad          |   154461 |      0.142 |          448.97 |
| Normal_Bonus           |    52402 |      0.048 |         1237.76 |
| Normal_GroupCollection |    41890 |      0.039 |           19.87 |
| Structuring            |     5405 |      0.005 |          285.02 |
| Deposit-Send           |     1630 |      0.002 |          412.36 |
| Layered_Fan_Out        |      901 |      0.001 |          427.81 |
| Layered_Fan_In         |      782 |      0.001 |          713.01 |
| Normal_LargeCash       |      771 |      0.001 |        14956    |
| Cycle                  |      697 |      0.001 |         1439.45 |
| Behavioural_Change_1   |      636 |      0.001 |          206.02 |
| Gather-Scatter         |      553 |      0.001 |          567.84 |
| Behavioural_Change_2   |      533 |      0     |          232.45 |
| Fan_In                 |      451 |      0     |          557.51 |
| Fan_Out                |      390 |      0     |          678.69 |
| Scatter-Gather         |      376 |      0     |          505.16 |
| Cash_Withdrawal        |      325 |      0     |          270.87 |
| Bipartite              |      279 |      0     |          682    |
| Stacked Bipartite      |      273 |      0     |          483.86 |
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
|               1 |         1.39 |            0.5  |          23.85 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |        total_in |
|:----------|------------:|-------------:|----------------:|
| fake      |        4965 |         4435 |      3.0404e+06 |
| unwitting |        4419 |         3561 | 491751          |
| witting   |        4111 |         3690 | 491254          |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 3,442; true 245 -> false alarm share 92.9% (target 90-95%)
- Launderers alerted after their start: 242 of 732 (33%); accounts closed: 194

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      771 |             3 |
| R2     |      802 |            16 |
| R3     |      888 |             4 |
| R4     |     1283 |           218 |
| R5     |        3 |             0 |
| R6     |      882 |            20 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        436 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   31.3 |              35.5 |             68 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          190 |        45 |       37 |
| Deposit-Send         |          111 |        42 |       33 |
| Behavioural_Change_1 |           50 |         3 |        1 |
| Layered_Fan_Out      |           50 |        17 |       15 |
| Layered_Fan_In       |           46 |        24 |       20 |
| Behavioural_Change_2 |           44 |         6 |        4 |
| Gather-Scatter       |           43 |        20 |       15 |
| Cycle                |           40 |        33 |       28 |
| Fan_In               |           33 |        11 |        8 |
| Scatter-Gather       |           27 |         9 |        7 |
| Fan_Out              |           25 |        13 |       11 |
| Bipartite            |           24 |         7 |        5 |
| Stacked Bipartite    |           22 |         3 |        3 |
| Cash_Withdrawal      |           18 |         9 |        7 |
| Smurfing             |            9 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.758 (average precision 0.172, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.440, money_in 0.483, money_out 0.482, max_in 0.588, n_senders 0.537, share_abroad 0.553, n_internal 0.591, spike 0.469
