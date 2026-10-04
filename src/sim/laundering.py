"""Step 5: plant laundering bursts on launderers (v0: one Fan_In-style pattern).

Each launderer gets one ~2-week burst from its start day: 3-4 payments come in from
outside victims, and each is split into ~2 transfers that leave within minutes to days
(RUSI timing). Networked launderers send part of the money to their next network member,
who forwards it on.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

from .common import Rows, lognormal_mean, sample_seconds, ext_ids

DELAY_BANDS = {  # minutes
    "under_15min": (1, 15), "15_to_60min": (15, 60), "1_to_24h": (60, 1440), "over_24h": (1440, 7 * 1440),
}


def _delays(rng, cfg, k):
    shares = cfg.get("laundering.forward_delay_shares")
    names = list(shares)
    pick = rng.choice(len(names), size=k, p=np.array(list(shares.values())) / sum(shares.values()))
    lo = np.array([DELAY_BANDS[names[i]][0] for i in pick])
    hi = np.array([DELAY_BANDS[names[i]][1] for i in pick])
    return rng.uniform(lo, hi) * 60  # seconds


def _destination(rng, cfg, k):
    cross = rng.random(k) < cfg.get("laundering.cross_border_share_out")
    hr = rng.random(k) < cfg.get("laundering.high_risk_share_of_cross_border")
    country = np.where(hr, rng.choice(cfg.get("countries.high_risk"), k),
                       rng.choice(cfg.get("countries.other_abroad"), k))
    rloc = np.where(cross, country, "UK")
    ptype = np.where(cross, "Cross-border", "ACH")
    return rloc, ptype


def generate_laundering(cfg, truth: pd.DataFrame, internal: pd.DataFrame, open_day: np.ndarray,
                        rng: np.random.Generator, pair_base: int) -> Rows:
    rows = Rows()
    days = cfg.get("size.observe_days")
    hw = cfg.get("normal.hour_weights")
    label = cfg.get("laundering.patterns")[0]
    start = truth["launder_start_day"].fillna(-1).to_numpy().astype(int)
    successor = internal["successor"].to_numpy()
    lmin, lmax = cfg.get("timing.incoming_per_burst")
    burst = cfg.get("timing.burst_days")
    keep_lo, keep_hi = cfg.get("laundering.holder_keeps")
    pieces_mean = cfg.get("laundering.out_pieces_mean")
    out_mean = cfg.get("laundering.out_transfer_mean")
    share_internal = cfg.get("networks.internal_pieces_share")
    pair = pair_base

    def active(j, day):
        return j >= 0 and start[j] >= 0 and start[j] <= day <= open_day[j] + days - 1

    for i in np.flatnonzero(start >= 0):
        k_in = int(rng.integers(lmin, lmax + 1))
        in_days = start[i] + np.sort(np.concatenate([[0], rng.integers(0, burst, size=k_in - 1)]))
        for d_in in in_days:
            s_in = int(sample_seconds(rng, 1, hw)[0])
            n_p = 1 + rng.poisson(pieces_mean - 1)
            piece = lognormal_mean(rng, out_mean, 0.6, n_p)
            keep = rng.uniform(keep_lo, keep_hi)
            amt_in = piece.sum() / (1 - keep)
            rows.add([i], [d_in], [s_in], "in", ext_ids(rng, 1), [amt_in], "ACH", label, is_l=1)
            t_out = d_in * 86400 + s_in + _delays(rng, cfg, n_p)
            t_out = np.minimum(t_out, (open_day[i] + days - 1) * 86400 + 86399)
            o_day, o_sec = (t_out // 86400).astype(int), (t_out % 86400).astype(int)
            rloc, ptype = _destination(rng, cfg, n_p)
            for p in range(n_p):
                j = successor[i]
                if j >= 0 and rng.random() < share_internal and active(j, o_day[p]):
                    # internal hop: i -> j, then j forwards it out after its own delay
                    rows.add([i], [o_day[p]], [o_sec[p]], "out", np.array([j], dtype=object), [piece[p]],
                             "ACH", label, is_l=1, pair=pair)
                    rows.add([j], [o_day[p]], [o_sec[p]], "in", np.array([i], dtype=object), [piece[p]],
                             "ACH", label, is_l=1, pair=pair)
                    pair += 1
                    t2 = o_day[p] * 86400 + o_sec[p] + _delays(rng, cfg, 1)[0]
                    t2 = min(t2, (open_day[j] + days - 1) * 86400 + 86399)
                    keep_j = rng.uniform(keep_lo, keep_hi)
                    r2, p2 = _destination(rng, cfg, 1)
                    rows.add([j], [int(t2 // 86400)], [int(t2 % 86400)], "out", ext_ids(rng, 1),
                             [piece[p] * (1 - keep_j)], p2, label, rloc=r2, is_l=1)
                else:
                    rows.add([i], [o_day[p]], [o_sec[p]], "out", ext_ids(rng, 1), [piece[p]],
                             ptype[p], label, rloc=rloc[p:p + 1], is_l=1)
    return rows
