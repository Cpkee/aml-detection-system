# Slide plan: Catching More Mule Accounts with the Same Alerts

BT4012 Fraud Analytics, Group 09. Drafted 19 Nov 2026 (Kee Chee Pheng, with Claude).
Replaces the structure of the current deck "BT4012 Group 9.pptx" (26 slides, SharePoint). Words follow
[`GLOSSARY.md`](../../GLOSSARY.md).

**Built 19 Nov 2026** as a Claude Slides deck from this plan (17 main + 12 backup slides, speaker notes on every
slide): https://claude.ai/artifact/WnCujmAAgHgagdxoiS9V3Z (private until shared from its Share menu; export to
`.pptx` / PDF or send to Canva from there). Where the built deck differs from the first draft of this plan, the plan
below has been updated to match; the list is in section 1.

**Contents**
1. How to use this plan
2. The one message and the storyline
3. Design rules
4. The recurring picture: life of a mule account
5. Presenters and timing
6. Slide by slide (17 main slides)
7. Backup slides
8. Chart data
9. Number ledger
10. What changes from the current deck
11. Brief to paste into Claude Design
12. Checks before presenting

---

## 1. How to use this plan

1. **Agree with your teammate** that the deck is rebuilt from this plan, so two versions don't drift apart.
2. **Download the current deck** from SharePoint (File → Download a copy) and upload it to Claude Design as a
   reference **for the NUS look only** (logo, navy). Its text and some of its numbers are out of date (section 10).
3. **Paste the brief** in section 11 into Claude Design, then paste section 6 (the slides) and section 8 (chart data).
4. **Fix slide by slide** in Claude Design until every slide meets the design rules (section 3).
5. **Send to Canva** (Claude Design's export menu). In Canva the deck is fully editable by the whole team.
6. **Check speaker notes arrived** in Canva. If they did not, paste them from section 6 (or ask Claude to add them
   through the Canva connector).
7. **Number check** (section 12): every number on every slide against the ledger (section 9). AI layout tools can
   reword text and change numbers.
8. **Export** from Canva to `.pptx` and PDF. Rehearse with a timer (section 5).

Steps 2–4 are done: the deck was built directly from this plan (link above). Start at step 5.

**Built deck: changes from the first draft of this plan** (all reflected below)
- Slide 5 headline says "realistic applications": BAF is generated from a real bank's applications, not copied.
- Slide 9 headline is "**Top** boosted trees tie": CatBoost, also boosted trees, is significantly behind (gain −0.049,
  95% −0.076 to −0.024, passes Holm). The draft's "gaps under 0.085 are within noise" was wrong and is removed: 0.085 is
  the pre-registered minimum detectable effect (the smallest gain the folds can reliably show), not a noise band.
- Slide 12: the grey "started laundering" area replaces the timeline strip along the top (no room under the chart).
- Slide 3: the footer's section tracker replaces the roadmap of six section names.
- Slide 15: "Few mules are real customers (16)" (the hyphenated label broke badly across lines).
- Section tracker sits in the footer row with the page number, not in a header. No NUS logo yet: add it by hand.
- Backup B9 shows the out-of-fold reliability table (`calibration/reliability.csv`), not the PNG. B10 says 233
  automated tests (233 passed, 3 skipped, 19 Nov), not 197.

---

## 2. The one message and the storyline

**The one sentence every slide supports:**

> With the same number of alerts each week as the bank's rules, a model that reads each account's first weeks
> caught **2.4× as many mule accounts (120 vs 50 of 163)**. It was **not earlier**, and **not thanks to the
> application form**: it read the laundering burst more precisely.

**The arc is question → answer.** Slide 3 asks two questions; slide 17 answers each with a clear yes or no:

| Question (slide 3) | Answer (slide 17) |
|---|---|
| Does account-opening data help catch mule accounts? | Not at the bank's alert budget: the gain comes from transactions |
| With the same alerts, can we catch more, or sooner? | More: 2.4×. Sooner: no (median 8 vs 9 days from start) |

**Six sections** (the order you set): Why this matters → Why we simulate → Method → Evaluation and results →
Limitations → Future work and conclusion.

---

## 3. Design rules

Clean and intuitive: **the slide shows, the speaker explains.**

| Rule | Detail |
|---|---|
| One idea per slide | The headline is that idea, written as a full sentence of at most 12 words |
| Word budget | At most **25 words** on a slide besides the headline, chart labels and numbers. Everything else goes to the speaker notes |
| One visual per slide | A chart, a diagram or the timeline, never a wall of cards. At most one row of big numbers per section |
| Colours | **NUS Blue `#003D7C` = the model.** **NUS Orange `#EF7C00` = the bank's rules.** Grey `#8C8C8C` = everything else. White backgrounds, dark text `#1A1A1A`. Never swap model and rules colours |
| Type | One sans-serif family (the current deck's). Headline ~32 pt, body ≥ 18 pt, chart labels ≥ 14 pt |
| Section tracker | Small footer row on every slide: **Why · Data · Method · Results · Limits · Conclusion**, current one bold, page number on the right. Replaces the 5 divider slides |
| Logo | NUS logo top right, as now (not in the built deck: add by hand) |
| Numbers | Counts as "120 of 163", shares as whole percentages ("43%"), never 4 decimals. Same number, same wording everywhere |
| Sources | External figures (BioCatch, RUSI, Oztas et al.) get a small footer citation. Internal sources (repo files) go only in speaker notes and backup slide B11, never on a slide |
| Words | Use `GLOSSARY.md`: **mule account**, **the bank's rules**, **flag**, **caught**, **weekly alert budget**, **days from start**. Never "earlier" to mean "caught when the rules never are" |

---

## 4. The recurring picture: life of a mule account

One horizontal timeline, drawn once and reused four times so the audience always knows where they are.

```
 opened ── quiet weeks ──▶ ┃ laundering burst (~2 weeks) ┃ ──▶ flagged ──▶ closed
 day 0     (fakes: median   ┃ money in, forwarded within  ┃     (rules: median
            week 13)        ┃ hours: 53% inside 1 hour    ┃      9 days after start)
```

| Appears on | What it highlights |
|---|---|
| Slide 2 (problem) | The whole life: hides among normal accounts, moves money fast, flagged late |
| Slide 5 (simulated bank) | What we plant: one burst, forwarded at the published speed |
| Slide 7 (weekly inputs) | A weekly cut-off line: the model sees only the past |
| Slide 12 (timing) | Both the model and the rules flag after the burst starts; the model flags far more of them |

---

## 5. Presenters and timing

15 minutes. The team fills in names.

| Slot | Slides | Sections | Time |
|---|---|---|---|
| A: ________ | 1–5 | Why this matters, why we simulate | 4:00 |
| B: ________ | 6–9 | Method | 3:30 |
| C: ________ | 10–13 | Evaluation and results | 4:00 |
| D: ________ | 14–17 | Robustness, limitations, future work, conclusion | 3:20 |

Speaker notes run at about 130 words a minute; each slide's notes fit its time.

---

## 6. Slide by slide

Each block: **headline** (on the slide) · **on slide** (the only other words) · **visual** · **notes** (what the
presenter says, not on the slide) · **replaces** (current deck slide numbers).

### Section 1: Why this matters

#### Slide 1 — Title · A · 0:20
- **Headline:** Catching More Mule Accounts with the Same Alerts
- **On slide:** "Can account-opening data plus early activity beat a bank's rules?" · BT4012 Fraud Analytics ·
  Group 09 · Kee Chee Pheng · Chai Li Ann · Keith Tan Beng Hui · Li Mingfen Emmy
- **Visual:** keep the current title slide's ranked-list graphic (rows with "flag" buttons).
- **Notes:** "Good morning. We're Group 9. Our project asks whether a bank can catch more money-mule accounts
  without hiring more investigators."
- **Replaces:** 1 (new title).

#### Slide 2 — The problem · A · 1:00
- **Headline:** Mule accounts pass stolen money on within hours
- **On slide:** "up to 0.3% of accounts" · "53% of the money leaves within 1 hour" · "90–95% of rule alerts are
  false" · three icons: Fake account · Witting mule · Unwitting mule
- **Visual:** the timeline (section 4), first appearance, with the three numbers pinned to it: 0.3% at "opened",
  53% at "forwarded", 90–95% at "flagged". Footer: BioCatch 2022; RUSI 2025; Oztas et al. 2024.
- **Notes:** "A mule account receives stolen money and passes it on, so the trail from victim to criminal breaks.
  There are three kinds: fake accounts opened with a stolen or invented identity, witting mules who sell or lend
  their account, and unwitting mules who are tricked into moving money. They are rare, up to 0.3% of accounts,
  about 1 in 330. And they are fast: in RUSI's 2025 study, over half the money left a mule account within an hour.
  Banks look for them with transaction-monitoring rules, but practitioners estimate 90 to 95% of rule alerts are
  false alarms, and every alert is reviewed by hand."
- **Replaces:** 3.

#### Slide 3 — Our question · A · 0:50
- **Headline:** Same number of alerts: can early data catch more mules, sooner?
- **On slide:** two question chips: "1. Does the application help?" · "2. More, or sooner?" · preview line:
  "Answer: 2.4× as many. Not sooner." (the footer's section tracker serves as the roadmap)
- **Visual:** two weekly review lists of the same length side by side, orange (the bank's rules) and blue (the
  model), labelled "same length every week".
- **Notes:** "Our question: if the bank keeps the same investigators, reviewing the same number of accounts each
  week, can a model that reads each new account's application and first weeks of activity catch more mule accounts,
  and catch them sooner? That is two questions, and we answer both at the end. The short answer: 2.4 times as many
  mule accounts, but not sooner. Here is how we got there."
- **Replaces:** 4 (its fair-test half moves to slide 10) and 5 (the 11-number project-flow slide is dropped).

### Section 2: Why we simulate

#### Slide 4 — The data gap · A · 0:50
- **Headline:** No public dataset follows an account from application to transactions
- **On slide:** three boxes, each with two ticks or crosses: **BAF** (applications ✓, transactions ✗) · **SAML-D**
  (applications ✗, laundering-labelled transactions ✓) · **Real bank data** (both ✓, private 🔒) → arrow → **Our
  simulator joins them**
- **Visual:** the three boxes as puzzle pieces that don't fit, our simulator as the bridge.
- **Notes:** "To answer this we need data that follows each account from its application to its later
  transactions, with labels saying which accounts are mules. That doesn't exist publicly. The Bank Account Fraud
  dataset, BAF, from NeurIPS 2022, has realistic account applications with fraud labels but nothing after the
  account opens. SAML-D has synthetic UK transactions with laundering labels across 28 typologies, but no
  applications. Real bank data has both, but it's confidential. So we built the link: BAF applications, 18 months
  of simulated banking, and laundering planted from published evidence. Every number in the simulator has a
  published source or is labelled an assumption and tested."
- **Replaces:** 6 (divider; it had one line on this). New slide; answers the professor's "justify your dataset".

#### Slide 5 — The simulated bank · A · 1:00
- **Headline:** We simulate 18 months of UK banking around realistic applications
- **On slide:** five steps with one number under four of them: Applications **244,000 accounts** → Hidden profiles
  **732 mule accounts (0.3%)** → Everyday banking **109M transactions** → Laundering planted → The bank's rules
  **93.4% of alerts false**
- **Visual:** a five-step pipeline of icons; the timeline (second appearance) sits inside step 4, showing one
  burst forwarded at the published speed.
- **Notes:** "Step one: 244,000 BAF applications become accounts opened over 8 months; BAF's fraud rows become fake
  accounts. Step two: 0.3% become mule accounts, 732 in all: 73% fake, the rest real customers recruited with the
  age profile reported by Cifas. Step three: everyday UK banking from UK Finance, Pay.UK and ONS figures, 109
  million transactions. Step four: each mule account gets one burst of about two weeks, in 15 shapes measured
  from SAML-D, with amounts and forwarding speed from RUSI. Step five: the bank's six rules, tuned so 93.4% of
  their alerts are false, inside the 90 to 95% practitioners report. They catch 32% of mule accounts, a median 9
  days after laundering starts."
- **Replaces:** 7.

### Section 3: Method

#### Slide 6 — What the data taught us · B · 0:50
- **Headline:** Three findings from the training months shaped the model
- **On slide:** three columns, finding → design choice:
  1. "Fakes look different at opening" → "The application enters as one score"
  2. "Nothing to see before laundering starts" → "Score every week"
  3. "Mules pay mules, but only after starting" → "No network features"
- **Visual:** three columns, each with a small icon and a down-arrow from finding to choice.
- **Notes:** "We explored only the training months. First, fake accounts already differ at opening, on housing,
  device and address history, with AUCs of 0.60 to 0.69; real-customer mules differ mainly by age: 65% are under 30,
  against 27% of normal accounts. Second, before laundering starts, activity adds nothing beyond the application;
  once a burst starts, activity separates strongly, AUCs of 0.70 to 0.86. Third, a mule's payees are other mules 20
  times more often than chance, but only 1 of 163 such links exists before both ends have started, so network
  features cannot bring the first catch forward."
- **Replaces:** 13 (moved before the model, where it belongs).

#### Slide 7 — Weekly inputs, no look-ahead · B · 0:50
- **Headline:** Each week, the model sees only what a bank would have seen
- **On slide:** "38 inputs per account per week" · five chips: Application score · Volume · Payers and payees ·
  Forwarding speed · Last 4 weeks
- **Visual:** the timeline (third appearance) with a vertical "this week" cut-off line; everything to its right
  greyed out and labelled "never used".
- **Notes:** "Each account gets one row per week since it opened. The inputs for week w use only transactions up
  to the end of week w, and a test re-computes all 19 million account-weeks to prove it. Cleaning is fitted on the
  training months only: negative codes in BAF become missing flags, categories are frozen. The 38 inputs are 28
  weekly activity features, 8 four-week windows, weeks since opening, and one application score. Accounts opened in
  months 0 to 4 train the model, month 5 calibrates it, and months 6 and 7 are the test, read once."
- **Replaces:** 10 (cleaning details → backup B2, B3) and the no-look-ahead part of 8.

#### Slide 8 — The two-stage model · B · 1:00
- **Headline:** An application score feeds a LightGBM that reads weekly activity
- **On slide:** "29 application fields → logistic regression → application score" · "+ 37 weekly activity inputs →
  LightGBM (5 seeds averaged) → weekly ranked list"
- **Visual:** a left-to-right flow diagram, two inputs merging into one model, ending in the ranked list cut at the
  rules' length. Small inset: "one tree on raw fields memorised the fake accounts".
- **Notes:** "Why two stages? A single LightGBM on all 29 raw application fields scored 1.00 on training data and
  0.40 on validation: it memorised the fake accounts, which are mules in every week. Squeezing the application into
  one out-of-fold logistic score closed most of that gap. LightGBM then reads the weekly activity: it handles mixed
  scales and meaningful missing values, learns rule-like thresholds, and fits 4.45 million rows fast with class
  weights instead of resampling. We average five seeds for stability, and calibrate on month 5 so each score reads as
  a probability."
- **Replaces:** 11.

#### Slide 9 — Model selection · B · 0:50
- **Headline:** Top boosted trees tie; logistic regression is clearly behind
- **On slide:** chart only; the top five bars sit in one shaded group labelled "Ties: gaps within noise"
- **Visual:** horizontal bar chart C2 (section 8): share of mule accounts caught at the rules' budget. Our model in
  blue, the bank's rules in orange, the rest grey.
- **Notes:** "We compared rivals on the training months only, before the test months were opened, under the same
  rule: catch as many mule accounts as possible at the rules' weekly budget. The top group, activity only, untuned
  LightGBM, our model, XGBoost and the graph neural network, all land between 0.45 and 0.46. Gaps that small are
  within noise, so we kept the model we had frozen beforehand. CatBoost is behind at 0.41, and that gap holds up in
  the paired test. Logistic regression is clearly behind at 0.30, and the bank's rules catch 0.14 on the same folds.
  Activity only, our model without the application score, comes up again on slide 13."
- **Replaces:** 12 (its label-free detectors → backup B6).

### Section 4: Evaluation and results

#### Slide 10 — The fair test · C · 0:50
- **Headline:** A fair test: same accounts, same weeks, same number of flags
- **On slide:** "50,061 accounts opened in months 6–7 · 163 mule accounts" · "each week: rules flag N, model flags
  its top N (about 10)" · "a flag is permanent" · "scored once, 2 Nov 2026"
- **Visual:** a loop diagram: the test accounts → each week since opening → two lists of equal length → lock icon.
- **Notes:** "The test is built so the only difference is the method. Same accounts: the 50,061 accounts opened in
  the test months, 163 of them mule accounts by week 26. Same clock: weeks since each account opened. Same workload:
  each week the model may flag exactly as many accounts as the rules alerted on, about 10 among 50,000. A flag is
  permanent, and accounts the bank closed count as caught. The test months were scored once, on 2 November, with a
  lock file; the plan was committed before the run."
- **Replaces:** 15 (and the "fair test" half of 4).

#### Slide 11 — The main result · C · 1:10
- **Headline:** With the same alerts, the model caught 2.4× as many mule accounts
- **On slide:** big numbers "120 vs 50 of 163" · "precision 43% vs 19%" · dot-grid legend: Both 43 · Model only
  77 · Rules only 7 · Neither 36
- **Visual:** chart C4: a grid of 163 dots, one per mule account, coloured by who caught it.
- **Notes:** "Over the first 26 weeks the model caught 120 of the 163 mule accounts, the rules 50. That's recall of
  74% against 31%. Because both flag about the same number of accounts, precision rises too: 43% of the model's
  flags are mule accounts, against 19% of the rules' alerts, and the model raises 54 fewer false alarms, 160 against
  214. Look at the grid: of the 84 mule accounts only one side caught, 77 were the model's and 7 the rules'. That
  split is far beyond chance: a paired McNemar test gives p of about 5 in 10 to the 16."
- **Replaces:** 16.

#### Slide 12 — Timing · C · 1:00
- **Headline:** More mules, about as fast: both catch once laundering starts
- **On slide:** "median 8 vs 9 days from start" · "2 of 120 flagged before laundering began"
- **Visual:** chart C1: two lines (model, rules) over weeks 0–26, with a light grey area for "mules that have
  started laundering", which stands in for the timeline's fourth appearance (quiet weeks, then the burst).
- **Notes:** "Both curves stay flat until about week 8, because fake accounts lie quiet for two to three months.
  Then the gap opens exactly when laundering starts. The model is not earlier: its median is 8 days from the start of
  laundering to the first flag, the rules' 9. Only 2 of its 120 catches came before laundering began. And by the
  first flag much of the money is gone. On month 5, mule accounts paid out £310,207 by week 26; flagging stops 33% of
  it with the model and 8% with the rules, and even for the mules the model caught, 64% of their money had already
  left."
- **Replaces:** 17.

#### Slide 13 — Where the gain comes from · C · 1:00
- **Headline:** The gain comes from transactions, not the application form
- **On slide:** "Application score alone: 24 of 210" · "Strongest signal: money forwarded within 1 hour"
- **Visual:** chart C5: paired bars, "with application score" vs "activity only", for three checks.
- **Notes:** "This answers our first question. We refitted the same model without the application score. On the
  training folds it caught 180 mule accounts with the score and 184 without; on month 5, 65 against 61; on a second
  simulated dataset, 56 and 56. Every difference is within chance. The application score alone catches 24 of 210. At
  about 10 flags a week, the top of the list is decided by the burst, not the form. The model does use the score to
  rank accounts, it's half of its split gain, but at this budget it doesn't change who is caught. The strongest
  activity signal is the share of money forwarded within an hour over the last four weeks."
- **Replaces:** 19.

### Section 5: Limitations (slide 14 closes the results; presenter D)

#### Slide 14 — Robustness · D · 1:00
- **Headline:** If one simulator guess is wrong, the model still leads
- **On slide:** "Holds 7 · Shrinks 1 · Falls behind 0" · "lead = model's share caught − rules' share caught"
- **Visual:** chart C3: one row per scenario, a dot for the lead and a line for its 95% interval, over a shaded
  chance band (0.31–0.55). "Larger transfers" in orange.
- **Notes:** "We changed one simulator guess at a time and re-ran everything: data, model and one locked test. The
  lead is the model's share of mule accounts caught minus the rules' share: 0.43 on our main data. Rebuilding the
  same data with another seed gives 0.54, so anything from 0.31 to 0.55 is chance. The lead holds in 7 of 8 changed
  scenarios: fewer fake accounts, repeated bursts, fakes starting late or early, young fakes, more older mules, and
  patient launderers who forward slowly. It shrinks once: if mules move £1,500 instead of £532, the rules catch 120 of
  163 themselves, and the lead falls to 0.17. The model never falls behind."
- **Replaces:** 22 (updated with Variant II and patient launderers, both 19 Nov).

#### Slide 15 — Limitations · D · 0:50
- **Headline:** Every result is a comparison inside a simulation
- **On slide:** four icons with short labels: "Simulated data" · "Few mules are real customers (16)" · "False alarms fall
  on older customers" · "One dataset, one locked test"
- **Visual:** four icons in a row; under "older customers" a tiny bar pair: 50+ false alarms per 1,000 normal
  accounts, model 6.1 vs rules 4.4.
- **Notes:** "Four limits. One: the data is simulated; we planted the laundering, and launderers don't react to
  being caught, so results are relative, not real detection times. Two: only 16 of the 163 test mules are real
  customers; the model caught 11 of them and the rules 4, too few for a separate claim, so the headline is mostly
  about fake accounts. Three: the model's false alarms follow the fake accounts' age profile: among normal customers
  aged 50 and over it flags 6.1 per 1,000, the rules 4.4, while under-30s get 1.9 against 4.2. Four: one dataset and
  one locked test, though eight robustness runs back it up."
- **Replaces:** 23 (updated: Variant II now run; fairness numbers added).

### Section 6: Future work and conclusion

#### Slide 16 — Future work · D · 0:40
- **Headline:** Next: run it silently beside a real bank's rules
- **On slide:** three steps: "Shadow run on real accounts" → "Harder simulation: more real-customer mules,
  launderers who adapt" → "Fix the age skew in false alarms"
- **Visual:** three-step arrow.
- **Notes:** "The next step is real data: run the model silently beside a bank's rules on its own accounts, before
  any flag reaches an investigator, and compare with its confirmed cases. The model can learn from those: trained only
  on the cases the bank confirmed, it still caught 54 of 78 on month 5, against 63 for the same recipe on the true
  labels. Second, a harder simulation, with more real-customer mules and launderers who change tactics. Third, deal
  with the age skew in false alarms before any real use."
- **Replaces:** the "next steps" half of 25.

#### Slide 17 — Conclusion and Q&A · D · 0:50
- **Headline:** Earlier? No. More mule accounts for the same alerts? Yes.
- **On slide:** two answer cards: "Does the application help? Not at this budget" · "More or sooner? 2.4× more (120
  vs 50 of 163), not sooner (8 vs 9 days)" · footer: "Thank you · Questions?" ·
  github.com/Cpkee/aml-detection-system
- **Visual:** the two question chips from slide 3, now answered; the slide stays up during Q&A.
- **Notes:** "Back to our two questions. Does account-opening data help? Not at the bank's alert budget: the gain
  comes from reading transactions. Can we do better with the same alerts? Yes: 2.4 times as many mule accounts, with
  more than twice the precision, though not sooner. For a bank that means a weekly ranked list, the same length as
  today's alert list, for the same investigators. Thank you; we're happy to take questions."
- **Replaces:** 24 and 26.

> **Order note:** this follows your original outline (limitations → future improvements → conclusion), so the
> conclusion is the last slide and stays on screen during Q&A. In round 3 I listed conclusion before next steps;
> swap 16 and 17 back if the team prefers.

---

## 7. Backup slides

For Q&A only; same design rules. Each reuses current-deck content where it exists.

| # | Title | Content | Source | From current slide |
|---|---|---|---|---|
| B1 | Variables and split | Public tables (accounts, transactions) vs hidden truth; split train 0–4, calibrate 5, test 6–7 | `src/amldata/`, `CLAUDE.md` data rules | 8 |
| B2 | Cleaning recipe | Missing codes → flags; real negatives kept; categories frozen; tree and linear modes | `notebooks/02_preprocess.ipynb` | 10 |
| B3 | The 38 inputs | Table by family (volume 8, counterparties 5, flow and speed 4, since opening 7, own history 4, four-week windows 8, + weeks since opening, application score) | `src/features/weekly.py`, `candidates.ADOPTED` | 10 |
| B4 | Who is caught | Caught by type (fake 109 of 147, real customers 11 of 16), age band and opening month, false alarms per 1,000 by age | `results/v1_full/final_test/summary_w26.csv`, `by_age_w26.csv`, `by_month_w26.csv` | 18 |
| B5 | How a bank would use it | Weekly scoring run; same-length ranked list; calibrated probability; investigators decide | report 4.5 | 20 |
| B6 | Label-free detectors | Month 5, 78 mule accounts, 124 flags: rules 16, frozen model 63, bank-label model 54, rarity score 16, rarity sum 39, Isolation Forest 16 | `outputs/modelling/outlier/v1_full/report.md` | 12 (right side) |
| B7 | A stronger rule set | Month 5: rules 16, hand-written scorecard 34, model 65 of 78 | `outputs/modelling/scorecard/PLAN.md` | — |
| B8 | Money gone before the first flag | Month 5: £310,207 paid out by week 26; stopped: rules 8.4%, scorecard 15.2%, model 32.9% | `results/v1_full/month5_cost/summary.csv` | — |
| B9 | Calibration | Month 5, out of fold: predicted vs observed mule-week rate per score band (isotonic); raw scores average 18.6% vs 0.24% observed | `models/v1_full/frozen_tuned_avg5/calibration/reliability.csv`, `report.md` | — |
| B10 | Reproducibility | Same settings, same data; model files shared; test locked and every look logged; 233 automated tests | `README.md`, `results/v1_full/final_test/` | 25 (left half) |
| B11 | Sources | Every external source, plus the internal files behind each slide | section 9 | footers of all slides |
| B12 | The longer horizon | Weeks 0–77: model 138 vs rules 59 of 180 | `results/v1_full/final_test/summary_w77.csv` | 16 (last row) |

---

## 8. Chart data

All values from committed files. Colours: model `#003D7C`, rules `#EF7C00`, other `#8C8C8C`.

### C1 — Catch curve (slide 12)
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

Plot: lines for model and rules; light grey area for "started". End labels: "model 74%", "rules 31%". The
weekly-alerts column is for the speaker or a backup; don't plot it on the main slide.

### C2 — Model selection (slide 9)
Source: `outputs/modelling/comparison/v1_full/folds.csv` (mean `catch_rules` over 3 training folds; XGBoost and
CatBoost rows from branch `comparison-boosted`, PR #58). Paired tests against our model from
`interim_paired_tests_folds.csv` (Holm over the rivals): XGBoost −0.003 (95% −0.017 to +0.010) and the graph neural
network −0.004 (−0.035 to +0.025) are ties; CatBoost −0.049 (−0.076 to −0.024) and logistic regression are
significantly behind. `MDE.json`'s 0.085 is the pre-registered minimum detectable effect (80% power), not a noise
band: don't put it on the slide.

| Method | Share of mule accounts caught at the rules' budget | Caught (of 210) |
|---|---|---|
| Activity only (our model without the application score) | 0.46 | 184 |
| LightGBM, untuned | 0.46 | 179 |
| **Our model (two-stage LightGBM)** | **0.45** | **180** |
| XGBoost, tuned | 0.45 | 179 |
| Graph neural network (GraphSAGE) | 0.45 | 181 |
| CatBoost, tuned | 0.41 | 163 |
| Logistic regression* | 0.30 | 125 |
| **The bank's rules** | **0.14** | — |

\* Logistic regression without the one-hour forwarding share (`A4b`, chosen after fold 1). With it, a share of 1
on a tiny balance tops the ranking and it catches 0.03. Say so in the notes if asked.

### C3 — Robustness (slide 14)
Source: `outputs/modelling/robustness/summary.csv`; Variant II and patient launderers from
`outputs/modelling/closing/PLAN.md` items 6 and 5 (item 5 on branch `item5-patient`). Lead = (model caught − rules
caught) / mule accounts, weeks 0–26, test months. Chance band 0.31–0.55.

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

### C4 — Dot grid (slide 11)
Source: `outputs/modelling/results/v1_full/final_test/launderers.csv`, summarised in `robustness.mcnemar`.

| Group | Mule accounts | Colour |
|---|---|---|
| Caught by both | 43 | blue dot, orange ring |
| Model only | 77 | blue |
| Rules only | 7 | orange |
| Neither | 36 | light grey |
| **Total** | **163** | |

Layout: 163 dots in a grid (e.g. 17 × 10, last row 3), grouped in the order above.

### C5 — Where the gain comes from (slide 13)
Sources: `comparison/v1_full/folds.csv` (`ref` vs `A1_activity`, `A3_app_only`); month 5 and seed 43 from
`CHANGELOG.md` (29 Oct entry, `evaluation.compare`).

| Check | With application score | Activity only | Mule accounts |
|---|---|---|---|
| Training folds | 180 | 184 | 210 |
| Month 5 (calibration month) | 65 | 61 | 78 |
| Month 5 of a second dataset (seed 43) | 56 | 56 | 65 |

Separate callout: application score alone, 24 of 210 (training folds).

---

## 9. Number ledger

Every number that appears on a slide or in the notes. Check each slide against this table after Canva (section 12).

| Number | Meaning | Source |
|---|---|---|
| up to 0.3% (1 in 330) | share of accounts that are mule accounts | BioCatch 2022, `configs/sim.yaml` `launderer_share` |
| 53% within 1 hour | money leaving a mule account within an hour (28% in 15 min + 25% in 15–60 min) | RUSI 2025, `sim.yaml` `forward_delay_shares` |
| 90–95% | practitioners' estimate of false rule alerts | Oztas et al. 2024, `sim.yaml` `false_alarm_target` |
| £532 | average transfer out of a mule account | RUSI 2025, `sim.yaml` `out_transfer_mean` |
| 244,000 · 109M · 732 | accounts, transactions, mule accounts in the main data | `CLAUDE.md` (v1_full result), `data/v1_full/data_card.md` |
| 73% fake | share of mule accounts that are fake | `sim.yaml` `in_window_mix` |
| 93.4% · 32% · 9 days | rules' false-alarm share, share of mule accounts alerted, median days from start | `CLAUDE.md` (v1_full result) |
| AUC 0.60–0.69 · 65% vs 27% · 0.70–0.86 | EDA: fakes at opening; real mules under 30; activity once a burst starts | `outputs/modelling/eda/report.md`, `CLAUDE.md` EDA findings |
| 20× · 1 of 163 | mules pay mules; links existing before both start | `CLAUDE.md` homophily finding |
| 38 inputs · 19.0M account-weeks · 4.45M rows | model inputs; feature store size; training account-weeks (4,450,113) | `CLAUDE.md`; `CHANGELOG.md` (feature store entry) |
| train 1.00 vs validation 0.40 | one tree on raw application fields | `CLAUDE.md` Phase 4 baselines |
| 0.458 … 0.141 | model selection (catch share at the rules' budget, training folds) | C2 |
| −0.049 (−0.076 to −0.024) | CatBoost vs our model, paired test (notes only) | C2 |
| 50,061 · 163 · about 10 a week | test accounts, mule accounts by week 26, rules' weekly alerts (280 over weeks 0–26) | `final_test/summary_w26.csv`, `settings.json` |
| 120 vs 50 · 74% vs 31% | caught, recall | `final_test/summary_w26.csv` |
| 42.9% vs 18.9% (say 43% vs 19%) · 160 vs 214 | precision; false alarms | `final_test/summary_w26.csv`, current slide 16 |
| 2.4× | 120 / 50 | arithmetic |
| 43 / 77 / 7 / 36 · p ≈ 5×10⁻¹⁶ | head to head; McNemar exact p | `closing/PLAN.md` item 1 |
| 8 vs 9 days · 2 of 120 | median days from start; flags before start | `final_test/summary_w26.csv` |
| £310,207 · 33% vs 8% · 64% | month 5: money paid out by week 26; share stopped; share gone for the model's catches | `closing/PLAN.md` item 7 |
| 180 vs 184 · 65 vs 61 · 56 vs 56 · 24 | onboarding value | C5 |
| half of split gain | application score's share of the model's split gain (0.507) | `models/v1_full/frozen_tuned_avg5/importance.csv` |
| 0.43 (0.35–0.52) · 0.31–0.55 · 7 hold, 1 shrinks | robustness | C3 |
| 16 · 11 vs 4 | real-customer mules in the test; caught by model vs rules | `final_test/summary_w26.csv` (witting 8/11 + unwitting 3/5; rules 3/11 + 1/5) |
| 6.1 vs 4.4 · 1.9 vs 4.2 | false alarms per 1,000 normal accounts, 50+ and under 30, model vs rules | `final_test/by_age_w26.csv` |
| 54 vs 63 of 78 | month 5: model trained on bank-confirmed cases only vs the same recipe on true labels (both retrained on one Mac) | `outputs/modelling/outlier/v1_full/report.md` |
| 65 of 78 | month 5: the model of record (`frozen_tuned_avg5`) | `CLAUDE.md` Phase 5 |
| 138 vs 59 of 180 | weeks 0–77 | `final_test/summary_w77.csv` |

**Two numbers that look alike:** "63 of 78" is the older model (`frozen_tuned`) and the Mac-retrained recipe used
in the bank-label check. "65 of 78" is the model of record. Use 65 everywhere except the bank-label comparison
(54 vs 63), which compares like with like.

---

## 10. What changes from the current deck

**Structure**
- [ ] Title: "Catching Mule Accounts Earlier" → "Catching More Mule Accounts with the Same Alerts"
- [ ] Remove the 5 section-divider slides (2, 6, 9, 14, 21); add the section tracker
- [ ] Remove slide 5 (project flow with 11 numbers); one preview line on slide 3 instead
- [ ] New slide 4 (the data gap)
- [ ] Move "Analytical Insights" (old 13) before the model (new 6)
- [ ] Move "Experimental Design" (old 15) to open the results (new 10)
- [ ] Old 8, 18, 20, 25 (left half) → backup B1, B4, B5, B10

**Numbers that are wrong or out of date**
- [ ] "63 of 78" on old slides 12, 20, 25 → 65 (model of record), except the bank-label "54 vs 63"
- [ ] Robustness: old 5 says "7 scenarios: 6 hold", old 22 "6 scenarios: 5 hold", old 24 "5 of 6" → **8
  changed scenarios: 7 hold, 1 shrinks** (Variant II 0.51 and patient launderers 0.48 added 19 Nov)
- [ ] Old 23 says the extra BAF datasets were "not run": Variant II has now run (holds)
- [ ] Old 25 next steps lists "neural networks" as unfinished: the graph neural network has run (0.45, ties)
- [ ] Old 4 defines "earlier" as "or caught when the rules never do": remove; speed is "days from start" only
- [ ] "Real BAF applications": BAF is privacy-preserving data generated from a real bank's applications (Jesus et
  al. 2022). Say "realistic applications" in the notes; check the wording against the paper

**Clean-up**
- [ ] Old 9's leftover "Presenter [B] · ~3 min · rubric: …" removed
- [ ] File-path source lines removed from slides; internal sources in speaker notes and B11
- [ ] The two matplotlib charts (old 17, 18) redrawn in the deck's style from section 8

**Before presenting:** merge or cite the branches that hold slide numbers: `item5-patient` (patient launderers)
and `comparison-boosted` (XGBoost, CatBoost), so every source exists on `main`.

---

## 11. Brief to paste into Claude Design

Paste this first, then sections 6 and 8 of this plan.

```text
Build a 16:9 presentation of 17 main slides plus 12 backup slides for a 15-minute university project talk
(BT4012 Fraud Analytics, NUS, Group 09). Audience: professor and classmates; some are not specialists.

Content: use ONLY the slide-by-slide plan and chart data I paste next. Do not invent, round differently or
reword any number. Do not add statistics.

The uploaded deck is a reference for the NUS look only (logo, navy, white). Its text and some numbers are out
of date: do not copy them.

Design rules:
- Clean and intuitive. One idea per slide; the headline is a full sentence of at most 12 words.
- At most 25 words on a slide besides the headline, chart labels and numbers. Put each slide's "Notes" text in
  that slide's speaker notes, never on the slide.
- One visual per slide: a chart, a simple diagram or the timeline. No walls of text cards.
- Colours: NUS Blue #003D7C always means the model; NUS Orange #EF7C00 always means the bank's rules; grey
  #8C8C8C for everything else; white backgrounds; dark text #1A1A1A.
- One sans-serif font. Headline about 32 pt, body at least 18 pt, chart labels at least 14 pt.
- A small section tracker in every slide's footer: Why · Data · Method · Results · Limits · Conclusion, with the
  current section bold. No section-divider slides.
- NUS logo top right.
- The "life of a mule account" timeline is drawn once and reused on slides 2, 5, 7 and 12 in the same style.
- Charts are drawn from the data tables exactly as given (C1-C5).
- Small footer citations only for external sources (BioCatch 2022, RUSI 2025, Oztas et al. 2024); no file paths.
```

---

## 12. Checks before presenting

- [ ] Every number on every slide matches section 9 (one person reads the slide, another reads the ledger)
- [ ] Model is blue and rules are orange on every slide and chart
- [ ] No slide has more than 25 words besides headline, labels and numbers
- [ ] Speaker notes present on all 17 main slides in Canva
- [ ] Glossary words used throughout (no "launderer", "benchmark", "detected earlier")
- [ ] Each presenter rehearses with a timer: A 4:00, B 3:30, C 4:00, D 3:20 (total under 15:00)
- [ ] Backup slides B1–B12 reachable, e.g. hyperlinked from slide 17
- [ ] Exported `.pptx` and PDF from Canva open correctly (fonts, charts, notes)
