import pandas as pd
from pathlib import Path
from functools import lru_cache

RENT_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "medianAskingRent_All.csv"
RESTAURANT_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "restaurant_data.csv"

# NYC ZIP code to neighborhood mapping
# A ZIP can map to multiple neighborhoods (shared boundaries)
ZIP_TO_NEIGHBORHOODS = {
    # Manhattan
    10001: ["Chelsea", "Flatiron"],
    10002: ["Lower East Side", "Chinatown"],
    10003: ["East Village", "Greenwich Village"],
    10004: ["Financial District"],
    10005: ["Financial District"],
    10006: ["Financial District"],
    10007: ["Tribeca", "Financial District"],
    10008: ["Financial District"],
    10009: ["East Village"],
    10010: ["Gramercy Park", "Flatiron"],
    10011: ["Chelsea", "Greenwich Village", "West Village"],
    10012: ["SoHo", "Greenwich Village", "Nolita", "Little Italy"],
    10013: ["Tribeca", "SoHo", "Chinatown"],
    10014: ["West Village", "Greenwich Village"],
    10016: ["Murray Hill", "Flatiron", "Midtown South"],
    10017: ["Midtown East", "Murray Hill"],
    10018: ["Midtown West", "Midtown South"],
    10019: ["Midtown West", "Midtown"],
    10020: ["Midtown West", "Midtown"],
    10021: ["Upper East Side"],
    10022: ["Midtown East"],
    10023: ["Upper West Side"],
    10024: ["Upper West Side"],
    10025: ["Upper West Side", "Morningside Heights"],
    10026: ["Harlem", "Central Harlem"],
    10027: ["Harlem", "Central Harlem", "Morningside Heights"],
    10028: ["Upper East Side"],
    10029: ["East Harlem"],
    10030: ["Harlem", "Central Harlem"],
    10031: ["Washington Heights", "Hamilton Heights", "West Harlem"],
    10032: ["Washington Heights"],
    10033: ["Washington Heights"],
    10034: ["Inwood"],
    10035: ["East Harlem"],
    10036: ["Midtown West", "Midtown"],
    10037: ["Harlem", "Central Harlem"],
    10038: ["Financial District"],
    10039: ["Harlem", "Central Harlem"],
    10040: ["Inwood", "Washington Heights"],
    10044: ["Roosevelt Island"],
    10055: ["Midtown East"],
    10065: ["Upper East Side"],
    10075: ["Upper East Side"],
    10128: ["Upper East Side"],
    10280: ["Battery Park City"],
    10282: ["Battery Park City"],
    # Brooklyn
    11201: ["Brooklyn Heights", "Downtown Brooklyn", "DUMBO"],
    11203: ["East Flatbush"],
    11204: ["Bensonhurst"],
    11205: ["Fort Greene", "Clinton Hill"],
    11206: ["Williamsburg", "Bushwick"],
    11207: ["Bushwick", "East New York"],
    11208: ["East New York"],
    11209: ["Bay Ridge"],
    11210: ["Flatbush", "Midwood"],
    11211: ["Williamsburg"],
    11212: ["Brownsville"],
    11213: ["Crown Heights"],
    11214: ["Bensonhurst", "Bath Beach"],
    11215: ["Park Slope", "Gowanus"],
    11216: ["Bedford-Stuyvesant"],
    11217: ["Park Slope", "Boerum Hill", "Prospect Heights"],
    11218: ["Borough Park", "Kensington"],
    11219: ["Borough Park"],
    11220: ["Sunset Park"],
    11221: ["Bedford-Stuyvesant", "Bushwick"],
    11222: ["Greenpoint"],
    11223: ["Gravesend"],
    11224: ["Coney Island"],
    11225: ["Crown Heights", "Prospect Lefferts Gardens"],
    11226: ["Flatbush", "Prospect Lefferts Gardens"],
    11228: ["Dyker Heights"],
    11229: ["Sheepshead Bay"],
    11230: ["Midwood"],
    11231: ["Carroll Gardens", "Cobble Hill", "Red Hook"],
    11232: ["Sunset Park", "Greenwood"],
    11233: ["Bedford-Stuyvesant"],
    11234: ["Bergen Beach"],
    11235: ["Brighton Beach", "Sheepshead Bay"],
    11236: ["Canarsie"],
    11237: ["Bushwick"],
    11238: ["Prospect Heights", "Crown Heights"],
    11239: ["East New York"],
    11249: ["Williamsburg"],
    # Queens
    11101: ["Long Island City"],
    11102: ["Astoria"],
    11103: ["Astoria"],
    11104: ["Sunnyside"],
    11105: ["Astoria"],
    11106: ["Astoria"],
    11109: ["Long Island City"],
    11354: ["Flushing"],
    11355: ["Flushing"],
    11356: ["College Point"],
    11357: ["Whitestone"],
    11358: ["Flushing"],
    11361: ["Bayside"],
    11364: ["Bayside", "Oakland Gardens"],
    11365: ["Fresh Meadows"],
    11366: ["Fresh Meadows"],
    11367: ["Kew Gardens Hills"],
    11368: ["Corona", "North Corona"],
    11369: ["East Elmhurst"],
    11370: ["East Elmhurst"],
    11372: ["Jackson Heights"],
    11373: ["Elmhurst"],
    11374: ["Rego Park"],
    11375: ["Forest Hills"],
    11377: ["Woodside"],
    11378: ["Maspeth"],
    11379: ["Middle Village"],
    11385: ["Ridgewood", "Glendale"],
    11414: ["Howard Beach"],
    11415: ["Kew Gardens"],
    11416: ["Ozone Park"],
    11417: ["Ozone Park"],
    11418: ["Richmond Hill"],
    11432: ["Jamaica"],
    11433: ["Jamaica"],
    11434: ["Jamaica"],
    11435: ["Jamaica", "Jamaica Estates"],
    11693: ["Rockaway All"],
    # Bronx
    10451: ["Mott Haven", "Concourse"],
    10452: ["Highbridge", "Concourse"],
    10453: ["Morris Heights"],
    10454: ["Mott Haven"],
    10455: ["Longwood"],
    10456: ["Morrisania", "Concourse"],
    10457: ["Tremont"],
    10458: ["Belmont", "Bedford Park"],
    10459: ["Longwood"],
    10460: ["West Farms"],
    10461: ["Westchester Square"],
    10462: ["Parkchester"],
    10463: ["Kingsbridge"],
    10464: ["City Island"],
    10465: ["Throgs Neck", "Pelham Bay"],
    10466: ["Wakefield", "Williamsbridge"],
    10467: ["Norwood", "Bedford Park"],
    10468: ["Fordham", "University Heights"],
    10469: ["Baychester"],
    10470: ["Woodlawn"],
    10471: ["Riverdale"],
    10472: ["Soundview"],
    10473: ["Soundview"],
    10474: ["Hunts Point"],
    10475: ["Co-op City"],
    # Staten Island
    10301: ["St. George"],
    10302: ["Port Richmond"],
    10303: ["Mariners Harbor"],
    10304: ["Stapleton"],
    10305: ["Rosebank"],
    10306: ["Midland Beach"],
    10307: ["Tottenville"],
    10308: ["Great Kills"],
    10309: ["Charleston"],
    10310: ["West Brighton"],
    10312: ["Eltingville"],
    10314: ["Heartland Village"],
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

    A restaurant in a ZIP that maps to multiple neighborhoods is counted for each.
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

    # Map ZIP codes to neighborhoods (one ZIP can map to multiple)
    a_grade["ZIPCODE"] = pd.to_numeric(a_grade["ZIPCODE"], errors="coerce")

    # Explode: each restaurant gets a row per neighborhood it maps to
    rows = []
    for _, row in a_grade.iterrows():
        zipcode = row["ZIPCODE"]
        if pd.notna(zipcode):
            neighborhoods = ZIP_TO_NEIGHBORHOODS.get(int(zipcode), [])
            for hood in neighborhoods:
                rows.append(hood)

    if not rows:
        # Full fallback: count by borough
        boro_map = {"MANHATTAN": "Manhattan", "BRONX": "Bronx",
                    "BROOKLYN": "Brooklyn", "QUEENS": "Queens",
                    "STATEN ISLAND": "Staten Island",
                    "1": "Manhattan", "2": "Bronx", "3": "Brooklyn",
                    "4": "Queens", "5": "Staten Island"}
        a_grade["Borough"] = a_grade["BORO"].str.upper().map(boro_map).fillna(a_grade["BORO"])
        borough_counts = a_grade.groupby("Borough").size().reset_index(name="restaurant_count")
        borough_counts.columns = ["Borough", "restaurant_count"]
        return borough_counts

    # Count per neighborhood
    neighborhood_series = pd.Series(rows)
    neighborhood_counts = neighborhood_series.value_counts().reset_index()
    neighborhood_counts.columns = ["areaName", "restaurant_count"]

    return neighborhood_counts


def get_recommendations(preferences=None, top_n=5, min_rent=None, max_rent=None, restaurant_importance=0):
    """Get neighborhood recommendations filtered by rent range and restaurant importance.

    Args:
        min_rent: Minimum rent budget
        max_rent: Maximum rent budget
        top_n: Number of recommendations to return
        restaurant_importance: 0-100 scale. 0 = rent-focused, 100 = restaurant-focused
    """
    # Clamp restaurant_importance to valid range
    restaurant_importance = max(0, min(100, restaurant_importance))

    df = load_data().copy()

    if min_rent is not None:
        df = df[df["rent"] >= min_rent]
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
