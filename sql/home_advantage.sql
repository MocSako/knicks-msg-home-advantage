-- Knicks MSG home-court advantage aggregates (SQLite)
-- Loaded from data/knicks_games.csv by src/analyze_sql.py

-- Overall home vs away win rate and scoring
SELECT
  CASE WHEN is_home = 1 THEN 'home' ELSE 'away' END AS location,
  COUNT(*) AS games,
  ROUND(AVG(won) * 100.0, 1) AS win_pct,
  ROUND(AVG(point_diff), 2) AS avg_point_diff,
  ROUND(AVG(knicks_score), 1) AS avg_knicks_score,
  ROUND(AVG(opponent_score), 1) AS avg_opponent_score
FROM games
GROUP BY is_home
ORDER BY is_home DESC;

-- Regular season only (cleaner competitive sample)
SELECT
  CASE WHEN is_home = 1 THEN 'home' ELSE 'away' END AS location,
  COUNT(*) AS games,
  ROUND(AVG(won) * 100.0, 1) AS win_pct,
  ROUND(AVG(point_diff), 2) AS avg_point_diff
FROM games
WHERE season_type = 'Regular Season'
GROUP BY is_home
ORDER BY is_home DESC;

-- Era trends (decade buckets)
SELECT
  (season / 10) * 10 AS decade,
  CASE WHEN is_home = 1 THEN 'home' ELSE 'away' END AS location,
  COUNT(*) AS games,
  ROUND(AVG(won) * 100.0, 1) AS win_pct,
  ROUND(AVG(point_diff), 2) AS avg_point_diff
FROM games
GROUP BY decade, is_home
ORDER BY decade, is_home DESC;

-- Home win-rate edge by season (home_win_pct - away_win_pct)
SELECT
  season,
  ROUND(100.0 * AVG(CASE WHEN is_home = 1 THEN won END), 1) AS home_win_pct,
  ROUND(100.0 * AVG(CASE WHEN is_home = 0 THEN won END), 1) AS away_win_pct,
  ROUND(
    100.0 * AVG(CASE WHEN is_home = 1 THEN won END)
    - 100.0 * AVG(CASE WHEN is_home = 0 THEN won END),
    1
  ) AS home_edge_pp
FROM games
WHERE season_type = 'Regular Season'
GROUP BY season
HAVING COUNT(*) >= 40
ORDER BY season;
