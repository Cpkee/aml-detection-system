# Appendix draft: what if the bank had no labels, or only its own?

Draft text for the report (31 Oct 2026). Numbers from `outputs/modelling/outlier/v1_full/report.md`, written by
`notebooks/12_outlier_detection.ipynb`; plan and decisions in `PLAN.md`.

## Why this appendix

Our model learns from the simulator's answer key, which marks every mule. A real bank never has that. It knows only
the mules its rules alerted and its investigators confirmed: in our simulation, 189 of 732 launderers. The other 543
look like ordinary customers in the bank's records. This appendix asks whether our main result depends on labels a
bank could not have. It tests two alternatives. The first uses no labels at all: outlier detection, which flags
account-weeks that look unusual. The second trains our model on the bank's own labels: only the mules the bank
confirmed count as mules.

## What we did

We compared six methods with the bank's six rules on the accounts opened in month 5 (29,120 accounts, 78 mules by
week 26). Month 5 is the calibration month, so the test months stay untouched. Every method got the same alert budget
as the rules, week by week (124 flags over weeks 0–26), and a flagged account stays flagged.

- **Two label-free detectors** use 19 weekly activity inputs that describe the shape of behaviour, not its size (how
  fast money passes through, how many payers, change from the account's own past). Each account-week is compared with
  accounts of exactly the same age. The **rarity score** (M3) asks, for each input, how rare the value is in its
  suspicious direction, then averages the three rarest. **Isolation Forest** (M4) flags unusual combinations.
- **The bank-label model** (M2) is our model's exact recipe, trained with only the confirmed mules as mules. Its
  yardstick (M1b) is the same recipe trained on the true labels on the same computer.

Every setting was fixed and committed before month 5 was scored, and month 5 was scored once. This stops us from
tuning the result to the data. We also wrote down in advance how each possible result would be read.

## What we found

| Method | Mules caught (of 78) | Never confirmed by the bank, caught (of 62) |
|---|---|---|
| Bank's rules | 16 | 3 |
| Our model, true labels (M1) | 63 | 50 |
| Our model, bank labels only (M2) | 54 | 42 |
| Rarity score, no labels (M3) | 16 | 12 |
| Isolation Forest, no labels (M4) | 16 | 13 |
| Rarity summed over all inputs, no labels (side by side only) | 39 | 30 |

1. **Without labels, outlier detection only matches the rules.** Both label-free detectors catch 16 mules, the same as
   the rules (95% intervals of the difference −11 to +10 and −10 to +10). They catch different mules from the rules:
   only 4 of their 16 are mules the rules also catch. So our model's advantage comes from learning from labels, not
   from the activity features alone.
2. **With the bank's own labels, our model still wins clearly.** It catches 54 instead of 63: 9 fewer (interval 2 to
   16). That is a real loss, but it keeps 86% of its catches and still finds 38 more mules than the rules (interval 28
   to 49). Of the 62 mules the bank never confirmed, it finds 42. Most of its catches are fake accounts (50 of 54),
   which look alike whether or not the bank caught them.
3. **The bank's labels miss most mules, and so do its rules.** The rules catch only 3 of the 62 mules the bank never
   confirmed. That is expected, because the bank's confirmations come from the rules' own alerts.
4. **How a detector adds up its evidence matters.** The same rarity values, summed over all 19 inputs instead of
   averaging the three rarest, catch 39 mules: 23 more than the rules (interval 12 to 33). We fixed this version in
   advance as a side-by-side comparison, never as our choice. Switching to it now would be choosing after seeing the
   answer, so it is a lead to test on fresh data, not a result.

## What it means for the main result

Our main result survives realistic labels. Trained only on what the bank knows, the model still catches more than
three times as many mules as the rules at the same alert budget. With perfect labels it catches 9 more (63 instead of 54),
so the main result is a best case, and we state that cost as a limitation. Outlier detection on its own is no
substitute for labels in our data. It catches a few mules the bank-label model misses (5 never confirmed), so
combining the two could help, but we did not test that at a fair budget.

## Limitations

- One month and 78 mules: counts move by about ±10 between resamples, so only differences whose interval excludes 0
  are treated as results.
- The 19 inputs come from features we chose by looking at labels earlier in the project. Even the "label-free"
  detectors therefore know what laundering looks like. A bank with truly no labels would start from more generic
  features and would likely do worse.
- The labels, the laundering and the bank's confirmations are all simulated; results are relative comparisons.
- The single scoring run happened on 31 Oct instead of the planned 6 Nov. The settings had already been frozen and
  committed, so this changed nothing.
- An autoencoder, a third common label-free method, was left out to keep the settings reviewable before the freeze.
  It is further work.
