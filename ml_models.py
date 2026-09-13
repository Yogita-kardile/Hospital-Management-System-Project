"""
ml_models.py
------------
Two ML components on top of the hospital database:

1. REGRESSION: predict how many doctors a hospital needs, given its beds,
   number of specializations, city tier, and hospital type.
   (RandomForestRegressor, with train/test split + evaluation)

2. CLUSTERING: group hospitals into natural size/capability tiers using
   KMeans on beds, doctors, and specialization count -- useful for spotting
   under- or over-staffed hospitals relative to their peers.

Run after generate_data.py and create_database.py.
"""

import sqlite3
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = str(PROJECT_DIR / "output" / "hospitals.db")
OUT_DIR = str(PROJECT_DIR / "output")


def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT h.*, COUNT(hs.spec_id) AS num_specializations
        FROM hospitals h
        LEFT JOIN hospital_specializations hs ON hs.hospital_id = h.hospital_id
        GROUP BY h.hospital_id
    """, conn)
    conn.close()
    return df


# ---------------------------------------------------------------------
# 1. REGRESSION -- predict doctors needed
# ---------------------------------------------------------------------
def run_regression(df: pd.DataFrame):
    features = ["beds", "city_tier", "hospital_type", "established_year"]
    target = "doctors"

    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    categorical = ["city_tier", "hospital_type"]
    numeric = ["beds", "established_year"]

    preprocessor = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ("num", "passthrough", numeric),
    ])

    model = Pipeline([
        ("prep", preprocessor),
        ("rf", RandomForestRegressor(n_estimators=300, random_state=42, max_depth=8)),
    ])

    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    print("=== Regression: Predicting Doctor Requirement ===")
    print(f"  Mean Absolute Error: {mae:.1f} doctors")
    print(f"  R^2 score: {r2:.3f}")

    # feature importance (approx, via permutation on the RF step is more
    # correct, but for a quick view we use the RF's built-in importances)
    rf = model.named_steps["rf"]
    feature_names = model.named_steps["prep"].get_feature_names_out()
    importances = pd.Series(rf.feature_importances_, index=feature_names).sort_values(ascending=False)
    print("\n  Top feature importances:")
    print(importances.head(6).to_string())

    joblib.dump(model, f"{OUT_DIR}/doctor_demand_model.joblib")
    print(f"\n  Model saved to {OUT_DIR}/doctor_demand_model.joblib")

    # Example prediction
    example = pd.DataFrame([{
        "beds": 300, "city_tier": "Tier 2", "hospital_type": "Private",
        "established_year": 2015,
    }])
    example_pred = model.predict(example)[0]
    print(f"\n  Example: a 300-bed private Tier-2 hospital -> "
          f"predicted doctors needed ~= {example_pred:.0f}")

    return model


# ---------------------------------------------------------------------
# 2. CLUSTERING -- group hospitals into capability tiers
# ---------------------------------------------------------------------
def run_clustering(df: pd.DataFrame, k: int = 4):
    features = ["beds", "doctors", "num_specializations"]
    X = df[features]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    df = df.copy()
    df["cluster"] = kmeans.fit_predict(X_scaled)

    cluster_summary = df.groupby("cluster")[features].mean().round(1)
    cluster_summary["num_hospitals"] = df["cluster"].value_counts().sort_index()

    # Label clusters by average bed count (small -> large)
    order = cluster_summary["beds"].sort_values().index
    labels = ["Small / Community", "Medium", "Large", "Mega / Super-Specialty"][:k]
    label_map = dict(zip(order, labels))
    df["tier_label"] = df["cluster"].map(label_map)
    cluster_summary["tier_label"] = cluster_summary.index.map(label_map)

    print("\n=== Clustering: Hospital Capability Tiers (KMeans, k={}) ===".format(k))
    print(cluster_summary.sort_values("beds").to_string())

    df[["hospital_id", "hospital_name", "city", "beds", "doctors",
        "num_specializations", "tier_label"]].to_csv(
        f"{OUT_DIR}/hospital_clusters.csv", index=False
    )
    print(f"\n  Cluster assignments saved to {OUT_DIR}/hospital_clusters.csv")

    return df


if __name__ == "__main__":
    df = load_data()
    run_regression(df)
    run_clustering(df)
