# Top N by application score at opening: month 5 of data/v1_full

Cohort: 29,120 accounts, 97 launder at some point in their 18 months (fake 70, unwitting 15, witting 12); launderer share 0.33%.
Application score: the saved logistic model inside `frozen_tuned_avg5` (fitted on months 0-4).

|   top_n | share_of_accounts   |   launderers | precision   |   reviews_per_launderer |   chance |   lift |   p_chance | share_caught   |   fake |   witting |   unwitting |   median_days_opening_to_start |
|--------:|:--------------------|-------------:|:------------|------------------------:|---------:|-------:|-----------:|:---------------|-------:|----------:|------------:|-------------------------------:|
|      25 | 0.09%               |            2 | 8.0%        |                    12.5 |     0.08 |   24   |   0.00313  | 2.1%           |      2 |         0 |           0 |                           74   |
|      50 | 0.17%               |            2 | 4.0%        |                    25   |     0.17 |   12   |   0.0121   | 2.1%           |      2 |         0 |           0 |                           74   |
|     100 | 0.34%               |            4 | 4.0%        |                    25   |     0.33 |   12   |   0.000355 | 4.1%           |      4 |         0 |           0 |                           75   |
|     200 | 0.69%               |           12 | 6.0%        |                    16.7 |     0.67 |   18   |   3.38e-12 | 12.4%          |     12 |         0 |           0 |                           81.5 |
|     500 | 1.72%               |           24 | 4.8%        |                    20.8 |     1.67 |   14.4 |   2.71e-21 | 24.7%          |     24 |         0 |           0 |                           89   |

- chance: launderers expected in a random pick of N; p_chance: chance of at least this many by luck.
- median_days_opening_to_start: the head start a flag at opening gives over the launderer's start.
- launderers are counted by the fixed final label (at any time in the 18 months), since the flag is raised on the opening day.
