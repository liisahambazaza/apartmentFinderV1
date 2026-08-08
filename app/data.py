import pandas as pd
from pathlib import Path
from functools import lru_cache

RENT_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "medianAskingRent_All.csv"
RESTAURANT_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "restaurant_data.csv"

# NYC ZIP code to neighborhood mapping (covers major neighborhoods in the rent dataset)
# Source: approximate groupings based on USPS/NYC planning data
ZIP_TO_NEIGHBORHOOD = {
    # Manhattan
    10001: "Chelsea", 10011: "Chelsea", 10018: "Chelsea",
    10002: "Lower East Side", 10003: "East Village", 10009: "East Village",
    10004: "Financial District", 10005: "Financial District", 10006: "Financial District",
    10007: "Tribeca", 10013: "Tribeca",
    10010: "Gramercy Park", 10016: "Murray Hill", 10017: "Murray Hill",
    10012: "SoHo", 10014: "West Village", 10012: "SoHo",
    10019: "Midtown West", 10020: "Midtown West", 10036: "Midtown West",
    10022: "Midtown East", 10017: "Midtown East", 10055: "Midtown East",
    10021: "Upper East Side", 10028: "Upper East Side", 10065: "Upper East Side",
    10075: "Upper East Side", 10128: "Upper East Side",
    10023: "Upper West Side", 10024: "Upper West Side", 10025: "Upper West Side",
    10026: "Harlem", 10027: "Harlem", 10030: "Harlem", 10037: "Harlem",
    10029: "East Harlem", 10035: "East Harlem",
    10031: "Washington Heights", 10032: "Washington Heights", 10033: "Washington Heights",
    10034: "Inwood", 10040: "Inwood",
    10038: "Seaport", 10008: "Financial District",
    10280: "Battery Park City", 10282: "Battery Park City",
    # Brooklyn
    11201: "Brooklyn Heights", 11231: "Carroll Gardens", 11215: "Park Slope",
    11217: "Park Slope", 11238: "Prospect Heights",
    11211: "Williamsburg", 11249: "Williamsburg", 11206: "Williamsburg",
    11222: "Greenpoint",
    11205: "Fort Greene", 11216: "Bedford-Stuyvesant", 11221: "Bedford-Stuyvesant",
    11233: "Bedford-Stuyvesant",
    11225: "Crown Heights", 11213: "Crown Heights",
    11226: "Flatbush", 11210: "Flatbush", 11203: "East Flatbush",
    11220: "Sunset Park", 11232: "Sunset Park",
    11209: "Bay Ridge", 11214: "Bensonhurst", 11204: "Bensonhurst",
    11219: "Borough Park", 11218: "Borough Park",
    11229: "Sheepshead Bay", 11235: "Brighton Beach",
    11207: "Bushwick", 11237: "Bushwick",
    11208: "East New York", 11239: "East New York",
    11234: "Bergen Beach", 11236: "Canarsie",
    # Queens
    11101: "Long Island City", 11109: "Long Island City", 11106: "Astoria",
    11102: "Astoria", 11103: "Astoria", 11105: "Astoria",
    11104: "Sunnyside", 11377: "Woodside",
    11372: "Jackson Heights", 11373: "Elmhurst",
    11354: "Flushing", 11355: "Flushing", 11358: "Flushing",
    11375: "Forest Hills", 11374: "Rego Park",
    11385: "Ridgewood", 11379: "Middle Village",
    11416: "Ozone Park", 11417: "Ozone Park",
    11432: "Jamaica", 11433: "Jamaica", 11434: "Jamaica",
    11361: "Bayside", 11364: "Bayside",
    11414: "Howard Beach", 11693: "Rockaway",
    # Bronx
    10451: "Mott Haven", 10452: "Highbridge", 10453: "Morris Heights",
    10454: "Mott Haven", 10455: "Longwood",
    10456: "Morrisania", 10457: "Tremont", 10458: "Belmont",
    10459: "Longwood", 10460: "West Farms",
    10461: "Westchester Square", 10462: "Parkchester",
    10463: "Kingsbridge", 10464: "City Island",
    10465: "Throgs Neck", 10466: "Wakefield",
    10467: "Norwood", 10468: "Fordham",
    10469: "Baychester", 10470: "Woodlawn",
    10471: "Riverdale", 10472: "Soundview",
    10473: "Soundview", 10474: "Hunts Point",
    10475: "Co-op City",
    # Staten Island
    10301: "St. George", 10302: "Port Richmond",
    10303: "Mariners Harbor", 10304: "Stapleton",
    10305: "Rosebank", 10306: "Midland Beach",
    10307: "Tottenville", 10308: "Great Kills",
    10309: "Charleston", 10310: "West Brighton",
    10312: "Eltingville", 10314: "Heartland Village",
}


@lru_cache(maxsize=1)
def load_food_data():
    """Load the restaurant CSV and return as DataFrame. Cached after first call."""
    if not RESTAURANT_DATA_PATH.exists():
        print(f"Warning: Restaurant data file not found at {RESTAURANT_DATA_PATH}")
        return None
    df = pd.read_csv(RESTAURANT_DATA_PATH)
    if df.empty:
        return None
    return df


@lru_cache(maxsize=1)
def load_data():
    """Load the median rent CSV and extract the latest month's rent. Cached after first call."""
    df = pd.read_csv(RENT_DATA_PATH)
    numeric_cols = df.columns[3:]
    latest_month_col = numeric_cols[-1]

    df = df[["areaName", "Borough", "areaType", latest_month_col]].copy()
    df.columns = ["areaName", "Borough", "areaType", "rent"]
    df["rent"] = pd.to_numeric(df["rent"], errors="coerce")
    df = df.dropna(subset=["rent"])
    return df


@lru_cache(maxsize=1)
def get_restaurant_counts_by_neighborhood():
    """Count unique A-grade restaurants per neighborhood using ZIP-to-neighborhood mapping.

    Falls back to borough-level counts if ZIP mapping doesn't produce matches.
    """
    restaurants = load_food_data()

    if restaurants is None:
        return pd.DataFrame(columns=["areaName", "restaurant_count"])

    # Normalize column names to handle both uppercase and lowercase CSVs
    restaurants.columns = restaurants.columns.str.upper()

    # Filter for A-grade restaurants only
    if "GRADE" in restaurants.columns:
        a_grade = restaurants[restaurants["GRADE"] == "A"].copy()
    else:
        a_grade = restaurants.copy()

    if a_grade.empty:
        return pd.DataFrame(columns=["areaName", "restaurant_count"])

    # Deduplicate by restaurant ID (CAMIS) to count unique restaurants
    a_grade = a_grade.drop_duplicates(subset="CAMIS")

    # Map ZIP codes to neighborhoods
    a_grade["ZIPCODE"] = pd.to_numeric(a_grade["ZIPCODE"], errors="coerce")
    a_grade["neighborhood"] = a_grade["ZIPCODE"].map(ZIP_TO_NEIGHBORHOOD)

    # Count unique restaurants per neighborhood (from ZIP mapping)
    neighborhood_counts = (
        a_grade[a_grade["neighborhood"].notna()]
        .groupby("neighborhood")
        .size()
        .reset_index(name="restaurant_count")
    )
    neighborhood_counts.columns = ["areaName", "restaurant_count"]

    # If ZIP mapping produced no results, fall back to borough-level
    if neighborhood_counts.empty:
        boro_map = {"Manhattan": "Manhattan", "Bronx": "Bronx",
                    "Brooklyn": "Brooklyn", "Queens": "Queens",
                    "Staten Island": "Staten Island",
                    "1": "Manhattan", "2": "Bronx", "3": "Brooklyn",
                    "4": "Queens", "5": "Staten Island"}
        a_grade["Borough"] = a_grade["BORO"].map(boro_map).fillna(a_grade["BORO"])
        borough_counts = a_grade.groupby("Borough").size().reset_index(name="restaurant_count")
        borough_counts.columns = ["Borough", "restaurant_count"]
        return borough_counts

    return neighborhood_counts


def get_recommendations(preferences=None, top_n=5, max_rent=None, restaurant_importance=0):
    """Get neighborhood recommendations filtered by max_rent budget and restaurant importance.

    Args:
        max_rent: Maximum rent budget
        top_n: Number of recommendations to return
        restaurant_importance: 0-100 scale. 0 = rent-focused, 100 = restaurant-focused
    """
    # Clamp restaurant_importance to valid range
    restaurant_importance = max(0, min(100, restaurant_importance))

    df = load_data().copy()

    if max_rent is not None:
        df = df[df["rent"] <= max_rent]

    if df.empty:
        return []

    # Load restaurant counts and merge
    restaurant_counts = get_restaurant_counts_by_neighborhood()

    if "areaName" in restaurant_counts.columns:
        # Neighborhood-level merge
        df = df.merge(restaurant_counts, on="areaName", how="left")
    elif "Borough" in restaurant_counts.columns:
        # Fallback: borough-level merge
        df = df.merge(restaurant_counts, on="Borough", how="left")

    df["restaurant_count"] = df["restaurant_count"].fillna(0)

    # Normalize scores for weighted ranking
    # Lower rent is better, so invert the score
    max_rent_val = df["rent"].max()
    min_rent_val = df["rent"].min()
    rent_range = max_rent_val - min_rent_val
    if rent_range > 0:
        df["rent_score"] = (max_rent_val - df["rent"]) / rent_range
    else:
        df["rent_score"] = 1.0

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
