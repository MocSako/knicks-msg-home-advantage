# Knicks MSG Home Advantage Analysis

**Is Madison Square Garden truly one of the toughest arenas to play in?**

**Headline finding:** Across **3,713** Knicks games from **1983–2025**, New York won **58.2%** at home vs **38.5%** on the road — a **+19.7 percentage-point** home edge. When point differential is available, the Knicks average **+1.5** at MSG and **-3.3** away (~4.8 point swing).

A logistic regression that controls for rest days, a simple opponent-strength proxy, and season still assigns a strong positive weight to playing at home (**+0.77** log-odds; ~**+18.6 pp** predicted win-probability lift on the held-out test set; ROC AUC **0.62**).

Interactive report: [outputs/report.html](outputs/report.html) (also published via GitHub Pages when enabled).

## What's in this repo

| Path | Purpose |
| --- | --- |
| `src/fetch_knicks_data.py` | Pull regular-season + playoff games from the NBA Stats API (`nba_api`) into CSV |
| `data/knicks_games.csv` | Committed analysis dataset (3.7k games) |
| `sql/home_advantage.sql` | Home vs away, regular-season, decade, and season-edge queries |
| `src/analyze_sql.py` | Load CSV → SQLite and run the SQL pack |
| `src/train_model.py` | Logistic regression win model + coefficient export |
| `src/generate_visuals.py` | PNG charts + Plotly HTML report |
| `outputs/` | Findings JSON, charts, interactive report |

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Optional: refresh data from NBA Stats
python src/fetch_knicks_data.py

# Reproduce analysis
python src/analyze_sql.py
python src/train_model.py
python src/generate_visuals.py
```

Open `outputs/report.html` in a browser after generating visuals.

## Method notes

- **Source:** [nba_api](https://github.com/swar/nba_api) `LeagueGameFinder` for team `1610612752` (Knicks), regular season and playoffs.
- **Coverage:** NBA Stats returns Knicks games from the **1983** season onward in this endpoint (not the full 1979 three-point era). Point differential is missing for some earlier seasons; win/loss is complete.
- **Opponent strength proxy:** historical Knicks win rate against that opponent (inverted). This is a simple control, not a full SRS/Elo model.
- **balldontlie:** the original free v1 API is no longer usable without auth; the pipeline was migrated to `nba_api`.

## Roadmap

- Stronger opponent adjustment (Elo / net rating) instead of opponent-history proxy
- Travel / back-to-back features beyond rest-day caps
- Streamlit app for live filtering by era and opponent

## Tools

Python, pandas, SQLite/SQL, scikit-learn, matplotlib, Plotly, nba_api, Git/GitHub
