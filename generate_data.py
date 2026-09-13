"""
generate_data.py
-----------------
Generates a realistic SAMPLE dataset of hospitals across major Indian cities.

IMPORTANT NOTE ON DATA SOURCE:
There is no single official, publicly downloadable file that lists every
hospital in India with exact bed/doctor counts. Real records are scattered
across state health departments, the National Health Profile, Ayushman
Bharat (PMJAY) empanelment lists, and private directories.

This script produces a REPRESENTATIVE, STRUCTURED sample dataset so the
rest of the pipeline (database, analysis, ML) is fully functional end to
end. To use REAL data instead, replace the output of build_dataset() with
rows loaded from your own CSV/API — the schema (columns) must stay the same
and everything downstream will keep working unchanged.
"""

import random
import pandas as pd
from pathlib import Path

random.seed(42)

# Major Indian cities grouped by tier (affects typical hospital size/count)
CITIES = {
    "Tier 1": {
        "Mumbai": "Maharashtra", "Delhi": "Delhi", "Bengaluru": "Karnataka",
        "Chennai": "Tamil Nadu", "Kolkata": "West Bengal", "Hyderabad": "Telangana",
        "Pune": "Maharashtra", "Ahmedabad": "Gujarat",
    },
    "Tier 2": {
        "Jaipur": "Rajasthan", "Lucknow": "Uttar Pradesh", "Chandigarh": "Chandigarh",
        "Kochi": "Kerala", "Indore": "Madhya Pradesh", "Nagpur": "Maharashtra",
        "Bhopal": "Madhya Pradesh", "Coimbatore": "Tamil Nadu", "Patna": "Bihar",
        "Surat": "Gujarat", "Visakhapatnam": "Andhra Pradesh",
    },
    "Tier 3": {
        "Ranchi": "Jharkhand", "Raipur": "Chhattisgarh", "Guwahati": "Assam",
        "Dehradun": "Uttarakhand", "Thiruvananthapuram": "Kerala",
        "Amritsar": "Punjab",
    },
}

SPECIALIZATIONS = [
    "Cardiology", "Neurology", "Oncology", "Orthopedics", "Pediatrics",
    "Gynecology & Obstetrics", "Nephrology", "Gastroenterology",
    "Dermatology", "ENT", "Ophthalmology", "Psychiatry",
    "General Medicine", "General Surgery", "Urology", "Pulmonology",
    "Endocrinology", "Emergency Medicine", "Radiology", "Anesthesiology",
]

HOSPITAL_TYPES = ["Government", "Private", "Trust/NGO"]

NAME_PATTERNS = [
    "{city} General Hospital", "{city} Institute of Medical Sciences",
    "All India Institute {city}", "{city} Multispecialty Hospital",
    "{city} Super Specialty Hospital", "St. Mary's Hospital {city}",
    "{city} District Hospital", "{city} City Care Hospital",
    "{city} Apex Hospital", "{city} Wellness & Research Hospital",
]

TIER_BED_RANGE = {"Tier 1": (150, 1200), "Tier 2": (80, 600), "Tier 3": (40, 350)}
TIER_HOSPITAL_COUNT = {"Tier 1": (6, 9), "Tier 2": (4, 6), "Tier 3": (2, 4)}


def build_dataset() -> pd.DataFrame:
    rows = []
    hospital_id = 1

    for tier, cities in CITIES.items():
        bed_lo, bed_hi = TIER_BED_RANGE[tier]
        count_lo, count_hi = TIER_HOSPITAL_COUNT[tier]

        for city, state in cities.items():
            n_hospitals = random.randint(count_lo, count_hi)
            used_names = set()

            for _ in range(n_hospitals):
                # unique-ish name
                pattern = random.choice(NAME_PATTERNS)
                name = pattern.format(city=city)
                suffix = 1
                base_name = name
                while name in used_names:
                    suffix += 1
                    name = f"{base_name} #{suffix}"
                used_names.add(name)

                h_type = random.choices(HOSPITAL_TYPES, weights=[0.35, 0.55, 0.10])[0]
                beds = random.randint(bed_lo, bed_hi)

                # doctor count roughly scales with beds (1 doctor per 4-9 beds) + noise
                doctor_ratio = random.uniform(4, 9)
                doctors = max(3, int(beds / doctor_ratio) + random.randint(-5, 10))

                # number of specializations scales with hospital size
                if beds < 100:
                    n_spec = random.randint(3, 6)
                elif beds < 400:
                    n_spec = random.randint(6, 12)
                else:
                    n_spec = random.randint(10, len(SPECIALIZATIONS))

                specs = random.sample(SPECIALIZATIONS, n_spec)

                established_year = random.randint(1960, 2022)
                rating = round(random.uniform(2.8, 4.9), 1)

                rows.append({
                    "hospital_id": hospital_id,
                    "hospital_name": name,
                    "city": city,
                    "state": state,
                    "city_tier": tier,
                    "hospital_type": h_type,
                    "beds": beds,
                    "doctors": doctors,
                    "num_specializations": len(specs),
                    "specializations": ", ".join(sorted(specs)),
                    "established_year": established_year,
                    "rating": rating,
                })
                hospital_id += 1

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = build_dataset()
    out_path = str(Path(__file__).resolve().parent.parent / "data" / "hospitals.csv")
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} hospital records across {df['city'].nunique()} cities.")
    print(f"Saved to {out_path}")
    print(df.head())
