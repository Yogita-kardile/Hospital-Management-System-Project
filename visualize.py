"""
visualize.py
------------
Generates PNG charts summarizing the hospital dataset.
Run after analysis.py and ml_models.py (uses their output CSVs).
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

OUT_DIR = str(Path(__file__).resolve().parent.parent / "output")


def chart_top_cities():
    df = pd.read_csv(f"{OUT_DIR}/summary_by_city.csv").head(12)
    fig, ax1 = plt.subplots(figsize=(11, 6))
    x = range(len(df))
    ax1.bar(x, df["num_hospitals"], color="#4C72B0", label="Hospitals")
    ax1.set_ylabel("Number of Hospitals", color="#4C72B0")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(df["city"], rotation=45, ha="right")
    ax1.set_title("Hospitals, Beds & Doctors — Top Cities (sample dataset)")

    ax2 = ax1.twinx()
    ax2.plot(x, df["total_beds"], color="#DD8452", marker="o", label="Total Beds")
    ax2.plot(x, df["total_doctors"] * 10, color="#55A868", marker="s",
              label="Total Doctors (x10)")
    ax2.set_ylabel("Beds / Doctors(x10)")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/chart_top_cities.png", dpi=140)
    plt.close(fig)


def chart_specializations():
    df = pd.read_csv(f"{OUT_DIR}/summary_by_specialization.csv").head(12)
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(df["specialization"][::-1], df["num_hospitals_offering"][::-1], color="#4C72B0")
    ax.set_xlabel("Number of Hospitals Offering")
    ax.set_title("Most Common Specializations (sample dataset)")
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/chart_specializations.png", dpi=140)
    plt.close(fig)


def chart_clusters():
    df = pd.read_csv(f"{OUT_DIR}/hospital_clusters.csv")
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = {"Small / Community": "#4C72B0", "Medium": "#55A868",
              "Large": "#DD8452", "Mega / Super-Specialty": "#C44E52"}
    for label, group in df.groupby("tier_label"):
        ax.scatter(group["beds"], group["doctors"], label=label,
                   color=colors.get(label, "gray"), alpha=0.7, s=50)
    ax.set_xlabel("Beds")
    ax.set_ylabel("Doctors")
    ax.set_title("Hospital Capability Tiers (KMeans clustering)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/chart_clusters.png", dpi=140)
    plt.close(fig)


if __name__ == "__main__":
    chart_top_cities()
    chart_specializations()
    chart_clusters()
    print("Charts saved: chart_top_cities.png, chart_specializations.png, chart_clusters.png")
