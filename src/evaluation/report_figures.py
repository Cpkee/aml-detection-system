"""Figures for the final report, drawn only from committed result files (no data folder needed).

  PYTHONPATH=src python -m evaluation.report_figures      -> outputs/modelling/report_figures/

Figure 4.3B: share of the test cohort's mules already flagged, by week since opening, model against the rules at
the rules' weekly budget (final test, months 6-7, weeks 0-26; outputs/modelling/results/v1_full/final_test/
weekly_w26.csv), with the share of those mules whose laundering has started as a reference line.
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

SRC = "outputs/modelling/results/v1_full/final_test/weekly_w26.csv"
OUT = "outputs/modelling/report_figures"
INK, MUTED, GRID = "#0b0b0b", "#898781", "#e1e0d9"
MODEL, RULES = "#2a78d6", "#e34948"            # the colours of the project's other report figures


def catch_by_week(src: str = SRC, out: str = OUT) -> str:
    w = pd.read_csv(src)
    w["started_share"] = w["started"] / w["mules"]
    plt.rcParams.update({"font.family": "Times New Roman", "font.size": 9, "axes.edgecolor": MUTED,
                         "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK})
    fig, ax = plt.subplots(figsize=(6.3, 2.6))
    ax.plot(w["week"], 100 * w["started_share"], color=MUTED, lw=1.2, ls=(0, (4, 3)),
            label="Mules whose laundering has started")
    ax.plot(w["week"], 100 * w["catch_model"], color=MODEL, lw=2, label="Model (flagged)")
    ax.plot(w["week"], 100 * w["catch_rules"], color=RULES, lw=2, label="Bank's rules (alerted)")
    last = w.iloc[-1]
    for col, colour in (("catch_model", MODEL), ("catch_rules", RULES)):
        ax.plot(last["week"], 100 * last[col], "o", ms=4.5, color=colour, mec="white", mew=1)
        ax.annotate(f"{100 * last[col]:.1f}%", (last["week"], 100 * last[col]), xytext=(6, 0),
                    textcoords="offset points", va="center", fontsize=9, color=INK)
    ax.set(xlim=(0, 26), ylim=(0, 104), xlabel="Week since the account opened",
           ylabel="Share of mules by this week (%)")
    ax.set_yticks(range(0, 101, 20))
    ax.set_xticks(range(0, 27, 2))
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="upper left", fontsize=8.5)
    fig.tight_layout()
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "fig_4_3b_catch_by_week.png")
    fig.savefig(path, dpi=300)
    plt.close(fig)
    return path


if __name__ == "__main__":
    print(catch_by_week())
