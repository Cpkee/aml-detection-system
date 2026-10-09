# Data card

Run: v1, seed 42, 244,000 accounts, 548 days each.

Overrides (--set): size.n_accounts=244000, rules.fixed_scale=1.516, profiles.in_window_mix={"fake": 0.56, "witting": 0.22, "unwitting": 0.22}. Code: 23fc46a. BAF file: data/raw/BAF_Base.csv (sha256 7bf10a37ce07). See run_manifest.json.

## Accounts by profile

| profile        |      n |   fraud_rows |
|:---------------|-------:|-------------:|
| normal         | 240921 |            0 |
| app_fraud_only |   2347 |         2347 |
| fake           |    410 |          410 |
| unwitting      |    161 |            0 |
| witting        |    161 |            0 |

## Activity per account (medians)

| profile        |   rows_per_month |   payments_per_month |   money_in_per_month |   money_out_per_month |   out_over_in |
|:---------------|-----------------:|---------------------:|---------------------:|----------------------:|--------------:|
| app_fraud_only |             24.5 |                 64.7 |                 5287 |                  3868 |          0.74 |
| fake           |             23.6 |                 60.5 |                 4603 |                  3463 |          0.76 |
| normal         |             24.5 |                 60.9 |                 4238 |                  3278 |          0.78 |
| unwitting      |             24.5 |                 58.9 |                 3760 |                  3014 |          0.81 |
| witting        |             24.9 |                 56.5 |                 3341 |                  2871 |          0.81 |

## Rows by type

| laundering_type        |    rows_ |   pct_rows |   median_amount |
|:-----------------------|---------:|-----------:|----------------:|
| Normal_Transfer        | 32882603 |     30.266 |          129.47 |
| Normal_DirectDebit     | 32117133 |     29.562 |           42.06 |
| Normal_Card            | 19290431 |     17.756 |          260.67 |
| Normal_CashWithdrawal  |  8784827 |      8.086 |          140    |
| Normal_Salary          |  6379641 |      5.872 |         1943.04 |
| Normal_TransferIn      |  4388881 |      4.04  |          100.04 |
| Normal_StandingOrder   |  3521279 |      3.241 |           54.18 |
| Normal_CashDeposit     |   525723 |      0.484 |          149.9  |
| Normal_Cheque          |   440383 |      0.405 |          100.16 |
| Normal_Abroad          |   153608 |      0.141 |          450.51 |
| Normal_Bonus           |   104216 |      0.096 |         1243.01 |
| Normal_GroupCollection |    40906 |      0.038 |           20.02 |
| Structuring            |     5454 |      0.005 |          283.16 |
| Deposit-Send           |     1350 |      0.001 |          449.27 |
| Layered_Fan_Out        |     1142 |      0.001 |          462.61 |
| Layered_Fan_In         |      894 |      0.001 |          729.09 |
| Normal_LargeCash       |      781 |      0.001 |        14770    |
| Gather-Scatter         |      650 |      0.001 |          583.02 |
| Behavioural_Change_2   |      628 |      0.001 |          242.62 |
| Cycle                  |      609 |      0.001 |         1539.48 |
| Behavioural_Change_1   |      461 |      0     |          224.04 |
| Stacked Bipartite      |      441 |      0     |          593.14 |
| Fan_Out                |      437 |      0     |          632.96 |
| Bipartite              |      352 |      0     |          583.34 |
| Scatter-Gather         |      316 |      0     |          532.01 |
| Fan_In                 |      290 |      0     |          573.5  |
| Cash_Withdrawal        |      212 |      0     |          267.03 |
| Smurfing               |      143 |      0     |          169.45 |

## Laundering start (days after opening)

| profile   |   n |   min_rel |   median_rel |   max_rel |   pct_year1 |
|:----------|----:|----------:|-------------:|----------:|------------:|
| fake      | 410 |        60 |           92 |       120 |       100   |
| unwitting | 161 |         0 |          303 |       525 |        57.8 |
| witting   | 161 |         7 |          308 |       526 |        59   |

## Launderer networks

| net         |   n |
|:------------|----:|
| big network | 183 |
| chain       | 549 |

## Outgoing rows: abroad, high-risk, internal (%)

|   is_laundering |   pct_abroad |   pct_high_risk |   pct_internal |
|----------------:|-------------:|----------------:|---------------:|
|               0 |         0.16 |            0.03 |           2.75 |
|               1 |         1.63 |            0.47 |          23.72 |

## Laundered money per launderer (GBP)

| profile   |   median_in |   median_out |         total_in |
|:----------|------------:|-------------:|-----------------:|
| fake      |        5483 |         4997 |      2.45297e+06 |
| unwitting |        4347 |         3860 | 834299           |
| witting   |        4034 |         3472 | 807413           |

## The bank's rules (benchmark)

- Threshold scale for R3-R6: 1.516 (frozen (rules.fixed_scale, not tuned on this run))
- Alerts: 3,587; true 227 -> false alarm share 93.7% (target 90-95%)
- Launderers alerted after their start: 227 of 732 (31%); accounts closed: 195

| rule   |   alerts |   true_alerts |
|:-------|---------:|--------------:|
| R1     |      781 |             0 |
| R2     |      803 |            10 |
| R3     |      808 |             3 |
| R4     |     1282 |           199 |
| R5     |        8 |             0 |
| R6     |     1103 |            23 |

Days from laundering start to the rules' first true alert:

|   median_days_to_catch |   min_days |   max_days |
|-----------------------:|-----------:|-----------:|
|                      9 |          0 |        403 |

Weekly alert budget (what every model gets):

|   mean_alerts_per_week |   median_per_week |   max_per_week |
|-----------------------:|------------------:|---------------:|
|                   32.9 |                34 |             97 |

Launderers by shape (alerted = first alert on or after start):

| shape                |   launderers |   alerted |   closed |
|:---------------------|-------------:|----------:|---------:|
| Structuring          |          192 |        39 |       34 |
| Deposit-Send         |          102 |        32 |       26 |
| Layered_Fan_Out      |           64 |        17 |       15 |
| Layered_Fan_In       |           53 |        24 |       21 |
| Gather-Scatter       |           47 |        14 |       12 |
| Behavioural_Change_2 |           46 |         7 |        6 |
| Cycle                |           38 |        28 |       23 |
| Behavioural_Change_1 |           35 |         5 |        5 |
| Fan_Out              |           34 |        10 |       10 |
| Stacked Bipartite    |           28 |        12 |       10 |
| Bipartite            |           25 |        13 |       11 |
| Scatter-Gather       |           24 |        13 |       12 |
| Fan_In               |           23 |         7 |        6 |
| Cash_Withdrawal      |           13 |         4 |        4 |
| Smurfing             |            8 |         0 |        0 |


## Too-easy check (5-fold, whole-window totals)

- Activity model AUC: 0.809 (average precision 0.182, base rate 0.0030)
- Application-only logistic AUC: 0.664
- Single-feature AUC: n_rows 0.446, money_in 0.472, money_out 0.474, max_in 0.577, n_senders 0.550, share_abroad 0.556, n_internal 0.599, spike 0.490
