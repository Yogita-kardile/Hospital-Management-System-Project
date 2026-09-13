"""
run_all.py -- runs the full pipeline in order:
  1. generate_data.py   -> data/hospitals.csv
  2. create_database.py -> output/hospitals.db
  3. analysis.py         -> output/summary_*.csv
  4. ml_models.py         -> output/doctor_demand_model.joblib, hospital_clusters.csv
  5. visualize.py         -> output/chart_*.png
"""
import subprocess
import sys

STEPS = [
    "scripts/generate_data.py",
    "scripts/create_database.py",
    "scripts/analysis.py",
    "scripts/ml_models.py",
    "scripts/visualize.py",
]

for step in STEPS:
    print(f"\n{'='*60}\nRunning {step}\n{'='*60}")
    result = subprocess.run([sys.executable, step])
    if result.returncode != 0:
        print(f"Step {step} failed.")
        sys.exit(1)

print("\nPipeline complete. See the output/ folder for the database, CSVs, model, and charts.")
