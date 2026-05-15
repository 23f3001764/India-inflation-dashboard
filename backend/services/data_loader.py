import json
from pathlib import Path
from functools import lru_cache

# Resolve path relative to repo root regardless of where uvicorn is launched
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "notebook" / "data" / "processed"


def _load(filename: str):
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"{filename} not found. "
            "Run the notebook first: notebook/analysis.ipynb"
        )
    with open(path) as f:
        return json.load(f)


@lru_cache(maxsize=None)
def get_summary():
    return _load("summary.json")


@lru_cache(maxsize=None)
def get_trend():
    return _load("trend.json")


@lru_cache(maxsize=None)
def get_annual():
    return _load("annual.json")


@lru_cache(maxsize=None)
def get_heatmap():
    return _load("heatmap.json")


@lru_cache(maxsize=None)
def get_categories():
    return _load("categories.json")


def clear_cache():
    """Call this if you re-run the notebook and want fresh data."""
    get_summary.cache_clear()
    get_trend.cache_clear()
    get_annual.cache_clear()
    get_heatmap.cache_clear()
    get_categories.cache_clear()
