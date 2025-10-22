# This creates the page for users to input data.
# The collected data should be appended to the 'data.csv' file.

import streamlit as st
import pandas as pd
import json  # To read study spots from data.json
import os    # File checks

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Survey",
    page_icon="📝",
)

# PAGE TITLE AND USER DIRECTIONS
st.title("Data Collection Survey 📝")
st.write("Pick a study spot and give it a rating. Your response is saved to **data.csv**.")

CSV_PATH = "data.csv"
JSON_PATH = "data.json"


def file_exists_and_not_empty(path: str) -> bool:
    """Return True if the file exists and has at least one byte."""
    return os.path.exists(path) and os.path.getsize(path) > 0


def load_spots_from_json() -> list[str]:
    """Load study spot labels from data.json → data_points[].label. Fallback to a default list."""
    fallback = [
        "Library",
        "Dorm",
        "Clough Commons",
        "Student Center",
        "Klaus Atrium",
        "Outdoor Greens",
        "Dining Hall",
    ]
    if file_exists_and_not_empty(JSON_PATH):
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                payload = json.load(f)
            points = payload.get("data_points", [])
            labels = [p.get("label") for p in points if isinstance(p, dict) and p.get("label")]
            return labels or fallback
        except Exception:
            return fallback
    return fallback


# Load options once for the form
study_spots = load_spots_from_json()

# DATA INPUT FORM
# 'st.form' groups inputs and runs only when you click the submit button.
with st.form("survey_form"):
    spot = st.selectbox("Choose a study spot:", options=study_spots)
    rating = st.slider("Rate this spot (1–10):", min_value=1, max_value=10, value=7)

    submitted = st.form_submit_button("Submit Rating")

# This block runs ONLY when the submit button is clicked.
if submitted:
    # Build a one-row DataFrame (column names match what Visuals.py expects)
    new_row_df = pd.DataFrame([
        {"category": spot, "value": rating}
    ])

    # Append or create the CSV
    if file_exists_and_not_empty(CSV_PATH):
        new_row_df.to_csv(CSV_PATH, mode="a", header=False, index=False)
    else:
        new_row_df.to_csv(CSV_PATH, index=False)

    st.success("Saved! Your rating was added to data.csv.")
    st.write(f"You chose **{spot}** and rated it **{rating}/10**.")


# DATA DISPLAY (helps you verify rows are being added)
st.divider()
st.header("Current Data in CSV")

if file_exists_and_not_empty(CSV_PATH):
    current_data_df = pd.read_csv(CSV_PATH)
    st.dataframe(current_data_df, use_container_width=True)
else:
    st.warning("The 'data.csv' file is empty or does not exist yet.")
