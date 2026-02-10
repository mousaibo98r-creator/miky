# Export Analytics Platform

## Overview
This is a Streamlit-based analytics platform designed for export data visualization and management. It features a dashboard, intelligence matrix, email center, and file manager.

## Features
- **Dashboard**: KPI metrics and interactive charts (Dual-axis, Donut).
- **Intelligence**: Filterable data matrix with entity profiles.
- **Email Center**: Mock email client and SMTP configuration.
- **File Manager**: Upload and manage files.
- **Settings**: Configuration for Supabase and API keys.

## Tech Stack
- Frontend: Streamlit
- Backend: Supabase (handling connection and mock fallback)
- Visualization: Plotly
- Data: Pandas

## Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application locally:
```bash
streamlit run streamlit_app.py
```

## Deployment

This app is ready for deployment on [Streamlit Cloud](https://streamlit.io/cloud).
1. Push this code to GitHub.
2. Connect your GitHub repository to Streamlit Cloud.
3. Add your Supabase secrets in the Streamlit Cloud dashboard.
