import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from api import upload_csv_to_backend

import Home
import Placement
import retrieval

import Logs

st.set_page_config(page_title="Cargo Management System", layout="wide")

with st.sidebar:
    page = option_menu("Menu", ["Home", "Placement", "Retrieval", "Search", "Log"],
                       icons=["house", "box", "arrow-down-up", "search", "clock"], default_index=0)

if page == "Home":
    Home.app()
elif page == "Placement":
    Placement.app()
elif page == "Retrieval":
    retrieval.app()
elif page == "Log":
    Logs.app()
