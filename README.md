# Hospital Management System – India Hospitals Database & ML Project

## Project Description

Developed a Python-based hospital data management and analysis system using SQLite, SQL, Pandas, and Machine Learning. Implemented hospital data analysis, visualizations, doctor demand prediction using Random Forest, and hospital clustering using KMeans. Created an interactive Streamlit dashboard for exploring hospital data.

## Technologies Used

- Python
- SQL
- SQLite
- Pandas
- Scikit-learn
- Matplotlib
- Streamlit
- Joblib

## Key Features

- Hospital data management and analysis
- SQL and Pandas-based analysis
- Data visualization
- Doctor demand prediction using Random Forest
- Hospital clustering using KMeans
- Interactive Streamlit dashboard
- CSV data download

 
## Project Structure

```text
hospital_project/
├── scripts/
│   ├── generate_data.py
│   ├── create_database.py
│   ├── analysis.py
│   ├── ml_models.py
│   └── visualize.py
├── data/
│   └── hospitals.csv
├── output/
├── run_all.py
├── app.py
└── requirements.txt
```

## Database Schema

The project uses a SQLite database (`output/hospitals.db`) with the following tables:

* **hospitals** — hospital ID, name, city, state, city tier, hospital type, beds, doctors, established year, and rating
* **specializations** — specialization ID and specialization name
* **hospital_specializations** — connects hospitals with their medical specializations

## Data Analysis

The project performs SQL and Pandas-based analysis to find:

* Total hospitals, beds, and doctors
* Hospital distribution by city and state
* Hospitals by medical specialization
* Hospital distribution by type
* Doctor-to-bed ratio by city


## Machine Learning

The project uses two machine learning techniques:

1. **Random Forest Regression** — predicts the required number of doctors based on hospital beds, city tier, hospital type, and established year.

2. **KMeans Clustering** — groups hospitals based on beds, doctors, and number of specializations to identify different hospital capability levels.

## Running the Project

Install the required libraries:

```bash
pip install -r requirements.txt
```

Run the complete project:

```bash
python run_all.py
```

The generated database, analysis results, machine learning models, and charts are saved in the `output/` folder.


## Launching the Dashboard

After running the project, start the Streamlit dashboard:

```bash
streamlit run app.py
```

The dashboard provides:

* Filters for state, city, hospital type, specialization, and bed range
* Searchable hospital data with CSV download
* City-wise and specialization-wise charts
* Doctor demand prediction using the trained Random Forest model


## Project Outcome

This project demonstrates practical knowledge of Python, SQL, data analysis, machine learning, data visualization, and Streamlit dashboard development using hospital data.
