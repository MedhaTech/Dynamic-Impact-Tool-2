import streamlit as st
from layout.sidebar import render_sidebar
from layout.upload_area import render_upload_area
from layout.tabs_single import render_single_tabs
from layout.tabs_comparison import render_comparison_tabs
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Dynamic Impact Tool", layout="wide")
st.title("📊 Dynamic Impact Tool")

if "mode" not in st.session_state:
    st.session_state["mode"] = "single"  # Default mode

if "dataset_sessions" not in st.session_state:
    st.session_state["dataset_sessions"] = {}

if "compare_sessions" not in st.session_state:
    st.session_state["compare_sessions"] = {}

if "current_session" not in st.session_state:
    st.session_state["current_session"] = None

if "current_compare" not in st.session_state:
    st.session_state["current_compare"] = None

render_sidebar()

render_upload_area()

if st.session_state["mode"] == "single":
    render_single_tabs()

elif st.session_state["mode"] == "comparison":
    render_comparison_tabs()
    