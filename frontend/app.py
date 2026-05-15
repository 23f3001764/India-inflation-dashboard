import json
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="India Inflation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

from frontend.pages import trend, annual, heatmap, categories

# Load JSON directly — no API call needed
DATA_DIR = Path(__file__).resolve().parent.parent / "notebook" / "data" / "processed"

@st.cache_data
def load(filename):
    with open(DATA_DIR / filename) as f:
        return json.load(f)

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

summary = load("summary.json")
if summary:
    st.markdown(f"### Latest: {summary['latest_month']}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Combined inflation", f"{summary['latest_combined_inflation']}%")
    c2.metric("Food inflation", f"{summary['latest_food_inflation']}%")
    c3.metric("Rural vs urban gap", f"{summary['rural_urban_gap']}pp")
    c4.metric("Peak year avg", f"{summary['peak_inflation']}%", f"{summary['peak_year']}")
    st.divider()

if page == "Monthly Trend":
    trend.render(load("trend.json"))
elif page == "Annual Comparison":
    annual.render(load("annual.json"))
elif page == "Seasonal Heatmap":
    heatmap.render(load("heatmap.json"))
elif page == "Category Breakdown":
    categories.render(load("categories.json"))
else:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Monthly CPI index")
        trend.render(load("trend.json"), compact=True)
    with col2:
        st.markdown("#### Annual avg inflation")
        annual.render(load("annual.json"), compact=True)
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### Seasonal heatmap")
        heatmap.render(load("heatmap.json"), compact=True)
    with col4:
        st.markdown("#### Category breakdown")
        categories.render(load("categories.json"), compact=True)
