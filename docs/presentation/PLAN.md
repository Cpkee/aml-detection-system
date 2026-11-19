# Slide plan: Early Detection of Money Mule Accounts

BT4012 Fraud Analytics, Group 09. Drafted 19 Nov 2026 (Kee Chee Pheng, with Claude); revised the same day for
technical depth (second pass, below). Replaces the structure of the old deck "BT4012 Group 9.pptx" (26 slides,
SharePoint). Words follow [`GLOSSARY.md`](../../GLOSSARY.md).

**Built deck:** a Claude Slides deck, **24 main + 12 backup slides**, speaker notes on every slide:
https://claude.ai/artifact/WnCujmAAgHgagdxoiS9V3Z (export to `.pptx` / PDF or send to Canva from its menu).
**The deck's speaker notes are the script**: this plan no longer repeats them. Due with the video: **20 Nov 2026,
23:59** (Canvas > Assignments > Project > Presentation).

**Contents**
1. How to use this plan
2. The one message and the storyline
3. Design rules
4. The recurring picture: life of a mule account
5. Presenters and timing
6. Slide by slide (24 main slides)
7. Backup slides
8. Chart data
9. Number ledger
10. What changes from the old deck
11. Open points for the team
12. Checks before recording

---

## 1. How to use this plan

1. **Read the deck** (link above) with this plan beside it. Each slide's footer names the report section it
   summarises ("Report §3.3"), so the talk doubles as a guide to the report.
2. **Settle the open points** in section 11 (title, two report numbers).
3. **Number check** (section 12): every number on every slide against the ledger (section 9).
4. **Export** to `.pptx` and PDF (or send to Canva). Check the speaker notes and the system diagram's arrows
   survived the export.
5. **Rehearse with a timer** (section 5), then record.

**Second pass, 19 Nov 2026 (why the deck grew from 17 to 24 main slides).** The talk has no Q&A and the professor
reviews it, so every method choice the report makes is now on a slide, and the talk follows the report's order:
- **New slides:** 6 the bank's rules (R1–R6 with thresholds and sources), 7 the training data (split by opening
  month, the weekly label, 4,449,169 rows), 11 training choices (folds, imbalance, tuning, seeds, calibration), 17 what
  drives the catches (permutation importance), 18 flagging at opening (Table 4.4E), 20 the rule-threshold check
  (Table 4.4D).
- **Promoted from backup:** 21 how a bank would use it (was B5).
- **Rebuilt:** 3 (two questions, each now answered on the slide; the empty review lists looked like placeholders),
  9 (Table 3.1: all eight input families), 10 (full system diagram with the model's settings), 12 (all 13 methods of
  Table 4.2, not 8), 15 (weekly alert budget added).
- **Added everywhere:** a "Report §" tag in each footer; backup B12 declares the use of generative AI, as the course
  asks.
- **Team edits kept:** the cover's NUS Computing logo and longer notes, and slide 5's notes, both edited in the deck
  on 19 Nov.

**First pass, 19 Nov 2026 (still true):** slide 5 says "realistic applications" (BAF is generated from a real bank's
applications, not copied); slide 12 says "**Top** boosted trees tie" (CatBoost is reliably behind: gain −0.049, 95%
−0.076 to −0.024); 0.085 is the pre-registered minimum detectable effect, not a noise band, and is not on any slide;
the section tracker in the footer replaces divider slides and the roadmap.

---

## 2. The one message and the storyline

**The one sentence every slide supports:**

> With the same number of alerts each week as the bank's rules, a model that reads each account's first weeks
> caught **2.4× as many mule accounts (120 vs 50 of 163)**. It was **not earlier**, and **not thanks to the
> application form**: it read the laundering burst more precisely.

**The arc is question → answer.** Slide 3 asks two questions and previews the answers; slide 24 answers each:

| Question (slide 3) | Answer (slide 24) |
|---|---|
| Does account-opening data help catch mule accounts? | Not at the bank's alert budget: the gain comes from transactions |
| With the same alerts, can we catch more, or sooner? | More: 2.4× (120 vs 50 of 163). Sooner: no (median 8 vs 9 days from start) |

**Six sections**, in the report's order: Why this matters → Why we simulate (data) → Method → Evaluation and
results → Limitations → Future work and conclusion.

---

## 3. Design rules

Clean and intuitive: **the slide shows, the speaker explains.**

| Rule | Detail |
|---|---|
| One idea per slide | The headline is that idea, written as a full sentence |
| Word budget | Storyline slides: at most **25 words** besides headline, labels and numbers. Technical slides (6, 7, 9, 10, 11, 12) may carry one table or diagram with the settings the report gives, since there is no Q&A; explanation still goes in the notes |
| One visual per slide | A chart, a diagram, a table or the timeline, never a wall of cards |
| Colours | **NUS Blue `#003D7C` = the model.** **Orange `#EF7C00` = the bank's rules** (text `#B35C00`). Greys for everything else. Never swap model and rules colours |
| Type | Inter. Headline 52 px on a 1920 × 1080 slide, body ≥ 22 px, chart labels ≥ 20 px |
| Footer | Section tracker **Why · Data · Method · Results · Limits · Conclusion** (current one bold), external sources, the report section ("Report §4.3, Table 4.3A"), page number |
| Logo | NUS Computing logo on the cover |
| Numbers | Counts as "120 of 163", shares as whole percentages ("43%"). Same number, same wording everywhere |
| Words | Use `GLOSSARY.md`: **mule account**, **the bank's rules**, **flag**, **caught**, **weekly alert budget**, **days from start**. Never "earlier" to mean "caught when the rules never are" |

---

## 4. The recurring picture: life of a mule account

```
 opened ── quiet weeks ──▶ ┃ laundering burst (~2 weeks) ┃ ──▶ flagged ──▶ closed
 day 0     (fakes: median   ┃ money in, forwarded within  ┃     (rules: median
            week 13)        ┃ hours: 53% inside 1 hour    ┃      9 days after start)
```

| Appears on | What it highlights |
|---|---|
| Slide 2 (problem) | The whole life: hides among normal accounts, moves money fast, flagged late |
| Slide 7 (training data) | The weekly label: a fake account is a mule from opening, a real customer from the start of laundering; weeks after closure are dropped |
| Slide 9 (inputs) | The weekly cut-off: the model sees only data up to the last day of week w |
| Slide 15 (timing) | The grey "started laundering" area: both sides flag once the burst starts |

---

## 5. Presenters and timing

At most 15 minutes; every member speaks (course guideline 1). Times are the deck's speaker notes at 130 words a
minute: **14:39 in all** (1,908 words). The team fills in names.

| Slot | Slides | Sections | Time |
|---|---|---|---|
| A: ________ | 1–6 | Why this matters; why we simulate; the bank's rules | 4:08 |
| B: ________ | 7–12 | Training data; method; model selection | 3:48 |
| C: ________ | 13–18 | The fair test and results | 3:28 |
| D: ________ | 19–24 | Robustness, use, limitations, future work, conclusion | 3:15 |

The cover stays up for its notes (about 40 s), well over the guideline's 8 seconds for reading the title. If a
presenter runs long, slides 17 (drivers), 18 (at opening) and 20 (thresholds) can each lose a sentence.

---

## 6. Slide by slide

Speaker notes: in the deck. Times as section 5.

| # | Headline | Visual | Report | Who · time |
|---|---|---|---|---|
| 1 | Early Detection of Money Mule Accounts | NUS Computing logo; question line; Group 09 and the four names | — | A · 0:41 |
| 2 | Mule accounts pass stolen money on within hours | Life-of-a-mule timeline with 0.3% · 53% within 1 hour · 90–95% of alerts false; three kinds of mule | §1.1–1.2 | A · 0:36 |
| 3 | Two questions, at the bank's own alert budget | Two 10-row review lists of the same length (illustration: rules 2 mules, model 4; precision 19% vs 43%); the two questions with their answers | §1.1 | A · 0:35 |
| 4 | No public dataset follows an account from application to transactions | BAF / SAML-D / real bank data boxes → our simulator | §2.1 | A · 0:34 |
| 5 | We simulate 18 months of UK banking around realistic applications | Five-step pipeline: 244,000 accounts → 732 mule accounts → 109M transactions → one burst → 93.4% of alerts false | §2.1–2.2 | A · 1:04 |
| 6 | The benchmark: six rules a bank would run each week | Table R1–R6 (C9); alert → 28-day pause → review 3–30 days → 80% of true alerts confirmed → closed | §2.2, App. B | A · 0:36 |
| 7 | One row per account per week: 4.45 million training rows | Split strip by opening month (C10); label strips over weeks 0–26 for a normal account, a fake account, a real-customer mule; 4,449,169 rows, 8,327 (0.19%) mule weeks | §2.2–2.3, §3.2 | B · 0:39 |
| 8 | Three findings from the training months shaped the model | Three findings → three design choices | §3.4 | B · 0:37 |
| 9 | 38 inputs per account-week, from data up to that week only | Cut-off strip; Table 3.1 (eight families, C11) | §3.1–3.2 | B · 0:33 |
| 10 | The system: two models feed one weekly ranked list | System diagram (C12); cards "Why two stages" (PR-AUC 1.00 train vs 0.40 validation; gap 0.74 → 0.18) and "Why LightGBM" | §3.3 | B · 0:42 |
| 11 | Every modelling choice was made on months 0–4 only | Fold grid over months 0–7 (C13); four steps; month-5 dry run 65 vs 16 of 78 | §3.3, §4.2 | B · 0:39 |
| 12 | Top boosted trees tie; how the inputs are fed matters more | 13 bars, Table 4.2 (C2), tie band shaded | §4.2 | B · 0:36 |
| 13 | A fair test: same accounts, same weeks, same number of flags | Four cards: 50,061 accounts, 163 mules · every week · top N · scored once | §4.1 | C · 0:33 |
| 14 | With the same alerts, the model caught 2.4× as many mule accounts | 163-dot grid (C4); 120 vs 50; precision 43% vs 19% | §4.3, Table 4.3A | C · 0:37 |
| 15 | More mules, about as fast: both catch once laundering starts | Catch curves with the "started" area (C1); 8 vs 9 days; 2 of 120 before the start; weekly budget bars | §4.3, Table 4.3B | C · 0:36 |
| 16 | The gain comes from transactions, not the application form | Paired bars with / without the application score (C5) | §4.4.2 | C · 0:34 |
| 17 | One input drives the catches: 1-hour forwarding | Permutation drops (C6); gain shares 51% / 13% / 7% | §3.4 | C · 0:32 |
| 18 | At opening: 3 months earlier, but 20 reviews per mule | Top N at opening (C7); 24 of 24 are fakes | §4.4.7, Table 4.4E | C · 0:33 |
| 19 | If one simulator guess is wrong, the model still leads | Lead with 95% interval per scenario, chance band 0.31–0.55 (C3) | §4.4.1 | D · 0:38 |
| 20 | The lead holds at every rule threshold we tried | Grouped bars, rules vs model, at 7 rule scales (C8) | §4.4.6, Table 4.4D | D · 0:30 |
| 21 | A bank would get a weekly ranked list, the same length as today | Four steps: score every week (≈6 s) · keep the top N · calibrated probability · investigators decide | §4.5 | D · 0:35 |
| 22 | Every result is a comparison inside a simulation | Four limits; 50+ false alarms per 1,000: model 6.1 vs rules 4.4 | §5.2 | D · 0:39 |
| 23 | Next: run it silently beside a real bank's rules | Three steps: shadow run · harder simulation · fix the age skew | §5.4 | D · 0:24 |
| 24 | Earlier? No. More mule accounts for the same alerts? Yes. | The two answers; "Thank you"; repository link | — | D · 0:27 |

---

## 7. Backup slides

Not presented (no Q&A); they stay in the exported deck as an appendix.

| # | Title | Content | Report |
|---|---|---|---|
| B1 | Model code reads two public tables; labels stay hidden | Public tables vs hidden truth; split train 0–4, calibrate 5, test 6–7 | §2.3 |
| B2 | Cleaning is fitted on the training months only | Missing codes → flags; real negatives kept; clip; categories frozen; log; 56 linear / 35 tree columns | §3.1 |
| B3 | 38 inputs in eight families; the application score holds half the gain | Split-gain share by family (51%, 22%, 13%, 8%, 3%, 2%, 1%, 1%) | §3.2 |
| B4 | The model catches more in every type, age band and opening month | Caught by type, age, opening month; false alarms per 1,000 by age | §4.3, §4.4.3 |
| B5 | Without labels, detectors catch 16 to 39 of 78; the model 63 | Month 5, 124 flags: model 63, bank-confirmed-only 54, rarity sum 39, rarity 16, Isolation Forest 16, rules 16 | §3.3, §4.4.4 |
| B6 | A stronger hand-written rule set closes only part of the gap | Month 5: rules 16, scorecard 34, model of record 65 of 78 | §5.2 |
| B7 | Even the model stops only a third of the money | Month 5: £310,207; stopped: rules 8%, scorecard 15%, model 33%; 64% gone by the first flag | §4.4.8 |
| B8 | After calibration, a 5% score means about 5% are mule weeks | Out-of-fold reliability table, 8 bands; raw 18.6% vs 0.24% observed, isotonic 0.24% vs 0.24% | §4.2 |
| B9 | Every result can be rebuilt, and the test months were read once | Seeded simulator; run records; shared model files; locked test; 233 automated tests | §5.3 |
| B10 | Every simulator number traces to a source or a tested assumption | Eight sources and what each sets | App. A |
| B11 | Over 78 weeks the gap holds: 138 vs 59 of 180 | Weeks 0–77; precision 19% vs 9% | §4.3 |
| B12 | Use of generative AI and external code | What Claude and Claude Code helped with; what the team did; libraries used | AI declaration |

---

## 8. Chart data

All values from committed files or the report's tables. Colours: model `#003D7C`, rules `#EF7C00`, other greys.

### C1 — Catch curve (slide 15)
Source: `outputs/modelling/results/v1_full/final_test/weekly_w26.csv` (columns `started`/`mules`, `catch_model`,
`catch_rules`, `budget`). "Caught so far" = share of the mule accounts at that week already flagged.

| Week since opening | Mules started laundering (%) | Model: mules caught so far (%) | Rules: mules caught so far (%) | Rules' alerts that week |
|---|---|---|---|---|
| 0 | 0 | 0.0 | 0.0 | 5 |
| 1 | 0 | 0.7 | 0.0 | 8 |
| 2 | 1 | 0.7 | 0.0 | 7 |
| 3 | 2 | 0.7 | 0.0 | 9 |
| 4 | 2 | 1.3 | 0.0 | 10 |
| 5 | 2 | 1.3 | 0.0 | 3 |
| 6 | 2 | 2.0 | 0.0 | 3 |
| 7 | 2 | 2.7 | 0.7 | 13 |
| 8 | 9 | 6.0 | 0.7 | 12 |
| 9 | 22 | 13.2 | 2.0 | 12 |
| 10 | 33 | 20.8 | 6.5 | 12 |
| 11 | 40 | 27.3 | 8.4 | 10 |
| 12 | 50 | 31.6 | 9.7 | 7 |
| 13 | 62 | 39.4 | 11.6 | 12 |
| 14 | 77 | 44.5 | 13.5 | 8 |
| 15 | 87 | 53.2 | 17.3 | 14 |
| 16 | 98 | 62.4 | 22.9 | 15 |
| 17 | 100 | 67.1 | 26.6 | 14 |
| 18 | 100 | 70.6 | 28.7 | 15 |
| 19 | 100 | 70.6 | 28.7 | 3 |
| 20 | 100 | 71.9 | 29.4 | 10 |
| 21 | 100 | 71.0 | 30.2 | 11 |
| 22 | 100 | 72.2 | 30.9 | 14 |
| 23 | 100 | 72.8 | 30.9 | 19 |
| 24 | 100 | 73.5 | 30.9 | 9 |
| 25 | 100 | 73.0 | 30.7 | 13 |
| 26 | 100 | 73.6 | 30.7 | 12 |

The last column is the small bar chart on the right of slide 15 (3–19 a week, 280 in weeks 0–26).

### C2 — Model selection (slide 12)
Source: report Table 4.2; `outputs/modelling/comparison/v1_full/folds.csv` and `interim_paired_tests_folds.csv`
(Holm over the rivals). Measure: share of mule accounts caught at the rules' weekly budget, mean over the 3 training
folds; "caught" summed over the folds (210 mule accounts).

| Method | Share caught | Caught of 210 |
|---|---|---|
| Activity only (no application score) | 0.458 | 184 |
| LightGBM, default settings | 0.456 | 179 |
| **Our model: two-stage LightGBM, 5 seeds** | **0.454** | **180** |
| XGBoost, tuned | 0.451 | 179 |
| Graph neural network (GraphSAGE) | 0.450 | 181 |
| Logistic + money-weighted interactions* | 0.417 | 165 |
| CatBoost, tuned | 0.405 | 163 |
| Half the budget to rules, half to model | 0.372 | 155 |
| LightGBM, raw application columns | 0.326 | 132 |
| Logistic, one input removed* | 0.303 | 125 |
| **The bank's rules** | **0.141** | 58 |
| Application score alone | 0.075 | 24 |
| Logistic, as pre-registered | 0.026 | 12 |

The first five are shaded as a tie. Paired gain vs ours (95% interval): XGBoost −0.003 (−0.017 to +0.010), GNN
−0.004 (−0.035 to +0.025); reliably behind: CatBoost −0.049 (−0.076 to −0.024), logistic + interactions −0.038
(−0.066 to −0.010). \* Post hoc. The pre-registered logistic regression ranks a one-hour forwarding share of 1 on a
tiny balance first; without that input it reaches 0.303.

### C3 — Robustness (slide 19)
Source: `outputs/modelling/robustness/summary.csv` and `summary_amendments.csv` (Variant II, patient launderers).
Lead = (model caught − rules caught) / mule accounts, weeks 0–26, test months. Chance band 0.31–0.55.

| Scenario | Lead | 95% interval | Model / rules caught | Verdict |
|---|---|---|---|---|
| **Main data (final test)** | **0.43** | 0.35–0.52 | 120 / 50 of 163 | headline |
| Main data rebuilt, another seed (chance yardstick) | 0.54 | 0.47–0.62 | 114 / 35 of 145 | yardstick |
| Fewer fake accounts (53%, not 73%) | 0.56 | 0.46–0.66 | 99 / 30 of 124 | holds |
| Older customers more often mules (Variant II) | 0.51 | 0.42–0.59 | 134 / 57 of 152 | holds |
| Young fake accounts | 0.50 | 0.42–0.58 | 128 / 47 of 163 | holds |
| Patient launderers (forward slowly) | 0.48 | 0.40–0.56 | 117 / 38 of 163 | holds |
| Repeated laundering bursts | 0.46 | 0.37–0.54 | 150 / 75 of 163 | holds |
| Fakes start early (15–45 days) | 0.39 | 0.31–0.48 | 118 / 54 of 163 | holds |
| Fakes start late (150–210 days) | 0.37 | 0.30–0.45 | 91 / 30 of 163 | holds |
| Larger transfers (£1,500, not £532) | 0.17 | 0.10–0.24 | 148 / 120 of 163 | **shrinks** |

### C4 — Dot grid (slide 14)
Source: `outputs/modelling/results/v1_full/final_test/launderers.csv`, summarised in `robustness.mcnemar`.

| Group | Mule accounts | Colour |
|---|---|---|
| Caught by both | 43 | blue dot, orange ring |
| Model only | 77 | blue |
| Rules only | 7 | orange |
| Neither | 36 | light grey |
| **Total** | **163** | |

### C5 — Where the gain comes from (slide 16)
Sources: `comparison/v1_full/folds.csv` (`ref` vs `A1_activity`, `A3_app_only`); month 5 and seed 43 from
`CHANGELOG.md` (29 Oct entry, `evaluation.compare`).

| Check | With application score | Activity only | Mule accounts |
|---|---|---|---|
| Training folds | 180 | 184 | 210 |
| Month 5 (calibration month) | 65 | 61 | 78 |
| Month 5 of a second dataset (seed 43) | 56 | 56 | 65 |

Separate callout: application score alone, 24 of 210 (training folds).

### C6 — What drives the catches (slide 17)
Source: report §3.4. Tuned model, 3 training folds, each input shuffled 3 times; drop in the early-catch score
(base about 0.45).

| Input | Drop |
|---|---|
| 1-hour forwarding share, last 4 weeks | −0.260 |
| Money in, last 4 weeks | −0.055 |
| Application score | −0.032 |
| Rows, last 4 weeks | −0.022 |
| 24-hour forwarding share, last 4 weeks | −0.013 |
| 1-hour forwarding share, this week | −0.008 |
| Largest payment in, this week | −0.007 |

Share of split gain (`frozen_tuned_avg5/importance.csv`): application score 51%, 1-hour share over 4 weeks 13%,
payers since opening 7%.

### C7 — Flagging at opening (slide 18)
Source: report §4.4.7, Table 4.4E. Month 5: 29,120 accounts ranked on their opening day by the application score;
97 launder at some point; one run, list sizes fixed in advance.

| Top N at opening | Future mules among them | By chance | Reviews per mule | Median days before laundering |
|---|---|---|---|---|
| 25 | 2 | 0.08 | 12.5 | 74 |
| 50 | 2 | 0.17 | 25 | 74 |
| 100 | 4 | 0.33 | 25 | 75 |
| 200 | 12 | 0.67 | 16.7 | 81.5 |
| 500 | 24 | 1.67 | 20.8 | 89 |

All 24 in the top 500 are fake accounts; 0 of 27 real-customer mules. The model at the rules' budget needs about
2 reviews per mule, after laundering starts.

### C8 — Rule threshold (slide 20)
Source: report §4.4.6, Table 4.4D. Month 5, 78 mule accounts, weeks 0–26; the model gets the same weekly alert
count as the rules at each scale. Approximate: data not rebuilt per scale, model not retrained, test months not read.

| Scale of R3–R6 | Rules' alerts | Rules caught | Model caught |
|---|---|---|---|
| ×1.0 | 1,432 | 40 | 78 |
| ×1.149 | 597 | 30 | 77 |
| ×1.32 | 246 | 24 | 73 |
| **×1.516 (used)** | **124** | **16** | **65** |
| ×1.741 | 69 | 10 | 47 |
| ×2.0 | 46 | 8 | 35 |
| ×2.639 | 33 | 3 | 26 |

### C9 — The bank's rules (slide 6)
Source: report §2.2 and Appendix B; `configs/sim.yaml` (rules). \* = starting threshold, scaled with the others.

| Rule | Fires when (checked every week) | Basis |
|---|---|---|
| R1 Large cash | One cash deposit of £10,000 or more | Money Laundering Regulations 2017 |
| R2 Repeated cash | Over £1,000 cash a day on 2+ days in 2 weeks, or £10,000 in 12 months | FCA proposed personal limits |
| R3 Many payers* | 8 or more different payers in one week | FFIEC red flag |
| R4 Pass-through* | 80%+ of the week's money in leaves the same week (money in over £2,000) | FFIEC red flag |
| R5 High-risk country* | £5,000+ sent to high-risk countries over 4 weeks | FFIEC red flag |
| R6 Sudden change* | Money in 10× the account's usual week, after 8 weeks of history | FFIEC and FinCEN red flags |

R3–R6 scaled together to ×1.516, so 93.4% of 3,614 alerts are false (target 90–95%). After an alert: 28-day pause,
review in 3–30 days, 80% of true alerts confirmed, confirmed accounts closed.

### C10 — Training data (slide 7)
Sources: `models/v1_full/frozen_tuned_avg5/manifest.json` (`rows`, `mule_rows`, `accounts`); `CLAUDE.md` (months
5–7).

| Opening months | Role | Accounts | Mule accounts |
|---|---|---|---|
| 0–4 | train | 164,819 | 455 |
| 5 | calibrate, dry run | 29,120 | 97 |
| 6–7 | test, read once | 50,061 | 180 (163 by week 26) |

Training rows: 4,449,169 account-weeks (weeks 0–26), of which 8,327 (0.19%) are mule weeks. Label `mule_by_day`: a
fake account from opening, a real customer from the start of laundering; account-weeks after the bank closes an
account are dropped.

### C11 — The 38 inputs (slide 9)
Source: report Table 3.1; `src/features/weekly.py`, `candidates.ADOPTED`.

| Family | n | Inputs (this week unless stated) |
|---|---|---|
| Application score | 1 | The 29 application fields as one number (stage 1) |
| Volume | 8 | rows; payments in and out; money in and out; largest payment in and out; card purchases |
| Payers and payees | 5 | distinct payers and payees this week and since opening; share of new payers |
| Flow and speed | 4 | share forwarded within 1 h and 24 h; pass-through (out ÷ in); median minutes from in to out |
| Since opening | 7 | money in, money out, rows; cash, abroad, high-risk and internal shares |
| Own past and peers | 4 | this week vs the account's own past (3); money in vs same-age, same-income peers |
| Last 4 weeks | 8 | rows, payments in, money in and out, payers, 1 h and 24 h shares, pass-through |
| Clock | 1 | weeks since opening |

### C12 — System diagram (slide 10)
Source: `models/v1_full/frozen_tuned_avg5/manifest.json`.

```
Application (29 BAF fields) → Clean (missing flags, log, one-hot, standardise: 56 columns)
  → STAGE 1 logistic regression (class_weight balanced; label mule by week 26; 5-fold out-of-fold) → 1 application score ┐
Transactions (≈109M rows, DuckDB) → Weekly feature store (rows up to the last day of week w) → 37 activity inputs ─────┤
  → STAGE 2 LightGBM (38 inputs; class_weight balanced; 500 trees; 15 leaves; ≥2,000 rows a leaf;                      ┘
    learning rate 0.033; colsample 0.90; subsample 0.92; mean of seeds 1–5)
  → Calibrate (isotonic, month 5) → Weekly list (flag the top N; N = the rules' alerts that week)
```

### C13 — Training choices (slide 11)
Source: report §3.3 and §4.2; `CLAUDE.md` (tuning, stability, calibration).

| Fold | Train (opening months) | Validate |
|---|---|---|
| 1 | 0–1 | 2 |
| 2 | 0–2 | 3 |
| 3 | 0–3 | 4 |
| Final model | 0–4 | calibrate on 5; test on 6–7, once |

Imbalance: class weights (0.19% mule weeks); 1:20 undersampling tested (same earliness, weaker ranking); no SMOTE
(synthetic account-weeks break the time order). Tuning: random search, 40 settings of 8 hyperparameters on the 3
folds. Stability: seed-to-seed spread above the limit set in advance (0.005), so the final score is the mean of 5
seeds, trained once and never retrained. Calibration: isotonic on month 5, Brier score 0.074 → 0.0018, order kept so
no catch changes. Dry run on month 5 before the test: model 65 of 78, rules 16; precision 0.52 vs 0.13.

---

## 9. Number ledger

Every number on a slide or in the notes. Check each slide against this table after any export or edit (section 12).

| Number | Meaning | Source |
|---|---|---|
| up to 0.3% (1 in 330) | share of accounts that are mule accounts | BioCatch 2022, `configs/sim.yaml` `launderer_share` |
| 53% within 1 hour | money leaving a mule account within an hour (28% in 15 min + 25% in 15–60 min) | RUSI 2025, `sim.yaml` `forward_delay_shares` |
| 90–95% | practitioners' estimate of false rule alerts | Oztas et al. 2024, `sim.yaml` `false_alarm_target` |
| £532 | average transfer out of a mule account | RUSI 2025, `sim.yaml` `out_transfer_mean` |
| 244,000 · 109M · 732 | accounts, transactions, mule accounts in the main data | `CLAUDE.md` (v1_full result), `data/v1_full/data_card.md` |
| 73% fake | share of mule accounts that are fake | `sim.yaml` `in_window_mix` |
| 93.4% of 3,614 · 32% · 9 days · ×1.516 | rules' false-alarm share and alerts, share of mule accounts alerted, median days from start, rule scale | `CLAUDE.md` (v1_full result) |
| R1–R6 thresholds | see C9 | report §2.2, Appendix B |
| 164,819 / 455 · 29,120 / 97 · 50,061 / 180 | accounts / mule accounts by opening months 0–4, 5, 6–7 | C10 |
| 4,449,169 · 8,327 (0.19%) | training account-weeks; mule weeks | `frozen_tuned_avg5/manifest.json` (the EDA check's 4,450,113 counts account-weeks before closed weeks are dropped) |
| AUC 0.60–0.69 · 0.70–0.86 · 0.95 | EDA: fakes at opening; activity once a burst starts; best single feature, first laundering week (`out_1h_share_wk` 0.954) | `outputs/modelling/eda/report.md`, `outputs/modelling/features/report.md` |
| 25 of 28 | weekly features that separate a first laundering week | `outputs/modelling/features/report.md` |
| 20× · 1 of 163 | mules pay mules; links existing before both start | `CLAUDE.md` homophily finding |
| 38 inputs · 19.0M account-weeks | model inputs; feature store size | `CLAUDE.md` |
| train 1.00 vs validation 0.40 · 0.74 → 0.18 | one tree on raw application fields; train–validation gap before and after the out-of-fold score | `CLAUDE.md` Phase 4 baselines, tuning step 1 |
| 500 · 15 · 2,000 · 0.033 · 5 seeds | LightGBM settings of the model of record | `frozen_tuned_avg5/manifest.json` |
| 40 settings × 8 · Brier 0.074 → 0.0018 | tuning search; calibration | report §3.3, §4.2 |
| 65 vs 16 of 78 · 0.52 vs 0.13 | month-5 dry run, model of record vs rules (124 vs 119 flags) | `results/v1_full/month5_dryrun_frozen_tuned_avg5/summary_w26.csv` |
| 0.458 … 0.026 | model selection (C2) | report Table 4.2 |
| 50,061 · 163 · about 10 a week · 280 | test accounts, mule accounts by week 26, rules' weekly alerts, alerts over weeks 0–26 | `final_test/summary_w26.csv`, `weekly_w26.csv` |
| 120 vs 50 · 74% vs 31% | caught, recall | `final_test/summary_w26.csv` |
| 43% vs 19% · 160 vs 214 | precision (42.9% vs 18.9%); false alarms | `final_test/summary_w26.csv` |
| 2.4× | 120 / 50 | arithmetic |
| 43 / 77 / 7 / 36 · p ≈ 5×10⁻¹⁶ | head to head; McNemar exact p | `closing/PLAN.md` item 1 |
| 8 vs 9 days · 2 of 120 | median days from start; flags before start | `final_test/summary_w26.csv` |
| 180 vs 184 · 65 vs 61 · 56 vs 56 · 24 | onboarding value | C5 |
| −0.260 … −0.007 · 51% / 13% / 7% | permutation drops; split-gain shares | C6 |
| 2 … 24 of top 500 · 20 reviews per mule · 74–89 days | flagging at opening | C7 |
| 1,432 … 33 alerts | rule-threshold check | C8 |
| about 6 s for 786,240 account-weeks | weekly scoring time, month 5 (median 5.6 s, Apple M5 Pro) | `CLAUDE.md` closing item 3 |
| 0.43 (0.35–0.52) · 0.31–0.55 · 7 hold, 1 shrinks | robustness | C3 |
| 16 · 11 vs 4 | real-customer mules in the test; caught by model vs rules | `final_test/summary_w26.csv` |
| 6.1 vs 4.4 · 1.9 vs 4.2 | false alarms per 1,000 normal accounts, 50+ and under 30, model vs rules | `final_test/by_age_w26.csv` |
| 54 vs 63 of 78 | month 5: model trained on bank-confirmed cases only vs the same recipe on true labels | `outputs/modelling/outlier/v1_full/report.md` |
| £310,207 · 33% vs 8% · 64% | month 5: money paid out by week 26; share stopped; share gone for the model's catches | `closing/PLAN.md` item 7 |
| 138 vs 59 of 180 | weeks 0–77 | `final_test/summary_w77.csv` |

**Two numbers that look alike:** "63 of 78" is the Mac-retrained recipe used in the bank-label check (and the older
model `frozen_tuned`); "65 of 78" is the model of record. Use 65 everywhere except the bank-label comparison
(54 vs 63) and the label-free backup (B5), which compare like with like.

---

## 10. What changes from the old deck

**Structure**
- [x] Title: "Catching Mule Accounts Earlier" → "Early Detection of Money Mule Accounts" (cover, 19 Nov; see
  section 11 for the deck's file name)
- [x] Five section-divider slides removed; section tracker in every footer
- [x] Project-flow slide with 11 numbers removed; slide 3 previews the answers instead
- [x] New: the data gap (4), the bank's rules (6), the training data (7), training choices (11), drivers (17), at
  opening (18), rule thresholds (20), AI declaration (B12)
- [x] "Analytical Insights" moved before the model (8); "Experimental Design" opens the results (13)

**Numbers that were wrong or out of date in the old deck**
- [x] "63 of 78" → 65 (model of record), except the bank-label "54 vs 63"
- [x] Robustness: "7 scenarios: 6 hold" / "6 scenarios: 5 hold" → **8 changed scenarios: 7 hold, 1 shrinks**
- [x] Variant II and the graph neural network have now run
- [x] "Earlier" no longer means "caught when the rules never are"; speed is "days from start" only
- [x] "Real BAF applications" → "realistic applications"

**Before submitting:** the branches that held slide numbers (`comparison-boosted`, PR #58) are merged; check that
`item5-patient` (patient launderers) is merged or cited.

---

## 11. Open points for the team

1. **Deck name vs cover title.** The cover says "Early Detection of Money Mule Accounts"; the deck file is still
   "Catching More Mule Accounts with the Same Alerts"; the report is titled "Anti-Money Laundering Mule Account
   Detection System". Pick one name for the deck, the video and the report.
2. **CatBoost in the report.** Report §3.3 / §4.2 says CatBoost is within the 0.085 margin; the paired test puts it
   reliably behind (−0.049, −0.076 to −0.024). The deck follows the paired test; the report should too (0.085 is the
   minimum detectable effect, not a noise band).
3. **Test count.** The report says 219 automated tests; backup B9 says 233 (233 passed, 3 skipped, 19 Nov). Use one.
4. **The old deck's robustness slide** shows model results at 0.1% and 1% prevalence; the report says those runs were
   not done. Leave them out unless they ran.

---

## 12. Checks before recording

- [ ] Every number on every slide matches section 9 (one person reads the slide, another reads the ledger)
- [ ] Model is blue and rules are orange on every slide and chart
- [ ] Each footer's "Report §" matches the final report's numbering (re-check if the report's sections move)
- [ ] Speaker notes present on all 24 main slides after export
- [ ] The system diagram's arrows (slide 10) survive the export
- [ ] Glossary words used throughout (no "launderer", "detected earlier")
- [ ] Each presenter rehearses with a timer: A 4:08, B 3:48, C 3:28, D 3:15 (total under 15:00)
- [ ] Title and names readable for at least 8 seconds at the start of the video
- [ ] Exported `.pptx` and PDF open correctly (fonts, charts, notes)
