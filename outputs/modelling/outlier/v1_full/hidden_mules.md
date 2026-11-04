# Who each method catches: cohort month(s) 5, weeks 0-26

78 mules by the end of week 26; every method flags at the rules' weekly budget (124 flags), permanently, as in `evaluation.score`.

## Bank-confirmed vs never confirmed

| group           |   mules |   rules |   frozen_tuned |   truth_macos |   bank_label |   rarity |   rarity_sum |   iforest |
|:----------------|--------:|--------:|---------------:|--------------:|-------------:|---------:|-------------:|----------:|
| never_confirmed |      62 |       3 |             50 |            50 |           42 |       12 |           30 |        13 |
| bank_confirmed  |      16 |      13 |             13 |            13 |           12 |        4 |            9 |         3 |

## By type

| group     |   mules |   rules |   frozen_tuned |   truth_macos |   bank_label |   rarity |   rarity_sum |   iforest |
|:----------|--------:|--------:|---------------:|--------------:|-------------:|---------:|-------------:|----------:|
| fake      |      70 |      13 |             59 |            59 |           50 |       14 |           34 |        15 |
| witting   |       5 |       3 |              3 |             3 |            3 |        2 |            4 |         1 |
| unwitting |       3 |       0 |              1 |             1 |            1 |        0 |            1 |         0 |

## By main laundering pattern

| group                |   mules |   rules |   frozen_tuned |   truth_macos |   bank_label |   rarity |   rarity_sum |   iforest |
|:---------------------|--------:|--------:|---------------:|--------------:|-------------:|---------:|-------------:|----------:|
| Structuring          |      28 |       4 |             23 |            24 |           21 |       12 |           22 |         8 |
| Deposit-Send         |      12 |       2 |              9 |             9 |            6 |        0 |            5 |         5 |
| Behavioural_Change_1 |       6 |       0 |              3 |             3 |            2 |        0 |            1 |         0 |
| Behavioural_Change_2 |       6 |       1 |              4 |             5 |            4 |        0 |            1 |         0 |
| Fan_In               |       5 |       3 |              5 |             5 |            5 |        2 |            2 |         1 |
| Gather-Scatter       |       5 |       2 |              5 |             5 |            4 |        0 |            2 |         1 |
| Cycle                |       3 |       1 |              3 |             2 |            2 |        1 |            2 |         0 |
| Fan_Out              |       3 |       2 |              3 |             3 |            3 |        0 |            1 |         0 |
| Layered_Fan_In       |       3 |       0 |              2 |             2 |            2 |        0 |            1 |         0 |
| Bipartite            |       2 |       0 |              2 |             1 |            2 |        0 |            1 |         0 |
| Cash_Withdrawal      |       2 |       1 |              2 |             2 |            1 |        1 |            1 |         1 |
| Scatter-Gather       |       2 |       0 |              1 |             1 |            1 |        0 |            0 |         0 |
| Layered_Fan_Out      |       1 |       0 |              1 |             1 |            1 |        0 |            0 |         0 |

## Paired differences in mules caught (1,000 account-level resamples, 95% interval)

| a            | b            |   caught_a |   caught_b |   difference |   low_95 |   high_95 | clear   |
|:-------------|:-------------|-----------:|-----------:|-------------:|---------:|----------:|:--------|
| rules        | frozen_tuned |         16 |         63 |          -47 |      -56 |       -37 | True    |
| rules        | truth_macos  |         16 |         63 |          -47 |      -56 |       -37 | True    |
| rules        | bank_label   |         16 |         54 |          -38 |      -49 |       -28 | True    |
| rules        | rarity       |         16 |         16 |            0 |      -10 |        11 | False   |
| rules        | rarity_sum   |         16 |         39 |          -23 |      -33 |       -12 | True    |
| rules        | iforest      |         16 |         16 |            0 |      -10 |        10 | False   |
| frozen_tuned | truth_macos  |         63 |         63 |            0 |       -4 |         4 | False   |
| frozen_tuned | bank_label   |         63 |         54 |            9 |        3 |        16 | True    |
| frozen_tuned | rarity       |         63 |         16 |           47 |       38 |        57 | True    |
| frozen_tuned | rarity_sum   |         63 |         39 |           24 |       14 |        34 | True    |
| frozen_tuned | iforest      |         63 |         16 |           47 |       37 |        56 | True    |
| truth_macos  | bank_label   |         63 |         54 |            9 |        2 |        16 | True    |
| truth_macos  | rarity       |         63 |         16 |           47 |       38 |        57 | True    |
| truth_macos  | rarity_sum   |         63 |         39 |           24 |       14 |        34 | True    |
| truth_macos  | iforest      |         63 |         16 |           47 |       38 |        56 | True    |
| bank_label   | rarity       |         54 |         16 |           38 |       29 |        48 | True    |
| bank_label   | rarity_sum   |         54 |         39 |           15 |        5 |        25 | True    |
| bank_label   | iforest      |         54 |         16 |           38 |       27 |        49 | True    |
| rarity       | rarity_sum   |         16 |         39 |          -23 |      -32 |       -15 | True    |
| rarity       | iforest      |         16 |         16 |            0 |      -10 |         9 | False   |
| rarity_sum   | iforest      |         39 |         16 |           23 |       14 |        32 | True    |

## Top 20 false alarms per method (normal accounts, highest score at the flag week)

In `alarms.csv`, with the outlier inputs of that account-week.
