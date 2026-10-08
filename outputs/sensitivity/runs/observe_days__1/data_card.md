# Data card

Run: v1, seed 42, 244,000 accounts, 365 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, size.observe_days=365. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             24.5 |                 64.7 |                 5327 |                  3886 |          0.74 |
| fake           |             24.5 |                 60.4 |                 4416 |                  3483 |          0.77 |
| normal         |             24.5 |                 61   |                 4222 |                  3282 |          0.78 |
| unwitting      |             24.4 |                 56.8 |                 3729 |                  3103 |          0.8  |
| witting        |             24.1 |                 55.7 |                 3625 |                  2870 |          0.8  |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 21769149 |     30.118 |          129.45 |
| Normal_DirectDebit     | 21373638 |     29.571 |           42.09 |
| Normal_Card            | 12918120 |     17.873 |          260.57 |
| Normal_CashWithdrawal  |  5847735 |      8.09  |          140    |
| Normal_Salary          |  4245284 |      5.873 |         1942.99 |
| Normal_TransferIn      |  2922707 |      4.044 |           99.98 |
| Normal_StandingOrder   |  2342477 |      3.241 |           54.16 |
| Normal_CashDeposit     |   349764 |      0.484 |          150.07 |
| Normal_Cheque          |   292727 |      0.405 |          100.19 |
| Normal_Abroad          |   103072 |      0.143 |          448.47 |
| Normal_Bonus           |    72827 |      0.101 |         1249.74 |
| Normal_GroupCollection |    27472 |      0.038 |           19.95 |
| Structuring            |     5225 |      0.007 |          290.35 |
| Deposit-Send           |     1234 |      0.002 |          437.91 |
| Layered_Fan_Out        |     1103 |      0.002 |          441.02 |
| Layered_Fan_In         |      949 |      0.001 |          692.29 |
| Cycle                  |      881 |      0.001 |         1420.02 |
| Behavioural_Change_1   |      567 |      0.001 |          215.79 |
| Fan_In                 |      547 |      0.001 |          601.45 |
| Normal_LargeCash       |      492 |      0.001 |        15009.3  |
| Behavioural_Change_2   |      488 |      0.001 |          260.21 |
| Fan_Out                |      474 |      0.001 |          635.1  |
| Gather-Scatter         |      461 |      0.001 |          524.51 |
| Scatter-Gather         |      381 |      0.001 |          519.16 |
| Bipartite              |      337 |      0     |          656.2  |
| Stacked Bipartite      |      336 |      0     |          430.18 |
| Cash_Withdrawal        |      309 |      0     |          272.06 |
| Smurfing               |      304 |      0     |          175.29 |

## Laundering start (days after opening)

| profile   |   n |   min_rel |   median_rel |   max_rel |   pct_year1 |
|:----------|----:|----------:|-------------:|----------:|------------:|
| fake      | 537 |        60 |           92 |       120 |         100 |
| unwitting |  97 |         6 |          195 |       340 |         100 |
| witting   |  98 |         1 |          193 |       343 |         100 |

## Launderer networks

| net         |   n |
|:------------|----:|
| big network | 183 |
| chain       | 549 |

## Outgoing rows: abroad, high-risk, internal (%)

|   is_laundering |   pct_abroad |   pct_high_risk |   pct_internal |
|----------------:|-------------:|----------------:|---------------:|
|               0 |         0.16 |            0.03 |           2.52 |
|               1 |         1.31 |            0.38 |          24.96 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5336 |         4885 |      3.25454e+06 |
| unwitting |        4430 |         3993 | 540103           |
| witting   |        5022 |         4053 | 514519           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 2,467; true 259 -> false alarm share 89.5% (target 90-95%)
- Launderers alerted after their start: 257 of 732 (35%); accounts closed: 208

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      492 |             0 |
| R2     |      506 |            11 |
| R3     |      548 |             3 |
| R4     |      971 |           235 |
| R5     |        5 |             0 |
| R6     |      682 |            20 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      8 |          0 |        240 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   29.7 |                29 |             85 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          174 |        53 |       43 |
| Deposit-Send         |           95 |        31 |       25 |
| Layered_Fan_Out      |           60 |        16 |       10 |
| Cycle                |           57 |        43 |       34 |
| Layered_Fan_In       |           56 |        26 |       25 |
| Behavioural_Change_1 |           44 |         1 |        1 |
| Fan_In               |           40 |        17 |       11 |
| Behavioural_Change_2 |           37 |         4 |        3 |
| Fan_Out              |           34 |        16 |       13 |
| Gather-Scatter       |           31 |        13 |       13 |
| Scatter-Gather       |           26 |         9 |        8 |
| Bipartite            |           25 |         8 |        7 |
| Stacked Bipartite    |           22 |         8 |        9 |
| Cash_Withdrawal      |           18 |         7 |        3 |
| Smurfing             |           13 |         3 |        3 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.793 (average precision 0.180, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.456, money_in 0.508, money_out 0.507, max_in 0.593, n_senders 0.582, share_abroad 0.553, n_internal 0.672, spike 0.453
