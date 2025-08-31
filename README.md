# Knicks MSG Home Advantage Analysis 🏀

**Is Madison Square Garden truly one of the toughest arenas to play in?**

This project builds a comprehensive dataset of New York Knicks games from the start of the three-point era (1979) through the present to quantify how much advantage the Knicks receive when playing at home. The repository demonstrates data engineering, SQL analytics, and machine learning.

## 📊 Project Highlights
- **Full season coverage:** 45+ years of regular season and playoff games.
- **Reproducible data pipeline:** `src/fetch_knicks_data.py` downloads raw game results from the [balldontlie API](https://www.balldontlie.io/).
- **Exploratory SQL analysis:** Load the raw CSV into SQLite and aggregate home vs. away performance, point differential, and era-to-era trends.
- **Predictive modeling:** Use Python, pandas, and scikit-learn to model win probability, controlling for opponent strength, rest days, and location.
- **Interactive visuals:** Build dashboards with Plotly or Streamlit to showcase the Garden's impact.

## 🛠️ Tools Used
- **Python 3.11** – scripting and analysis
- **balldontlie API** – open NBA game data
- **pandas** – data wrangling (install locally)
- **SQLite / SQL** – data storage and queries
- **Jupyter Notebook** – iterative exploration
- **Plotly / Matplotlib** – visualizations
- **scikit-learn** – logistic regression & feature importance
- **Git & GitHub** – version control and collaboration

## 🚀 Getting Started
1. **Fetch data**
   ```bash
   python src/fetch_knicks_data.py 1979 2024
   ```
   This creates `data/knicks_games.csv`. It is ignored in git due to size; a two-row `data/sample_knicks_games.csv` illustrates the schema.

2. **Load into SQLite**
   ```bash
   sqlite3 knicks.db
   .mode csv
   .import data/knicks_games.csv games
   ```

3. **Run SQL analysis**
   Calculate home vs. away win percentage:
   ```sql
   SELECT 
       CASE WHEN home_team = 'NYK' THEN 'Home' ELSE 'Away' END AS location,
       AVG(CASE WHEN (home_team = 'NYK' AND home_score > visitor_score) \
                 OR (visitor_team = 'NYK' AND visitor_score > home_score) \
                THEN 1 ELSE 0 END) AS win_pct
   FROM games
   GROUP BY location;
   ```

4. **Modeling & Visualization**
   Use pandas and scikit-learn within notebooks to build models and Plotly/Streamlit dashboards.

## ⭐ Why it stands out
- Demonstrates an end-to-end analytics workflow: data acquisition, storage, analysis, modeling, and visualization.
- Highlights proficiency in Python, SQL, machine learning, and storytelling through data.
- Provides a reusable template for analyzing home-court advantage for any team or sport.

## 📁 Repository Structure
```
.
├── src/                # Data acquisition scripts
├── data/               # Sample data and generated CSV (ignored)
├── README.md           # Project overview and instructions
├── .gitignore
```

---
This repository serves as a strong portfolio piece to discuss data engineering, statistical analysis, and visualization in sports analytics.
