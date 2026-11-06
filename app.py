import os
from pathlib import Path
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Bengaluru Real Estate Intelligence", layout="wide")

st.title("Bengaluru Real Estate Lead Database")
st.markdown("Centralized B2B Lead Generation & Intelligence System (Excel Backend)")

BASE_DIR = Path(__file__).resolve().parent
EXCEL_PATH = BASE_DIR / "data" / "bengaluru_real_estate_master.xlsx"

@st.cache_data
def load_data():
    if not EXCEL_PATH.exists():
        return pd.DataFrame()
    return pd.read_excel(EXCEL_PATH, sheet_name="All_Companies")

df = load_data()

if df.empty:
    st.warning("No data found yet. Run your scraper script to populate the Excel file.")
else:
    # Sidebar Filters
    st.sidebar.header("Filters")
    zones = ["All"] + list(df['zone'].dropna().unique()) if 'zone' in df.columns else ["All"]
    selected_zone = st.sidebar.selectbox("Select Zone", zones)
    
    categories = ["All"] + list(df['business_category'].dropna().unique()) if 'business_category' in df.columns else ["All"]
    selected_category = st.sidebar.selectbox("Business Category", categories)

    filtered_df = df.copy()
    if selected_zone != "All":
        filtered_df = filtered_df[filtered_df['zone'] == selected_zone]
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df['business_category'] == selected_category]

    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Companies", len(filtered_df))
    col2.metric("Emails Available", int(filtered_df['company_email'].notnull().sum()) if 'company_email' in filtered_df.columns else 0)
    col3.metric("Phone Numbers", int(filtered_df['contact_number'].notnull().sum()) if 'contact_number' in filtered_df.columns else 0)
    col4.metric("Verified Status", int(len(filtered_df[filtered_df.get('verification_status', '') == 'Verified'])))

    # Data Table
    st.dataframe(filtered_df, use_container_width=True)

    # Export Button
    if EXCEL_PATH.exists():
        with open(EXCEL_PATH, "rb") as f:
            excel_bytes = f.read()
        st.download_button(
            label="Download Master Excel File",
            data=excel_bytes,
            file_name="bengaluru_real_estate_master.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
