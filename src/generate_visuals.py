#!/usr/bin/env python3
"""Generate static charts + an interactive Plotly HTML report."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

DATA_PATH = Path("data/knicks_games.csv")
OUT_DIR = Path("outputs")
SQL_FINDINGS = OUT_DIR / "sql_findings.json"
MODEL_FINDINGS = OUT_DIR / "model_findings.json"


def style_matplotlib() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#333333",
            "axes.labelcolor": "#222222",
            "text.color": "#222222",
            "xtick.color": "#333333",
            "ytick.color": "#333333",
            "font.size": 11,
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
        }
    )


def chart_home_vs_away(df: pd.DataFrame) -> Path:
    home = df[df["is_home"] == 1]["won"].mean() * 100
    away = df[df["is_home"] == 0]["won"].mean() * 100
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(["Home (MSG)", "Away"], [home, away], color=["#006BB6", "#F58426"])
    ax.set_ylabel("Win rate (%)")
    ax.set_title("Knicks win rate: home vs away")
    ax.set_ylim(0, 100)
    for bar, val in zip(bars, [home, away], strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            val + 2,
            f"{val:.1f}%",
            ha="center",
            va="bottom",
            fontweight="bold",
        )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    path = OUT_DIR / "home_vs_away.png"
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def chart_era_trends(df: pd.DataFrame) -> Path:
    tmp = df.copy()
    tmp["decade"] = (tmp["season"] // 10) * 10
    grouped = (
        tmp.groupby(["decade", "is_home"], as_index=False)["won"]
        .mean()
        .assign(win_pct=lambda d: d["won"] * 100)
    )
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for is_home, label, color in (
        (1, "Home", "#006BB6"),
        (0, "Away", "#F58426"),
    ):
        subset = grouped[grouped["is_home"] == is_home]
        ax.plot(subset["decade"], subset["win_pct"], marker="o", label=label, color=color)
    ax.set_xlabel("Decade")
    ax.set_ylabel("Win rate (%)")
    ax.set_title("Knicks home vs away win rate by decade")
    ax.legend()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    path = OUT_DIR / "era_trends.png"
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def chart_feature_importance() -> Path | None:
    if not MODEL_FINDINGS.exists():
        return None
    findings = json.loads(MODEL_FINDINGS.read_text(encoding="utf-8"))
    coefs = findings["coefficients"]
    names = list(coefs.keys())
    values = [coefs[n] for n in names]
    colors = ["#006BB6" if v >= 0 else "#F58426" for v in values]

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.barh(names, values, color=colors)
    ax.axvline(0, color="#666666", linewidth=1)
    ax.set_xlabel("Logistic regression coefficient")
    ax.set_title("Win-probability model coefficients")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    path = OUT_DIR / "feature_importance.png"
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def build_plotly_report(df: pd.DataFrame) -> Path:
    headline = {}
    if SQL_FINDINGS.exists():
        headline = json.loads(SQL_FINDINGS.read_text(encoding="utf-8")).get("headline", {})
    model = {}
    if MODEL_FINDINGS.exists():
        model = json.loads(MODEL_FINDINGS.read_text(encoding="utf-8"))

    season = (
        df[df["season_type"] == "Regular Season"]
        .groupby(["season", "is_home"], as_index=False)["won"]
        .mean()
    )
    home = season[season["is_home"] == 1]
    away = season[season["is_home"] == 0]
    merged = home.merge(away, on="season", suffixes=("_home", "_away"))
    merged["edge_pp"] = (merged["won_home"] - merged["won_away"]) * 100

    fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=(
            "Regular-season win rate by season",
            "Home win-rate edge (percentage points)",
        ),
        vertical_spacing=0.12,
    )
    fig.add_trace(
        go.Scatter(
            x=home["season"],
            y=home["won"] * 100,
            name="Home",
            line=dict(color="#006BB6"),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=away["season"],
            y=away["won"] * 100,
            name="Away",
            line=dict(color="#F58426"),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=merged["season"],
            y=merged["edge_pp"],
            name="Home edge (pp)",
            marker_color="#006BB6",
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    title_bits = ["Knicks MSG Home Advantage"]
    if headline:
        title_bits.append(
            f"Home {headline.get('home_win_pct')}% vs Away {headline.get('away_win_pct')}% "
            f"(+{headline.get('home_edge_pp')} pp)"
        )
    if model:
        title_bits.append(
            f"Model AUC {model.get('roc_auc')} · home lift {model.get('home_probability_lift')}"
        )

    fig.update_layout(
        title="<br>".join(title_bits),
        height=720,
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    fig.update_yaxes(title_text="Win %", row=1, col=1)
    fig.update_yaxes(title_text="Edge (pp)", row=2, col=1)
    fig.update_xaxes(title_text="Season", row=2, col=1)

    path = OUT_DIR / "report.html"
    fig.write_html(path, include_plotlyjs="cdn")
    return path


def main() -> None:
    if not DATA_PATH.exists():
        raise SystemExit(f"Missing {DATA_PATH}. Run: python src/fetch_knicks_data.py")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    style_matplotlib()
    df = pd.read_csv(DATA_PATH)

    paths = [
        chart_home_vs_away(df),
        chart_era_trends(df),
        chart_feature_importance(),
        build_plotly_report(df),
    ]
    for path in paths:
        if path:
            print(f"Wrote {path}")


if __name__ == "__main__":
    main()
