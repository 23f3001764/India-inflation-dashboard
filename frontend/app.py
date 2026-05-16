import json
import sys
import streamlit as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

st.set_page_config(
    page_title="India Macro Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

from frontend.components import trend, annual, heatmap, categories
from frontend.components import credit_trend, credit_sectoral, credit_growth

DATA_DIR = ROOT / "notebook" / "data" / "processed"


@st.cache_data
def load(filename):
    with open(DATA_DIR / filename) as f:
        return json.load(f)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 India Macro Dashboard")
    st.markdown("**Source:** RBI DBIE · MoSPI")
    st.divider()

    project = st.radio("Project", ["🏷️ CPI Inflation", "🏦 Bank Credit"])
    st.divider()

    if project == "🏷️ CPI Inflation":
        page = st.radio("View", ["Overview", "Monthly Trend",
                                  "Annual Comparison", "Seasonal Heatmap",
                                  "Category Breakdown"])
    else:
        page = st.radio("View", ["Overview", "Monthly Credit Trend",
                                  "Sectoral Breakdown", "Sectoral Growth Rates"])
    st.divider()
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()


# ── PROJECT 1: CPI Inflation ──────────────────────────────────────────────────
if project == "🏷️ CPI Inflation":
    summary = load("summary.json")
    st.markdown(f"## 🏷️ CPI Inflation Dashboard")
    st.markdown(f"*Latest: {summary['latest_month']}*")
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


# ── PROJECT 2: Bank Credit ────────────────────────────────────────────────────
else:
    cs = load("credit_summary.json")
    st.markdown("## 🏦 Bank Credit Growth Dashboard")
    st.markdown(f"*Latest fortnight: {cs['latest_date']}  |  Sectoral data: March {cs['latest_sectoral_year']}*")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Bank Credit", f"₹{cs['total_credit_lakh_cr']} L.Cr")
    c2.metric("YoY Credit Growth", f"{cs['credit_growth_yoy']}%")
    c3.metric("Total Deposits", f"₹{cs['total_deposits_lakh_cr']} L.Cr")
    c4.metric("Credit-Deposit Ratio", f"{cs['cd_ratio']}%")
    st.divider()

    if page == "Monthly Credit Trend":
        credit_trend.render(load("credit_monthly.json"))
    elif page == "Sectoral Breakdown":
        credit_sectoral.render(load("credit_sectoral.json"), load("credit_sector_shares.json"))
    elif page == "Sectoral Growth Rates":
        credit_growth.render(load("credit_sectoral_growth.json"))
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Monthly Credit Trend")
            credit_trend.render(load("credit_monthly.json"), compact=True)
        with col2:
            st.markdown("#### Sector Shares")
            credit_sectoral.render(load("credit_sectoral.json"),
                                   load("credit_sector_shares.json"), compact=True)
        st.markdown("#### Sectoral Growth Rates")
        credit_growth.render(load("credit_sectoral_growth.json"), compact=True)
