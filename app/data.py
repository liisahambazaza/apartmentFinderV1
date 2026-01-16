import pandas as pd
from pathlib import Path

RENT_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "medianAskingRent_All.csv"


def load_data():
    """Load the median rent CSV and extract the latest month's rent."""
    df = pd.read_csv(RENT_DATA_PATH)
    # Get the last month with data (rightmost numeric column)
    # Columns are: areaName, Borough, areaType, then YYYY-MM columns
    numeric_cols = df.columns[3:]  # Skip areaName, Borough, areaType
    latest_month_col = numeric_cols[-1]  # Last column is the latest month
    
    df = df[["areaName", "Borough", "areaType", latest_month_col]].copy()
    df.columns = ["areaName", "Borough", "areaType", "rent"]
    df["rent"] = pd.to_numeric(df["rent"], errors="coerce")
    df = df.dropna(subset=["rent"])  # Remove rows with no rent data
    return df


def get_recommendations(preferences=None, top_n=5, max_rent=None):
    """Get neighborhood recommendations filtered by max_rent budget."""
    df = load_data()
    
    # Filter by max_rent if provided
    if max_rent is not None:
        df = df[df["rent"] <= max_rent]
    
    # Sort by rent (descending) to show most expensive neighborhoods first (within budget)
    df = df.sort_values("rent", ascending=False).head(top_n)
    return df.to_dict(orient="records")
