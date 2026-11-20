# Rule scorecard: a stronger rule benchmark (plan, drafted 18 Nov 2026)

**Status: scenarios and starting values accepted 18 Nov 2026 (Kee Chee Pheng); committed before any labelled run.
Step 2 (scale, months 0–4) run 18 Nov 2026; month 5 scored once 18 Nov 2026 (result below).** Report-appendix work only. It changes nothing in
the simulator, the six rules, the data, the feature store, the frozen feature list or the model of record, and it
never reads test months 6–7. The headline result (final test, 2 Nov 2026) stays as it is.

## Why

Our benchmark is six rules that we wrote and tuned ourselves. A reader can fairly ask: "would a better rule set
have closed the gap?" A source check (18 Nov 2026) also showed that the rules' *behaviours* are backed by published
red flags, but their thresholds and their catch rate are ours. This appendix gives the rules a second, more
generous chance: three more standard monitoring scenarios, scored at the same weekly budget as everything else.

## The question

On month 5 (78 mules by week 26), at the rules' own weekly alert count, how many mules does a hand-written
scorecard catch, next to the six rules (16) and the model of record (65)?

## What it is

`src/models/rule_scorecard.py`. For every account and every week since opening (0–26), three scenarios are checked
on the public weekly feature store. No model is fitted. No label is read.

| Scenario | Fires when (starting values) | Behaviour it stands for |
|---|---|---|
| S1 fast forwarding | 80%+ of the week's money in is paid out within 24 hours of the latest payment in (`out_24h_share_wk` ≥ 0.8), and money in ≥ £1,000 | FFIEC: transfers received, then "almost immediately, all or most" sent on |
| S2 new payers | 5+ payers in the week (`n_payers_wk`), 80%+ of them never seen before (`new_payer_share_wk`) | FFIEC: "many small, incoming transfers" |
| S3 pass-through | 80%+ of the week's money in leaves the same week (`passthrough_wk`), and money in ≥ £2,000 | Same idea as R4, on the account's own week since opening |

- **The starting values are ours** (round numbers; £2,000 and 80% are R4's starting values). They are assumptions,
  not published figures.
- **Points.** A fired scenario adds `measure / threshold`, capped at 3. An account-week where nothing fires scores 0.
  A missing value never fires. The harness ranks accounts by points each week.
- **Scale.** The amounts and the payer count are multiplied by one common scale, as R3–R6 are. The 80% shares are
  not scaled.

### Dropped (label-free count, months 0–4, 18 Nov 2026)

Two more scenarios were drafted and dropped before any label was read:

| Drafted scenario | Share of account-weeks it fired on | Why |
|---|---|---|
| Money in 5x+ similar accounts (`peer_ratio_money_in`) | 26% | Most people are paid monthly, so every payday week is far above a typical week |
| Money in far above the account's own past (`self_vs_past_money_in` ≥ 10) | 6% | Same reason. R6 already covers sudden change with an 8-week baseline |

The three kept scenarios fire on 0.24% of account-weeks at scale 1 (10,440 of 4,450,113; about 390 a week over
164,819 accounts): S1 2,331, S2 2,012, S3 6,513. The rules' budget is about 0.02% of accounts a week, so the
ranking decides who is flagged.

## Steps

1. **Team agrees this plan; it is committed before any labelled run.**
2. **Choosing the scale (months 0–4 only).** Five scales: 0.5, 0.71, 1.0, 1.41, 2.0. For each, write the scores and
   run the harness on months 0–4, weeks 0–26. Keep the scale that catches the most mules; if two tie, the one
   nearer 1.0. This gives the scorecard its best chance, as the six rules had when they were tuned on labels.
3. **Freeze.** The chosen scale is written into this plan and committed. Done 18 Nov 2026: scale 1.0 (below).
4. **One run on month 5.** Weeks 0–26. Reported whatever it shows. Done 18 Nov 2026 (below).

```bash
# step 2, once per scale S
PYTHONPATH=src python -m models scorecard --out data/v1_full --months 0 1 2 3 4 --scale S --to data/v1_full/scores/scorecard_tune_S.parquet
PYTHONPATH=src python -m evaluation.score --out data/v1_full --months 0 1 2 3 4 --horizons 26 --scores data/v1_full/scores/scorecard_tune_S.parquet --name scorecard_tune_S

# step 4, once
PYTHONPATH=src python -m models scorecard --out data/v1_full --months 5 --scale 1.0
PYTHONPATH=src python -m evaluation.score --out data/v1_full --months 5 --horizons 26 --scores data/v1_full/scores/scorecard_m5.parquet --name month5_scorecard
```

## Step 2 result: scale frozen at 1.0 (18 Nov 2026)

Months 0–4 (164,819 accounts, 361 mules by week 26), weeks 0–26, budget 828 flags; the six rules catch 109.
Results: `outputs/modelling/results/v1_full/scorecard_tune_<scale>/`.

| Scale | Mules caught of 361 | Precision | Fake | Witting | Unwitting | Weeks with ties at the cut (tied accounts) |
|---|---|---|---|---|---|---|
| 0.5 | 119 | 0.144 | 105/320 | 5/16 | 9/25 | 21 (595) |
| 0.71 | 143 | 0.173 | 126/320 | 6/16 | 11/25 | 8 (81) |
| **1.0** | **178** | 0.215 | 157/320 | 6/16 | 15/25 | 6 (32) |
| 1.41 | 155 | 0.187 | 138/320 | 6/16 | 11/25 | 15 (94) |
| 2.0 | 164 | 0.198 | 148/320 | 4/16 | 12/25 | 23 (too few accounts fire: the rest of the budget is filled by account id) |

**Frozen: scale 1.0** (the starting values, unchanged), by the rule in step 2. On these training months the
scorecard catches 178 against the rules' 109. This is the tuning result, chosen on these same months, so it is
not the answer to the question; month 5 is. The model of record is not shown here: it was trained on these months.

## Result: month 5, run once (18 Nov 2026)

Month 5 (29,120 accounts, 78 mules by week 26), weeks 0–26, the rules' weekly budget, scale 1.0 as frozen.
Results: `outputs/modelling/results/v1_full/month5_scorecard/` (the harness labels the scorecard `model` there).
The model of record's numbers are from `month5_dryrun_frozen_tuned_avg5/`, same cohort and budget.

| | Six rules | Scorecard | Model of record |
|---|---|---|---|
| Flagged | 119 | 124 | 124 |
| Mules caught of 78 | 16 | **34** | 65 |
| Precision | 0.13 | 0.27 | 0.52 |
| Fake caught of 70 | 13 | 30 | 61 |
| Witting caught of 5 | 3 | 2 | 3 |
| Unwitting caught of 3 | 0 | 2 | 1 |
| Median days from start to first flag | 8.5 | 9.5 | 9 |
| Flagged before laundering starts | 0 | 0 | 0 |

- **Reading (second row of the table decided above):** better rules help, and the model still leads. Three
  hand-written scenarios double the rules' catch (16 to 34); the model catches about twice as many again (65).
- **Overlap:** 31 of the scorecard's 34 are also caught by the model; 3 are caught by the scorecard only; 34 by the
  model only; 10 by neither. Where both catch a mule, they flag it in the same week 20 times, the model earlier 8
  times, the scorecard earlier 3 times.
- **Scorecard or rules together** catch 37 of 78.
- **Ties:** 5 of 27 weeks, 13 tied accounts in all, so account-id tie-breaking barely matters here.
- **Not earlier:** like the model, the scorecard flags nothing before laundering starts.
- This run is spent: the scenarios, thresholds and scale do not change after it.

## What is reported

Caught of 78, precision, median days from laundering start, caught by type (fake / witting / unwitting), and the
harness's `tied_at_cut`, beside the six rules and the model of record on the same cohort and budget.

## How we will read it (decided now)

| Month-5 result | What we say |
|---|---|
| Scorecard near the six rules (16) | A few more hand-written scenarios do not close the gap; the model's lead is not an artefact of a small rule set |
| Scorecard clearly above the rules, well below the model (65) | Better rules help, and the model still leads; we report both gaps |
| Scorecard near the model | The lead in our headline comes mostly from a weak benchmark; we say so plainly |

"Near" is judged with the measured noise we already have: the model of record gave 63 vs 65 on two machines, and
78 mules is a small sample, so differences of a few mules are not differences.

## Limits, stated in advance

- **Hindsight.** The scenarios were written after the model's results were known, and S1 uses the forwarding-speed
  measure the model leans on. This makes the benchmark generous to the rules. That is the point, and the report
  says it.
- **Not the bank's real system.** Three scenarios are still far fewer than a real bank runs.
- **Stand-alone.** The scorecard is scored on its own, not added to R1–R6: the store cannot rebuild R1, R2 and R5
  exactly (it holds cash and high-risk *shares*, not amounts). The six rules' own result is shown beside it.
- **No closures.** In the simulation only the six rules close accounts. The scorecard flags accounts but closes
  none, exactly like the model.
- **Month 5 has been used before** (dry runs, calibration, the outlier look). This is one more use of it, for a
  setting frozen beforehand.
- **Related result.** The label-free rarity score in the outlier appendix used the same kinds of inputs and
  caught 16 of 78 on month 5, the same as the rules. A similar outcome here would not be a surprise.
- **Ties.** If fewer accounts fire than the week's budget, the harness fills the rest by account id. At scale 2.0
  only about 30 account-weeks a week fire in months 0–4, so this can happen there; `tied_at_cut` shows it.

## Decisions for the team

1. ~~Are the three scenarios and their starting values acceptable as assumptions?~~ Accepted 18 Nov 2026
   (Kee Chee Pheng).
2. Stand-alone (proposed), or try to add it to the six rules' own alerts?
3. Choose the scale by mules caught in weeks 0–26 on months 0–4 (proposed)?
