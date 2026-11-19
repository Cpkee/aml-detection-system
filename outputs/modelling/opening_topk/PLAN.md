# Top N at opening: what account-opening data buys (plan, drafted 19 Nov 2026)

**Status: plan accepted 19 Nov 2026 (Kee Chee Pheng); committed before the run.** Report-appendix work only. It changes nothing in
the simulator, the rules, the data, the feature store, the frozen feature list or the model of record, fits no
model, and never reads test months 6–7. The headline result (final test, 2 Nov 2026) stays as it is.

## Why

Our question is whether account-opening data helps catch mules **earlier**. The main comparison cannot answer the
"earlier" part:

- At the rules' budget the model had only **24 flags** to spend in weeks 0–7 of month 5, the weeks before any fake
  account starts laundering (fakes start in weeks 8–17). None of the 24 was a future mule.
- That zero proves little. An application-only model hits a mule with roughly 5% of its flags (early baseline:
  35 of 662 on the test cohort), so 24 flags should catch about 1, and catching none happens by luck about 3 times
  in 10.

So the harness cannot tell "no early signal" from "a modest early signal". This appendix measures the early signal
directly, with enough flags to see it.

## The question

If the bank reviewed the N most suspicious applications on the day the accounts open, how many of them would later
launder, and how many reviews does each early catch cost?

## What is measured

`src/evaluation/opening_topk.py`. Month 5 (29,120 accounts, 97 of them launder at some point). Accounts are ranked
by the application score already saved inside the model of record (`frozen_tuned_avg5/app_logreg.json`, a logistic
model fitted on months 0–4 only, so month 5 is unseen by it). **No model is fitted.**

For N = 25, 50, 100, 200, 500 (fixed here; 500 is 1.7% of the cohort):

| Column | Meaning |
|---|---|
| launderers | Of the top N, accounts that launder at any time in their 18 months, by type |
| precision, reviews per launderer | launderers / N, and N / launderers |
| chance | Launderers expected in a random pick of N (0.08 at N = 25, 1.67 at N = 500) |
| lift, p_chance | launderers / chance, and the chance of at least this many by luck |
| share caught | launderers / 97 |
| head start | Median days from opening to the launderer's laundering start |

Launderers are counted by the fixed final label, because the flag is raised on the opening day, before anyone
has started.

## One run

```bash
PYTHONPATH=src python -m evaluation.opening_topk --out data/v1_full
```

-> `outputs/modelling/opening_topk/v1_full/table.csv` + `report.md`. Run once, reported whatever it shows.

## How we will read it (decided now)

The **N = 500 row is the test**; the other rows describe the shape and are not tested separately.

| Result at N = 500 | What we say |
|---|---|
| Not above chance (p_chance > 0.05) | Account-opening data carries no usable early signal here. The hypothesis' "earlier" half is not supported |
| Above chance | Account-opening data does flag some mules early, by the head start shown, at a cost of so many reviews per mule. We report that cost beside the activity flags' cost (the model of record: about 2 reviews per mule, 65 of 124 on month 5) and say which types it finds |

Either way the report states a number in place of "not supported at the bank's budget".

## Limits, stated in advance

- **Partly built in.** Fake mules are drawn from BAF's fraud-flagged applications, and only about one in five of
  those becomes a mule. So the score is recognising application fraud, the link to laundering is our assumption,
  and even a perfect fraud detector would be wrong about laundering most of the time.
- **Real customers.** Customers who turn mule later opened honestly; we expect almost none in the top N. The
  by-type columns show it.
- **Not a policy test.** A flag here closes no account and changes no later activity. It says what a review at
  opening would find, not what the bank would then do.
- **Not the same budget.** The top 500 is about 4 times the rules' whole 27-week budget on this cohort (124). This
  is a trade-off table, not a like-for-like comparison with the headline.
- **Month 5 has been used before** (dry runs, calibration, the outlier look, the scorecard, the budget curve). One
  more use, for settings fixed here.
- **Small numbers.** 97 launderers; a difference of a few is not a difference.

## Decisions (accepted as proposed, 19 Nov 2026, Kee Chee Pheng)

1. Are N = 25, 50, 100, 200, 500 the right sizes?
2. Is the saved application score of the model of record the right ranking (proposed), not a new model?
3. Count launderers by the final label (proposed)?
