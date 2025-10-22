# This creates the page for displaying data visualizations.
# It should read data from both 'data.csv' and 'data.json' to create graphs.

import streamlit as st
import pandas as pd
import json  # The 'json' module is needed to work with JSON files.
import os    # The 'os' module helps with file system operations.

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Visualizations",
    page_icon="📈",
)

# PAGE TITLE AND INFORMATION
st.title("Data Visualizations 📈")
st.write("This page displays graphs based on the collected data.")

CSV_PATH = "data.csv"
JSON_PATH = "data.json"

# DATA LOADING
# A crucial step is to load the data from the files.
# It's important to add error handling to prevent the app from crashing if a file is empty or missing.



# 1) Load CSV safely
if os.path.exists(CSV_PATH) and os.path.getsize(CSV_PATH) > 0:
    try:
        csv_df = pd.read_csv(CSV_PATH)
    except Exception:
        csv_df = pd.DataFrame(columns=["category", "value"])  # fallback
else:
    csv_df = pd.DataFrame(columns=["category", "value"])  # empty structure

# Ensure a numeric column for charts that need numbers
if "value" in csv_df.columns:
    csv_df["numeric_value"] = pd.to_numeric(csv_df["value"], errors="coerce")
else:
    csv_df["numeric_value"] = pd.Series(dtype=float)

# Simple order index (handy if needed later)
csv_df["entry_index"] = range(1, len(csv_df) + 1)

# 2) Load JSON safely
if os.path.exists(JSON_PATH) and os.path.getsize(JSON_PATH) > 0:
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            json_payload = json.load(f)
    except Exception:
        json_payload = {"chart_title": "JSON Chart", "data_points": []}
else:
    json_payload = {"chart_title": "JSON Chart", "data_points": []}

# Convert JSON "data_points" into a DataFrame for easy plotting
json_points = json_payload.get("data_points", [])
json_df = pd.DataFrame(json_points)
if not json_df.empty and {"label", "value"}.issubset(json_df.columns):
    # Index on label so st.bar_chart can use it directly
    json_bar_df = json_df.rename(columns={"label": "Label", "value": "Value"}).set_index("Label")[["Value"]]
else:
    json_bar_df = pd.DataFrame({"Value": []})

st.success("Data loaded. If files are empty, placeholder structures are used.")

# GRAPH CREATION
# The lab requires you to create 3 graphs: one static and two dynamic.
# You must use both the CSV and JSON data sources at least once.

st.divider()
st.header("Graphs")

# GRAPH 1: STATIC GRAPH (BAR)
st.subheader("Graph 1: Baseline Bar Graph")
# Static bar chart using data.json as a reference baseline.
if not json_bar_df.empty:
    st.bar_chart(json_bar_df)
    st.caption("Static baseline from **data.json** (bar chart). Compare this reference with the live user ratings below.")
else:
    st.warning("No valid JSON data to plot yet.")

# Prepare category list from CSV for dynamic charts
all_categories = (
    sorted([c for c in csv_df["category"].dropna().unique()]) if "category" in csv_df.columns else []
)

# Use Session State in a simple, explicit way
if "favorites" not in st.session_state:
    st.session_state["favorites"] = []  # persistent list across interactions  #NEW

# GRAPH 2: DYNAMIC GRAPH (LINE) – Average rating per spot
st.subheader("Graph 2: Average rating per spot")
# - Dynamic line chart driven by multiselect + Top-K slider.
# - Uses Session State for a persistent favorites list.

if csv_df["numeric_value"].notna().sum() == 0:
    st.warning("No numeric values in **data.csv** yet. Submit ratings on the Survey page.")
else:
    picked = st.multiselect(  #NEW
        "Choose spots to include",
        options=all_categories,
        default=all_categories,
        key="picked_categories",
    )

    if st.button("Add current picks to favorites"):  #NEW
        st.session_state["favorites"] = sorted(list({*st.session_state["favorites"], *picked}))
        st.success(f"Favorites updated: {st.session_state['favorites']}")

    top_k = st.slider(  #NEW
        "Show Top K spots (by average rating)",
        min_value=1,
        max_value=max(1, len(all_categories) if all_categories else 1),
        value=min(5, len(all_categories) if all_categories else 1),
    )

    # Filter to selected + favorites
    filt_df = csv_df.dropna(subset=["numeric_value"]).copy()
    effective = set(picked) | set(st.session_state["favorites"])
    if effective:
        filt_df = filt_df[filt_df["category"].isin(list(effective))]

    # Average rating per spot
    avgs = (
        filt_df.groupby("category", as_index=False)["numeric_value"]
        .mean()
        .rename(columns={"numeric_value": "avg_rating"})
    )
    avgs = avgs.sort_values("avg_rating", ascending=False).head(top_k)

    if not avgs.empty:
        # LINE CHART with explicit x/y so categories appear on the x-axis
        st.line_chart(avgs, x="category", y="avg_rating")
        st.caption("Average rating per spot from **data.csv** (line chart). Use the multiselect, favorites, and Top-K slider.")
    else:
        st.info("No rows match your current selection.")

# GRAPH 3: DYNAMIC GRAPH (SCATTER) – Number of ratings per spot
st.subheader("Graph 3: Number of ratings per spot")
# - Dynamic scatter chart that counts how many ratings each spot has received.

if len(csv_df) == 0 or not all_categories:
    st.warning("Add some ratings on the Survey page to see this chart.")
else:
    # Reuse the same selection and favorites
    selected = st.session_state.get("picked_categories", all_categories)
    effective = set(selected) | set(st.session_state["favorites"])

    count_df = csv_df.copy()  # counts don't require numeric values
    if effective:
        count_df = count_df[count_df["category"].isin(list(effective))]

    counts = count_df.groupby("category", as_index=False).size().rename(columns={"size": "num_ratings"})

    show_k = st.slider(  #NEW
        "Show Top K spots (by number of ratings)",
        min_value=1,
        max_value=max(1, len(counts) if not counts.empty else 1),
        value=min(5, len(counts) if not counts.empty else 1),
        key="topk_counts",
    )

    counts = counts.sort_values("num_ratings", ascending=False).head(show_k)

    if not counts.empty:
        # SCATTER CHART with categorical x and numeric y
        st.scatter_chart(counts, x="category", y="num_ratings")
        st.caption("Number of ratings per spot from **data.csv** (scatter chart). Uses the same selection and favorites state.")
    else:
        st.info("No rows match your current selection.")
