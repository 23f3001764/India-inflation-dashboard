from fastapi import APIRouter, HTTPException
from typing import List
from backend.schemas.models import (
    Summary, TrendPoint, AnnualPoint, HeatmapPoint, CategoryPoint
)
from backend.services import data_loader

router = APIRouter()


@router.get("/summary", response_model=Summary)
def summary():
    """Key headline numbers — latest inflation, peak year, rural/urban gap."""
    try:
        return data_loader.get_summary()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/trend", response_model=List[TrendPoint])
def trend():
    """Monthly CPI index and YoY inflation — rural, urban, combined."""
    try:
        return data_loader.get_trend()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/annual", response_model=List[AnnualPoint])
def annual():
    """Average annual inflation by year (2014 onwards)."""
    try:
        return data_loader.get_annual()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/heatmap", response_model=List[HeatmapPoint])
def heatmap():
    """YoY inflation by year × month — for seasonal pattern heatmap."""
    try:
        return data_loader.get_heatmap()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/categories", response_model=List[CategoryPoint])
def categories():
    """Category-wise inflation breakdown for the latest available month."""
    try:
        return data_loader.get_categories()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/refresh-cache")
def refresh_cache():
    """Clear in-memory cache so re-run notebook data is picked up."""
    data_loader.clear_cache()
    return {"message": "Cache cleared. Next request will reload from disk."}
