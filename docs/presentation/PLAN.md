# Slide plan: Early Detection of Money Mule Accounts

BT4012 Fraud Analytics, Group 09. Drafted 19 Nov 2026 (Kee Chee Pheng, with Claude); revised the same day for
technical depth (second pass), to fold the backup slides into the talk (third pass) and to state hypotheses
before the results (fourth pass, below). Replaces the structure
of the old deck "BT4012 Group 9.pptx" (26 slides, SharePoint). Words follow [`GLOSSARY.md`](../../GLOSSARY.md).

**Built deck:** a Claude Slides deck, **28 main slides + 2 appendix slides** (References, AI declaration), speaker
notes on every slide: https://claude.ai/artifact/WnCujmAAgHgagdxoiS9V3Z. **The deck's speaker notes are the
script**: this plan no longer repeats them. In the deck's editor, "Show speaker notes" shows and edits them and
"Present with speaker notes" presents with them; Download > PowerPoint (.pptx) with "Include speaker notes" ticked,
or PDF, exports them. Canva has no direct send: to use Canva, import the `.pptx` once, after the last edit here (one
way: edits made in Canva do not come back). Due with the video: **20 Nov 2026, 23:59** (Canvas > Assignments >
Project > Presentation).

**Contents**
1. How to use this plan
2. The one message and the storyline
3. Design rules
4. The recurring picture: life of a mule account
5. Presenters and timing
6. Slide by slide (28 main slides)
7. Appendix slides and the removed backups
8. Chart data
9. Number ledger
10. What changes from the old deck
11. Open points for the team
12. Checks before recording

---

## 1. How to use this plan

1. **Read the deck** (link above) with this plan beside it. Each slide's footer names the report section it
   summarises ("Report §3.3"), so the talk doubles as a guide to the report.
2. **Settle the open points** in section 11 (talk length, report title, report numbers and references).
3. **Number check** (section 12): every number on every slide against the ledger (section 9).
4. **Export** to `.pptx` (speaker notes included) and PDF; import into Canva only after the last edit here. Check
   the speaker notes, the NUS Computing logo and the system diagram's arrows survived the export.
5. **Rehearse with a timer** (section 5), then record.

**Fourth pass, 19 Nov 2026 (slide 3 no longer gives the answers away).** Slide 3 states the report's research
question and three hypotheses (H1 more mule accounts, H2 earlier, H3 opening data helps) beside two blank review
lists of the same length; the answers wait for the results, and slide 28 gives a verdict on each (supported / not
supported / not at this budget). Slides 11 and 14 keep their month-5 numbers (65 vs 16, 63 vs 16): they are checks,
not the test. Team edits kept: the closing slide no longer lists the names; slide 13 was rebuilt in a separate
session ("No method beats ours", notes 160 words). The talk is now **17:21** (section 5).

**Third pass, 19 Nov 2026 (why the deck grew from 24 to 28 main slides and lost its backups).** With no Q&A a
backup slide is never shown, so what matters moved into the talk and the rest was deleted:
- **Cover and closing slide share one frame:** the off-white background of every other slide, the NUS Computing logo
  top left, an orange bar along the bottom, a large navy title and the four names. The closing slide keeps the two
  answers, "Thank you" and the repository link.
- **New main slides from backups:** 12 calibration (was B8), 14 label-free detectors (B5), 17 who is caught (B4), 24
  stronger rules and money stopped (B6 + B7).
- **Folded into existing slides:** the reproducibility points (B9) as a strip on slide 15; the 78-week result (B11)
  as one line on slide 16.
- **Deleted:** B1–B3 (their point is already on slides 7, 9, 10 and 20) and B7, B9, B11 once their content moved.
- **Appendix after "Thank you", not presented:** References (was B10, now the full source list) and the AI
  declaration (B12). Section 7 maps every old backup to where it went.
- **Deck renamed** "Early Detection of Money Mule Accounts", as on the cover.
- **Talk length:** 2,152 words, about **16:33** at 130 words a minute, over the course's 15-minute maximum; the team
  accepted up to about 16:30 (section 11).

**Second pass, 19 Nov 2026 (why the deck grew from 17 to 24 main slides; slide numbers as in the 24-slide deck).**
The talk has no Q&A and the professor reviews it, so every method choice the report makes is now on a slide, and the
talk follows the report's order:
- **New slides:** 6 the bank's rules (R1–R6 with thresholds and sources), 7 the training data (split by opening
  month, the weekly label, 4,449,169 rows), 11 training choices (folds, imbalance, tuning, seeds, calibration), 17 what
  drives the catches (permutation importance), 18 flagging at opening (Table 4.4E), 20 the rule-threshold check
  (Table 4.4D).
- **Promoted from backup:** 21 how a bank would use it (a backup in the first pass).
- **Rebuilt:** 3 (two questions, each now answered on the slide; the empty review lists looked like placeholders),
  9 (Table 3.1: all eight input families), 10 (full system diagram with the model's settings), 12 (all 13 methods of
  Table 4.2, not 8), 15 (weekly alert budget added).
- **Added everywhere:** a "Report §" tag in each footer; backup B12 declares the use of generative AI, as the course
  asks.
- **Team edits kept:** the cover's NUS Computing logo and longer notes, and slide 5's notes, both edited in the deck
  on 19 Nov.

**First pass, 19 Nov 2026 (still true):** slide 5 says "realistic applications" (BAF is generated from a real bank's
applications, not copied); CatBoost is shown as reliably behind (gain −0.049, 95% −0.076 to −0.024; slide 13 now
reads "No method beats ours"); 0.085 is the pre-registered minimum detectable effect, not a noise band, and is not on any slide;
the section tracker in the footer replaces divider slides and the roadmap.

---

## 2. The one message and the storyline

**The one sentence every slide supports:**

> With the same number of alerts each week as the bank's rules, a model that reads each account's first weeks
> caught **2.4× as many mule accounts (120 vs 50 of 163)**. It was **not earlier**, and **not thanks to the
> application form**: it read the laundering burst more precisely.

**The arc is hypothesis → verdict.** Slide 3 states the report's research question ("At the same weekly alert
budget as the bank's rules, can a model using account-opening data and early activity catch mule accounts
earlier?") and three hypotheses, without the answers; the results section tests them; slide 28 gives a verdict on
each:

| Hypothesis (slide 3) | Verdict (slide 28) |
|---|---|
| H1 More mule accounts: the model catches more than the rules with the same alerts | Supported: 120 vs 50 of 163 (2.4×) |
| H2 Earlier: it catches them sooner, ideally before laundering starts | Not supported: 2 of 120 caught before the start; median 8 vs 9 days from start |
| H3 Opening data helps: the application adds to what activity alone catches | Not at this budget: with vs without it 180 vs 184 of 210 (folds), 65 vs 61 of 78 (month 5) |

**Six sections**, in the report's order: Why this matters → Why we simulate (data) → Method → Evaluation and
results → Limitations → Future work and conclusion.

---

## 3. Design rules

Clean and intuitive: **the slide shows, the speaker explains.**

| Rule | Detail |
|---|---|
| One idea per slide | The headline is that idea, written as a full sentence |
| Word budget | Storyline slides: at most **25 words** besides headline, labels and numbers. Technical slides (6, 7, 9–13, 17) may carry one table or diagram with the settings the report gives, since there is no Q&A; explanation still goes in the notes |
| One visual per slide | A chart, a diagram, a table or the timeline, never a wall of cards |
| Colours | **NUS Blue `#003D7C` = the model.** **Orange `#EF7C00` = the bank's rules** (text `#B35C00`). Greys for everything else. Never swap model and rules colours |
| Type | Inter. Headline 52 px on a 1920 × 1080 slide, body ≥ 22 px, chart labels ≥ 20 px |
| Footer | Section tracker **Why · Data · Method · Results · Limits · Conclusion** (current one bold), external sources, the report section ("Report §4.3, Table 4.3A"), page number. None on the cover and the closing slide |
| Cover and closing slide | One frame: off-white background (as every slide), NUS Computing logo top left, orange bottom bar, large navy title; the four names on the cover |
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
| Slide 18 (timing) | The grey "started laundering" area: both sides flag once the burst starts |

---

## 5. Presenters and timing

At most 15 minutes; every member speaks (course guideline 1). Times are the deck's speaker notes at 130 words a
minute: **17:21 in all** (2,255 words), **about 2:20 over the guideline** and about 50 s over the ~16:30 the team
accepted on 19 Nov when it moved the backup slides' plots into the talk. Most of the rise since then is slide 13's
rebuilt notes (78 → 160 words, +0:38). Section 11 says what to cut. The team fills in names.

| Slot | Slides | Sections | Time |
|---|---|---|---|
| A: ________ | 1–6 | Why this matters; the hypotheses; why we simulate; the bank's rules | 4:11 |
| B: ________ | 7–13 | Training data; method; calibration; model selection | 4:50 |
| C: ________ | 14–20 | Label-free detectors; the fair test and results; what drives the catches | 4:01 |
| D: ________ | 21–28 | At opening; robustness; stronger rules; use in a bank; limitations; future work; verdicts | 4:18 |

The cover stays up for its notes (about 40 s), well over the guideline's 8 seconds for reading the title. If a
presenter runs long, slides 20 (drivers), 21 (at opening) and 23 (thresholds) can each lose a sentence. To get under
15:00: take slide 13's notes back to about 80 words (−0:38) and drop the four slides that came from the backups
(12, 14, 17, 24; −1:36): 15:07. Part B (4:50) is the longest slot.

---

## 6. Slide by slide

Speaker notes: in the deck. Times as section 5.

| # | Headline | Visual | Report | Who · time |
|---|---|---|---|---|
| 1 | Early Detection of Money Mule Accounts | Cover frame: NUS Computing logo; question line; Group 09 and the four names | — | A · 0:42 |
| 2 | Mule accounts pass stolen money on within hours | Life-of-a-mule timeline with 0.3% · 53% within 1 hour · 90–95% of alerts false; three kinds of mule | §1.1–1.2 | A · 0:36 |
| 3 | Three hypotheses, tested at the bank's own alert budget | Two blank 10-row review lists of the same length ("Which list holds more mule accounts?"); the research question; H1 more mule accounts, H2 earlier, H3 opening data helps; no answers | §1.1 | A · 0:39 |
| 4 | No public dataset follows an account from application to transactions | BAF / SAML-D / real bank data boxes → our simulator | §2.1 | A · 0:34 |
| 5 | We simulate 18 months of UK banking around realistic applications | Five-step pipeline: 244,000 accounts → 732 mule accounts → 109M transactions → one burst → 93.4% of alerts false | §2.1–2.2 | A · 1:04 |
| 6 | The benchmark: six rules a bank would run each week | Table R1–R6 (C9); alert → 28-day pause → review 3–30 days → 80% of true alerts confirmed → closed | §2.2, App. B | A · 0:36 |
| 7 | One row per account per week: 4.45 million training rows | Split strip by opening month (C10); label strips over weeks 0–26 for a normal account, a fake account, a real-customer mule; 4,449,169 rows, 8,327 (0.19%) mule weeks | §2.2–2.3, §3.2 | B · 0:40 |
| 8 | Three findings from the training months shaped the model | Three findings → three design choices | §3.4 | B · 0:38 |
| 9 | 38 inputs per account-week, from data up to that week only | Cut-off strip; Table 3.1 (eight families, C11) | §3.1–3.2 | B · 0:34 |
| 10 | The system: two models feed one weekly ranked list | System diagram (C12); cards "Why two stages" (PR-AUC 1.00 train vs 0.40 validation; gap 0.74 → 0.18) and "Why LightGBM" | §3.3 | B · 0:42 |
| 11 | Every modelling choice was made on months 0–4 only | Fold grid over months 0–7 (C13); four steps; month-5 dry run 65 vs 16 of 78 | §3.3, §4.2 | B · 0:40 |
| 12 | Calibrated: a 5% score means about 5% are mule weeks | Out-of-fold reliability table, 8 bands (C14); raw 18.6% vs 0.24%, isotonic 0.24% vs 0.24%; Brier 0.074 → 0.0018 | §4.2 | B · 0:23 |
| 13 | No method beats ours; how the inputs are fed matters more | 13 bars, Table 4.2 (C2): ours on top as the reference, the four tied methods shaded with gain and 95% interval, then the methods behind; caught of 210 | §4.2, Table 4.2 | B · 1:14 |
| 14 | Without labels, detectors catch 16 to 39 of 78; the model 63 | Bars, month 5, 124 flags each (C15); of 62 mules the bank never confirmed: 50 / 42 / 3 | §3.3, §4.4.4 | C · 0:24 |
| 15 | A fair test: same accounts, same weeks, same number of flags | Four cards: 50,061 accounts, 163 mules · every week · top N · scored once; strip "Reproducible": seeded data, run records, shared model files, plan committed first, 233 automated tests | §4.1 | C · 0:43 |
| 16 | With the same alerts, the model caught 2.4× as many mule accounts | 163-dot grid (C4); 120 vs 50; precision 43% vs 19%; over all 78 weeks 138 vs 59 of 180 | §4.3, Table 4.3A | C · 0:44 |
| 17 | The model catches more in every type, age band and opening month | Table by type, age band, opening month (C16); false alarms per 1,000 by age | §4.3, §4.4.3 | C · 0:25 |
| 18 | More mules, about as fast: both catch once laundering starts | Catch curves with the "started" area (C1); 8 vs 9 days; 2 of 120 before the start; weekly budget bars | §4.3, Table 4.3B | C · 0:37 |
| 19 | The gain comes from transactions, not the application form | Paired bars with / without the application score (C5) | §4.4.2 | C · 0:35 |
| 20 | One input drives the catches: 1-hour forwarding | Permutation drops (C6); gain shares 51% / 13% / 7% | §3.4 | C · 0:33 |
| 21 | At opening: 3 months earlier, but 20 reviews per mule | Top N at opening (C7); 24 of 24 are fakes | §4.4.7, Table 4.4E | D · 0:33 |
| 22 | If one simulator guess is wrong, the model still leads | Lead with 95% interval per scenario, chance band 0.31–0.55 (C3) | §4.4.1 | D · 0:39 |
| 23 | The lead holds at every rule threshold we tried | Grouped bars, rules vs model, at 7 rule scales (C8) | §4.4.6, Table 4.4D | D · 0:30 |
| 24 | Stronger hand-written rules close only part of the gap | Two bar groups, month 5 (C17): caught of 78 (16 / 34 / 65); money stopped of £310,207 (8% / 15% / 33%) | §4.4.8, §5.2 | D · 0:24 |
| 25 | A bank would get a weekly ranked list, the same length as today | Four steps: score every week (≈6 s) · keep the top N · calibrated probability · investigators decide | §4.5 | D · 0:35 |
| 26 | Every result is a comparison inside a simulation | Four limits; 50+ false alarms per 1,000: model 6.1 vs rules 4.4 | §5.2 | D · 0:40 |
| 27 | Next: run it silently beside a real bank's rules | Three steps: shadow run · harder simulation · fix the age skew | §5.4 | D · 0:24 |
| 28 | Earlier? No. More mule accounts, same alerts? Yes. | Cover frame: a verdict card per hypothesis (H1 supported, H2 not supported, H3 not at this budget); "Thank you"; repository link | — | D · 0:34 |

---

## 7. Appendix slides and the removed backups

After "Thank you" and not presented (no Q&A); they stay in the exported deck.

| # | Title | Content | Report |
|---|---|---|---|
| 29 | References | 12 sources: BAF (Jesus et al. 2022), SAML-D (Oztas 2023), RUSI (Westmore & Owen 2025), BioCatch 2022, Oztas et al. 2024 and PwC 2020, Cifas 2026, Which? 2018, Synectics 2024, Vocalink 2017, UK Finance / Pay.UK / ONS, MLR 2017 / FCA / FFIEC / FinCEN, OCBC | References, App. A |
| 30 | Use of generative AI and external code | What Claude and Claude Code helped with; what the team did; libraries used | AI declaration |

**Where the 12 old backups went (third pass, 19 Nov 2026):**

| Old backup | Now |
|---|---|
| B1 Public tables vs hidden labels | Deleted; slide 7 shows the time split and the label |
| B2 Cleaning | Deleted; the "Clean" box on slide 10 |
| B3 Gain by input family | Deleted; slide 20 gives the gain shares, slide 9 the families |
| B4 Who is caught | Main slide 17 |
| B5 Label-free detectors | Main slide 14 |
| B6 Rule scorecard, B7 money stopped | Main slide 24 (both) |
| B8 Calibration | Main slide 12 |
| B9 Reproducibility | Strip on slide 15 |
| B10 Sources | Appendix slide 29, References (full list) |
| B11 78 weeks | One line on slide 16 |
| B12 AI declaration | Appendix slide 30 |

---

## 8. Chart data

All values from committed files or the report's tables. Colours: model `#003D7C`, rules `#EF7C00`, other greys.

### C1 — Catch curve (slide 18)
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

The last column is the small bar chart on the right of slide 18 (3–19 a week, 280 in weeks 0–26).

### C2 — Model selection (slide 13)
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

### C3 — Robustness (slide 22)
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

### C4 — Dot grid (slide 16)
Source: `outputs/modelling/results/v1_full/final_test/launderers.csv`, summarised in `robustness.mcnemar`.

| Group | Mule accounts | Colour |
|---|---|---|
| Caught by both | 43 | blue dot, orange ring |
| Model only | 77 | blue |
| Rules only | 7 | orange |
| Neither | 36 | light grey |
| **Total** | **163** | |

### C5 — Where the gain comes from (slide 19)
Sources: `comparison/v1_full/folds.csv` (`ref` vs `A1_activity`, `A3_app_only`); month 5 and seed 43 from
`CHANGELOG.md` (29 Oct entry, `evaluation.compare`).

| Check | With application score | Activity only | Mule accounts |
|---|---|---|---|
| Training folds | 180 | 184 | 210 |
| Month 5 (calibration month) | 65 | 61 | 78 |
| Month 5 of a second dataset (seed 43) | 56 | 56 | 65 |

Separate callout: application score alone, 24 of 210 (training folds).

### C6 — What drives the catches (slide 20)
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

### C7 — Flagging at opening (slide 21)
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

### C8 — Rule threshold (slide 23)
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

### C14 — Calibration (slide 12)
Source: `outputs/modelling/models/v1_full/frozen_tuned_avg5/calibration/reliability.csv` and `report.md`. Month 5,
isotonic, out of fold; "observed" = share of mule weeks among the account-weeks in the band.

| Calibrated score | Account-weeks | Predicted | Observed |
|---|---|---|---|
| under 0.01% | 270,612 | 0.001% | 0.009% |
| 0.01–0.1% | 334,813 | 0.03% | 0.03% |
| 0.1–0.3% | 115,726 | 0.23% | 0.24% |
| 0.3–1% | 39,339 | 0.58% | 0.68% |
| 1–3% | 17,602 | 1.8% | 1.7% |
| 3–10% | 6,763 | 5.3% | 5.1% |
| 10–30% | 527 | 13.8% | 11.6% |
| 30–100% | 739 | 69.0% | 67.4% |

Average score vs observed rate: raw 18.6% vs 0.24%; isotonic 0.24% vs 0.24%. Brier score 0.074 → 0.0018. Ranks do
not change, so no catch changes.

### C15 — Label-free detectors (slide 14)
Source: `outputs/modelling/outlier/v1_full/report.md` (the one pre-registered look, 31 Oct). Month 5, 78 mule
accounts, 124 flags each. "Model, true labels" is the earlier frozen recipe retrained on this Mac (63 of 78; the
model of record catches 65), so the bank-label comparison is like with like.

| Method | Caught of 78 | Of the 62 the bank never confirmed |
|---|---|---|
| Model, true labels | 63 | 50 |
| Model, bank-confirmed cases only | 54 | 42 |
| Rarity sum, no labels | 39 | — |
| Rarity score, no labels | 16 | — |
| Isolation Forest, no labels | 16 | — |
| The bank's rules | 16 | 3 |

### C16 — Who is caught (slide 17)
Sources: `outputs/modelling/results/v1_full/final_test/launderers.csv` (type), `by_age_w26.csv`, `by_month_w26.csv`.
Test months, weeks 0–26.

| Mule accounts | In the test | Model caught | Rules caught |
|---|---|---|---|
| Fake accounts | 147 | 109 | 46 |
| Witting mules | 11 | 8 | 3 |
| Unwitting mules | 5 | 3 | 1 |
| Age under 30 | 26 | 21 | 8 |
| Age 30–49 | 80 | 62 | 25 |
| Age 50+ | 57 | 37 | 17 |
| Opened month 6 | 93 | 72 | 30 |
| Opened month 7 | 70 | 48 | 20 |

False alarms per 1,000 normal accounts, model vs rules: under 30 1.9 vs 4.2; 30–49 2.9 vs 4.3; 50+ 6.1 vs 4.4. Fewer
false alarms overall (160 vs 214), but they fall on older customers.

### C17 — Stronger rules and money stopped (slide 24)
Sources: `outputs/modelling/scorecard/PLAN.md` (month 5 scored once, 18 Nov); `results/v1_full/month5_cost/`
(closing item 7). Month 5, 78 mule accounts, weeks 0–26, the rules' weekly budget.

| | Caught of 78 | Laundered money stopped (of £310,207 paid out) |
|---|---|---|
| The bank's rules | 16 | 8% (8.4%) |
| Rule scorecard (fast forwarding, new payers, pass-through) | 34 | 15% (15.2%) |
| Model of record | 65 | 33% (32.9%; £76k more than the rules, 95% £48k–£107k) |

The scorecard was written with hindsight, so it is generous to the rules. For the mules the model caught, 64% of
their money had already gone by its first flag.

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
| 63 · 54 · 39 · 16 · 16 · 16 · 50 / 42 / 3 of 62 | label-free detectors, month 5 | C15 |
| 18.6% vs 0.24% · 0.24% vs 0.24% | month 5 average score vs observed mule-week rate, raw and calibrated | C14 |
| 147 / 109 / 46 … 70 / 48 / 20 · 160 vs 214 | caught by type, age band, opening month; false alarms | C16 |
| 16 · 34 · 65 of 78 | month 5: rules, rule scorecard, model of record | `outputs/modelling/scorecard/PLAN.md` |
| £310,207 · 33% vs 15% vs 8% · 64% | month 5: money paid out by week 26; share stopped by model, scorecard, rules; share gone for the model's catches | `closing/PLAN.md` item 7, C17 |
| 233 automated tests | pytest, 19 Nov (233 passed, 3 skipped); the report says 219 | section 11 |
| 138 vs 59 of 180 | weeks 0–77 | `final_test/summary_w77.csv` |

**Two numbers that look alike:** "63 of 78" is the Mac-retrained recipe used in the bank-label check (and the older
model `frozen_tuned`); "65 of 78" is the model of record. Use 65 everywhere except the bank-label comparison
(54 vs 63) and the label-free slide (14), which compare like with like.

---

## 10. What changes from the old deck

**Structure**
- [x] Title: "Catching Mule Accounts Earlier" → "Early Detection of Money Mule Accounts" (cover and deck name,
  19 Nov)
- [x] Cover and closing slide in one frame, on the same background as every other slide
- [x] No backup slides: their plots are in the talk (slides 12, 14, 17, 24, 15, 16) or deleted; References and the
  AI declaration follow "Thank you" as an appendix
- [x] Five section-divider slides removed; section tracker in every footer
- [x] Project-flow slide with 11 numbers removed; slide 3 previews the answers instead
- [x] New: the data gap (4), the bank's rules (6), the training data (7), training choices (11), calibration (12),
  label-free detectors (14), who is caught (17), drivers (20), at opening (21), rule thresholds (23), stronger rules
  and money stopped (24), References (29), AI declaration (30)
- [x] "Analytical Insights" moved before the model (8); "Experimental Design" opens the results (15)

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

1. **Talk length.** 17:21 at 130 words a minute, over the course's "no more than 15 minutes" and over the ~16:30
   the team accepted on 19 Nov. Slide 13's rebuilt notes (160 words, 1:14) are the largest single item; bringing them
   back to about 80 words saves 0:38. Taking slides 12, 14, 17 and 24 out of the talk saves 1:36 more (15:07).
2. **Report title.** The deck and its cover are "Early Detection of Money Mule Accounts"; the report is titled
   "Anti-Money Laundering Mule Account Detection System". Use one name for the deck, the video and the report.
3. **CatBoost in the report.** Report §3.3 / §4.2 says CatBoost is within the 0.085 margin; the paired test puts it
   reliably behind (−0.049, −0.076 to −0.024). The deck follows the paired test; the report should too (0.085 is the
   minimum detectable effect, not a noise band).
4. **Test count.** The report says 219 automated tests; slide 15's reproducibility strip says 233 (233 passed,
   3 skipped, 19 Nov). Use one.
5. **The report's References list** lacks Oztas et al. 2024, RUSI (Westmore & Owen 2025), Vocalink 2017, Which? 2018
   and Synectics 2024, which its text or Appendix A cites and the deck's References slide (29) lists. Add them.
6. **The report's AI declaration** lists the libraries without XGBoost, CatBoost and PyTorch, which the methods
   comparison used; slide 30 lists them.
7. **"Report §" tags.** The team removed them from slides 6, 7 and 8 on 19 Nov; 23 other slides still carry one.
   Keep them on all slides or remove them from all.
8. **The old deck's robustness slide** shows model results at 0.1% and 1% prevalence; the report says those runs were
   not done. Leave them out unless they ran.

---

## 12. Checks before recording

- [ ] Every number on every slide matches section 9 (one person reads the slide, another reads the ledger)
- [ ] Model is blue and rules are orange on every slide and chart
- [ ] Each footer's "Report §" matches the final report's numbering (re-check if the report's sections move)
- [ ] Speaker notes present on all 28 main slides and both appendix slides after export
- [ ] The NUS Computing logo shows on the cover and the closing slide after export
- [ ] The system diagram's arrows (slide 10) survive the export
- [ ] Glossary words used throughout (no "launderer", "detected earlier")
- [ ] Each presenter rehearses with a timer: A 4:11, B 4:50, C 4:01, D 4:18 (total 17:21; over the 15:00 guideline, see section 11)
- [ ] Title and names readable for at least 8 seconds at the start of the video
- [ ] Exported `.pptx` and PDF open correctly (fonts, charts, notes)
