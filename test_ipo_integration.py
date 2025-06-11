import streamlit as st
from components.ipo_tracker import IPOTracker

st.set_page_config(page_title="IPO Test", layout="wide")
st.title("IPO Tracker Test")

tracker = IPOTracker()
tracker.render_ipo_tracker()
