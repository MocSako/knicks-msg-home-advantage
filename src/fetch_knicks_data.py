#!/usr/bin/env python3
"""Download Knicks game results from the NBA Stats API via nba_api."""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder

TEAM_ID = 1610612752  # New York Knicks
DEFAULT_OUT = Path("data/knicks_games.csv")


def fetch_games(season_type: str) -> pd.DataFrame:
    gf = leaguegamefinder.LeagueGameFinder(
        team_id_nullable=TEAM_ID,
        season_type_nullable=season_type,
    )
    df = gf.get_data_frames()[0]
    df["season_type"] = season_type
    return df


def build_dataset(start_season: int = 1979) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for season_type in ("Regular Season", "Playoffs"):
        frames.append(fetch_games(season_type))
        time.sleep(0.8)

    raw = pd.concat(frames, ignore_index=True)
    raw = raw.dropna(subset=["WL", "PTS"]).copy()

    raw["season"] = raw["SEASON_ID"].astype(str).str[-4:].astype(int)
    raw["date"] = pd.to_datetime(raw["GAME_DATE"])
    raw["is_home"] = raw["MATCHUP"].str.contains(r"vs\.", regex=True)
    raw["opponent"] = raw["MATCHUP"].str.replace(r"^NYK\s+(vs\.|@)\s+", "", regex=True)
    raw["knicks_score"] = raw["PTS"].astype(int)
    raw["opponent_score"] = (raw["PTS"] - raw["PLUS_MINUS"]).round()
    raw["won"] = (raw["WL"] == "W").astype(int)
    raw["point_diff"] = raw["PLUS_MINUS"]

    raw = raw.sort_values("date").reset_index(drop=True)
    raw["rest_days"] = raw.groupby("season_type")["date"].diff().dt.days
    raw.loc[raw["rest_days"] > 14, "rest_days"] = pd.NA

    clean = pd.DataFrame(
        {
            "game_id": raw["GAME_ID"],
            "date": raw["date"].dt.strftime("%Y-%m-%d"),
            "season": raw["season"],
            "season_type": raw["season_type"],
            "matchup": raw["MATCHUP"],
            "is_home": raw["is_home"].astype(int),
            "opponent": raw["opponent"],
            "knicks_score": raw["knicks_score"],
            "opponent_score": raw["opponent_score"],
            "point_diff": raw["point_diff"],
            "won": raw["won"],
            "rest_days": raw["rest_days"],
        }
    )
    return clean[clean["season"] >= start_season].sort_values("date").reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-season", type=int, default=1979)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    df = build_dataset(start_season=args.start_season)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"Wrote {len(df)} games ({df['season'].min()}–{df['season'].max()}) → {args.out}")


if __name__ == "__main__":
    main()
