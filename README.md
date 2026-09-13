# India Hospitals Database & ML Project

A complete Python pipeline: sample hospital dataset → SQLite database →
SQL/pandas analysis → machine learning (regression + clustering) → charts.

## ⚠️ About the data

There is no single official, downloadable file listing *every* hospital in
India with exact bed/doctor counts — real records are scattered across
state health departments, the National Health Profile, Ayushman Bharat
(PMJAY) empanelment data, and private directories. Public aggregate figures
(2025 estimates) put India at roughly **70,000 hospitals** (~26,000
government + ~43,500 private), led by Uttar Pradesh, Maharashtra, Tamil
Nadu, and Karnataka.

This project ships with a **realistic sample dataset** (139 hospitals
across 25 major cities, 3 city tiers, 20 specializations) so the entire
pipeline runs end-to-end out of the box. **To use real data**, replace the
CSV produced by `scripts/generate_data.py` with your own data (same
columns), then re-run steps 2–5 — nothing else needs to change.

## Project structure

```
hospital_project/
├── scripts/
│   ├── generate_data.py    # builds data/hospitals.csv (swap this for real data)
│   ├── create_database.py  # builds output/hospitals.db (normalized SQLite)
│   ├── analysis.py         # SQL/pandas summaries -> output/summary_*.csv
│   ├── ml_models.py        # regression + clustering -> output/*.joblib, *.csv
│   └── visualize.py        # charts -> output/chart_*.png
├── data/hospitals.csv      # generated sample data
├── output/                 # database, CSVs, trained model, charts
├── run_all.py               # runs the full pipeline in one command
└── requirements.txt
```

## Database schema (SQLite, `output/hospitals.db`)

- **hospitals** — hospital_id, name, city, state, city_tier, hospital_type
  (Government/Private/Trust), beds, doctors, established_year, rating
- **specializations** — spec_id, spec_name (20 medical specializations)
- **hospital_specializations** — many-to-many junction table

## Analysis (`scripts/analysis.py`)

Answers exactly the questions asked:
- Total hospitals, beds, doctors nationwide
- Breakdown by city and by state
- Breakdown by specialization (how many hospitals offer each)
- Breakdown by hospital type
- Doctor-to-bed ratio per city

## Machine learning (`scripts/ml_models.py`)

1. **Regression (Random Forest)** — predicts how many doctors a hospital
   needs based on its bed count, city tier, hospital type, and founding
   year. Reports MAE and R², and saves the trained model
   (`output/doctor_demand_model.joblib`) so you can reuse it.
2. **Clustering (KMeans)** — groups hospitals into 4 natural capability
   tiers (Small/Community → Mega/Super-Specialty) based on beds, doctors,
   and specialization count. Useful for spotting hospitals that are
   under- or over-staffed relative to peers of similar size.

## Running it

```bash
pip install -r requirements.txt
python run_all.py
```

Or run each script individually in order (see `run_all.py` for the
sequence). All outputs land in `output/`.

## Launching the dashboard

Once `run_all.py` has been run at least once (so `output/hospitals.db` and
`output/doctor_demand_model.joblib` exist), launch the Streamlit app:

```bash
streamlit run app.py
```

This opens an interactive dashboard in your browser with:
- Filters by state, city, hospital type, specialization, and bed range
- A searchable/sortable hospital table with CSV download
- City-wise and specialization-wise charts
- A live form to predict doctors needed, using the trained regression model
