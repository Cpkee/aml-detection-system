# Data card

Run: v1, seed 42, 244,000 accounts, 365 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, size.observe_days=365. Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| fake           |             25   |                 61.5 |                 4730 |                  3639 |          0.77 |
| normal         |             24.5 |                 61   |                 4222 |                  3282 |          0.78 |
| unwitting      |             24.7 |                 58.5 |                 4037 |                  3232 |          0.8  |
| witting        |             24.6 |                 57.6 |                 3692 |                  3027 |          0.8  |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 21771612 |     30.118 |          129.46 |
| Normal_DirectDebit     | 21375740 |     29.571 |           42.09 |
| Normal_Card            | 12919424 |     17.872 |          260.58 |
| Normal_CashWithdrawal  |  5848325 |      8.09  |          140    |
| Normal_Salary          |  4245756 |      5.873 |         1942.98 |
| Normal_TransferIn      |  2922955 |      4.044 |           99.98 |
| Normal_StandingOrder   |  2342728 |      3.241 |           54.16 |
| Normal_CashDeposit     |   349781 |      0.484 |          150.07 |
| Normal_Cheque          |   292754 |      0.405 |          100.2  |
| Normal_Abroad          |   103083 |      0.143 |          448.49 |
| Normal_Bonus           |    72835 |      0.101 |         1249.76 |
| Normal_GroupCollection |    27472 |      0.038 |           19.95 |
| Structuring            |     5236 |      0.007 |          291.03 |
| Deposit-Send           |     1258 |      0.002 |          433.94 |
| Layered_Fan_Out        |     1133 |      0.002 |          433.1  |
| Layered_Fan_In         |      949 |      0.001 |          692.29 |
| Cycle                  |      929 |      0.001 |         1383.9  |
| Behavioural_Change_1   |      576 |      0.001 |          215.56 |
| Fan_In                 |      547 |      0.001 |          601.45 |
| Behavioural_Change_2   |      509 |      0.001 |          262.76 |
| Normal_LargeCash       |      493 |      0.001 |        15012.5  |
| Fan_Out                |      475 |      0.001 |          637.12 |
| Gather-Scatter         |      461 |      0.001 |          524.51 |
| Scatter-Gather         |      369 |      0.001 |          519.16 |
| Stacked Bipartite      |      348 |      0     |          430.18 |
| Bipartite              |      340 |      0     |          659.54 |
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
|               1 |         1.31 |            0.38 |          25.25 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5377 |         5029 |      3.29154e+06 |
| unwitting |        4426 |         4035 | 537301           |
| witting   |        5022 |         4053 | 514519           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 5,209; true 203 -> false alarm share 96.1% (target 90-95%)
- Launderers alerted after their start: 201 of 732 (27%); accounts closed: 163

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      493 |             1 |
| R2     |      507 |            12 |
| R3     |      209 |             0 |
| R4     |      513 |           182 |
| R5     |        1 |             0 |
| R6     |     4207 |            16 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      7 |          0 |        240 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   63.5 |              25.5 |            166 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          174 |        34 |       28 |
| Deposit-Send         |           95 |        28 |       23 |
| Layered_Fan_Out      |           60 |        14 |        9 |
| Cycle                |           57 |        38 |       31 |
| Layered_Fan_In       |           56 |        23 |       22 |
| Behavioural_Change_1 |           44 |         0 |        0 |
| Fan_In               |           40 |        13 |        8 |
| Behavioural_Change_2 |           37 |         2 |        2 |
| Fan_Out              |           34 |        13 |       11 |
| Gather-Scatter       |           31 |        10 |       10 |
| Scatter-Gather       |           26 |         7 |        6 |
| Bipartite            |           25 |         5 |        5 |
| Stacked Bipartite    |           22 |         6 |        6 |
| Cash_Withdrawal      |           18 |         5 |        1 |
| Smurfing             |           13 |         1 |        1 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.811 (average precision 0.143, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.495, money_in 0.531, money_out 0.533, max_in 0.594, n_senders 0.605, share_abroad 0.554, n_internal 0.700, spike 0.461
