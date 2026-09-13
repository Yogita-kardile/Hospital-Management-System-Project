"""
create_database.py
-------------------
Builds a normalized SQLite database from data/hospitals.csv.

Schema:
    hospitals            (hospital_id PK, name, city, state, city_tier,
                           hospital_type, beds, doctors, established_year, rating)
    specializations       (spec_id PK, spec_name UNIQUE)
    hospital_specializations (hospital_id FK, spec_id FK)   -- many-to-many
"""

import sqlite3
import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = str(PROJECT_DIR / "output" / "hospitals.db")
CSV_PATH = str(PROJECT_DIR / "data" / "hospitals.csv")

SCHEMA = """
DROP TABLE IF EXISTS hospital_specializations;
DROP TABLE IF EXISTS specializations;
DROP TABLE IF EXISTS hospitals;

CREATE TABLE hospitals (
    hospital_id       INTEGER PRIMARY KEY,
    hospital_name     TEXT NOT NULL,
    city              TEXT NOT NULL,
    state             TEXT NOT NULL,
    city_tier         TEXT NOT NULL,
    hospital_type     TEXT NOT NULL,
    beds              INTEGER NOT NULL,
    doctors           INTEGER NOT NULL,
    established_year  INTEGER,
    rating            REAL
);

CREATE TABLE specializations (
    spec_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    spec_name   TEXT UNIQUE NOT NULL
);

CREATE TABLE hospital_specializations (
    hospital_id  INTEGER NOT NULL,
    spec_id      INTEGER NOT NULL,
    PRIMARY KEY (hospital_id, spec_id),
    FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id),
    FOREIGN KEY (spec_id) REFERENCES specializations(spec_id)
);

CREATE INDEX idx_hospitals_city ON hospitals(city);
CREATE INDEX idx_hospitals_state ON hospitals(state);
"""


def main():
    df = pd.read_csv(CSV_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(SCHEMA)

    # Insert hospitals
    hosp_cols = ["hospital_id", "hospital_name", "city", "state", "city_tier",
                 "hospital_type", "beds", "doctors", "established_year", "rating"]
    df[hosp_cols].to_sql("hospitals", conn, if_exists="append", index=False)

    # Insert specializations (unique set) + junction rows
    all_specs = sorted({s.strip() for row in df["specializations"] for s in row.split(",")})
    cur.executemany("INSERT INTO specializations (spec_name) VALUES (?)",
                     [(s,) for s in all_specs])
    conn.commit()

    spec_id_map = dict(cur.execute("SELECT spec_name, spec_id FROM specializations").fetchall())

    junction_rows = []
    for _, row in df.iterrows():
        for s in row["specializations"].split(","):
            junction_rows.append((row["hospital_id"], spec_id_map[s.strip()]))

    cur.executemany(
        "INSERT INTO hospital_specializations (hospital_id, spec_id) VALUES (?, ?)",
        junction_rows,
    )
    conn.commit()

    # sanity check
    n_hosp = cur.execute("SELECT COUNT(*) FROM hospitals").fetchone()[0]
    n_spec = cur.execute("SELECT COUNT(*) FROM specializations").fetchone()[0]
    n_link = cur.execute("SELECT COUNT(*) FROM hospital_specializations").fetchone()[0]
    print(f"Database created at {DB_PATH}")
    print(f"  hospitals: {n_hosp} rows")
    print(f"  specializations: {n_spec} rows")
    print(f"  hospital_specializations: {n_link} rows")

    conn.close()


if __name__ == "__main__":
    main()
