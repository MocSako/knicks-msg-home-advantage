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
