# Sensitivity runs: which assumptions move the bank's rules (8 Oct 2026)

42 runs on top of the main full-size dataset (`data/v1_full`: 244,000 accounts, seed 42). Each run changes **one**
setting to a `test` value from `configs/sim.yaml`, with the bank's rules **frozen** at the main run's scale (1.741).
All 42 runs pass the 10 data checks. One row per run is in `summary.csv`; each run's data card and manifest are in
`runs/<name>/` (the large files were deleted and can be rebuilt exactly with `python -m sim.sensitivity --run`).

**Chance yardstick.** The main run repeated with seeds 43 and 44 gives false alarms 96.7–96.9% and launderers caught
24–26%. Differences inside that range are noise.

Main run: 96.9% false alarms, 25% of launderers caught, median 9 days after start, ~54 alerts a week.

## Large effects

| Change | False alarms | Caught | Why |
|---|---|---|---|
| Laundering transfers £1,500 instead of RUSI's £532 (`out_transfer_mean`) | 91.4% | **71%** | Bigger money in a week trips R4 (pass-through over £3,482) |
| Launderers repeat a burst every 30 days until closed (`bursts_per_launderer`) | 91.0% | **67%** | More bursts, more chances; median catch 96 days after the first burst |
| Prevalence 1% (`launderer_share`, 244k) | **90.8%** | 24% | More launderers among the same false alarms; inside the published 90–95% band |
| Prevalence 0.1% (`launderer_share`, 732k) | **99.0%** | 22% | Fewer launderers, same false alarms |
| Cash deposits twice as large (£300) or twice as often (4/month) | **98.9%** | 27–28% | R2 fires on normal customers: ~13,000 R2 alerts vs 806; budget ~165/week |
| Group collections of 15–22 payers (`group_collection`) | 97.6% | 25% | R3 alerts 2,178 vs 329; with 4–8 payers R3 almost never fires (1 alert) |
| Transfers in from friends 0.5 / 2 per month | 96.0% / 97.9% | 25% | Changes how often R6 ("sudden change") fires on normal accounts |

## Small or no effect (inside or near the seed range)

Launderer mix (`in_window_mix`; caught 22–24%), fake accounts' ages (`young_weighted`), fake accounts' start
(15–45 or 150–210 days), cheque size, large-cash size and rate, abroad share of laundering (1× or 6×), bonuses,
cash withdrawals, money-in source (HMRC), investigator confirm share (60% / 100%), group-collection size of
payments and rate, observation window (365 / 730 days: 96.1% / 96.7%, caught 27% / 29%).

## What this means for the report

1. **The share of launderers the rules catch depends on how launderers behave**, not on normal banking: only
   transfer size and repeated use moved it (25% → ~70%). Both are weakly sourced (RUSI £532 average; one burst
   is an assumption), so the report should give the rules' catch rate as a range, not a single number.
2. **The false-alarm share depends mostly on prevalence and normal cash use.** At 1% prevalence the frozen rules
   land at 90.8%, inside the practitioners' 90–95%; at 0.3% they cannot get below ~97%. The "target unreachable"
   finding is therefore partly a prevalence effect.
3. **R2 and R3 false alarms are driven by our own assumptions** (cash deposit size/frequency; group-collection
   size). R3's alerts come almost entirely from legitimate group collections.
4. These runs measure the **benchmark only**. Whether our model still beats the rules should be re-checked on the
   high-impact scenarios (transfer size, repeated bursts, both prevalences, doubled cash).
