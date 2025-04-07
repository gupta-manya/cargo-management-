import streamlit as st
import requests
import pandas as pd

backend_url = "http://localhost:8000"

def fetch_logs():
    try:
        response = requests.get(f"{backend_url}/logs")
        if response.status_code == 200:
            return response.json().get("logs", [])
        else:
            st.error(f"Failed to fetch logs: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"An error occurred while fetching logs: {e}")
    return []

def app():
    st.title("Logs - Action History")
    st.markdown("### History of Placement and Retrieval Actions")

    logs = fetch_logs()
    if logs:
        df = pd.DataFrame(logs)
        if not df.empty:
            st.dataframe(df)
        else:
            st.info("No logs available.")
    else:
        st.warning("No logs to display or failed to fetch logs.")
