# This creates the page for users to input data.
# The collected data should be appended to the 'data.csv' file.

import streamlit as st
import pandas as pd
import os  # The 'os' module is used for file system operations (e.g., checking if a file exists).

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Survey",
    page_icon="📝",
)

# PAGE TITLE AND USER DIRECTIONS
st.title("Data Collection Survey 📝")
st.write("Please fill out the form below to add your data to the dataset.")

CSV_PATH = "data.csv"


def file_exists_and_not_empty(path: str) -> bool:
    """Return True if the CSV exists and has at least one byte."""
    return os.path.exists(path) and os.path.getsize(path) > 0


# DATA INPUT FORM
# 'st.form' creates a container that groups input widgets.
# The form is submitted only when the user clicks the 'st.form_submit_button'.
# This is useful for preventing the app from re-running every time a widget is changed.
with st.form("survey_form"):
    # Create text input widgets for the user to enter data.
    # The first argument is the label that appears above the input box.
    category_input = st.text_input("Enter a category:")
    value_input = st.text_input("Enter a corresponding value:")

    # The submit button for the form.
    submitted = st.form_submit_button("Submit Data")

# This block of code runs ONLY when the submit button is clicked.
if submitted:
    # --- IMPLEMENTATION: Append a new row to data.csv ---
    # 1) Validate inputs
    if not category_input.strip() or not value_input.strip():
        st.error("Both fields are required. Please fill in all inputs.")
    else:
        # 2) Build a one-row DataFrame
        new_row_df = pd.DataFrame([
            {"category": category_input.strip(), "value": value_input.strip()}
        ])

        # 3) Append to the CSV
        #    - If the file already has data, append without header.
        #    - If it doesn't exist (or is empty), create it with header.
        if file_exists_and_not_empty(CSV_PATH):
            new_row_df.to_csv(CSV_PATH, mode="a", header=False, index=False)
        else:
            new_row_df.to_csv(CSV_PATH, index=False)

        st.success("Your data has been submitted!")
        st.write(f"You entered: **Category:** {category_input}, **Value:** {value_input}")


# DATA DISPLAY
# This section shows the current contents of the CSV file, which helps in debugging.
st.divider()  # Adds a horizontal line for visual separation.
st.header("Current Data in CSV")

# Check if the CSV file exists and is not empty before trying to read it.
if file_exists_and_not_empty(CSV_PATH):
    # Read the CSV file into a pandas DataFrame.
    current_data_df = pd.read_csv(CSV_PATH)
    # Display the DataFrame as a table.
    st.dataframe(current_data_df, use_container_width=True)
else:
    st.warning("The 'data.csv' file is empty or does not exist yet.")
