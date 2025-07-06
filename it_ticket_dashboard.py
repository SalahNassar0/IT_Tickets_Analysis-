import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import io
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="IT Ticket Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Loading and Caching ---
@st.cache_data
def load_and_process_data(uploaded_file):
    """Loads, cleans, and processes the IT ticket data from a CSV file."""
    try:
        df = pd.read_csv(uploaded_file)
        required_cols = ["Created", "Resolved", "Issue Type", "Location", "Assignee", "Status", "Priority", "Issue key"]
        if not all(col in df.columns for col in required_cols):
            st.error(f"Error: Your CSV must contain the following columns: {', '.join(required_cols)}")
            return None

        df = df.dropna(subset=["Created", "Resolved"])
        df["Created"] = pd.to_datetime(df["Created"], errors="coerce")
        df["Resolved"] = pd.to_datetime(df["Resolved"], errors="coerce")
        df.dropna(subset=["Created", "Resolved"], inplace=True)

        df["Resolution Time (hrs)"] = (df["Resolved"] - df["Created"]).dt.total_seconds() / 3600
        df["Created Date"] = df["Created"].dt.date

        return df
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
        return None

@st.cache_data
def convert_df_to_csv(df):
    """Converts a DataFrame to a CSV string for downloading."""
    return df.to_csv(index=False).encode('utf-8')

# --- PDF Report Generation ---
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "IT Operations Ticket Report", 0, 0, "C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

def create_pdf_report(metrics, charts, start_date, end_date):
    """Generates a colorful, well-aligned PDF report."""
    pdf = PDF()
    pdf.add_page()

    # Add Report Period
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"Report Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}", 0, 1, "C")
    pdf.ln(5)

    # --- KPIs Section ---
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(230, 230, 230) # Light gray background for header
    pdf.cell(0, 10, "Key Performance Indicators", 0, 1, "L", fill=True)
    pdf.ln(5)

    pdf.set_font("Arial", "", 11)
    col_width = pdf.w / 2.5
    for name, value in metrics.items():
        pdf.cell(col_width, 8, f"{name}:", 0, 0)
        pdf.cell(col_width, 8, str(value), 0, 1)
    pdf.ln(10)

    # --- Visualizations Section ---
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, "Visualizations", 0, 1, "L", fill=True)
    pdf.ln(5)

    for title, fig in charts.items():
        if pdf.get_y() > 190:
            pdf.add_page()

        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 10, title, 0, 1, "L")

        img_bytes = fig.to_image(format="png", scale=2)
        img_buffer = io.BytesIO(img_bytes)

        pdf.image(img_buffer, w=180)
        pdf.ln(5)

    return bytes(pdf.output())

# --- Main Application ---
st.title("🚀 IT Operations Dashboard")

uploaded_file = st.file_uploader("Upload your IT ticket data (CSV file)", type=["csv"])

if uploaded_file is not None:
    df = load_and_process_data(uploaded_file)

    if df is not None:
        # --- Sidebar Filters ---
        st.sidebar.header("Filter Options")

        # Date range filter
        start_date = st.sidebar.date_input("Start date", df["Created Date"].min())
        end_date = st.sidebar.date_input("End date", df["Created Date"].max())

        # Other filters
        locations = st.sidebar.multiselect("Select Location:", options=df["Location"].unique(), default=df["Location"].unique())
        issue_types = st.sidebar.multiselect("Select Issue Type:", options=df["Issue Type"].unique(), default=df["Issue Type"].unique())

        # Validate date range
        if start_date > end_date:
            st.sidebar.error("Error: End date must be after start date.")
            st.stop()
        
        # Apply all filters
        df_selection = df.query(
            "(@start_date <= `Created Date` <= @end_date) & "
            "Location == @locations & `Issue Type` == @issue_types"
        )


        if df_selection.empty:
            st.warning("No data available for the selected filters. Please adjust your selections.")
        else:
            # --- Prepare Metrics and Charts ---
            total_tickets = len(df_selection)
            avg_res_time = round(df_selection["Resolution Time (hrs)"].mean(), 2)

            metrics_dict = {
                "Total Tickets": total_tickets,
                "Average Resolution Time (hrs)": avg_res_time,
            }

            # --- Dashboard Tabs ---
            tab1, tab2 = st.tabs(["📊 Dashboard", "📂 Raw Data"])

            with tab1:
                # --- KPI Cards ---
                st.subheader("📌 Overview Metrics")
                col1, col2 = st.columns(2)
                col1.metric("Total Tickets", total_tickets)
                col2.metric("Avg. Resolution Time (hrs)", avg_res_time)

                st.markdown("---")

                # --- Visualizations ---
                charts_to_export = {}
                color_sequence = px.colors.qualitative.Plotly

                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("📂 Issue Type Distribution")
                    issue_counts = df_selection["Issue Type"].value_counts()
                    fig_issue = px.bar(issue_counts, x=issue_counts.values, y=issue_counts.index, orientation='h', text_auto=True, color=issue_counts.index, color_discrete_sequence=color_sequence)
                    fig_issue.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, xaxis_title="Ticket Count", yaxis_title="Issue Type")
                    st.plotly_chart(fig_issue, use_container_width=True)
                    charts_to_export["Issue Type Distribution"] = fig_issue

                    st.subheader("🧑‍💼 Assignee Workload")
                    assignee_counts = df_selection["Assignee"].value_counts()
                    fig_assignee = px.bar(assignee_counts, x=assignee_counts.values, y=assignee_counts.index, orientation='h', text_auto=True, color=assignee_counts.index, color_discrete_sequence=color_sequence)
                    fig_assignee.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, xaxis_title="Ticket Count", yaxis_title="Assignee")
                    st.plotly_chart(fig_assignee, use_container_width=True)
                    charts_to_export["Assignee Workload"] = fig_assignee

                with col2:
                    st.subheader("🏬 Locations by Ticket Volume")
                    location_counts = df_selection["Location"].value_counts()
                    fig_loc = px.bar(location_counts, x=location_counts.values, y=location_counts.index, orientation='h', text_auto=True, color=location_counts.index, color_discrete_sequence=color_sequence)
                    fig_loc.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, xaxis_title="Ticket Count", yaxis_title="Location")
                    st.plotly_chart(fig_loc, use_container_width=True)
                    charts_to_export["Locations by Ticket Volume"] = fig_loc

                    st.subheader("📊 Priority Distribution")
                    priority_counts = df_selection["Priority"].value_counts()
                    fig_prio = px.pie(priority_counts, values=priority_counts.values, names=priority_counts.index, hole=0.3, color=priority_counts.index, color_discrete_map={p:c for p,c in zip(priority_counts.index, color_sequence)})
                    st.plotly_chart(fig_prio, use_container_width=True)
                    charts_to_export["Priority Distribution"] = fig_prio

            with tab2:
                st.subheader("🕒 All Ticket Data (Filtered)")
                df_display = df_selection.sort_values(by="Resolution Time (hrs)", ascending=False)
                df_display.index = range(1, len(df_display) + 1)
                st.dataframe(df_display, use_container_width=True)

            # --- Sidebar Download Buttons ---
            st.sidebar.markdown("---")
            st.sidebar.header("Download Reports")

            csv_data = convert_df_to_csv(df_selection)
            st.sidebar.download_button(
               label="📥 Download Filtered Data as CSV",
               data=csv_data,
               file_name='filtered_it_tickets.csv',
               mime='text/csv',
            )

            pdf_data = create_pdf_report(metrics_dict, charts_to_export, start_date, end_date)
            st.sidebar.download_button(
                label="📄 Download Full Report as PDF",
                data=pdf_data,
                file_name="it_ticket_report.pdf",
                mime="application/pdf"
            )

else:
    st.info("👋 Welcome! Please upload a CSV file to begin your analysis.")