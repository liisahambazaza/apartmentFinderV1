"""Unit tests for app.data module — recommendation engine and data loading."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.data import (
    load_data,
    load_food_data,
    get_restaurant_counts_by_neighborhood,
    get_recommendations,
    ZIP_TO_NEIGHBORHOODS,
)


class TestLoadData:
    """Tests for rent data loading."""

    def test_load_data_returns_dataframe(self):
        df = load_data()
        assert df is not None
        assert len(df) > 0

    def test_load_data_has_required_columns(self):
        df = load_data()
        required = {"areaName", "Borough", "areaType", "rent"}
        assert required.issubset(set(df.columns))

    def test_load_data_rent_is_numeric(self):
        df = load_data()
        assert df["rent"].dtype == float

    def test_load_data_no_null_rents(self):
        df = load_data()
        assert df["rent"].isna().sum() == 0

    def test_load_data_has_multiple_boroughs(self):
        df = load_data()
        boroughs = df["Borough"].dropna().unique()
        assert len(boroughs) >= 4  # Manhattan, Brooklyn, Queens, Bronx at minimum


class TestLoadFoodData:
    """Tests for restaurant data loading."""

    def test_load_food_data_returns_dataframe_or_none(self):
        result = load_food_data()
        # Either a DataFrame with data or None if file missing
        if result is not None:
            assert len(result) >= 0

    def test_load_food_data_has_required_columns(self):
        result = load_food_data()
        if result is not None and len(result) > 0:
            # Column names should exist (case may vary)
            cols_upper = [c.upper() for c in result.columns]
            assert "CAMIS" in cols_upper or "camis" in result.columns
            assert "GRADE" in cols_upper or "grade" in result.columns
            assert "ZIPCODE" in cols_upper or "zipcode" in result.columns


class TestZipMapping:
    """Tests for ZIP-to-neighborhood mapping."""

    def test_mapping_is_not_empty(self):
        assert len(ZIP_TO_NEIGHBORHOODS) > 50

    def test_all_values_are_lists(self):
        for zipcode, neighborhoods in ZIP_TO_NEIGHBORHOODS.items():
            assert isinstance(neighborhoods, list), f"ZIP {zipcode} value is not a list"
            assert len(neighborhoods) > 0, f"ZIP {zipcode} has empty neighborhood list"

    def test_key_neighborhoods_are_mapped(self):
        """Critical Manhattan neighborhoods that should have at least one ZIP mapped."""
        all_neighborhoods = set()
        for hoods in ZIP_TO_NEIGHBORHOODS.values():
            all_neighborhoods.update(hoods)

        must_have = [
            "Chelsea", "Greenwich Village", "East Village", "West Village",
            "SoHo", "Tribeca", "Flatiron", "Midtown West", "Midtown East",
            "Upper East Side", "Upper West Side", "Harlem", "Williamsburg",
            "Park Slope", "Astoria", "Flushing", "Bedford Park"
        ]
        for name in must_have:
            assert name in all_neighborhoods, f"{name} not in any ZIP mapping"

    def test_zip_codes_are_valid_nyc(self):
        """All ZIP codes should be in valid NYC ranges."""
        for zipcode in ZIP_TO_NEIGHBORHOODS.keys():
            assert isinstance(zipcode, int)
            # NYC ZIPs: Manhattan 100xx, Bronx 104xx, Brooklyn 112xx, Queens 11xxx, SI 103xx
            valid = (10000 <= zipcode <= 10499) or (11000 <= zipcode <= 11999)
            assert valid, f"ZIP {zipcode} doesn't look like a NYC ZIP code"


class TestRestaurantCounts:
    """Tests for restaurant counting by neighborhood."""

    def test_returns_dataframe(self):
        counts = get_restaurant_counts_by_neighborhood()
        assert counts is not None

    def test_has_required_columns(self):
        counts = get_restaurant_counts_by_neighborhood()
        assert "areaName" in counts.columns or "Borough" in counts.columns
        assert "restaurant_count" in counts.columns

    def test_counts_are_non_negative(self):
        counts = get_restaurant_counts_by_neighborhood()
        assert (counts["restaurant_count"] >= 0).all()

    def test_greenwich_village_has_restaurants(self):
        """Regression: Greenwich Village was previously missing."""
        counts = get_restaurant_counts_by_neighborhood()
        if "areaName" in counts.columns:
            gv = counts[counts["areaName"] == "Greenwich Village"]
            assert len(gv) > 0, "Greenwich Village missing from restaurant counts"
            assert gv.iloc[0]["restaurant_count"] > 0

    def test_flatiron_has_restaurants(self):
        """Regression: Flatiron was previously missing."""
        counts = get_restaurant_counts_by_neighborhood()
        if "areaName" in counts.columns:
            fl = counts[counts["areaName"] == "Flatiron"]
            assert len(fl) > 0, "Flatiron missing from restaurant counts"
            assert fl.iloc[0]["restaurant_count"] > 0


class TestGetRecommendations:
    """Tests for the recommendation engine."""

    def test_returns_list(self):
        recs = get_recommendations(max_rent=3000)
        assert isinstance(recs, list)

    def test_default_returns_results(self):
        recs = get_recommendations(max_rent=5000, top_n=5)
        assert len(recs) > 0

    def test_respects_top_n(self):
        recs = get_recommendations(max_rent=5000, top_n=3)
        assert len(recs) <= 3

    def test_respects_max_rent(self):
        max_rent = 2500
        recs = get_recommendations(max_rent=max_rent, top_n=10)
        for r in recs:
            assert r["rent"] <= max_rent, f"{r['areaName']} rent {r['rent']} exceeds max {max_rent}"

    def test_respects_min_rent(self):
        min_rent = 2000
        recs = get_recommendations(min_rent=min_rent, max_rent=5000, top_n=10)
        for r in recs:
            assert r["rent"] >= min_rent, f"{r['areaName']} rent {r['rent']} below min {min_rent}"

    def test_min_and_max_rent_range(self):
        """Results should be within the specified range."""
        recs = get_recommendations(min_rent=2500, max_rent=3500, top_n=10)
        for r in recs:
            assert 2500 <= r["rent"] <= 3500, f"{r['areaName']} rent {r['rent']} outside range"

    def test_empty_when_budget_too_low(self):
        recs = get_recommendations(max_rent=100, top_n=5)
        assert recs == []

    def test_empty_when_min_exceeds_max(self):
        recs = get_recommendations(min_rent=5000, max_rent=1000, top_n=5)
        assert recs == []

    def test_restaurant_importance_zero_is_rent_focused(self):
        """At 0% restaurant importance, cheapest should rank first."""
        recs = get_recommendations(max_rent=5000, top_n=10, restaurant_importance=0)
        if len(recs) >= 2:
            # First result should have rent <= second result (cheapest first)
            assert recs[0]["rent"] <= recs[1]["rent"]

    def test_restaurant_importance_100_is_food_focused(self):
        """At 100% restaurant importance, most restaurants should rank first."""
        recs = get_recommendations(max_rent=5000, top_n=10, restaurant_importance=100)
        if len(recs) >= 2:
            assert recs[0]["restaurant_count"] >= recs[1]["restaurant_count"]

    def test_restaurant_importance_clamped_high(self):
        """Values above 100 should be clamped, not crash."""
        recs = get_recommendations(max_rent=5000, top_n=5, restaurant_importance=200)
        assert isinstance(recs, list)
        assert len(recs) > 0

    def test_restaurant_importance_clamped_low(self):
        """Negative values should be clamped, not crash."""
        recs = get_recommendations(max_rent=5000, top_n=5, restaurant_importance=-50)
        assert isinstance(recs, list)
        assert len(recs) > 0

    def test_results_have_required_fields(self):
        recs = get_recommendations(max_rent=4000, top_n=3)
        for r in recs:
            assert "areaName" in r
            assert "Borough" in r
            assert "rent" in r
            assert "restaurant_count" in r
            assert "combined_score" in r

    def test_combined_score_between_0_and_1(self):
        recs = get_recommendations(max_rent=5000, top_n=10, restaurant_importance=50)
        for r in recs:
            assert 0 <= r["combined_score"] <= 1, f"Score {r['combined_score']} out of range"

    def test_results_sorted_by_combined_score(self):
        recs = get_recommendations(max_rent=5000, top_n=10, restaurant_importance=50)
        scores = [r["combined_score"] for r in recs]
        assert scores == sorted(scores, reverse=True)

    def test_manhattan_appears_at_higher_budgets(self):
        """Regression: Manhattan neighborhoods should show up at higher budgets."""
        recs = get_recommendations(min_rent=4000, max_rent=6000, top_n=10, restaurant_importance=50)
        boroughs = [r["Borough"] for r in recs]
        assert "Manhattan" in boroughs, "Manhattan missing at $4000-6000 budget"
