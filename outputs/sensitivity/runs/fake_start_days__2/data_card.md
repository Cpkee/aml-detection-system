# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.741, timing.fake_start_days=[150, 210]. Code: bb5b24e. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| fake           |             24.7 |                 61.5 |                 4602 |                  3576 |          0.76 |
| normal         |             24.5 |                 60.9 |                 4238 |                  3278 |          0.78 |
| unwitting      |             24.8 |                 60.1 |                 3956 |                  3225 |          0.81 |
| witting        |             25.4 |                 57.6 |                 3376 |                  2759 |          0.8  |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32887384 |     30.267 |          129.46 |
| Normal_DirectDebit     | 32120795 |     29.561 |           42.05 |
| Normal_Card            | 19292835 |     17.756 |          260.66 |
| Normal_CashWithdrawal  |  8785856 |      8.086 |          140    |
| Normal_Salary          |  6380657 |      5.872 |         1942.95 |
| Normal_TransferIn      |  4389461 |      4.04  |          100.04 |
| Normal_StandingOrder   |  3521699 |      3.241 |           54.18 |
| Normal_CashDeposit     |   525720 |      0.484 |          149.89 |
| Normal_Cheque          |   440433 |      0.405 |          100.16 |
| Normal_Abroad          |   153587 |      0.141 |          450.49 |
| Normal_Bonus           |   104234 |      0.096 |         1243.03 |
| Normal_GroupCollection |    40934 |      0.038 |           20.01 |
| Structuring            |     5543 |      0.005 |          277.3  |
| Deposit-Send           |     1345 |      0.001 |          422.25 |
| Layered_Fan_Out        |     1200 |      0.001 |          455.75 |
| Layered_Fan_In         |      956 |      0.001 |          707.44 |
| Normal_LargeCash       |      780 |      0.001 |        14761.8  |
| Behavioural_Change_1   |      678 |      0.001 |          216.99 |
| Stacked Bipartite      |      600 |      0.001 |          559.27 |
| Gather-Scatter         |      588 |      0.001 |          579.04 |
| Fan_In                 |      585 |      0.001 |          601.91 |
| Cycle                  |      576 |      0.001 |         1491.32 |
| Behavioural_Change_2   |      506 |      0     |          235.16 |
| Scatter-Gather         |      362 |      0     |          496.76 |
| Fan_Out                |      299 |      0     |          696.13 |
| Bipartite              |      273 |      0     |          623.67 |
| Cash_Withdrawal        |      233 |      0     |          276.62 |
| Smurfing               |      163 |      0     |          152.77 |

## Laundering start (days after opening)

| profile   |   n |   min_rel |   median_rel |   max_rel |   pct_year1 |
|:----------|----:|----------:|-------------:|----------:|------------:|
| fake      | 537 |       150 |          182 |       210 |       100   |
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
|               1 |         1.37 |            0.4  |          25.43 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5073 |         4618 |      3.11521e+06 |
| unwitting |        4853 |         4032 | 533266           |
| witting   |        4191 |         3875 | 479367           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.741 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 5,938; true 192 -> false alarm share 96.8% (target 90-95%)
- Launderers alerted after their start: 189 of 732 (26%); accounts closed: 153

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      780 |             1 |
| R2     |      804 |            13 |
| R3     |      328 |             0 |
| R4     |      680 |           171 |
| R5     |        5 |             0 |
| R6     |     4494 |            11 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      8 |          0 |        336 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   54.5 |                28 |            166 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          196 |        30 |       25 |
| Deposit-Send         |          101 |        19 |       18 |
| Layered_Fan_Out      |           63 |        15 |       11 |
| Behavioural_Change_1 |           46 |         4 |        4 |
| Layered_Fan_In       |           45 |        21 |       17 |
| Cycle                |           44 |        31 |       23 |
| Gather-Scatter       |           42 |        14 |       11 |
| Fan_In               |           38 |        12 |       10 |
| Behavioural_Change_2 |           36 |         1 |        1 |
| Stacked Bipartite    |           30 |        10 |        9 |
| Scatter-Gather       |           25 |         7 |        6 |
| Fan_Out              |           23 |        11 |        9 |
| Bipartite            |           21 |         6 |        6 |
| Cash_Withdrawal      |           14 |         4 |        3 |
| Smurfing             |            8 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.763 (average precision 0.146, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.484, money_in 0.518, money_out 0.517, max_in 0.588, n_senders 0.573, share_abroad 0.551, n_internal 0.646, spike 0.483
