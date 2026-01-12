import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_nyc.csv"


def load_data():
    df = pd.read_csv(DATA_PATH)
    return df


def score_df(df):
    cols = ["rent", "crime_rate", "transit_score", "school_score", "walk_score"]
    norm = df[cols].astype(float).copy()
    for c in cols:
        v = norm[c]
        norm[c] = (v - v.min()) / (v.max() - v.min()) if v.max() != v.min() else 0

    score = (
        (1 - norm["rent"]) * 0.3
        + (1 - norm["crime_rate"]) * 0.25
        + norm["transit_score"] * 0.2
        + norm["school_score"] * 0.15
        + norm["walk_score"] * 0.1
    )

    out = df.copy()
    out["score"] = score
    return out


def get_recommendations(preferences=None, top_n=5):
    df = load_data()
    df = score_df(df)
    top = df.sort_values("score", ascending=False).head(top_n)
    return top.to_dict(orient="records")
