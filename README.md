# India CPI Inflation Dashboard

End-to-end CPI data pipeline and interactive dashboard — **RBI DSIM internship portfolio, Project 1**.

## Architecture

```
notebook/      Jupyter: CSV → clean → export JSON
backend/       FastAPI: REST API at /api/*
frontend/      Streamlit: dashboard (proxied through FastAPI)
```

Single process on Render: FastAPI starts Streamlit as a subprocess and reverse-proxies all non-API traffic to it. One port, one deploy.

## Local setup

```bash
pip install -r requirements.txt

# Step 1: run the notebook to generate processed data
cd notebook && jupyter notebook analysis.ipynb
# Run all cells → data/processed/*.json

# Step 2: start the app (both API + dashboard)
cd ..
uvicorn backend.main:app --reload --port 8000
```

Open http://localhost:8000 → dashboard  
Open http://localhost:8000/docs → API explorer

## Deploy to Render (free tier)

1. Push this repo to GitHub
2. Go to render.com → New → Web Service → connect your repo
3. Render auto-detects `render.yaml` and deploys with one click
4. Your app is live at `https://your-app-name.onrender.com`

> **Before deploying:** make sure `notebook/data/processed/*.json` files are committed to the repo (they are the pre-processed data the API reads).

## API endpoints

| Endpoint | Description |
|---|---|
| `GET /api/summary` | Latest KPIs |
| `GET /api/trend` | Monthly CPI index + YoY inflation |
| `GET /api/annual` | Average annual inflation by year |
| `GET /api/heatmap` | Year × month inflation (seasonal) |
| `GET /api/categories` | Category-wise breakdown, latest month |
| `POST /api/refresh-cache` | Reload JSON from disk |

## Data sources

- **CPI Rural/Urban/Combined** — RBI DBIE (Base 2012=100, Jan 2013–Dec 2025)
- **CPI Industrial Workers** — Labour Bureau via RBI DBIE
