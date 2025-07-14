import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import timedelta

# --- Page Configuration ---
st.set_page_config(
    page_title="IT Ticket Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Loading & Caching ---
@st.cache_data
def load_and_process_data(uploaded_file):
    """Loads, cleans, and processes the IT ticket data from a CSV file."""
    try:
        df = pd.read_csv(uploaded_file)
        required_cols = [
            "Created", "Resolved", "Issue Type", "Location",
            "Assignee", "Status", "Priority", "Issue key"
        ]
        if not all(col in df.columns for col in required_cols):
            st.error(f"Error: Your CSV must contain: {', '.join(required_cols)}")
            return None

        # Parse datetimes
        df = df.dropna(subset=["Created", "Resolved"])
        df["Created"] = pd.to_datetime(df["Created"], errors="coerce")
        df["Resolved"] = pd.to_datetime(df["Resolved"], errors="coerce")
        df.dropna(subset=["Created", "Resolved"], inplace=True)

        # Compute resolution time
        df["Resolution Time (hrs)"] = (
            (df["Resolved"] - df["Created"]).dt.total_seconds() / 3600
        )
        df["Created Date"] = df["Created"].dt.date

        return df

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
        return None

@st.cache_data
def convert_df_to_csv(df):
    """Converts a DataFrame to a CSV string for downloading."""
    return df.to_csv(index=False).encode("utf-8")

# --- Main Application ---
st.title("🚀 IT Operations Dashboard")

uploaded_file = st.file_uploader("Upload your IT ticket data (CSV file)", type=["csv"])
if not uploaded_file:
    st.info("👋 Welcome! Please upload a CSV file to begin your analysis.")
    st.stop()

df = load_and_process_data(uploaded_file)
if df is None:
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("Filter Options")
min_date, max_date = df["Created Date"].min(), df["Created Date"].max()
start_date = st.sidebar.date_input("Start date", min_date)
end_date   = st.sidebar.date_input("End date",   max_date)

locations = st.sidebar.multiselect(
    "Select Location:", df["Location"].unique(), default=df["Location"].unique()
)
issue_types = st.sidebar.multiselect(
    "Select Issue Type:", df["Issue Type"].unique(), default=df["Issue Type"].unique()
)

if start_date > end_date:
    st.sidebar.error("Error: Start date must be on or before End date.")
    st.stop()

# --- Filter Data ---
mask = (
    df["Created Date"].between(start_date, end_date)
    & df["Location"].isin(locations)
    & df["Issue Type"].isin(issue_types)
)
df_sel = df[mask]
if df_sel.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# --- Core Metrics ---
total_tickets = len(df_sel)
avg_res_time  = round(df_sel["Resolution Time (hrs)"].mean(), 2)

# --- Tabs ---
tab1, tab2 = st.tabs(["📊 Dashboard", "📂 Raw Data"])
color_seq = px.colors.qualitative.Plotly

with tab1:
    # Overview Metrics
    st.subheader("📌 Overview Metrics")
    c1, c2 = st.columns(2)
    c1.metric("Total Tickets", total_tickets)
    c2.metric("Avg. Resolution Time (hrs)", avg_res_time)
    st.markdown("---")

    # Issue Type Distribution
    st.subheader("📂 Issue Type Distribution")
    ic = df_sel["Issue Type"].value_counts()
    fig1 = px.bar(
        ic, x=ic.values, y=ic.index, orientation="h",
        text_auto=True, color=ic.index, color_discrete_sequence=color_seq
    )
    fig1.update_layout(
        yaxis={"categoryorder": "total ascending"},
        showlegend=False,
        xaxis_title="Ticket Count",
        yaxis_title="Issue Type",
        margin=dict(l=120)
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Assignee Workload
    st.subheader("🧑‍💼 Assignee Workload")
    ac = df_sel["Assignee"].value_counts()
    fig2 = px.bar(
        ac, x=ac.values, y=ac.index, orientation="h",
        text_auto=True, color=ac.index, color_discrete_sequence=color_seq
    )
    fig2.update_layout(
        yaxis={"categoryorder": "total ascending"},
        showlegend=False,
        xaxis_title="Ticket Count",
        yaxis_title="Assignee",
        margin=dict(l=120)
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Priority Distribution
    st.subheader("📊 Priority Distribution")
    pc = df_sel["Priority"].value_counts()
    fig3 = px.pie(
        pc, values=pc.values, names=pc.index, hole=0.3,
        color=pc.index,
        color_discrete_map={p: c for p, c in zip(pc.index, color_seq)}
    )
    fig3.update_layout(showlegend=True, margin=dict(t=20, b=20))
    st.plotly_chart(fig3, use_container_width=True)

    # Daily Ticket Volume Trend
    st.subheader("🎢 Ticket Volume Trend (Daily)")
    daily = (
        df_sel.groupby("Created Date")
        .size().rename("Ticket Count")
        .reset_index()
    )
    fig4 = px.line(daily, x="Created Date", y="Ticket Count", markers=True)
    st.plotly_chart(fig4, use_container_width=True)

    # Locations by Ticket Volume
    st.subheader("🏬 Locations by Ticket Volume")
    lc = df_sel["Location"].value_counts()
    num_loc = len(lc)
    height = max(400, num_loc * 30)
    fig5 = px.bar(
        lc, x=lc.values, y=lc.index, orientation="h",
        text_auto=True, color=lc.index, color_discrete_sequence=color_seq
    )
    fig5.update_layout(
        height=height,
        yaxis={"categoryorder": "total ascending"},
        showlegend=False,
        xaxis_title="Ticket Count",
        yaxis_title="Location",
        margin=dict(l=120, t=20, b=20)
    )
    st.plotly_chart(fig5, use_container_width=True, height=height)

with tab2:
    st.subheader("🕒 All Ticket Data (Filtered)")
    df_display = df_sel.sort_values("Resolution Time (hrs)", ascending=False)
    df_display.index = range(1, len(df_display) + 1)
    st.dataframe(df_display, use_container_width=True)

# --- CSV Download ---
csv_data = convert_df_to_csv(df_sel)
st.sidebar.header("Download")
st.sidebar.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv_data,
    file_name="filtered_it_tickets.csv",
    mime="text/csv",
)
