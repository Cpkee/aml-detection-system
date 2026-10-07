"""Step 4: everyday UK banking for every account (launderers too, so they hide among normals)."""
from __future__ import annotations
import datetime as dt
import numpy as np

from .common import MONTH, Rows, interp_anchor, lognormal_mean, lognormal_median, sample_seconds, ext_ids


def _calendar_day(cfg, year, month, day):
    d0 = dt.date.fromisoformat(cfg.get("meta.day0_date"))
    return (dt.date(year, month, day) - d0).days


def generate_normal(cfg, batch, all_open: np.ndarray, rng: np.random.Generator) -> Rows:
    """batch: DataFrame with columns acct (global index), open_day, income."""
    rows = Rows()
    hw = cfg.get("normal.hour_weights")
    days = cfg.get("size.observe_days")
    n_months = days / MONTH
    acct = batch["acct"].to_numpy()
    o = batch["open_day"].to_numpy()
    inc = batch["income"].to_numpy().astype(float)
    n = len(acct)
    sig = cfg.get("normal.amount_sigma")

    # ---- money in and spending per account ---------------------------------------
    mult = lognormal_mean(rng, 1.0, cfg.get("income.personal_sigma"), n)
    src = cfg.get("income.money_in_source")
    anchors = cfg.get("income.ons_household_disposable_annual") if src == "ons_household" \
        else cfg.get("income.hmrc_individual_gross_annual")
    ax = cfg.get("income.anchor_points")
    annual_in = interp_anchor(inc, anchors, ax) * mult
    monthly_in = annual_in / 12
    weekly_spend = interp_anchor(inc, cfg.get("income.spend_weekly_household"), ax) * mult
    spend = np.minimum(weekly_spend * 52 / 12, cfg.get("income.spend_cap_share_of_income") * monthly_in)
    avg_weekly_spend = cfg.get("income.spend_weekly_household")[1]   # the average household: reference for "spending ratio"
    ratio = spend / (avg_weekly_spend * 52 / 12)

    def per_window(rate_per_month, scale=1.0):
        return rng.poisson(rate_per_month * n_months * scale)

    def anywhere(owner_pos, k):
        """k random days inside each owner's window (owner_pos indexes the batch)."""
        return o[owner_pos] + rng.integers(0, days, size=k)

    # ---- salary --------------------------------------------------------------------
    freq = cfg.get("income.pay_frequency")
    names = list(freq)
    period = {"monthly": MONTH, "weekly": 7.0, "fortnightly": 14.0, "four_weekly": 28.0}
    kind = rng.choice(len(names), size=n, p=np.array(list(freq.values())) / sum(freq.values()))
    per = np.array([period[names[k]] for k in kind])
    first = rng.uniform(0, per)
    k_pay = np.floor((days - 1 - first) / per).astype(int) + 1
    pos = np.repeat(np.arange(n), k_pay)
    step = np.arange(len(pos)) - np.repeat(np.cumsum(k_pay) - k_pay, k_pay)
    pay_day = o[pos] + np.floor(first[pos] + step * per[pos]).astype(int)
    pay_amt = annual_in[pos] * per[pos] / 365.25
    employer = ext_ids(rng, n)
    rows.add(acct[pos], pay_day, sample_seconds(rng, len(pos), hw), "in", employer[pos],
             pay_amt, "ACH", "Normal_Salary")

    # ---- bonuses (once a year in the chosen month) ---------------------------------
    has_bonus = rng.random(n) < cfg.get("normal.bonus_share")
    dec_mar = rng.random(n) < cfg.get("normal.bonus_dec_to_mar_share")
    month = np.where(dec_mar, rng.choice([12, 1, 2, 3], size=n), rng.choice(range(4, 12), size=n))
    bonus_size = cfg.get("normal.bonus_avg") * annual_in / np.median(annual_in)
    d0_year = dt.date.fromisoformat(cfg.get("meta.day0_date")).year
    for year in range(d0_year, d0_year + 4):
        bday = np.array([_calendar_day(cfg, year, int(m), 15) for m in month])
        ok = has_bonus & (bday >= o) & (bday <= o + days - 1)
        idx = np.flatnonzero(ok)
        rows.add(acct[idx], bday[idx], sample_seconds(rng, len(idx), hw), "in", employer[idx],
                 lognormal_mean(rng, bonus_size[idx], sig, len(idx)), "ACH", "Normal_Bonus")

    # ---- weekly card totals (one row per account per week) -------------------------
    w_first = o // 7
    w_last = (o + days - 1) // 7
    k_w = w_last - w_first + 1
    pos = np.repeat(np.arange(n), k_w)
    week = np.repeat(w_first, k_w) + (np.arange(len(pos)) - np.repeat(np.cumsum(k_w) - k_w, k_w))
    wday = np.clip(week * 7 + 6, o[pos], o[pos] + days - 1)
    per_week = cfg.get("normal.card_per_month") * 7 / MONTH
    split = cfg.get("normal.card_split_exponent")
    count = rng.poisson(per_week * ratio[pos] ** split)
    keep = count > 0
    pos, wday, count = pos[keep], wday[keep], count[keep]
    item_avg = cfg.get("normal.card_avg_amount") * ratio[pos] ** split
    amt = count * item_avg * lognormal_mean(rng, 1.0, cfg.get("normal.card_week_sigma"), len(pos))
    rows.add(acct[pos], wday, np.full(len(pos), 23 * 3600 + 59 * 60), "out", "CARD_MERCHANTS",
             amt, "Debit card", "Normal_Card", item_count=count)

    # ---- budget for the other outgoing payments ------------------------------------
    card_month = cfg.get("normal.card_per_month") * cfg.get("normal.card_avg_amount") * ratio
    cash_month = cfg.get("normal.cash_withdrawals_per_month") * cfg.get("normal.cash_withdrawal_amount")["median"]
    rest = np.maximum(spend - card_month - cash_month, 0.1 * spend)
    w = cfg.get("normal.non_card_value_weights")
    has_so = rng.random(n) < cfg.get("normal.standing_order_share")
    denom = w["direct_debit"] + w["standing_order"] * has_so + w["transfer_out"]
    dd_total = rest * w["direct_debit"] / denom
    so_total = rest * w["standing_order"] * has_so / denom
    fp_total = rest * w["transfer_out"] / denom

    # ---- Direct Debits: fixed payees, fixed day of month, steady amounts -----------
    n_dd = np.maximum(1, rng.poisson(cfg.get("normal.direct_debits_per_month"), size=n))
    payee_owner = np.repeat(np.arange(n), n_dd)
    share = rng.gamma(cfg.get("normal.dd_split_gamma_shape"), size=len(payee_owner))
    share = share / np.bincount(payee_owner, weights=share)[payee_owner]
    payee_amt = share * dd_total[payee_owner]
    payee_off = rng.integers(0, 28, size=len(payee_owner))
    payee_id = ext_ids(rng, len(payee_owner))
    m_count = int(np.ceil(n_months)) + 1
    p_rep = np.repeat(np.arange(len(payee_owner)), m_count)
    m_idx = np.tile(np.arange(m_count), len(payee_owner))
    owner = payee_owner[p_rep]
    dday = o[owner] + np.floor(m_idx * MONTH).astype(int) + payee_off[p_rep]
    ok = dday <= o[owner] + days - 1
    p_rep, owner, dday = p_rep[ok], owner[ok], dday[ok]
    rows.add(acct[owner], dday, sample_seconds(rng, len(owner), hw), "out", payee_id[p_rep],
             payee_amt[p_rep] * lognormal_mean(rng, 1.0, 0.05, len(owner)), "ACH", "Normal_DirectDebit")

    # ---- standing order: one per month for accounts that have one ------------------
    so_acc = np.flatnonzero(has_so)
    so_rep = np.repeat(so_acc, m_count)
    so_m = np.tile(np.arange(m_count), len(so_acc))
    so_off = rng.integers(0, 28, size=n)
    sday = o[so_rep] + np.floor(so_m * MONTH).astype(int) + so_off[so_rep]
    ok = sday <= o[so_rep] + days - 1
    so_rep, sday = so_rep[ok], sday[ok]
    so_payee = ext_ids(rng, n)
    rows.add(acct[so_rep], sday, sample_seconds(rng, len(so_rep), hw), "out", so_payee[so_rep],
             so_total[so_rep], "ACH", "Normal_StandingOrder")

    # ---- one-off transfers out (some to other accounts in our data) ----------------
    rate = cfg.get("normal.transfers_out_per_month")
    k = per_window(rate, np.ones(n))
    pos = np.repeat(np.arange(n), k)
    tday = anywhere(pos, len(pos))
    tamt = lognormal_mean(rng, fp_total[pos] / rate, sig, len(pos))
    tsec = sample_seconds(rng, len(pos), hw)
    internal = rng.random(len(pos)) < cfg.get("normal.internal_share_of_transfers")
    recv = rng.integers(0, len(all_open), size=len(pos))
    internal &= (recv != acct[pos]) & (all_open[recv] <= tday) & (tday <= all_open[recv] + days - 1)
    ext = ~internal
    rows.add(acct[pos][ext], tday[ext], tsec[ext], "out", ext_ids(rng, ext.sum()), tamt[ext], "ACH",
             "Normal_Transfer")
    ii = np.flatnonzero(internal)
    pair = np.arange(len(ii)) + batch.attrs.get("pair_base", 0)
    cp_out = np.empty(len(ii), dtype=object); cp_out[:] = list(recv[ii])
    cp_in = np.empty(len(ii), dtype=object); cp_in[:] = list(acct[pos][ii])
    rows.add(acct[pos][ii], tday[ii], tsec[ii], "out", cp_out, tamt[ii], "ACH", "Normal_Transfer", pair=pair)
    rows.add(recv[ii], tday[ii], tsec[ii], "in", cp_in, tamt[ii], "ACH", "Normal_Transfer", pair=pair)

    # ---- transfers in from friends and family --------------------------------------
    k = per_window(cfg.get("normal.transfers_in_per_month"), np.ones(n))
    pos = np.repeat(np.arange(n), k)
    rows.add(acct[pos], anywhere(pos, len(pos)), sample_seconds(rng, len(pos), hw), "in",
             ext_ids(rng, len(pos)), lognormal_median(rng, cfg.get("normal.transfer_in_median"), cfg.get("normal.transfer_in_sigma"), len(pos)),
             "ACH", "Normal_TransferIn")

    # ---- cheques --------------------------------------------------------------------
    chq = cfg.get("normal.cheque_amount")
    k = per_window(cfg.get("normal.cheques_per_month"), np.ones(n))
    pos = np.repeat(np.arange(n), k)
    rows.add(acct[pos], anywhere(pos, len(pos)), sample_seconds(rng, len(pos), hw), "out",
             ext_ids(rng, len(pos)), lognormal_median(rng, chq["median"], chq["sigma"], len(pos)), "Cheque", "Normal_Cheque")

    # ---- cash withdrawals ------------------------------------------------------------
    cw = cfg.get("normal.cash_withdrawal_amount")
    k = per_window(cfg.get("normal.cash_withdrawals_per_month"), np.ones(n))
    pos = np.repeat(np.arange(n), k)
    amt = np.clip(np.round(lognormal_median(rng, cw["median"], cfg.get("normal.cash_withdrawal_sigma"), len(pos)) / 10) * 10, 10, cw["max"])
    rows.add(acct[pos], anywhere(pos, len(pos)), sample_seconds(rng, len(pos), hw), "out", "CASH",
             amt, "Cash Withdrawal", "Normal_CashWithdrawal")

    # ---- cash deposits (heavy cash users) and rare large cash deposits ----------------
    dep = rng.random(n) < cfg.get("normal.cash_depositor_share")
    k = per_window(cfg.get("normal.cash_deposits_per_month"), dep.astype(float))
    pos = np.repeat(np.arange(n), k)
    rows.add(acct[pos], anywhere(pos, len(pos)), sample_seconds(rng, len(pos), hw), "in", "CASH",
             lognormal_median(rng, cfg.get("normal.cash_deposit_median"), cfg.get("normal.cash_deposit_sigma"), len(pos)),
             "Cash Deposit", "Normal_CashDeposit")
    p_large = 1 - (1 - cfg.get("normal.large_cash_yearly_rate")) ** (days / 365.25)
    big = np.flatnonzero(rng.random(n) < p_large)
    rows.add(acct[big], anywhere(big, len(big)), sample_seconds(rng, len(big), hw), "in", "CASH",
             rng.uniform(*cfg.get("normal.large_cash_amount"), len(big)), "Cash Deposit", "Normal_LargeCash")

    # ---- money sent abroad ------------------------------------------------------------
    sender = rng.random(n) < cfg.get("normal.abroad_sender_share")
    k = per_window(cfg.get("normal.abroad_per_month"), sender.astype(float))
    pos = np.repeat(np.arange(n), k)
    hr = rng.random(len(pos)) < cfg.get("normal.high_risk_share_of_abroad")
    country = np.where(hr, rng.choice(cfg.get("countries.high_risk"), len(pos)),
                       rng.choice(cfg.get("countries.other_abroad"), len(pos)))
    rows.add(acct[pos], anywhere(pos, len(pos)), sample_seconds(rng, len(pos), hw), "out",
             ext_ids(rng, len(pos)), lognormal_median(rng, cfg.get("normal.abroad_median"), cfg.get("normal.abroad_sigma"), len(pos)),
             "Cross-border", "Normal_Abroad", rloc=country)

    # ---- group collections: several small payments in one week (normal.group_collection) ---
    gc = cfg.get("normal.group_collection")
    k = rng.poisson(cfg.get("normal.group_collection_yearly_rate") * days / 365.25, size=n)
    ev = np.repeat(np.arange(n), k)
    ev_day = anywhere(ev, len(ev))
    size = rng.integers(gc["payers"][0], gc["payers"][1] + 1, size=len(ev))
    pos = np.repeat(ev, size)
    gday = np.minimum(np.repeat(ev_day, size) + rng.integers(0, gc["spread_days"], size=len(pos)), o[pos] + days - 1)
    rows.add(acct[pos], gday, sample_seconds(rng, len(pos), hw), "in", ext_ids(rng, len(pos)),
             lognormal_median(rng, gc["median"], gc["sigma"], len(pos)), "ACH", "Normal_GroupCollection")
    return rows
