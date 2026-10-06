"""Automatic checks + data card + "too easy?" test for a simulator run.

  PYTHONPATH=src python -m sim.checks --out data/v0 --baf PATH
Exits with code 1 if any check fails. Writes <out>/data_card.md.
"""
from __future__ import annotations
import argparse
import os
import sys
import tempfile

import duckdb
import numpy as np
import pandas as pd

from .config import Cfg
from .common import BAF_FEATURES

PUBLIC_ACCOUNTS = ["account_id", "open_month", "open_day"] + BAF_FEATURES
PUBLIC_TX = ["txn_id", "account_id", "direction", "counterparty_id", "day", "time", "amount", "item_count",
             "payment_type", "sender_bank_location", "receiver_bank_location"]


def connect(out):
    con = duckdb.connect()
    con.execute("PRAGMA memory_limit='1500MB'")
    con.execute(f"PRAGMA temp_directory='{tempfile.gettempdir()}/sim_duckdb'")
    for name in ["accounts", "accounts_truth", "transactions", "transactions_truth", "aml_alerts", "aml_outcomes"]:
        con.execute(f"CREATE VIEW {name} AS SELECT * FROM read_parquet('{os.path.join(out, name + '.parquet')}')")
    con.execute(f"CREATE VIEW acc_internal AS SELECT * FROM read_parquet('{os.path.join(out, '_internal/accounts_internal.parquet')}')")
    return con


def run_checks(con, cfg, baf_path):
    q = lambda s: con.execute(s).fetchone()[0]
    days = cfg.get("size.observe_days")
    res = []

    def check(name, ok, detail=""):
        res.append((name, bool(ok), detail))

    # 1. keys
    dup_acc = q("SELECT count(*) - count(DISTINCT account_id) FROM accounts")
    orphan = q("SELECT count(*) FROM transactions t ANTI JOIN accounts a USING (account_id)")
    dup_tx = q("SELECT count(*) FROM (SELECT txn_id, account_id FROM transactions GROUP BY 1, 2 HAVING count(*) > 1)")
    dup_tr = q("SELECT count(*) - count(DISTINCT txn_id) FROM transactions_truth")
    miss_tr = q("SELECT count(*) FROM (SELECT DISTINCT txn_id FROM transactions) t ANTI JOIN transactions_truth USING (txn_id)")
    check("1 keys", dup_acc == 0 and orphan == 0 and dup_tx == 0 and dup_tr == 0 and miss_tr == 0,
          f"dup accounts {dup_acc}, orphan rows {orphan}, dup (txn,account) {dup_tx}, dup truth ids {dup_tr}, rows without truth {miss_tr}")

    # 2. no leaks into public files
    acc_cols = [r[0] for r in con.execute("DESCRIBE accounts").fetchall()]
    tx_cols = [r[0] for r in con.execute("DESCRIBE transactions").fetchall()]
    check("2 no leaks", acc_cols == PUBLIC_ACCOUNTS and tx_cols == PUBLIC_TX,
          f"accounts {len(acc_cols)} cols, transactions {len(tx_cols)} cols")

    # 3. timing
    bad_t = q(f"""SELECT count(*) FROM transactions t JOIN accounts a USING (account_id)
                  WHERE t.day < a.open_day OR t.day > a.open_day + {days - 1}""")
    after_exit = q("""SELECT count(*) FROM transactions t JOIN aml_outcomes o USING (account_id)
                      WHERE o.aml_exit_day IS NOT NULL AND t.day > o.aml_exit_day""")
    check("3 timing", bad_t == 0 and after_exit == 0, f"rows outside window: {bad_t}, rows after closure: {after_exit}")

    # 4. laundering only on launderers, on/after start
    bad_l = q("""SELECT count(*) FROM transactions t JOIN transactions_truth r USING (txn_id)
                 JOIN accounts_truth a USING (account_id)
                 WHERE r.is_laundering = 1 AND (a.is_launderer = 0 OR t.day < a.launder_start_day)""")
    no_l = q("""SELECT count(*) FROM accounts_truth a WHERE is_launderer = 1 AND account_id NOT IN
                (SELECT t.account_id FROM transactions t JOIN transactions_truth r USING (txn_id) WHERE r.is_laundering = 1)""")
    check("4 laundering placement", bad_l == 0 and no_l == 0, f"misplaced rows {bad_l}, launderers with no laundering {no_l}")

    # 5. internal transfers come in matching pairs
    bad_p = q("""WITH p AS (SELECT txn_id, count(*) n, count(DISTINCT direction) d, count(DISTINCT day) dd,
                       count(DISTINCT time) tt, count(DISTINCT amount) aa FROM transactions
                       WHERE counterparty_id LIKE 'A%' GROUP BY 1)
                 SELECT count(*) FROM p WHERE n <> 2 OR d <> 2 OR dd <> 1 OR tt <> 1 OR aa <> 1""")
    check("5 internal pairs", bad_p == 0, f"broken pairs: {bad_p}")

    # 6. shares
    n = q("SELECT count(*) FROM accounts")
    n_l = q("SELECT sum(is_launderer) FROM accounts_truth")
    want = round(cfg.get("profiles.launderer_share") * n)
    check("6 shares", n == cfg.get("size.n_accounts") and n_l == want, f"accounts {n:,}, launderers {n_l} (target {want})")

    # 7. money
    bad_m = q("SELECT count(*) FROM accounts_truth WHERE laundered_out > laundered_in + 0.01")
    check("7 money", bad_m == 0, f"accounts with more out than in: {bad_m}")

    # 8. BAF unchanged
    if baf_path:
        cols = " AND ".join([f'a."{c}" IS NOT DISTINCT FROM b."{c}"' for c in BAF_FEATURES])
        bad_b = q(f"""SELECT count(*) FROM accounts a JOIN acc_internal i USING (account_id)
                      JOIN (SELECT *, row_number() OVER () - 1 AS baf_row FROM read_csv_auto('{baf_path}')) b
                      ON b.baf_row = i.baf_row WHERE NOT ({cols})""")
        check("8 BAF unchanged", bad_b == 0, f"rows differing from BAF: {bad_b}")
    # 9. the bank's rules behaved as specified
    pause = cfg.get("rules.pause_days")
    r_lo, r_hi = cfg.get("rules.review_days")
    too_close = q(f"""SELECT count(*) FROM (SELECT alert_day - lag(alert_day) OVER (PARTITION BY account_id ORDER BY alert_day) gap
                     FROM aml_alerts) WHERE gap < {pause}""")
    bad_rev = q(f"SELECT count(*) FROM aml_alerts WHERE review_days < {r_lo} OR review_days > {r_hi}")
    bad_conf = q("""SELECT count(*) FROM aml_alerts a JOIN accounts_truth t USING (account_id)
                    WHERE a.confirmed = 1 AND (t.is_launderer = 0 OR t.launder_start_day > a.alert_day)""")
    bad_exit = q("""SELECT count(*) FROM aml_outcomes o LEFT JOIN
                    (SELECT account_id, min(alert_day + review_days) e FROM aml_alerts WHERE confirmed = 1 GROUP BY 1) c
                    USING (account_id) WHERE o.aml_exit_day IS DISTINCT FROM c.e""")
    check("9 rules", too_close == 0 and bad_rev == 0 and bad_conf == 0 and bad_exit == 0,
          f"alerts closer than {pause} days {too_close}, bad review {bad_rev}, wrong confirmations {bad_conf}, exit mismatches {bad_exit}")
    return res


def rules_card(con, out):
    lines = []
    tot = con.execute("""SELECT count(*) n, sum(CASE WHEN t.is_launderer = 1 AND t.launder_start_day <= a.alert_day THEN 1 ELSE 0 END) tp
                         FROM aml_alerts a JOIN accounts_truth t USING (account_id)""").fetchone()
    n, tp = tot
    caught = con.execute("""SELECT count(DISTINCT a.account_id) FROM aml_alerts a JOIN accounts_truth t USING (account_id)
                            WHERE t.is_launderer = 1 AND t.launder_start_day <= a.alert_day""").fetchone()[0]
    n_l = con.execute("SELECT sum(is_launderer) FROM accounts_truth").fetchone()[0]
    closed = con.execute("SELECT count(aml_exit_day) FROM aml_outcomes").fetchone()[0]
    lines.append(f"- Alerts: {n:,}; true {tp} -> false alarm share {1 - tp / max(n, 1):.1%} (target 90-95%)")
    lines.append(f"- Launderers alerted after their start: {caught} of {n_l} ({caught / n_l:.0%}); accounts closed: {closed}")
    t = con.execute("""WITH a AS (SELECT a.*, t.is_launderer = 1 AND t.launder_start_day <= a.alert_day AS tru
                       FROM aml_alerts a JOIN accounts_truth t USING (account_id)),
                   r AS (SELECT unnest(string_split(rules_fired, ';')) AS rule_id, tru FROM a)
                   SELECT rule_id AS rule, count(*) alerts, sum(tru::int) true_alerts FROM r GROUP BY 1 ORDER BY 1""").df()
    lines += ["", t.to_markdown(index=False), ""]
    t = con.execute("""WITH f AS (SELECT a.account_id, min(a.alert_day) d FROM aml_alerts a JOIN accounts_truth t USING (account_id)
                         WHERE t.is_launderer = 1 AND t.launder_start_day <= a.alert_day GROUP BY 1)
                   SELECT round(median(d - t.launder_start_day)) median_days_to_catch, min(d - t.launder_start_day) min_days,
                          max(d - t.launder_start_day) max_days FROM f JOIN accounts_truth t USING (account_id)""").df()
    lines += ["Days from laundering start to the rules' first true alert:", "", t.to_markdown(index=False), ""]
    t = con.execute("""SELECT round(avg(c), 1) mean_alerts_per_week, median(c) median_per_week, max(c) max_per_week
                       FROM (SELECT alert_day // 7 w, count(*) c FROM aml_alerts GROUP BY 1)""").df()
    lines += ["Weekly alert budget (what every model gets):", "", t.to_markdown(index=False), ""]
    shp = os.path.join(out, "_internal/launderer_shapes.parquet")
    if os.path.exists(shp):
        con.execute(f"CREATE OR REPLACE VIEW shapes AS SELECT * FROM read_parquet('{shp}')")
        t = con.execute("""SELECT s.shape, count(*) launderers,
                   sum(CASE WHEN o.aml_alert_day IS NOT NULL AND o.aml_alert_day >= t.launder_start_day THEN 1 ELSE 0 END) alerted,
                   count(o.aml_exit_day) closed
                   FROM shapes s JOIN accounts_truth t USING (account_id) JOIN aml_outcomes o USING (account_id)
                   GROUP BY 1 ORDER BY 2 DESC""").df()
        lines += ["Launderers by shape (alerted = first alert on or after start):", "", t.to_markdown(index=False), ""]
    return "\n".join(lines)


def data_card(con, cfg):
    days = cfg.get("size.observe_days")
    months = days / 30.4375
    parts = []
    t = con.execute("SELECT profile, count(*) n, sum(baf_fraud_bool) fraud_rows FROM accounts_truth GROUP BY 1 ORDER BY 2 DESC").df()
    parts.append(("Accounts by profile", t))
    t = con.execute(f"""WITH x AS (SELECT t.account_id, a.profile, sum(item_count) items, count(*) rows_,
            sum(CASE WHEN direction='in' THEN amount ELSE 0 END) i, sum(CASE WHEN direction='out' THEN amount ELSE 0 END) o
            FROM transactions t JOIN accounts_truth a USING (account_id) GROUP BY 1, 2)
        SELECT profile, round(median(rows_)/{months},1) rows_per_month, round(median(items)/{months},1) payments_per_month,
               round(median(i)/{months}) money_in_per_month, round(median(o)/{months}) money_out_per_month,
               round(median(o/i),2) out_over_in FROM x GROUP BY 1 ORDER BY 1""").df()
    parts.append(("Activity per account (medians)", t))
    t = con.execute("""SELECT r.laundering_type, count(*) rows_, round(100.0*count(*)/sum(count(*)) OVER (),3) pct_rows,
            round(median(amount),2) median_amount FROM transactions t JOIN transactions_truth r USING (txn_id)
            GROUP BY 1 ORDER BY 2 DESC""").df()
    parts.append(("Rows by type", t))
    t = con.execute("""SELECT profile, count(*) n, min(launder_start_day - a.open_day) min_rel,
            round(median(launder_start_day - a.open_day)) median_rel, max(launder_start_day - a.open_day) max_rel,
            round(100.0*avg(CASE WHEN launder_start_day - a.open_day < 365 THEN 1 ELSE 0 END),1) pct_year1
            FROM accounts_truth JOIN accounts a USING (account_id) WHERE is_launderer = 1 GROUP BY 1""").df()
    parts.append(("Laundering start (days after opening)", t))
    t = con.execute("""SELECT CASE WHEN network_id = 'NET_BIG' THEN 'big network' WHEN network_id IS NULL THEN 'none'
            ELSE 'chain' END net, count(*) n FROM accounts_truth WHERE is_launderer = 1 GROUP BY 1""").df()
    parts.append(("Launderer networks", t))
    t = con.execute("""SELECT r.is_laundering,
            round(100.0*avg(CASE WHEN receiver_bank_location <> 'UK' THEN 1 ELSE 0 END),2) pct_abroad,
            round(100.0*avg(CASE WHEN receiver_bank_location IN ('Mexico','Turkey','Morocco','UAE') THEN 1 ELSE 0 END),2) pct_high_risk,
            round(100.0*avg(CASE WHEN counterparty_id LIKE 'A%' THEN 1 ELSE 0 END),2) pct_internal
            FROM transactions t JOIN transactions_truth r USING (txn_id) WHERE direction = 'out' GROUP BY 1""").df()
    parts.append(("Outgoing rows: abroad, high-risk, internal (%)", t))
    t = con.execute("""SELECT a.profile, round(median(laundered_in)) median_in, round(median(laundered_out)) median_out,
            round(sum(laundered_in)) total_in FROM accounts_truth a WHERE is_launderer = 1 GROUP BY 1""").df()
    parts.append(("Laundered money per launderer (GBP)", t))
    lines = ["# Data card", "", f"Run: {cfg.get('meta.version')}, seed {cfg.get('meta.seed')}, "
             f"{cfg.get('size.n_accounts'):,} accounts, {days} days each.", ""]
    for title, df in parts:
        lines += [f"## {title}", "", df.to_markdown(index=False), ""]
    return "\n".join(lines)


def too_easy(con, out):
    """Quick model on whole-window account totals. Near-perfect = laundering is too obvious."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_predict, StratifiedKFold
    from sklearn.metrics import roc_auc_score, average_precision_score
    f = con.execute("""
        WITH w AS (SELECT account_id, day // 7 wk, sum(CASE WHEN direction='in' THEN amount ELSE 0 END) win
                   FROM transactions GROUP BY 1, 2),
             s AS (SELECT account_id, max(win) / (median(win) + 1) spike FROM w GROUP BY 1),
             t AS (SELECT account_id, count(*) n_rows,
                     sum(CASE WHEN direction='in' THEN amount ELSE 0 END) money_in,
                     sum(CASE WHEN direction='out' THEN amount ELSE 0 END) money_out,
                     max(CASE WHEN direction='in' THEN amount END) max_in,
                     count(DISTINCT CASE WHEN direction='in' THEN counterparty_id END) n_senders,
                     avg(CASE WHEN direction='out' AND receiver_bank_location <> 'UK' THEN 1.0 ELSE 0 END) share_abroad,
                     sum(CASE WHEN counterparty_id LIKE 'A%' THEN 1 ELSE 0 END) n_internal
                   FROM transactions GROUP BY 1)
        SELECT t.*, s.spike, a.is_launderer FROM t JOIN s USING (account_id) JOIN accounts_truth a USING (account_id)""").df()
    y = f.pop("is_launderer").to_numpy()
    X = f.drop(columns=["account_id"]).fillna(0).to_numpy()
    cv = StratifiedKFold(5, shuffle=True, random_state=0)
    p = cross_val_predict(HistGradientBoostingClassifier(max_iter=200), X, y, cv=cv, method="predict_proba")[:, 1]
    single = {c: roc_auc_score(y, f[c].fillna(0)) for c in f.columns if c != "account_id"}
    acc = con.execute("SELECT a.*, t.is_launderer FROM accounts a JOIN accounts_truth t USING (account_id)").df()
    num = acc[BAF_FEATURES].select_dtypes("number").fillna(0).to_numpy()
    pa = cross_val_predict(LogisticRegression(max_iter=2000), (num - num.mean(0)) / (num.std(0) + 1e-9),
                           acc["is_launderer"].to_numpy(), cv=cv, method="predict_proba")[:, 1]
    return {"activity_auc": roc_auc_score(y, p), "activity_ap": average_precision_score(y, p),
            "application_auc": roc_auc_score(acc["is_launderer"], pa),
            "single_feature_auc": single, "base_rate": y.mean()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/sim.yaml")
    ap.add_argument("--out")
    ap.add_argument("--baf")
    a = ap.parse_args()
    cfg = Cfg(a.config)
    out = a.out or cfg.get("paths.out_dir")
    con = connect(out)
    res = run_checks(con, cfg, a.baf or cfg.get("paths.baf_file"))
    for name, ok, detail in res:
        print(f"{'PASS' if ok else 'FAIL'}  {name:24s} {detail}")
    card = data_card(con, cfg)
    card += "\n## The bank's rules (benchmark)\n\n" + rules_card(con, out) + "\n"
    te = too_easy(con, out)
    card += "\n## Too-easy check (5-fold, whole-window totals)\n\n"
    card += f"- Activity model AUC: {te['activity_auc']:.3f} (average precision {te['activity_ap']:.3f}, base rate {te['base_rate']:.4f})\n"
    card += f"- Application-only logistic AUC: {te['application_auc']:.3f}\n"
    card += "- Single-feature AUC: " + ", ".join(f"{k} {v:.3f}" for k, v in te["single_feature_auc"].items()) + "\n"
    with open(os.path.join(out, "data_card.md"), "w") as fh:
        fh.write(card)
    print(card)
    sys.exit(0 if all(ok for _, ok, _ in res) else 1)


if __name__ == "__main__":
    main()
