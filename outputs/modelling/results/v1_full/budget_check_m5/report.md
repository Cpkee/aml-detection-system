# Budget check: rule alerts vs distinct accounts

Data `data/v1_full`, cohort months [5], model `frozen_tuned_avg5` (`python -m evaluation.budget_check`).
The harness's budget counts rule alerts; the rules can alert one account more than once, so the model flags a few more distinct accounts than the rules. Here the model is scored again with the budget capped at the accounts the rules alerted for the first time each week. Test months are not read.

| weeks   | budget            |   budget_total |   flagged |   caught |   mules |   precision |   catch_mean |
|:--------|:------------------|---------------:|----------:|---------:|--------:|------------:|-------------:|
| 0-26    | alerts (harness)  |            124 |       124 |       65 |      78 |       0.524 |        0.384 |
| 0-26    | distinct accounts |            119 |       119 |       65 |      78 |       0.546 |        0.379 |
| 0-77    | alerts (harness)  |            382 |       382 |       79 |      97 |       0.207 |        0.678 |
| 0-77    | distinct accounts |            350 |       350 |       79 |      97 |       0.226 |        0.676 |

Rules (the same under both budgets): weeks 0-26: 16 of 78, precision 0.134; weeks 0-77: 29 of 97, precision 0.083.

**Reading:** the model catches the same number of mules under both budgets at every horizon, so counting alerts instead of accounts does not drive the comparison on this cohort.
