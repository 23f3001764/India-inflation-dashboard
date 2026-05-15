import os
import streamlit as st

st.set_page_config(
    page_title="India Inflation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

import requests
from frontend.pages import trend, annual, heatmap, categories

# On Render: API_BASE is set by main.py to http://localhost:8000/api
# Locally with separate terminals: set API_BASE env var or use default
API_BASE = os.environ.get("API_BASE", "http://localhost:8000/api")


@st.cache_data(ttl=300)
def fetch(endpoint: str):
    try:
        r = requests.get(f"{API_BASE}/{endpoint}", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API error on /{endpoint}: {e}")
        return None


with st.sidebar:
    st.markdown("## 📊 India CPI Dashboard")
    st.markdown("**Source:** RBI DBIE · MoSPI")
    st.markdown("**Base year:** 2012 = 100")
    st.divider()
    page = st.radio("View", ["Overview", "Monthly Trend",
                              "Annual Comparison", "Seasonal Heatmap",
                              "Category Breakdown"])
    st.divider()
    if st.button("🔄 Refresh data"):
        st.cache_data.clear()
        st.rerun()

summary = fetch("summary")
if summary:
    st.markdown(f"### Latest: {summary['latest_month']}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Combined inflation", f"{summary['latest_combined_inflation']}%")
    c2.metric("Food inflation", f"{summary['latest_food_inflation']}%")
    c3.metric("Rural vs urban gap", f"{summary['rural_urban_gap']}pp")
    c4.metric("Peak year avg", f"{summary['peak_inflation']}%", f"{summary['peak_year']}")
    st.divider()

if page == "Monthly Trend":
    data = fetch("trend")
    if data: trend.render(data)

elif page == "Annual Comparison":
    data = fetch("annual")
    if data: annual.render(data)

elif page == "Seasonal Heatmap":
    data = fetch("heatmap")
    if data: heatmap.render(data)

elif page == "Category Breakdown":
    data = fetch("categories")
    if data: categories.render(data)

else:
    col1, col2 = st.columns(2)
    with col1:
        t = fetch("trend")
        if t:
            st.markdown("#### Monthly CPI index")
            trend.render(t, compact=True)
    with col2:
        a = fetch("annual")
        if a:
            st.markdown("#### Annual avg inflation")
            annual.render(a, compact=True)
    col3, col4 = st.columns(2)
    with col3:
        h = fetch("heatmap")
        if h:
            st.markdown("#### Seasonal heatmap")
            heatmap.render(h, compact=True)
    with col4:
        cat = fetch("categories")
        if cat:
            st.markdown("#### Category breakdown")
            categories.render(cat, compact=True)
