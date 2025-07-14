# IT_Tickets_Analysis

A Streamlit dashboard for analyzing IT operation tickets. Upload your IT ticket CSV and get instant insights, trends, and downloadable reports.

## Features
- Upload and analyze IT ticket data (CSV)
- Interactive filters (date, location, issue type)
- Visualizations: Issue type, assignee workload, priority, trends, locations
- Download filtered data as CSV

## Usage
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. (Optional) Install system dependencies (for some environments):
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install -y chromium chromium-driver libgl1-mesa-glx libegl1-mesa libxrandr2 libxss1 libxcursor1 libxcomposite1 libasound2 libxi6 libxtst6
   ```
3. Run the app:
   ```bash
   streamlit run it_ticket_dashboard.py
   ```
4. Upload your IT ticket CSV file when prompted.

## Sample CSV Structure
Your CSV should contain the following columns:
- Created
- Resolved
- Issue Type
- Location
- Assignee
- Status
- Priority
- Issue key

Example:
```csv
Created,Resolved,Issue Type,Location,Assignee,Status,Priority,Issue key
2024-01-01 08:00,2024-01-01 12:00,Network,New York,John Doe,Closed,High,IT-001
2024-01-02 09:30,2024-01-02 10:30,Hardware,London,Jane Smith,Closed,Medium,IT-002
2024-01-03 11:00,2024-01-03 15:00,Software,Berlin,Max Mustermann,Closed,Low,IT-003
2024-01-04 14:00,2024-01-04 18:00,Network,Paris,Marie Curie,Closed,High,IT-004
2024-01-05 10:00,2024-01-05 13:00,Hardware,New York,John Doe,Closed,Medium,IT-005
```

## Screenshot
![Dashboard Screenshot](screenshot.png)

## Notes
- The `fonts/` directory is not used by the dashboard. You may remove it if not needed.
- The `packages.txt` file lists system dependencies for deployment environments.
