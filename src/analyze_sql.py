#!/usr/bin/env python3
"""Load knicks_games.csv into SQLite and run home-advantage SQL analytics."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd

DATA_PATH = Path("data/knicks_games.csv")
SQL_PATH = Path("sql/home_advantage.sql")
OUT_DIR = Path("outputs")
DB_PATH = OUT_DIR / "knicks.db"
FINDINGS_PATH = OUT_DIR / "sql_findings.json"


def split_statements(sql_text: str) -> list[str]:
    chunks: list[str] = []
    buf: list[str] = []
    for line in sql_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        buf.append(line)
        if stripped.endswith(";"):
            stmt = "\n".join(buf).strip().rstrip(";").strip()
            if stmt:
                chunks.append(stmt)
            buf = []
    return chunks


def main() -> None:
    if not DATA_PATH.exists():
        raise SystemExit(f"Missing {DATA_PATH}. Run: python src/fetch_knicks_data.py")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_PATH)

    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("games", conn, index=False, if_exists="replace")

    statements = split_statements(SQL_PATH.read_text(encoding="utf-8"))
    results = []
    for i, stmt in enumerate(statements, start=1):
        result_df = pd.read_sql_query(stmt, conn)
        print(f"\n=== Query {i} ===")
        print(result_df.to_string(index=False))
        results.append(
            {
                "query_index": i,
                "sql": stmt,
                "rows": json.loads(result_df.to_json(orient="records")),
            }
        )

    # Headline metrics for README / portfolio
    home = df[df["is_home"] == 1]
    away = df[df["is_home"] == 0]
    headline = {
        "games_count": int(len(df)),
        "season_min": int(df["season"].min()),
        "season_max": int(df["season"].max()),
        "home_win_pct": round(float(home["won"].mean()) * 100, 1),
        "away_win_pct": round(float(away["won"].mean()) * 100, 1),
        "home_edge_pp": round(
            float(home["won"].mean() - away["won"].mean()) * 100, 1
        ),
        "home_avg_point_diff": round(float(home["point_diff"].mean(skipna=True)), 2),
        "away_avg_point_diff": round(float(away["point_diff"].mean(skipna=True)), 2),
    }
    payload = {"headline": headline, "queries": results}
    FINDINGS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    conn.close()

    print("\nHeadline findings:")
    for k, v in headline.items():
        print(f"  {k}: {v}")
    print(f"\nWrote {FINDINGS_PATH} and {DB_PATH}")


if __name__ == "__main__":
    main()
