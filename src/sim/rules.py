"""Step 6: the bank's existing rule system (the benchmark models must beat).

Six rules run once a week on transactions only (never on hidden files):
  R1 large cash        one cash deposit >= GBP 10,000                         (MLR 2017 reg 14)
  R2 repeated cash     >GBP 1,000 cash in a day on 2+ days within 2 weeks,
                       or the 12-month cash total crosses GBP 10,000          (FCA proposed limits)
  R3 many senders      8+ different payers in one week                        (tuned)
  R4 pass-through      80%+ of the week's money in leaves the same week,
                       with money in above GBP 2,000                           (tuned)
  R5 high-risk country GBP 5,000+ sent to MX/TR/MA/UAE over 4 weeks           (tuned)
  R6 sudden change     money in >= 10x the usual week (avg of previous 8)     (tuned)
Then: at most one alert per account every 28 days; each alert is reviewed for 3-30 days;
80% of true alerts are confirmed; a confirmed account is closed at alert day + review days,
and all its later activity is removed. R3-R6 thresholds are scaled together until 90-95% of
alerts are false alarms (R1 and R2 are legal limits and stay fixed).
"""
from __future__ import annotations
import numpy as np
import pandas as pd

RULES = ["R1", "R2", "R3", "R4", "R5", "R6"]


def weekly_features(con, tx_rel: str, acc_path: str, days: int, high_risk: list[str], r2_day: float) -> pd.DataFrame:
    """One row per account-week with everything the six rules look at."""
    hr = ", ".join(f"'{c}'" for c in high_risk)
    f = con.execute(_features(con, tx_rel, acc_path, days, hr).replace("{R2DAY}", str(float(r2_day)))).df()
    # previous week's 12-month cash total, so the yearly limit fires when it is crossed, not every week after
    f["cash_52wk_prev"] = f.groupby("acct")["cash_52wk"].shift(1).fillna(0.0)
    return f


def _features(con, tx_rel, acc_path, days, hr):
    sql = f"""
    WITH acc AS (SELECT row_number() OVER () - 1 AS acct, account_id, open_day FROM read_parquet('{acc_path}')),
    t AS (SELECT a.acct, x.day, x.day // 7 AS w, x.direction, x.counterparty_id, x.amount, x.payment_type,
                 x.receiver_bank_location FROM {tx_rel} x JOIN acc a USING (account_id)),
    wk AS (SELECT acct, w,
             sum(amount) FILTER (WHERE direction = 'in')  AS money_in,
             sum(amount) FILTER (WHERE direction = 'out') AS money_out,
             max(amount) FILTER (WHERE payment_type = 'Cash Deposit') AS max_cash,
             count(DISTINCT counterparty_id) FILTER (WHERE direction = 'in' AND counterparty_id <> 'CASH') AS n_senders,
             sum(amount) FILTER (WHERE direction = 'out' AND receiver_bank_location IN ({hr})) AS hr_out,
             sum(amount) FILTER (WHERE payment_type = 'Cash Deposit') AS cash_in
           FROM t GROUP BY 1, 2),
    cday AS (SELECT acct, day // 7 AS w, count(*) AS days_over FROM
               (SELECT acct, day, sum(amount) s FROM t WHERE payment_type = 'Cash Deposit' GROUP BY 1, 2)
             WHERE s > {{R2DAY}} GROUP BY 1, 2),
    grid AS (SELECT acct, unnest(range(open_day // 7, (open_day + {days} - 1) // 7 + 1)) AS w FROM acc),
    g AS (SELECT g.acct, g.w, coalesce(money_in, 0) money_in, coalesce(money_out, 0) money_out,
                 coalesce(max_cash, 0) max_cash, coalesce(n_senders, 0) n_senders, coalesce(hr_out, 0) hr_out,
                 coalesce(cash_in, 0) cash_in, coalesce(days_over, 0) days_over
          FROM grid g LEFT JOIN wk USING (acct, w) LEFT JOIN cday USING (acct, w))
    SELECT acct, w, money_in, money_out, max_cash, n_senders,
      sum(days_over) OVER (PARTITION BY acct ORDER BY w ROWS BETWEEN 1 PRECEDING AND CURRENT ROW)  AS days_over_2wk,
      sum(cash_in)   OVER (PARTITION BY acct ORDER BY w ROWS BETWEEN 51 PRECEDING AND CURRENT ROW) AS cash_52wk,
      sum(hr_out)    OVER (PARTITION BY acct ORDER BY w ROWS BETWEEN 3 PRECEDING AND CURRENT ROW)  AS hr_4wk,
      avg(money_in)  OVER (PARTITION BY acct ORDER BY w ROWS BETWEEN 8 PRECEDING AND 1 PRECEDING)  AS usual_in,
      count(*)       OVER (PARTITION BY acct ORDER BY w ROWS BETWEEN 8 PRECEDING AND 1 PRECEDING)  AS hist
    FROM g ORDER BY acct, w"""
    return sql


def hits(f: pd.DataFrame, cfg, scale: float) -> pd.DataFrame:
    g = lambda k: cfg.get(f"rules.{k}")
    h0, h1 = g("R6_history_weeks")
    flags = pd.DataFrame({
        "R1": f["max_cash"].to_numpy() >= g("R1_large_cash"),
        "R2": (f["days_over_2wk"].to_numpy() >= g("R2_days_in_2wk"))
              | ((f["cash_52wk"].to_numpy() > g("R2_cash_per_year")) & (f["cash_52wk_prev"].to_numpy() <= g("R2_cash_per_year"))),
        "R3": f["n_senders"].to_numpy() >= max(2, round(g("R3_senders_week") * scale)),
        "R4": (f["money_in"].to_numpy() >= g("R4_min_in") * scale)
              & (f["money_out"].to_numpy() >= g("R4_out_share") * f["money_in"].to_numpy()),
        "R5": f["hr_4wk"].to_numpy() >= g("R5_high_risk_4wk") * scale,
        "R6": (f["hist"].to_numpy() >= h0) & (f["money_in"].to_numpy() >= g("R6_min_in"))
              & (f["usual_in"].fillna(0).to_numpy() >= g("R6_min_usual"))
              & (f["money_in"].to_numpy() >= max(1.5, g("R6_multiple") * scale) * f["usual_in"].fillna(np.inf).to_numpy()),
    })
    any_ = flags.to_numpy().any(axis=1)
    out = flags[any_].copy()
    out.insert(0, "w", f["w"].to_numpy()[any_])
    out.insert(0, "acct", f["acct"].to_numpy()[any_])
    return out.reset_index(drop=True)


def decide(h: pd.DataFrame, cfg, start_day: np.ndarray, is_l: np.ndarray, seed: int):
    """28-day pause, review, confirmation, closure. Deterministic per (account, week)."""
    pause_w = cfg.get("rules.pause_days") // 7
    r_lo, r_hi = cfg.get("rules.review_days")
    conf = cfg.get("rules.confirm_share")
    acct, w = h["acct"].to_numpy(), h["w"].to_numpy()
    keep = np.zeros(len(h), dtype=bool)
    last_a, last_w, closed = -1, -10 ** 9, False
    review = np.zeros(len(h), dtype=int)
    confirmed = np.zeros(len(h), dtype=bool)
    exit_day = {}
    for k in range(len(h)):
        a, wk = acct[k], w[k]
        if a != last_a:
            last_a, last_w, closed = a, -10 ** 9, False
        if closed or wk - last_w < pause_w:
            continue
        keep[k], last_w = True, wk
        u = np.random.default_rng([seed, 3, int(a), int(wk)]).random(2)
        review[k] = r_lo + int(u[0] * (r_hi - r_lo + 1))
        day = wk * 7 + 6
        true = is_l[a] == 1 and 0 <= start_day[a] <= day
        if true and u[1] < conf:
            confirmed[k], closed = True, True
            exit_day[a] = day + review[k]
    al = h[keep].copy()
    al["alert_day"] = al["w"] * 7 + 6
    al["review_days"] = review[keep]
    al["confirmed"] = confirmed[keep].astype(int)
    al["true_alert"] = [(is_l[a] == 1) and (0 <= start_day[a] <= d) for a, d in zip(al["acct"], al["alert_day"])]
    return al.reset_index(drop=True), exit_day


def tune(f, cfg, start_day, is_l, seed):
    lo, hi = cfg.get("rules.false_alarm_target")
    rows = []
    for s in np.geomspace(0.25, 8, 26):
        al, _ = decide(hits(f, cfg, s), cfg, start_day, is_l, seed)
        n = len(al)
        tp = int(al["true_alert"].sum())
        caught = al.loc[al["true_alert"], "acct"].nunique()
        rows.append({"scale": round(float(s), 3), "alerts": n, "true_alerts": tp,
                     "false_alarm_share": 1 - tp / n if n else np.nan, "launderers_caught": caught})
    t = pd.DataFrame(rows)
    ok = t[(t["false_alarm_share"] >= lo) & (t["false_alarm_share"] <= hi)]
    if len(ok):
        best = ok.sort_values(["launderers_caught", "scale"], ascending=[False, True]).iloc[0]
    else:
        best = t.iloc[(t["false_alarm_share"] - (lo + hi) / 2).abs().argsort().iloc[0]]
    return float(best["scale"]), t
