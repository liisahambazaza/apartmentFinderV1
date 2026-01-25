import pandas as pd
from pathlib import Path

RENT_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "medianAskingRent_All.csv"
RESTAURANT_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "DOHMH_New_York_City_Restaurant_Inspection_Results_20260125.csv"

def load_food_data():
    """Load the restaurant CSV and return as DataFrame. Returns None if file doesn't exist."""
    if not RESTAURANT_DATA_PATH.exists():
        print(f"Warning: Restaurant data file not found at {RESTAURANT_DATA_PATH}")
        return None
    df = pd.read_csv(RESTAURANT_DATA_PATH)
    return df

def load_data():
    """Load the median rent CSV and extract the latest month's rent."""
    df = pd.read_csv(RENT_DATA_PATH)
    numeric_cols = df.columns[3:]
    latest_month_col = numeric_cols[-1]
    
    df = df[["areaName", "Borough", "areaType", latest_month_col]].copy()
    df.columns = ["areaName", "Borough", "areaType", "rent"]
    df["rent"] = pd.to_numeric(df["rent"], errors="coerce")
    df = df.dropna(subset=["rent"])
    return df

def get_restaurant_counts_by_neighborhood():
    """Count A-grade restaurants per borough."""
    restaurants = load_food_data()
    
    if restaurants is None:
        return pd.DataFrame(columns=["Borough", "restaurant_count"])
    
    # Filter for A-grade restaurants only
    a_grade_restaurants = restaurants[restaurants["GRADE"] == "A"]
    
    # Count by BORO (borough)
    restaurant_counts = a_grade_restaurants.groupby("BORO").size().reset_index(name="restaurant_count")
    restaurant_counts.columns = ["Borough", "restaurant_count"]
    
    return restaurant_counts

def get_recommendations(preferences=None, top_n=5, max_rent=None, restaurant_importance=0):
    """Get neighborhood recommendations filtered by max_rent budget and restaurant importance.
    
    Args:
        max_rent: Maximum rent budget
        top_n: Number of recommendations to return
        restaurant_importance: 0-100 scale. 0 = rent-focused, 100 = restaurant-focused
    """
    df = load_data()
    
    if max_rent is not None:
        df = df[df["rent"] <= max_rent]
    
    # Load restaurant data and merge
    restaurant_counts = get_restaurant_counts_by_neighborhood()
    df = df.merge(restaurant_counts, on="Borough", how="left")
    df["restaurant_count"] = df["restaurant_count"].fillna(0)
    
    # Normalize scores for weighted ranking
    # Lower rent is better, so invert the score
    max_rent_val = df["rent"].max()
    df["rent_score"] = (max_rent_val - df["rent"]) / max_rent_val
    
    # Higher restaurant count is better
    max_restaurants = df["restaurant_count"].max()
    if max_restaurants > 0:
        df["restaurant_score"] = df["restaurant_count"] / max_restaurants
    else:
        df["restaurant_score"] = 0
    
    # Weighted combination based on restaurant importance
    importance_weight = restaurant_importance / 100.0
    df["combined_score"] = ((1 - importance_weight) * df["rent_score"] + 
                             importance_weight * df["restaurant_score"])
    
    # Sort by combined score (descending)
    df = df.sort_values("combined_score", ascending=False).head(top_n)
    
    return df.to_dict(orient="records")
