

import sqlite3
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "output" / "hospitals.db"
MODEL_PATH = BASE_DIR / "output" / "doctor_demand_model.joblib"

st.set_page_config(page_title="India Hospitals Dashboard", layout="wide")


@st.cache_data
def load_hospitals():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT h.hospital_id, h.hospital_name, h.city, h.state, h.city_tier,
               h.hospital_type, h.beds, h.doctors, h.established_year, h.rating,
               GROUP_CONCAT(sp.spec_name, ', ') AS specializations
        FROM hospitals h
        LEFT JOIN hospital_specializations hs ON hs.hospital_id = h.hospital_id
        LEFT JOIN specializations sp ON sp.spec_id = hs.spec_id
        GROUP BY h.hospital_id
    """, conn)
    conn.close()
    return df


@st.cache_resource
def load_model():
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    return None


if not DB_PATH.exists():
    st.error(
        "Database not found. Run `python run_all.py` in this project folder "
        "first to generate output/hospitals.db."
    )
    st.stop()

df = load_hospitals()
model = load_model()

st.title("🏥 India Hospitals Dashboard")


# ---------------- Sidebar filters ----------------
st.sidebar.header("Filters")
states = sorted(df["state"].unique())
sel_states = st.sidebar.multiselect("State", states, default=[])

cities_pool = df[df["state"].isin(sel_states)]["city"].unique() if sel_states else df["city"].unique()
sel_cities = st.sidebar.multiselect("City", sorted(cities_pool), default=[])

sel_types = st.sidebar.multiselect(
    "Hospital type", sorted(df["hospital_type"].unique()), default=[]
)

all_specs = sorted({s.strip() for row in df["specializations"].dropna() for s in row.split(",")})
sel_spec = st.sidebar.selectbox("Has specialization", ["Any"] + all_specs)

bed_min, bed_max = int(df["beds"].min()), int(df["beds"].max())
sel_bed_range = st.sidebar.slider("Beds range", bed_min, bed_max, (bed_min, bed_max))

# ---------------- Apply filters ----------------
filtered = df.copy()
if sel_states:
    filtered = filtered[filtered["state"].isin(sel_states)]
if sel_cities:
    filtered = filtered[filtered["city"].isin(sel_cities)]
if sel_types:
    filtered = filtered[filtered["hospital_type"].isin(sel_types)]
if sel_spec != "Any":
    filtered = filtered[filtered["specializations"].str.contains(sel_spec, na=False)]
filtered = filtered[filtered["beds"].between(*sel_bed_range)]

# ---------------- Headline metrics ----------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Hospitals", f"{len(filtered):,}")
c2.metric("Total Beds", f"{filtered['beds'].sum():,}")
c3.metric("Total Doctors", f"{filtered['doctors'].sum():,}")
c4.metric("Cities covered", filtered["city"].nunique())

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(
    ["Hospital list", "By city", "By specialization", "Predict doctors needed"]
)

with tab1:
    st.subheader("Hospitals")
    st.dataframe(
        filtered[["hospital_name", "city", "state", "hospital_type", "beds",
                  "doctors", "rating", "specializations"]]
        .sort_values("beds", ascending=False),
        use_container_width=True,
        height=500,
    )
    st.download_button(
        "Download filtered results as CSV",
        filtered.to_csv(index=False).encode("utf-8"),
        file_name="filtered_hospitals.csv",
        mime="text/csv",
    )

with tab2:
    st.subheader("Hospitals, beds & doctors by city")
    by_city = (
        filtered.groupby(["city", "state"])
        .agg(num_hospitals=("hospital_id", "count"),
             total_beds=("beds", "sum"),
             total_doctors=("doctors", "sum"),
             avg_rating=("rating", "mean"))
        .round(2)
        .sort_values("num_hospitals", ascending=False)
        .reset_index()
    )
    st.dataframe(by_city, use_container_width=True)
    st.bar_chart(by_city.set_index("city")[["total_beds"]])

with tab3:
    st.subheader("Specialization availability")
    spec_rows = []
    for row in filtered["specializations"].dropna():
        spec_rows.extend([s.strip() for s in row.split(",")])
    if spec_rows:
        spec_counts = pd.Series(spec_rows).value_counts()
        st.bar_chart(spec_counts)
        st.dataframe(spec_counts.rename("num_hospitals_offering"))
    else:
        st.info("No hospitals match the current filters.")

with tab4:
    st.subheader("Predict how many doctors a hospital needs")
    if model is None:
        st.warning(
            "No trained model found. Run `python scripts/ml_models.py` first."
        )
    else:
        colA, colB = st.columns(2)
        with colA:
            in_beds = st.number_input("Beds", min_value=10, max_value=2000, value=300, step=10)
            in_tier = st.selectbox("City tier", ["Tier 1", "Tier 2", "Tier 3"])
        with colB:
            in_type = st.selectbox("Hospital type", ["Government", "Private", "Trust/NGO"])
            in_year = st.number_input("Established year", min_value=1900, max_value=2026, value=2015)

        if st.button("Predict"):
            example = pd.DataFrame([{
                "beds": in_beds, "city_tier": in_tier,
                "hospital_type": in_type, "established_year": in_year,
            }])
            pred = model.predict(example)[0]
            st.success(f"Estimated doctors needed: **{pred:.0f}**")
            st.caption(
                f"≈ {in_beds / pred:.1f} beds per doctor, based on patterns "
                "learned from the sample dataset."
            )



st.markdown(
    """
    <div style="
        margin-top: 40px;
        padding: 18px;
        border-radius: 12px;
        text-align: center;
        background: linear-gradient(90deg, #f0f4ff, #f9f0ff);
        border: 1px solid #e0e0f0;
    ">
        <p style="margin: 0; font-size: 15px; color: #444;">
            🏥 Built with Python, SQLite & Streamlit
        </p>
        <p style="margin: 4px 0 0 0; font-size: 14px; color: #666;">
            Made with ❤️ by <b>Yogita kardile</b>
        </p>
        <p style="margin: 2px 0 0 0; font-size: 13px;">
            📧 <a href="mailto:kardileyogita70@gmail.com" style="color:#6c5ce7; text-decoration:none;">
                kardileyogita70@gmail.com
            </a>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
