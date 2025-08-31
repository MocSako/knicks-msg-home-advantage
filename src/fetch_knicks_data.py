#!/usr/bin/env python3
"""Download Knicks game results from the free balldontlie API."""
from __future__ import annotations
import csv
import json
import sys
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import urlopen

TEAM_ID = 20  # New York Knicks ID on balldontlie
BASE_URL = "https://www.balldontlie.io/api/v1/games"


def fetch_season(season: int):
    """Yield all Knicks games for a given season."""
    page = 1
    while True:
        params = {
            "team_ids[]": TEAM_ID,
            "seasons[]": season,
            "per_page": 100,
            "page": page,
        }
        url = BASE_URL + "?" + urlencode(params)
        with urlopen(url) as resp:
            data = json.load(resp)
        for game in data["data"]:
            yield game
        if page >= data["meta"]["total_pages"]:
            break
        page += 1

def main(start_season: int = 1979, end_season: int | None = None, out_path: str = "data/knicks_games.csv"):
    if end_season is None:
        end_season = datetime.now().year
    fieldnames = [
        "id",
        "date",
        "season",
        "home_team",
        "home_score",
        "visitor_team",
        "visitor_score",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for season in range(start_season, end_season + 1):
            for game in fetch_season(season):
                writer.writerow(
                    {
                        "id": game["id"],
                        "date": game["date"][:10],
                        "season": game["season"],
                        "home_team": game["home_team"]["abbreviation"],
                        "home_score": game["home_team_score"],
                        "visitor_team": game["visitor_team"]["abbreviation"],
                        "visitor_score": game["visitor_team_score"],
                    }
                )

if __name__ == "__main__":
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1979
    end = int(sys.argv[2]) if len(sys.argv) > 2 else None
    main(start, end)
