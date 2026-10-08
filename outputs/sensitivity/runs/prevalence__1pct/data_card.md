# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, profiles.launderer_share=0.01. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

## Accounts by profile

| profile        |      n |   fraud_rows |
|:---------------|-------:|-------------:|
| normal         | 240592 |            0 |
| fake           |   1789 |         1789 |
| app_fraud_only |    968 |          968 |
| witting        |    326 |            0 |
| unwitting      |    325 |            0 |

## Activity per account (medians)

| profile        |   rows_per_month |   payments_per_month |   money_in_per_month |   money_out_per_month |   out_over_in |
|:---------------|-----------------:|---------------------:|---------------------:|----------------------:|--------------:|
| app_fraud_only |             24.6 |                 64.6 |                 5267 |                  3851 |          0.74 |
| fake           |             24.3 |                 61.4 |                 4515 |                  3459 |          0.76 |
| normal         |             24.5 |                 60.9 |                 4238 |                  3278 |          0.78 |
| unwitting      |             24.5 |                 57.1 |                 3690 |                  3046 |          0.8  |
| witting        |             24.5 |                 58.3 |                 3896 |                  3221 |          0.79 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32835594 |     30.254 |          129.43 |
| Normal_DirectDebit     | 32078111 |     29.556 |           42.04 |
| Normal_Card            | 19266649 |     17.752 |          260.6  |
| Normal_CashWithdrawal  |  8773979 |      8.084 |          140    |
| Normal_Salary          |  6370530 |      5.87  |         1943.74 |
| Normal_TransferIn      |  4383436 |      4.039 |          100.04 |
| Normal_StandingOrder   |  3516912 |      3.24  |           54.16 |
| Normal_CashDeposit     |   525045 |      0.484 |          149.89 |
| Normal_Cheque          |   439790 |      0.405 |          100.17 |
| Normal_Abroad          |   153328 |      0.141 |          450.53 |
| Normal_Bonus           |   104109 |      0.096 |         1242.23 |
| Normal_GroupCollection |    40839 |      0.038 |           20.02 |
| Structuring            |    17746 |      0.016 |          291.08 |
| Deposit-Send           |     4500 |      0.004 |          418.98 |
| Layered_Fan_Out        |     2833 |      0.003 |          439.72 |
| Layered_Fan_In         |     2206 |      0.002 |          711.73 |
| Cycle                  |     2048 |      0.002 |         1396.11 |
| Fan_In                 |     1942 |      0.002 |          580.16 |
| Behavioural_Change_1   |     1921 |      0.002 |          208.02 |
| Behavioural_Change_2   |     1870 |      0.002 |          222.18 |
| Gather-Scatter         |     1708 |      0.002 |          553.92 |
| Stacked Bipartite      |     1598 |      0.001 |          520.69 |
| Fan_Out                |     1362 |      0.001 |          625.06 |
| Bipartite              |     1219 |      0.001 |          579.78 |
| Scatter-Gather         |     1110 |      0.001 |          505.49 |
| Smurfing               |      874 |      0.001 |          165.88 |
| Cash_Withdrawal        |      811 |      0.001 |          273.5  |
| Normal_LargeCash       |      778 |      0.001 |        14751.2  |

## Laundering start (days after opening)

| profile   |    n |   min_rel |   median_rel |   max_rel |   pct_year1 |
|:----------|-----:|----------:|-------------:|----------:|------------:|
| fake      | 1789 |        60 |           90 |       120 |       100   |
| unwitting |  325 |         1 |          288 |       525 |        62.8 |
| witting   |  326 |         0 |          322 |       526 |        57.4 |

## Launderer networks

| net         |    n |
|:------------|-----:|
| big network |  610 |
| chain       | 1830 |

## Outgoing rows: abroad, high-risk, internal (%)

|   is_laundering |   pct_abroad |   pct_high_risk |   pct_internal |
|----------------:|-------------:|----------------:|---------------:|
|               0 |         0.16 |            0.03 |           2.75 |
|               1 |         1.57 |            0.39 |          23.17 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |    total_in |
|:----------|------------:|-------------:|------------:|
| fake      |        4947 |         4488 | 9.97824e+06 |
| unwitting |        4350 |         3785 | 1.57872e+06 |
| witting   |        4273 |         3681 | 1.58704e+06 |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 4,119; true 769 -> false alarm share 81.3% (target 90-95%)
- Launderers alerted after their start: 759 of 2440 (31%); accounts closed: 628

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      778 |             5 |
| R2     |      817 |            32 |
| R3     |      812 |            13 |
| R4     |     1767 |           679 |
| R5     |        8 |             0 |
| R6     |     1153 |            79 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      8 |          0 |        436 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   37.8 |                39 |             95 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          642 |       164 |      140 |
| Deposit-Send         |          335 |        97 |       80 |
| Layered_Fan_Out      |          172 |        49 |       39 |
| Layered_Fan_In       |          149 |        60 |       50 |
| Fan_In               |          145 |        54 |       44 |
| Behavioural_Change_1 |          143 |        12 |       10 |
| Behavioural_Change_2 |          137 |         8 |        6 |
| Cycle                |          136 |       102 |       92 |
| Gather-Scatter       |          127 |        45 |       32 |
| Stacked Bipartite    |          103 |        37 |       30 |
| Fan_Out              |           94 |        49 |       37 |
| Bipartite            |           88 |        36 |       29 |
| Scatter-Gather       |           79 |        31 |       27 |
| Cash_Withdrawal      |           46 |        11 |        9 |
| Smurfing             |           44 |         3 |        3 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.875 (average precision 0.401, base rate 0.0100)
- Application-only logistic AUC: 0.740
- Single-feature AUC: n_rows 0.452, money_in 0.490, money_out 0.486, max_in 0.599, n_senders 0.546, share_abroad 0.559, n_internal 0.577, spike 0.490
