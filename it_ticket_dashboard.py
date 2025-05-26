
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="IT Ticket Dashboard", layout="wide")
st.title("📊 IT Operations Ticket Dashboard")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    #Test Branch
    # Clean and parse datetime columns
    df = df.dropna(subset=["Created", "Resolved"])
    df["Created"] = pd.to_datetime(df["Created"], errors="coerce")
    df["Resolved"] = pd.to_datetime(df["Resolved"], errors="coerce")
    df["Resolution Time (hrs)"] = (df["Resolved"] - df["Created"]).dt.total_seconds() / 3600

    st.subheader("📌 Overview Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tickets", len(df))
    col2.metric("Average Resolution Time (hrs)", round(df["Resolution Time (hrs)"].mean(), 2))
    col3.metric("Unique Locations", df["Location"].nunique())

    st.subheader("📂 Issue Type Distribution")
    issue_type_counts = df["Issue Type"].value_counts()
    st.bar_chart(issue_type_counts)

    st.subheader("🕒 Resolution Time Per Ticket")
    st.dataframe(df[["Issue key", "Issue Type", "Created", "Resolved", "Resolution Time (hrs)"]].sort_values(by="Resolution Time (hrs)", ascending=False))

    st.subheader("🏬 Top Locations by Ticket Count")
    location_counts = df["Location"].value_counts()
    st.bar_chart(location_counts)

    st.subheader("🧑‍💼 Assignee Workload")
    assignee_counts = df["Assignee"].value_counts()
    st.bar_chart(assignee_counts)

    st.subheader("📊 Ticket Status & Priority")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Status Distribution**")
        st.bar_chart(df["Status"].value_counts())
    with col2:
        st.write("**Priority Distribution**")
        st.bar_chart(df["Priority"].value_counts())

    st.subheader("📆 Ticket Creation Timeline")
    df["Created Date"] = df["Created"].dt.date
    created_timeline = df.groupby("Created Date").size()
    st.line_chart(created_timeline)

    st.success("Dashboard successfully loaded!")
else:
    st.info("Please upload a CSV file to begin.")
