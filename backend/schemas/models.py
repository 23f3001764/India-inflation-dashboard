from pydantic import BaseModel
from typing import Optional


class Summary(BaseModel):
    latest_month: str
    latest_combined_inflation: Optional[float]
    latest_rural_inflation: Optional[float]
    latest_urban_inflation: Optional[float]
    latest_food_inflation: Optional[float]
    peak_year: int
    peak_inflation: float
    rural_urban_gap: Optional[float]


class TrendPoint(BaseModel):
    date: str
    rural_index: Optional[float]
    urban_index: Optional[float]
    combined_index: Optional[float]
    rural_inflation: Optional[float]
    urban_inflation: Optional[float]
    combined_inflation: Optional[float]


class AnnualPoint(BaseModel):
    year: int
    avg_combined: Optional[float]
    avg_rural: Optional[float]
    avg_urban: Optional[float]


class HeatmapPoint(BaseModel):
    year: int
    month: str
    inflation: float


class CategoryPoint(BaseModel):
    category: str
    index_val: Optional[float]
    inflation: Optional[float]
