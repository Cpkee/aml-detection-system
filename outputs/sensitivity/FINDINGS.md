# Sensitivity runs: which assumptions move the bank's rules (9 Oct 2026, after the R6 fix)

42 runs on top of the main full-size dataset (`data/v1_full`: 244,000 accounts, seed 42). Each run changes **one**
setting to a `test` value from `configs/sim.yaml`, with the bank's rules **frozen** at the main run's scale (1.516).
All 42 runs pass the 10 data checks. One row per run is in `summary.csv`; each run's data card and manifest are in
`runs/<name>/` (the large files were deleted and can be rebuilt exactly with `python -m sim.sensitivity --run`).

These results replace the first batch (7–8 Oct), which was run before R6 was fixed to wait 8 weeks before judging
a new account. The pattern of what matters is the same; the levels are lower because the rules no longer raise
thousands of false alarms on new accounts' first salary.

**Chance yardstick.** The main run repeated with seeds 43 and 44 gives false alarms 93.1–93.4% and launderers
caught 32–33%. Differences inside that range are noise.

Main run: 93.4% false alarms (inside the 90–95% practitioners report), 32% of launderers caught, median 9 days
after start, ~33 alerts a week.

## Large effects

| Change | False alarms | Caught | Why |
|---|---|---|---|
| Launderers repeat a burst every 30 days until closed (`bursts_per_launderer`) | 84.1% | **76%** | More bursts, more chances; median catch 60 days after the first burst |
| Laundering transfers £1,500 instead of RUSI's £532 (`out_transfer_mean`) | 85.5% | **75%** | Bigger money in a week trips R4 (pass-through over £3,032) |
| Prevalence 1% (`launderer_share`, 244k) | **81.3%** | 31% | More launderers among the same false alarms; below the published 90–95% |
| Prevalence 0.1% (`launderer_share`, 732k) | **97.8%** | 30% | Fewer launderers, same false alarms |
| Cash deposits twice as large (£300) or twice as often (4/month) | **98.4%** | 34–35% | R2 fires on normal customers: ~13,000 R2 alerts vs 804; budget ~140–150/week |
| Group collections of 15–22 payers / 4–8 payers (`group_collection`) | 95.7% / 91.5% | 33% / 32% | R3 alerts 2,935 / 5 vs 810: R3's false alarms come from legitimate collections |
| Observation window 12 months (`observe_days` 365) | 89.5% | 35% | Shorter window, fewer normal weeks to raise false alarms |

## Small effects

Group collections twice as common (94.6%), legitimate £10k+ cash deposits twice as common (94.5%), HMRC instead of
ONS income (94.3%), a 24-month window (94.3%, 36% caught), fewer fake accounts in the launderer mix (53% fake: 29%
caught, the only run that lowers the catch rate noticeably).

## No effect (inside or within about 1 point of the seed range)

Fake accounts' ages (`young_weighted`) and start times, cheque size, large-cash size, bonuses, cash withdrawals,
transfers in from friends, internal transfers, abroad share of laundering (1× or 6×), investigator confirm share
(60% / 100%), group-collection payment size.

## What this means for the report

1. **The share of launderers the rules catch depends on how launderers behave**, not on normal banking: only
   transfer size and repeated use moved it (32% → ~75%). Both are weakly sourced (RUSI £532 average; one burst
   is an assumption), so the report should give the rules' catch rate as a range, not a single number.
2. **The false-alarm share depends mostly on prevalence** (the professor's comment 1): 81.3% at 1%, 93.4% at
   0.3%, 97.8% at 0.1%; precision falls from about 19% to 7% to 2%. It also depends on our assumptions about
   normal cash use (R2) and group collections (R3).
3. **The model must be re-checked on the high-impact scenarios** (transfer size, repeated bursts, both
   prevalences, doubled cash, fewer fakes): these runs measure the benchmark only.
