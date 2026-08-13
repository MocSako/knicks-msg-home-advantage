#!/usr/bin/env python3
"""Logistic regression: Knicks win probability with home court + controls."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

DATA_PATH = Path("data/knicks_games.csv")
OUT_DIR = Path("outputs")
MODEL_FINDINGS = OUT_DIR / "model_findings.json"


def opponent_strength(df: pd.DataFrame) -> pd.Series:
    """Proxy: opponent's historical win rate against the Knicks (leave-one-out-ish via expand)."""
    # Simpler stable proxy: share of Knicks losses vs that opponent over the full sample
    opp_win_vs_knicks = 1 - df.groupby("opponent")["won"].transform("mean")
    return opp_win_vs_knicks


def main() -> None:
    if not DATA_PATH.exists():
        raise SystemExit(f"Missing {DATA_PATH}. Run: python src/fetch_knicks_data.py")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_PATH)
    # Prefer regular season for cleaner modeling sample
    model_df = df[df["season_type"] == "Regular Season"].copy()
    model_df["opp_strength"] = opponent_strength(model_df)

    features = ["is_home", "rest_days", "opp_strength", "season"]
    X = model_df[features]
    y = model_df["won"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    numeric = ["rest_days", "opp_strength", "season"]
    binary = ["is_home"]

    pre = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric,
            ),
            ("bin", "passthrough", binary),
        ]
    )

    clf = Pipeline(
        steps=[
            ("pre", pre),
            (
                "model",
                LogisticRegression(max_iter=1000, random_state=42),
            ),
        ]
    )
    clf.fit(X_train, y_train)
    proba = clf.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)

    model: LogisticRegression = clf.named_steps["model"]
    # Column order after ColumnTransformer: numeric then binary
    coef_names = numeric + binary
    coefficients = {
        name: round(float(coef), 4)
        for name, coef in zip(coef_names, model.coef_[0], strict=True)
    }

    # Marginal home effect: average predicted win prob home vs away on test fold
    X_home = X_test.copy()
    X_away = X_test.copy()
    X_home["is_home"] = 1
    X_away["is_home"] = 0
    home_lift = float(
        clf.predict_proba(X_home)[:, 1].mean() - clf.predict_proba(X_away)[:, 1].mean()
    )

    findings = {
        "sample_size": int(len(model_df)),
        "train_size": int(len(X_train)),
        "test_size": int(len(X_test)),
        "accuracy": round(float(accuracy_score(y_test, pred)), 3),
        "roc_auc": round(float(roc_auc_score(y_test, proba)), 3),
        "coefficients": coefficients,
        "home_probability_lift": round(home_lift, 3),
        "interpretation": (
            "Positive is_home coefficient means higher win log-odds at MSG after "
            "controlling for rest days, opponent strength proxy, and season."
        ),
    }
    MODEL_FINDINGS.write_text(json.dumps(findings, indent=2), encoding="utf-8")
    print(json.dumps(findings, indent=2))
    print(f"\nWrote {MODEL_FINDINGS}")


if __name__ == "__main__":
    main()
