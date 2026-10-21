import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Walgreens Asset Protection Analytics",
    page_icon="🛡️",
    layout="wide",
)

# App Header
st.title("🛡️ Retail Asset Protection & Shrink Optimization Engine")
st.markdown(
    "Evaluating high-risk product protection strategies, shrink reduction, and customer friction trade-offs."
)

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("store_summary_analytics.csv")
    return df


df = load_data()

# Sidebar Filters
st.sidebar.header("Filter Options")
selected_region = st.sidebar.selectbox(
    "Select Region", options=["All"] + list(df["region"].unique())
)
selected_format = st.sidebar.selectbox(
    "Select Store Format", options=["All"] + list(df["store_format"].unique())
)

# Apply Filters
filtered_df = df.copy()
if selected_region != "All":
    filtered_df = filtered_df[filtered_df["region"] == selected_region]
if selected_format != "All":
    filtered_df = filtered_df[filtered_df["store_format"] == selected_format]

# Top KPI Metric Cards
st.subheader("Key Performance Indicators (KPIs)")
col1, col2, col3, col4 = st.columns(4)

total_shrink = filtered_df["total_shrink"].sum()
total_revenue = filtered_df["total_estimated_revenue"].sum()
avg_shrink_per_store = filtered_df["total_shrink"].mean()
locked_store_count = filtered_df[filtered_df["has_locked_cases"] == 1][
    "store_id"
].count()

col1.metric("Total Store Shrink", f"${total_shrink:,.2f}")
col2.metric("Estimated Revenue", f"${total_revenue:,.2f}")
col3.metric("Avg Shrink / Store", f"${avg_shrink_per_store:,.2f}")
col4.metric("Stores with Locked Cases", locked_store_count)

st.markdown("---")

# Comparison Section: Locked Cases vs Open Display
st.subheader("Impact Analysis: Locked Cases vs. Open Merchandising")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Shrink Value by Protection Type")
    shrink_by_lock = (
        filtered_df.groupby("has_locked_cases")["total_shrink"]
        .mean()
        .reset_index()
    )
    shrink_by_lock["Protection Status"] = shrink_by_lock["has_locked_cases"].map(
        {0: "Open Display", 1: "Locked Cases"}
    )
    st.bar_chart(
        shrink_by_lock.set_index("Protection Status")["total_shrink"]
    )

with col2:
    st.markdown("### Revenue by Protection Type")
    rev_by_lock = (
        filtered_df.groupby("has_locked_cases")["total_estimated_revenue"]
        .mean()
        .reset_index()
    )
    rev_by_lock["Protection Status"] = rev_by_lock["has_locked_cases"].map(
        {0: "Open Display", 1: "Locked Cases"}
    )
    st.bar_chart(
        rev_by_lock.set_index("Protection Status")["total_estimated_revenue"]
    )

st.markdown("---")

# Raw Data Table
st.subheader("Store-Level Performance Data")
st.dataframe(filtered_df, use_container_width=True)
