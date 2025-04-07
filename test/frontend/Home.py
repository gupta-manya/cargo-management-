import streamlit as st
import requests
import pandas as pd

import os
backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000 ").strip()


def fetch_summary():
    try:
        response = requests.get(f"{backend_url}/summary")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Failed to fetch summary: {e}")
    return {}

def upload_csv(label, endpoint):
    st.markdown(f"### Upload CSV for {label}")
    uploaded_file = st.file_uploader(f"Upload a CSV file for {label}", type=["csv"], key=label)

    if uploaded_file is not None:
        if st.button(f"Upload {label} CSV"):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                response = requests.post(f"{backend_url}/{endpoint}", files=files)

                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Successfully uploaded {result['count']} {label.lower()}.")
                    st.json(result)
                else:
                    st.error(f"Upload failed: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {e}")

def app():
    st.title("Home - Cargo Management System")
    st.markdown("### System Overview")

    summary = fetch_summary()
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Items Placed", summary.get("total_items", 0))
    with col2:
        st.metric("Total Containers", summary.get("total_containers", 0))
    with col3:
        st.metric("Total Space Available", f"{summary.get('total_space_available', 0)} units")

    st.markdown("## Upload CSV Files")
    upload_csv("Containers", "import-containers")
    upload_csv("Items", "import-items")
