# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, timing.fake_start_days=[15, 45]. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

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
| app_fraud_only |             24.5 |                 64.7 |                 5311 |                  3889 |          0.74 |
| fake           |             24.2 |                 59.4 |                 4160 |                  3242 |          0.77 |
| normal         |             24.5 |                 60.9 |                 4238 |                  3278 |          0.78 |
| unwitting      |             24.6 |                 57.6 |                 3514 |                  2924 |          0.8  |
| witting        |             24.9 |                 56.6 |                 3542 |                  2778 |          0.77 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32877790 |     30.266 |          129.45 |
| Normal_DirectDebit     | 32112449 |     29.562 |           42.05 |
| Normal_Card            | 19287934 |     17.756 |          260.64 |
| Normal_CashWithdrawal  |  8783342 |      8.086 |          140    |
| Normal_Salary          |  6378806 |      5.872 |         1942.84 |
| Normal_TransferIn      |  4388315 |      4.04  |          100.04 |
| Normal_StandingOrder   |  3520739 |      3.241 |           54.17 |
| Normal_CashDeposit     |   525330 |      0.484 |          149.89 |
| Normal_Cheque          |   440325 |      0.405 |          100.16 |
| Normal_Abroad          |   153543 |      0.141 |          450.53 |
| Normal_Bonus           |   104227 |      0.096 |         1243.05 |
| Normal_GroupCollection |    40901 |      0.038 |           20.02 |
| Structuring            |     5445 |      0.005 |          289.31 |
| Deposit-Send           |     1385 |      0.001 |          455.43 |
| Layered_Fan_Out        |      807 |      0.001 |          453.27 |
| Normal_LargeCash       |      780 |      0.001 |        14761.8  |
| Layered_Fan_In         |      722 |      0.001 |          686.06 |
| Stacked Bipartite      |      618 |      0.001 |          525.08 |
| Behavioural_Change_1   |      607 |      0.001 |          204.46 |
| Cycle                  |      596 |      0.001 |         1378.68 |
| Fan_In                 |      595 |      0.001 |          548.9  |
| Behavioural_Change_2   |      467 |      0     |          227.28 |
| Gather-Scatter         |      422 |      0     |          615.27 |
| Bipartite              |      404 |      0     |          668.57 |
| Fan_Out                |      364 |      0     |          623.7  |
| Scatter-Gather         |      337 |      0     |          511.86 |
| Cash_Withdrawal        |      325 |      0     |          272.32 |
| Smurfing               |      182 |      0     |          193.52 |

## Laundering start (days after opening)

| profile   |   n |   min_rel |   median_rel |   max_rel |   pct_year1 |
|:----------|----:|----------:|-------------:|----------:|------------:|
| fake      | 537 |        15 |           31 |        45 |       100   |
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
|               1 |         1.31 |            0.27 |          24.2  |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5015 |         4527 |      3.02788e+06 |
| unwitting |        4343 |         3794 | 473683           |
| witting   |        4149 |         3611 | 483692           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 3,610; true 236 -> false alarm share 93.5% (target 90-95%)
- Launderers alerted after their start: 233 of 732 (32%); accounts closed: 197

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      780 |             1 |
| R2     |      802 |            11 |
| R3     |      813 |             7 |
| R4     |     1313 |           216 |
| R5     |        8 |             0 |
| R6     |     1090 |            11 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        507 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   33.1 |                34 |             94 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          191 |        56 |       50 |
| Deposit-Send         |          104 |        31 |       20 |
| Layered_Fan_Out      |           46 |        16 |       15 |
| Behavioural_Change_1 |           43 |         5 |        4 |
| Fan_In               |           43 |        14 |       13 |
| Layered_Fan_In       |           43 |        16 |       13 |
| Cycle                |           42 |        28 |       26 |
| Stacked Bipartite    |           41 |        15 |       12 |
| Behavioural_Change_2 |           34 |         4 |        4 |
| Gather-Scatter       |           34 |        10 |        8 |
| Fan_Out              |           30 |        13 |       12 |
| Bipartite            |           26 |        14 |       12 |
| Scatter-Gather       |           26 |         7 |        4 |
| Cash_Withdrawal      |           19 |         4 |        4 |
| Smurfing             |           10 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.777 (average precision 0.238, base rate 0.0030)
- Application-only logistic AUC: 0.734
- Single-feature AUC: n_rows 0.442, money_in 0.451, money_out 0.452, max_in 0.581, n_senders 0.526, share_abroad 0.549, n_internal 0.584, spike 0.451
