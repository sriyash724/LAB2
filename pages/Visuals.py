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

st.divider()
st.header("Load Data")

# 1. Load CSV safely
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

# Add a simple order index so we can plot values over time/order
csv_df["entry_index"] = range(1, len(csv_df) + 1)

# 2. Load JSON safely
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
    json_bar_df = json_df.rename(columns={"label": "Label", "value": "Value"}).set_index("Label")[
        ["Value"]
    ]
else:
    json_bar_df = pd.DataFrame({"Value": []})

st.success("Data loaded. If files are empty, placeholder structures are used.")


# GRAPH CREATION
# The lab requires you to create 3 graphs: one static and two dynamic.
# You must use both the CSV and JSON data sources at least once.

st.divider()
st.header("Graphs")

# GRAPH 1: STATIC GRAPH
st.subheader("Graph 1: Static – JSON bar chart")  # CHANGE THIS TO THE TITLE OF YOUR GRAPH
# - Create a static graph (e.g., bar chart, line chart) using st.bar_chart() or st.line_chart().
# - Use data from either the CSV or JSON file.
# - Write a description explaining what the graph shows.
if not json_bar_df.empty:
    st.bar_chart(json_bar_df)  # static chart from JSON
    st.caption("Static bar chart using **data.json**. Each bar shows the 'Value' for a 'Label'.")
else:
    st.warning("Placeholder for your first graph. (No valid JSON data to plot yet.)")


# Prepare category list from CSV for dynamic charts
all_categories = (
    sorted([c for c in csv_df["category"].dropna().unique()]) if "category" in csv_df.columns else []
)

# Use Session State in a simple, explicit way
if "favorites" not in st.session_state:
    st.session_state["favorites"] = []  # persistent list across interactions  #NEW


# GRAPH 2: DYNAMIC GRAPH
st.subheader("Graph 2: Dynamic – CSV totals by category")  # CHANGE THIS TO THE TITLE OF YOUR GRAPH
# - Create a dynamic graph that changes based on user input.
# - Use at least one interactive widget (e.g., st.slider, st.selectbox, st.multiselect).
# - Use Streamlit's Session State (st.session_state) to manage the interaction.
# - Add a '#NEW' comment next to at least 3 new Streamlit functions you use in this lab.
# - Write a description explaining the graph and how to interact with it.

if csv_df["numeric_value"].notna().sum() == 0:
    st.warning("No numeric values in **data.csv** yet. Submit numeric 'value' entries on the Survey page.")
else:
    picked = st.multiselect(  #NEW
        "Choose categories to include",
        options=all_categories,
        default=all_categories,
        key="picked_categories",
    )

    # Button to persist current picks into a favorites list stored in session state
    if st.button("Add current picks to favorites"):  #NEW
        st.session_state["favorites"] = sorted(list({*st.session_state["favorites"], *picked}))
        st.success(f"Favorites updated: {st.session_state['favorites']}")

    top_k = st.slider(  #NEW
        "Show Top K categories (by total value)",
        min_value=1,
        max_value=max(1, len(all_categories) if all_categories else 1),
        value=min(5, len(all_categories) if all_categories else 1),
    )

    # Filter and aggregate
    filt_df = csv_df.dropna(subset=["numeric_value"]).copy()
    if picked:
        filt_df = filt_df[filt_df["category"].isin(picked)]

    totals = (
        filt_df.groupby("category", as_index=False)["numeric_value"].sum().rename(columns={"numeric_value": "total"})
    )
    totals = totals.sort_values("total", ascending=False).head(top_k)

    if not totals.empty:
        bar_df = totals.set_index("category")["total"].to_frame()
        st.area_chart(bar_df)
        st.caption(
            "Dynamic bar chart using **data.csv**. Use the multiselect to choose categories and the slider to limit to Top‑K."
        )
    else:
        st.info("No rows match your current selection.")


# GRAPH 3: DYNAMIC GRAPH
st.subheader("Graph 3: Dynamic – CSV values over entry order")  # CHANGE THIS TO THE TITLE OF YOUR GRAPH
# - Create another dynamic graph.
# - If you used CSV data for Graph 1 & 2, you MUST use JSON data here (or vice-versa).
#   (We used JSON in Graph 1 and CSV in Graph 2, so CSV here is acceptable.)
# - This graph must also be interactive and use Session State.
# - Remember to add a description and use '#NEW' comments.

if csv_df["numeric_value"].notna().sum() == 0 or not all_categories:
    st.warning("Add some numeric CSV rows with categories to see this chart.")
else:
    # Default to first favorite if available, otherwise first category
    default_cat = st.session_state["favorites"][0] if st.session_state["favorites"] else all_categories[0]
    chosen_cat = st.selectbox(  #NEW
        "Pick a category to plot over entry order",
        options=all_categories,
        index=all_categories.index(default_cat) if default_cat in all_categories else 0,
        key="chosen_category",
    )

    series_df = csv_df[(csv_df["category"] == chosen_cat) & (csv_df["numeric_value"].notna())][
        ["entry_index", "numeric_value"]
    ].set_index("entry_index")

    if not series_df.empty:
        st.line_chart(series_df)  # simple time/order series from CSV
        st.caption(
            "Dynamic line chart from **data.csv**. The select box chooses which category to plot; favorites persist in session state."
        )
    else:
        st.info("No numeric rows for the selected category yet.")
