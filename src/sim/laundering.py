"""Step 5: plant laundering bursts on launderers, in 15 SAML-D shapes.

Each launderer gets one ~2-week burst from its start day. Its shape (drawn with SAML-D's
weights) decides who pays in (how many payers, transfer or cash), and how the money leaves
(how many receivers, transfers or cash withdrawals, how often abroad). Amounts are anchored to
RUSI's GBP 532 average and leave at RUSI's speed. Networked launderers pass some pieces to their
next network member, who forwards them on ("layered" shapes do this twice as often).
"""
from __future__ import annotations
import numpy as np
import pandas as pd

from .common import Rows, lognormal_mean, sample_seconds, ext_ids


def abroad_share(cfg):
    """Launderers' share of transfers sent abroad = SAML-D ratio x our normal accounts' share."""
    abroad = cfg.get("normal.abroad_sender_share") * cfg.get("normal.abroad_per_month")
    normal_share = abroad / (cfg.get("normal.transfers_out_per_month") + abroad)
    return min(1.0, cfg.get("laundering.abroad_ratio_vs_normal") * normal_share)


def _delays(rng, cfg, k):
    shares = cfg.get("laundering.forward_delay_shares")
    names = list(shares)
    bands = cfg.get("laundering.forward_delay_bands_minutes")
    pick = rng.choice(len(names), size=k, p=np.array(list(shares.values())) / sum(shares.values()))
    lo = np.array([bands[names[i]][0] for i in pick])
    hi = np.array([bands[names[i]][1] for i in pick])
    return rng.uniform(lo, hi) * 60  # seconds


def _destination(rng, cfg, k, p_abroad):
    cross = rng.random(k) < p_abroad
    hr = rng.random(k) < cfg.get("laundering.high_risk_share_of_cross_border")
    country = np.where(hr, rng.choice(cfg.get("countries.high_risk"), k),
                       rng.choice(cfg.get("countries.other_abroad"), k))
    return np.where(cross, country, "UK"), np.where(cross, "Cross-border", "ACH")


def _payers(rng, spec, k):
    if spec == "all":
        return ext_ids(rng, k)
    pool = ext_ids(rng, int(spec))
    return pool[rng.permutation(np.arange(k) % len(pool))]


def generate_laundering(cfg, truth: pd.DataFrame, internal: pd.DataFrame, open_day: np.ndarray,
                        rng: np.random.Generator, pair_base: int) -> tuple[Rows, dict]:
    rows = Rows()
    days = cfg.get("size.observe_days")
    hw = cfg.get("normal.hour_weights")
    shapes = cfg.get("laundering.shapes")
    names = list(shapes)
    weights = np.array([shapes[n]["weight"] for n in names], dtype=float)
    start = truth["launder_start_day"].fillna(-1).to_numpy().astype(int)
    successor = internal["successor"].to_numpy()
    burst = cfg.get("timing.burst_days")
    keep_lo, keep_hi = cfg.get("laundering.holder_keeps")
    pieces_mean = cfg.get("laundering.out_pieces_mean")
    out_mean = cfg.get("laundering.out_transfer_mean")
    base_internal = cfg.get("networks.internal_pieces_share")
    base_abroad = abroad_share(cfg)
    piece_sigma = cfg.get("laundering.piece_sigma")
    split_max = cfg.get("laundering.split_max_n_in")
    half_cash = cfg.get("laundering.half_cash_share")
    layered_x = cfg.get("laundering.layered_internal_multiplier")
    cash_piece_max = cfg.get("laundering.cash_out_piece_max")
    pair = pair_base
    shape_of = {}

    def end_sec(j):
        return (open_day[j] + days - 1) * 86400 + 86399

    def active(j, day):
        return j >= 0 and start[j] >= 0 and start[j] <= day <= open_day[j] + days - 1

    def add_out(acct, t_sec, amount, cp, ptype, rloc, label, pair_id=-1, link=-1):
        t_sec = np.minimum(np.asarray(t_sec, dtype=float), end_sec(acct))
        rows.add(np.full(len(t_sec), acct), (t_sec // 86400).astype(int), (t_sec % 86400).astype(int), "out",
                 cp, amount, ptype, label, rloc=rloc, is_l=1, pair=pair_id, link=link)

    for i in np.flatnonzero(start >= 0):
        name = names[rng.choice(len(names), p=weights / weights.sum())]
        sh = shapes[name]
        shape_of[i] = name
        lo, hi = sh["n_in"]
        many_small = hi > split_max
        k_in = int(rng.integers(lo, hi + 1))
        in_days = start[i] + np.sort(np.concatenate([[0], rng.integers(0, burst, size=k_in - 1)]))
        payers = _payers(rng, sh["senders"], k_in)
        receivers = ext_ids(rng, int(sh["recipients"]))
        piece_mean = out_mean * sh["amount_rel"]
        p_abroad = min(1.0, base_abroad * sh["abroad_rel"])
        p_internal = min(1.0, base_internal * (layered_x if sh["layered"] else 1))

        for e, d_in in enumerate(in_days):
            s_in = int(sample_seconds(rng, 1, hw)[0])
            n_p = 1 if many_small else 1 + rng.poisson(pieces_mean - 1)
            piece = lognormal_mean(rng, piece_mean, piece_sigma, n_p)
            keep = rng.uniform(keep_lo, keep_hi)
            amt_in = piece.sum() / (1 - keep)
            cash_in = sh["in_kind"] == "cash" or (sh["in_kind"] == "half_cash" and rng.random() < half_cash)
            rows.add([i], [d_in], [s_in], "in", "CASH" if cash_in else payers[e:e + 1], [amt_in],
                     "Cash Deposit" if cash_in else "ACH", name, is_l=1)
            t0 = d_in * 86400 + s_in

            if sh["out_kind"] == "cash_withdrawal":
                total = piece.sum()
                n_w = int(np.ceil(total / cash_piece_max))
                add_out(i, t0 + _delays(rng, cfg, n_w), np.full(n_w, total / n_w), "CASH",
                        "Cash Withdrawal", "UK", name)
                continue

            t_out = t0 + _delays(rng, cfg, n_p)
            rloc, ptype = _destination(rng, cfg, n_p, p_abroad)
            for p in range(n_p):
                o_day = int(min(t_out[p], end_sec(i)) // 86400)
                j = successor[i]
                if j >= 0 and rng.random() < p_internal and active(j, o_day):
                    # internal hop i -> j (both rows share one transfer id), then j forwards it on
                    t_p = min(t_out[p], end_sec(i))
                    cp_j = np.array([j], dtype=object)
                    cp_i = np.array([i], dtype=object)
                    add_out(i, [t_p], [piece[p]], cp_j, "ACH", "UK", name, pair_id=pair)
                    rows.add([j], [int(t_p // 86400)], [int(t_p % 86400)], "in", cp_i, [piece[p]], "ACH", name,
                             is_l=1, pair=pair)
                    keep_j = rng.uniform(keep_lo, keep_hi)
                    r2, p2 = _destination(rng, cfg, 1, p_abroad)
                    add_out(j, [t_p + _delays(rng, cfg, 1)[0]], [piece[p] * (1 - keep_j)], ext_ids(rng, 1),
                            p2, r2, name, link=pair)
                    pair += 1
                else:
                    cp = receivers[rng.integers(0, len(receivers)):][:1]
                    add_out(i, t_out[p:p + 1], piece[p:p + 1], cp, ptype[p:p + 1], rloc[p:p + 1], name)
    return rows, shape_of
