# Stability checks and 1:20 undersampling (notebook 10)

## Summary (written by hand after the run)

1. **Reproducibility.** The default model is fully reproducible on one machine: two runs in a row match exactly (0
   difference in every measure and every score), and today's run equals this Mac's 26–27 Oct runs (mean weekly recall
   0.4086). The three different numbers (0.4086 / 0.4023 / 0.4123) came from three computers with three copies of
   `data/v1_full`; nudging the app score by one part in a million moves the mean to 0.4122, so last-digit differences
   between machines are enough to explain them. The gaps are about the size of the seed spread.
2. **Seed spread.** For the tuned model the SD over 5 seeds of `catch_0.1pct` (0.006–0.008) exceeds the 0.005 limit in
   all folds (`catch_rules` 0.004–0.010 stays under 0.012), so by the pre-registered rule we **recommend averaging 5
   seeds' scores** in the final model. The tuned model's lead over the default is larger than the seed spread on weekly
   recall (+0.010 to +0.044 per fold) but not on `catch_0.1pct`, `catch_rules` or `first_caught_2wk`.
3. **1:20 undersampling.** Same early detection as class weights (`catch_rules` +0.003, `first_caught_2wk` +0.006),
   slightly weaker ranking (weekly recall −0.007, PR-AUC −0.020, mostly fold 1), 2–4x faster training.

**Decisions for the team**

- Average 5 seeds in the final model (rule triggered), or keep the frozen single seed and state the seed spread in the
  report? Averaging needs a change to `src/models/train.py` and a retrain before the 4 Nov freeze.
- Produce every reported number on one machine and one data copy; optionally compare data hashes across machines.
- Should the lab's noise levels include seed spread (e.g. judge candidates on a seed average), given that the seed SD of
  `catch_0.1pct` is above its placebo noise level?
- The tuned settings' gain does not reach the rules-budget measures: keep them (weekly recall is the agreed tuning
  measure), but say so in the report.
- Report the 1:20 ablation as "no gain in early detection, slightly worse ranking, faster": class weights stay.

**Looks:** 22 model variants were fitted and scored on the v1_full folds (6 in experiment 1, 11 in experiment 2, 5 in
experiment 3); none chose a feature or a setting. On top of the lab ledger's trials and tuning step 2's 40 trials, the
folds have now been used many times: they are a development yardstick, not an unbiased estimate.

Written by `notebooks/10_stability_undersampling.ipynb` on 2026-10-29, data `v1_full` (this Mac's copy), commit fe96d48-dirty, macOS-26.5.1-arm64-arm-64bit, 15 cores, lightgbm 4.7.0. Months 0-4 only, the lab's 3 temporal folds; month 5 and test months 6-7 never read.

**Data copy.** This Mac's `data/v1_full` (`run_manifest.json` sha256 4ce1c4fb593a...) differs by hash from the copies the frozen models were trained on (frozen 1c08c3e81fd6..., frozen_tuned c5aa290d0721...); the hash also covers the BAF path, git commit and package versions, so it does not by itself prove the data differ. Absolute numbers are for comparison inside this report only.

**Looks at the v1_full folds.** 22 model variants were fitted and scored on the 3 folds here (none is a feature trial and none was chosen by these numbers; no lab ledger rows were written, because only the lab's own command appends to it).

## Experiment 1: reproducibility

Rule (fixed before the run): reproducible on one machine only if two runs match to 1e-9 on every fold. Largest difference between two runs of the lab's baseline: measures 0, validation scores 0. **Reproducible on one machine.**

Recorded runs of the same default model (weekly recall per fold):

|                                        |        1 |        2 |        3 |     mean |
|:---------------------------------------|---------:|---------:|---------:|---------:|
| 26 Oct, this Mac (agent-trials-phases) | 0.406939 | 0.366146 | 0.452648 | 0.408578 |
| 27 Oct, this Mac (max-out-vs-hist)     | 0.406939 | 0.366146 | 0.452648 | 0.408578 |
| 28 Oct, Emmy (noise-placebo5)          | 0.419522 | 0.354095 | 0.433354 | 0.402323 |
| 28 Oct, Emmy (graph)                   | 0.419522 | 0.354095 | 0.433354 | 0.402323 |
| 28 Oct, Windows (notebook 08 trial 0)  | 0.411366 | 0.378645 | 0.446889 | 0.412300 |
| today, this Mac, run A                 | 0.406939 | 0.366146 | 0.452648 | 0.408578 |

This Mac today reproduces this Mac's 26-27 Oct runs to 1e-9: **True**.

Checks (default model unless stated; max |score - A| = largest change in any validation score):

| run                                 |   weekly_recall f1 |   weekly_recall f2 |   weekly_recall f3 |   weekly_recall mean |   catch_rules mean |   catch_0.1pct mean |   max |score - A| |
|:------------------------------------|-------------------:|-------------------:|-------------------:|---------------------:|-------------------:|--------------------:|------------------:|
| A: lab baseline                     |           0.406939 |           0.366146 |           0.452648 |             0.408578 |           0.452358 |            0.556883 |       0           |
| B: lab baseline again               |           0.406939 |           0.366146 |           0.452648 |             0.408578 |           0.452358 |            0.556883 |       0           |
| C: same model, this notebook's loop |           0.406939 |           0.366146 |           0.452648 |             0.408578 |           0.452358 |            0.556883 |       0           |
| D: notebook 08 trial-0 settings     |           0.406939 |           0.366146 |           0.452648 |             0.408578 |           0.452358 |            0.556883 |       4.66552e-10 |
| E: app score x (1 + 1e-9 noise)     |           0.406939 |           0.366146 |           0.452648 |             0.408578 |           0.452358 |            0.556883 |       0           |
| F: app score x (1 + 1e-6 noise)     |           0.425626 |           0.358451 |           0.452648 |             0.412242 |           0.453142 |            0.553208 |       0.69569     |

## Experiment 2: seed spread (tuned settings, random_state 1-5; default settings for comparison)

|                 |   weekly_recall f1 |   weekly_recall f2 |   weekly_recall f3 |   weekly_recall mean |   catch_0.1pct f1 |   catch_0.1pct f2 |   catch_0.1pct f3 |   catch_0.1pct mean |   catch_rules f1 |   catch_rules f2 |   catch_rules f3 |   catch_rules mean |   first_caught_2wk f1 |   first_caught_2wk f2 |   first_caught_2wk f3 |   first_caught_2wk mean |   start_recall f1 |   start_recall f2 |   start_recall f3 |   start_recall mean |
|:----------------|-------------------:|-------------------:|-------------------:|---------------------:|------------------:|------------------:|------------------:|--------------------:|-----------------:|-----------------:|-----------------:|-------------------:|----------------------:|----------------------:|----------------------:|------------------------:|------------------:|------------------:|------------------:|--------------------:|
| ('default', 1)  |             0.4072 |             0.3607 |             0.4347 |               0.4009 |            0.5587 |            0.5427 |            0.5633 |              0.5549 |           0.4782 |           0.4665 |           0.4223 |             0.4557 |                0.9688 |                0.9286 |                0.9600 |                  0.9524 |            0.8189 |            0.6957 |            0.8146 |              0.7764 |
| ('default', 2)  |             0.4130 |             0.3604 |             0.4527 |               0.4087 |            0.5809 |            0.5242 |            0.5574 |              0.5542 |           0.4806 |           0.4557 |           0.4291 |             0.4552 |                0.9688 |                0.9286 |                0.9600 |                  0.9524 |            0.8346 |            0.7319 |            0.8344 |              0.8003 |
| ('default', 3)  |             0.4056 |             0.3735 |             0.4425 |               0.4072 |            0.5840 |            0.5412 |            0.5655 |              0.5636 |           0.4867 |           0.4545 |           0.4366 |             0.4593 |                0.9688 |                0.9143 |                0.9733 |                  0.9521 |            0.8189 |            0.7101 |            0.8079 |              0.7790 |
| ('default', 4)  |             0.4075 |             0.3739 |             0.4568 |               0.4128 |            0.5770 |            0.5445 |            0.5591 |              0.5602 |           0.4776 |           0.4532 |           0.4198 |             0.4502 |                0.9688 |                0.9286 |                0.9733 |                  0.9569 |            0.8268 |            0.7174 |            0.8146 |              0.7862 |
| ('default', 5)  |             0.4121 |             0.3761 |             0.4472 |               0.4118 |            0.5836 |            0.5477 |            0.5641 |              0.5651 |           0.4800 |           0.4546 |           0.4475 |             0.4607 |                0.9688 |                0.9286 |                0.9733 |                  0.9569 |            0.8268 |            0.7174 |            0.8278 |              0.7907 |
| ('default', 42) |             0.4069 |             0.3661 |             0.4526 |               0.4086 |            0.5833 |            0.5329 |            0.5544 |              0.5569 |           0.4758 |           0.4545 |           0.4267 |             0.4524 |                0.9688 |                0.9286 |                0.9733 |                  0.9569 |            0.8268 |            0.6957 |            0.8212 |              0.7812 |
| ('tuned', 1)    |             0.4255 |             0.4062 |             0.4530 |               0.4282 |            0.5737 |            0.5383 |            0.5710 |              0.5610 |           0.4608 |           0.4498 |           0.4283 |             0.4463 |                0.9688 |                0.9286 |                0.9733 |                  0.9569 |            0.8425 |            0.7681 |            0.8278 |              0.8128 |
| ('tuned', 2)    |             0.4299 |             0.4036 |             0.4597 |               0.4311 |            0.5806 |            0.5340 |            0.5606 |              0.5584 |           0.4811 |           0.4599 |           0.4423 |             0.4611 |                0.9688 |                0.9429 |                0.9733 |                  0.9616 |            0.8268 |            0.7536 |            0.8278 |              0.8027 |
| ('tuned', 3)    |             0.4328 |             0.4125 |             0.4555 |               0.4336 |            0.5720 |            0.5462 |            0.5627 |              0.5603 |           0.4733 |           0.4498 |           0.4298 |             0.4510 |                0.9688 |                0.9286 |                0.9733 |                  0.9569 |            0.8346 |            0.7754 |            0.8278 |              0.8126 |
| ('tuned', 4)    |             0.4251 |             0.4222 |             0.4636 |               0.4370 |            0.5632 |            0.5474 |            0.5698 |              0.5601 |           0.4765 |           0.4546 |           0.4416 |             0.4576 |                0.9688 |                0.9286 |                0.9733 |                  0.9569 |            0.8268 |            0.7536 |            0.8278 |              0.8027 |
| ('tuned', 5)    |             0.4225 |             0.4202 |             0.4532 |               0.4320 |            0.5675 |            0.5546 |            0.5563 |              0.5595 |           0.4574 |           0.4498 |           0.4426 |             0.4499 |                0.9688 |                0.9429 |                0.9733 |                  0.9616 |            0.8504 |            0.7826 |            0.8278 |              0.8203 |
| ('tuned', 42)   |             0.4292 |             0.3991 |             0.4625 |               0.4303 |            0.5850 |            0.5481 |            0.5627 |              0.5653 |           0.4765 |           0.4497 |           0.4340 |             0.4534 |                0.9688 |                0.9429 |                0.9733 |                  0.9616 |            0.8346 |            0.7609 |            0.8212 |              0.8056 |

SD across seeds 1-5 (ddof = 1):

|                |   weekly_recall_sd |   catch_0.1pct_sd |   catch_rules_sd |   first_caught_2wk_sd |   start_recall_sd |
|:---------------|-------------------:|------------------:|-----------------:|----------------------:|------------------:|
| ('default', 1) |             0.0033 |            0.0105 |           0.0036 |                0.0000 |            0.0066 |
| ('default', 2) |             0.0077 |            0.0092 |           0.0054 |                0.0064 |            0.0132 |
| ('default', 3) |             0.0087 |            0.0035 |           0.0112 |                0.0073 |            0.0109 |
| ('tuned', 1)   |             0.0041 |            0.0066 |           0.0102 |                0.0000 |            0.0103 |
| ('tuned', 2)   |             0.0082 |            0.0081 |           0.0045 |                0.0078 |            0.0130 |
| ('tuned', 3)   |             0.0046 |            0.0062 |           0.0072 |                0.0000 |            0.0000 |

Rule (fixed before the run): average 5 seeds if the SD of catch_0.1pct > 0.005 or of catch_rules > 0.012 in any fold. Folds over the limit: catch_0.1pct [1, 2, 3], catch_rules none. **Recommendation: average the 5 seeds’ scores in the final model.**

Tuned lead over the default (means over seeds 1-5; `lead (seed 42)` = tuned seed 42 minus Experiment 1's run A):

| measure          |   fold |   tuned mean |   default mean |   lead (means) |   lead (seed 42) |   SD tuned |   SD default | lead > seed SD   |   2 SE of lead | lead > 2 SE   |
|:-----------------|-------:|-------------:|---------------:|---------------:|-----------------:|-----------:|-------------:|:-----------------|---------------:|:--------------|
| weekly_recall    |      1 |       0.4272 |         0.4091 |         0.0181 |           0.0222 |     0.0041 |       0.0033 | True             |         0.0047 | True          |
| weekly_recall    |      2 |       0.4129 |         0.3689 |         0.0440 |           0.0329 |     0.0082 |       0.0077 | True             |         0.0101 | True          |
| weekly_recall    |      3 |       0.4570 |         0.4468 |         0.0102 |           0.0099 |     0.0046 |       0.0087 | True             |         0.0088 | True          |
| catch_0.1pct     |      1 |       0.5714 |         0.5768 |        -0.0054 |           0.0017 |     0.0066 |       0.0105 | False            |         0.0111 | False         |
| catch_0.1pct     |      2 |       0.5441 |         0.5401 |         0.0041 |           0.0152 |     0.0081 |       0.0092 | False            |         0.0109 | False         |
| catch_0.1pct     |      3 |       0.5641 |         0.5619 |         0.0022 |           0.0084 |     0.0062 |       0.0035 | False            |         0.0064 | False         |
| catch_rules      |      1 |       0.4698 |         0.4806 |        -0.0108 |           0.0007 |     0.0102 |       0.0036 | True             |         0.0097 | True          |
| catch_rules      |      2 |       0.4528 |         0.4569 |        -0.0042 |          -0.0048 |     0.0045 |       0.0054 | False            |         0.0063 | False         |
| catch_rules      |      3 |       0.4369 |         0.4311 |         0.0058 |           0.0073 |     0.0072 |       0.0112 | False            |         0.0119 | False         |
| first_caught_2wk |      1 |       0.9688 |         0.9688 |         0.0000 |           0.0000 |     0.0000 |       0.0000 | False            |         0.0000 | False         |
| first_caught_2wk |      2 |       0.9343 |         0.9257 |         0.0086 |           0.0143 |     0.0078 |       0.0064 | True             |         0.0090 | False         |
| first_caught_2wk |      3 |       0.9733 |         0.9680 |         0.0053 |           0.0000 |     0.0000 |       0.0073 | False            |         0.0065 | False         |
| start_recall     |      1 |       0.8362 |         0.8252 |         0.0110 |           0.0079 |     0.0103 |       0.0066 | True             |         0.0109 | True          |
| start_recall     |      2 |       0.7667 |         0.7145 |         0.0522 |           0.0652 |     0.0130 |       0.0132 | True             |         0.0165 | True          |
| start_recall     |      3 |       0.8278 |         0.8199 |         0.0079 |           0.0000 |     0.0000 |       0.0109 | False            |         0.0097 | False         |

## Experiment 3: 1:20 undersampling vs class weights (tuned settings, seeds 1-5, paired by seed)

|   fold |   train rows (all) |   train rows (sample) |   mule rows |   label-0 rows (sample) |   label-0 per mule row |   accounts (all) |   accounts (sample) |   share of rows kept |
|-------:|-------------------:|----------------------:|------------:|------------------------:|-----------------------:|-----------------:|--------------------:|---------------------:|
|      1 |            1708442 |                 73889 |        3518 |                   70371 |                20.0031 |            63293 |                2754 |               0.0432 |
|      2 |            2613390 |                104820 |        4991 |                   99829 |                20.0018 |            96816 |                3906 |               0.0401 |
|      3 |            3604780 |                137656 |        6555 |                  131101 |                20.0002 |           133540 |                5128 |               0.0382 |

|                         |   class weights (mean of seeds) |   1:20 sample (mean of seeds) |   paired change (mean) |   paired change (min) |   paired change (max) |
|:------------------------|--------------------------------:|------------------------------:|-----------------------:|----------------------:|----------------------:|
| ('acc_pr_auc', 1)       |                          0.8709 |                        0.8474 |                -0.0235 |               -0.0304 |               -0.0173 |
| ('acc_pr_auc', 2)       |                          0.8625 |                        0.8249 |                -0.0375 |               -0.0522 |               -0.0228 |
| ('acc_pr_auc', 3)       |                          0.8664 |                        0.8688 |                 0.0025 |               -0.0031 |                0.0054 |
| ('catch_0.1pct', 1)     |                          0.5714 |                        0.5663 |                -0.0051 |               -0.0179 |                0.0096 |
| ('catch_0.1pct', 2)     |                          0.5441 |                        0.5406 |                -0.0035 |               -0.0158 |                0.0090 |
| ('catch_0.1pct', 3)     |                          0.5641 |                        0.5674 |                 0.0033 |               -0.0075 |                0.0169 |
| ('catch_rules', 1)      |                          0.4698 |                        0.4755 |                 0.0057 |               -0.0023 |                0.0198 |
| ('catch_rules', 2)      |                          0.4528 |                        0.4548 |                 0.0020 |               -0.0172 |                0.0217 |
| ('catch_rules', 3)      |                          0.4369 |                        0.4392 |                 0.0023 |               -0.0003 |                0.0094 |
| ('first_caught_2wk', 1) |                          0.9688 |                        0.9781 |                 0.0094 |                0.0000 |                0.0156 |
| ('first_caught_2wk', 2) |                          0.9343 |                        0.9429 |                 0.0086 |                0.0000 |                0.0143 |
| ('first_caught_2wk', 3) |                          0.9733 |                        0.9733 |                 0.0000 |                0.0000 |                0.0000 |
| ('fit_seconds', 1)      |                          7.0064 |                        3.0218 |                -3.9846 |               -5.4988 |               -2.3076 |
| ('fit_seconds', 2)      |                         73.6346 |                        4.6726 |               -68.9620 |             -318.6055 |               -4.9141 |
| ('fit_seconds', 3)      |                         15.3666 |                        4.5886 |               -10.7780 |              -14.8725 |               -7.0107 |
| ('start_recall', 1)     |                          0.8362 |                        0.8362 |                -0.0000 |               -0.0157 |                0.0079 |
| ('start_recall', 2)     |                          0.7667 |                        0.7812 |                 0.0145 |                0.0072 |                0.0290 |
| ('start_recall', 3)     |                          0.8278 |                        0.8265 |                -0.0013 |               -0.0066 |                0.0000 |
| ('weekly_recall', 1)    |                          0.4272 |                        0.4048 |                -0.0224 |               -0.0299 |               -0.0156 |
| ('weekly_recall', 2)    |                          0.4129 |                        0.4176 |                 0.0046 |               -0.0043 |                0.0118 |
| ('weekly_recall', 3)    |                          0.4570 |                        0.4533 |                -0.0037 |               -0.0148 |                0.0054 |

Mean of folds and seeds:

|                  |   class weights |   1:20 sample |   change |   seeds where the sample is higher |   folds where the sample is higher (mean of seeds) |
|:-----------------|----------------:|--------------:|---------:|-----------------------------------:|---------------------------------------------------:|
| weekly_recall    |          0.4324 |        0.4252 |  -0.0072 |                                  0 |                                                  1 |
| catch_0.1pct     |          0.5599 |        0.5581 |  -0.0017 |                                  1 |                                                  1 |
| catch_rules      |          0.4532 |        0.4565 |   0.0033 |                                  4 |                                                  3 |
| first_caught_2wk |          0.9588 |        0.9648 |   0.0060 |                                  5 |                                                  2 |
| start_recall     |          0.8102 |        0.8146 |   0.0044 |                                  3 |                                                  1 |
| acc_pr_auc       |          0.8666 |        0.8471 |  -0.0195 |                                  0 |                                                  1 |
| fit_seconds      |         32.0025 |        4.0943 | -27.9082 |                                  0 |                                                  0 |

Fit time is LightGBM's fit only, on this Mac with other jobs possibly running; compare the two columns, not the absolute seconds.

