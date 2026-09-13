"""
analysis.py
-----------
Queries the SQLite database to answer the core questions:
  - How many hospitals, in which city?
  - How many beds per city/hospital?
  - How many doctors per city/hospital?
  - Which specializations are available, and how common are they?

Outputs summary CSVs to output/ and prints headline numbers.
"""

import sqlite3
import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = str(PROJECT_DIR / "output" / "hospitals.db")
OUT_DIR = str(PROJECT_DIR / "output")


def q(conn, sql):
    return pd.read_sql_query(sql, conn)


def main():
    conn = sqlite3.connect(DB_PATH)

    # 1. National totals
    totals = q(conn, """
        SELECT COUNT(*) AS total_hospitals,
               SUM(beds) AS total_beds,
               SUM(doctors) AS total_doctors
        FROM hospitals;
    """)
    print("=== National Totals (sample dataset) ===")
    print(totals.to_string(index=False))

    # 2. Per-city breakdown
    per_city = q(conn, """
        SELECT city, state,
               COUNT(*) AS num_hospitals,
               SUM(beds) AS total_beds,
               SUM(doctors) AS total_doctors,
               ROUND(AVG(beds), 1) AS avg_beds_per_hospital,
               ROUND(AVG(rating), 2) AS avg_rating
        FROM hospitals
        GROUP BY city, state
        ORDER BY num_hospitals DESC, total_beds DESC;
    """)
    per_city.to_csv(f"{OUT_DIR}/summary_by_city.csv", index=False)
    print("\n=== Hospitals / Beds / Doctors by City (top 10) ===")
    print(per_city.head(10).to_string(index=False))

    # 3. Per-state rollup
    per_state = q(conn, """
        SELECT state,
               COUNT(*) AS num_hospitals,
               SUM(beds) AS total_beds,
               SUM(doctors) AS total_doctors
        FROM hospitals
        GROUP BY state
        ORDER BY num_hospitals DESC;
    """)
    per_state.to_csv(f"{OUT_DIR}/summary_by_state.csv", index=False)

    # 4. Specialization frequency (how many hospitals offer each)
    per_spec = q(conn, """
        SELECT sp.spec_name AS specialization,
               COUNT(*) AS num_hospitals_offering,
               ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM hospitals), 1) AS pct_of_hospitals
        FROM hospital_specializations hs
        JOIN specializations sp ON sp.spec_id = hs.spec_id
        GROUP BY sp.spec_name
        ORDER BY num_hospitals_offering DESC;
    """)
    per_spec.to_csv(f"{OUT_DIR}/summary_by_specialization.csv", index=False)
    print("\n=== Specialization Availability (top 10) ===")
    print(per_spec.head(10).to_string(index=False))

    # 5. Hospital type breakdown (Govt / Private / Trust)
    per_type = q(conn, """
        SELECT hospital_type,
               COUNT(*) AS num_hospitals,
               SUM(beds) AS total_beds,
               SUM(doctors) AS total_doctors
        FROM hospitals
        GROUP BY hospital_type
        ORDER BY num_hospitals DESC;
    """)
    per_type.to_csv(f"{OUT_DIR}/summary_by_type.csv", index=False)
    print("\n=== By Hospital Type ===")
    print(per_type.to_string(index=False))

    # 6. Doctor-to-bed ratio per city (a useful derived metric)
    ratio = per_city.copy()
    ratio["doctors_per_100_beds"] = round(ratio["total_doctors"] / ratio["total_beds"] * 100, 1)
    ratio[["city", "state", "doctors_per_100_beds"]].to_csv(
        f"{OUT_DIR}/doctor_bed_ratio_by_city.csv", index=False
    )

    conn.close()
    print(f"\nAll summary CSVs saved to {OUT_DIR}/")


if __name__ == "__main__":
    main()
