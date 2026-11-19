# Alert triage: plan (written 2 Nov 2026)

A proposal for the team (Kee Chee Pheng, 2 Nov 2026). **Report-appendix work only, run after the 5 Nov final test.**
It changes nothing in the frozen model (`frozen_tuned`), the feature store, the frozen feature list,
`configs/sim.yaml` or `amldata`, and it never reads test months 6–7. Every setting below is fixed **before** the
labels are joined to the scores, so the result cannot be tuned to look good.

## Why

The bank's rules raise many alerts, and most are false: 93.4% on v1_full. Each alert costs an investigator's time.
The outlier appendix asked which mules the rules *miss*. This appendix asks the opposite question: among the
accounts the rules *do* alert, which ones look like fraud but are innocent? If a score can sort each week's alerts
so the real ones come first, investigators could skip many false alarms and keep almost all the true ones. This
speaks to professor comment 1 (false alarms under imbalance, `docs/professor_feedback.md`).

## Question

Does any score we already have sort the rules' alerts better than chance, and better than the rules' own
information (how many rules fired)? Which works best with information a bank really has?

## What we use (all fixed already)

- **Alerts:** every rule alert on an account opened in month 5, raised in weeks 0–26 since opening (the main
  horizon). Counted 2 Nov 2026 via `amldata.evaluation()`, no labels: **124 alerts on 119 accounts, weeks 1–26**.
  From the outlier look we already know that 16 of these accounts are mules (rules 16 of 78).
- **Scores:** the six month-5 score files of the outlier look, unchanged, checked by the sha256 in
  `outputs/modelling/outlier/v1_full/LOOK.json`: `frozen_tuned` (M1), `truth_macos` (M1b), `bank_label` (M2),
  `rarity` (M3), `rarity_sum` (M3s), `iforest` (M4). Nothing is retrained or rescored, so there is no setting to
  tune.
- **Rules baseline (B1):** the number of rules that fired on the alert (`rules_fired`), which an investigator sees
  on the alert itself. It is coarse: of the 124 alerts, 95 fired one rule, 18 two (R1;R2) and 11 three (R1;R2;R6),
  so most alerts tie. **Chance (B0):** a random order.
- **Who counts as bank-realistic:** M2, M3, M4 and B1 use only what a bank could have. M1 and M1b learned from the
  simulator's truth, so they are a best case.

## Proposed settings (decisions for the team, T1–T4)

- **T1, true alert:** an alert is true when the account is a mule by the alert's week (`mule_by_day` at that
  `weeks_since_open`: a fake account from opening, a real customer from the start). This is the main result's label.
  Check, reported beside it: the simulator's own definition (laundering has started by the alert day).
- **T2, which score:** the account's score at the end of the alert's week (`weeks_since_open = (alert_day -
  open_day) // 7`). The review takes 3–30 days, so an end-of-week score is available before it ends. Check: the
  score one week earlier, strictly before the alert (every alert is in week 1 or later).
- **T3, main measure:** AUC of each score among the 124 alerts (true vs false), with a 95% interval from 1,000
  account-level bootstrap resamples (accounts, not alerts, since one account has 2 alerts and one has 5). A score **sorts
  alerts** only if its interval excludes 0.5. Two scores differ only if the paired interval of their AUC difference
  excludes 0. Ties take the average rank.
- **T4, plain-language table:** for each score, if investigators review only the top half of the alerts (62),
  how many true alerts they keep and how many false alarms they skip; and how many alerts they must review to keep
  every true alert. Ties at the cut are broken by `alert_id` (fixed order).

## How each result will be read (written before the run)

| Result | Reading |
|---|---|
| M2 sorts alerts, M3 / M4 do not | A bank's own labels help triage; being unusual does not tell innocent alerts apart. |
| M3 or M4 sorts alerts | Unusualness helps triage even without labels: a label-free tool for the alert queue. |
| A score beats B1 | It adds information beyond what the alert itself shows. |
| Nothing beats B0 | Our scores cannot tell the rules' true and false alerts apart; stated as a finding. |
| M3 / M4 AUC below 0.5 | False alarms look *more* unusual than true ones: expected if the false alarms are mostly busy innocent accounts. |

Expectation stated in advance (from the outlier look): the detectors' own top false alarms were fan-in weeks that
look like group collections, so M3 / M4 may sort the rules' alerts poorly.

## Limits

- **Small:** 16 mule accounts among 119. Intervals will be wide; only differences whose interval excludes 0 count.
- **Month 5 again:** the scores and month 5's labels were already used in the outlier look. This is a new question
  on the same month, so it is one more look, recorded here. The test months stay untouched.
- **Weeks 0–26 only:** the models were trained on weeks 0–26; alerts later in life are out of scope.
- **Not tested:** a triage model trained on past alerts and their outcomes. It needs the alerts as a model input,
  which means an `amldata` change (a team decision). Stated as further work.

## Steps (after 5 Nov)

1. Team agrees T1–T4.
2. Code in `src/evaluation/triage.py` (reads alerts via `amldata.evaluation()`, as `budget.py` does) and a test on
   `data/v1` in `tests/test_triage.py`; commit before the run.
3. One run on month 5 of v1_full -> `outputs/modelling/triage/v1_full/`; never re-run with other settings.
4. Write-up in a notebook (`notebooks/13_alert_triage.ipynb`) that reads only the committed outputs, and a short
   appendix paragraph.
