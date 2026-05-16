# India Macro Dashboard 📊

An interactive macroeconomic dashboard built as an **RBI DSIM Research Internship portfolio project**.

**Live demo:** [india-inflation-dashboard.onrender.com](https://india-inflation-dashboard.onrender.com)

---

## Project 1 — CPI Inflation Dashboard 🏷️

Tracks Consumer Price Index trends across Rural, Urban and Combined series from 2013 to 2025.

**Data source:** RBI DBIE · MoSPI
**Base year:** 2012 = 100

### What it shows
- **Monthly trend** — CPI index and YoY inflation for Rural, Urban and Combined series with RBI's 2–6% target band
- **Annual comparison** — Average inflation by year (2014–2025), grouped by Rural/Urban/Combined
- **Seasonal heatmap** — Year × month inflation matrix revealing seasonal patterns (monsoon effect, harvest cycles)
- **Category breakdown** — Latest month inflation across Food, Fuel, Housing, Clothing, Miscellaneous

### Key findings
- Inflation peaked at **9.4% average in 2013** and has structurally declined since RBI adopted flexible inflation targeting
- **Food inflation** is the primary driver of headline CPI volatility
- COVID years (2020–22) saw a resurgence driven by supply disruptions
- December 2025 combined inflation stands at **1.33%** — below the RBI lower bound of 2%

---

## Project 2 — Bank Credit Growth Analyser 🏦

Analyses deployment and growth of bank credit across sectors of the Indian economy.

**Data source:** RBI DBIE
**Coverage:** Fortnightly data 2010–2026 · Annual sectoral data 2019–2025

### What it shows
- **Monthly credit trend** — Outstanding bank credit and deposits (₹ Lakh Crore) with YoY growth rate
- **Sectoral breakdown** — Share of total credit deployed to Agriculture, Industry, Services, Personal Loans, NBFCs, Trade, Real Estate
- **Sectoral growth rates** — Year-on-year growth comparison across sectors

### Key findings
- Total bank credit stands at **₹212 Lakh Crore** (April 2026), growing at **16.6% YoY**
- **Personal loans** have been the fastest growing segment, raising RBI concern about retail credit concentration
- **Credit-Deposit ratio at 82%** — elevated compared to historical norms
- Industry credit growth has lagged services and retail, reflecting the shift in India's economic structure

---

## Architecture

```
notebook/
  data/
    raw/          ← CSVs downloaded from RBI DBIE
    processed/    ← cleaned JSONs (committed to repo, read by Streamlit)
  analysis.ipynb            ← Project 1 data pipeline
  credit_analysis.ipynb     ← Project 2 data pipeline

frontend/
  app.py                    ← Streamlit app
  components/               ← chart modules
```

Data flow: **Jupyter notebook → JSON → Streamlit** (no backend server needed)

---

## Local setup

```bash
pip install -r requirements.txt
streamlit run frontend/app.py
```

---

## Deploy (Render)

Start command:
```
streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true --server.enableCORS false --server.enableXsrfProtection false --browser.gatherUsageStats false
```

No environment variables required. Processed JSON files are committed to the repo so no data processing happens on the server.

---

## Data sources

| Dataset | Source | Frequency |
|---|---|---|
| CPI Rural/Urban/Combined | RBI DBIE → Statistics → Real Sector | Monthly |
| Sectoral Non-Food Bank Credit | RBI DBIE → Statistics → Financial Sector | Annual |
| SCB Business in India | RBI DBIE → Statistics → Banking | Fortnightly |

All data publicly available at [dbie.rbi.org.in](https://dbie.rbi.org.in)
