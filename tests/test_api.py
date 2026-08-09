"""Unit tests for the FastAPI API endpoints."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestIndexEndpoint:
    """Tests for the homepage."""

    def test_index_returns_200(self):
        response = client.get("/")
        assert response.status_code == 200

    def test_index_returns_html(self):
        response = client.get("/")
        assert "text/html" in response.headers["content-type"]

    def test_index_contains_title(self):
        response = client.get("/")
        assert "NYC Apartment Recommender" in response.text

    def test_index_contains_map(self):
        response = client.get("/")
        assert "leaflet" in response.text

    def test_index_contains_budget_sliders(self):
        response = client.get("/")
        assert "minBudgetSlider" in response.text
        assert "maxBudgetSlider" in response.text

    def test_index_contains_restaurant_slider(self):
        response = client.get("/")
        assert "restaurantSlider" in response.text


class TestRecommendEndpoint:
    """Tests for the /api/recommend endpoint."""

    def test_recommend_returns_200(self):
        response = client.get("/api/recommend")
        assert response.status_code == 200

    def test_recommend_returns_json(self):
        response = client.get("/api/recommend")
        assert "application/json" in response.headers["content-type"]

    def test_recommend_has_recommendations_key(self):
        response = client.get("/api/recommend")
        data = response.json()
        assert "recommendations" in data

    def test_recommend_default_params(self):
        response = client.get("/api/recommend")
        data = response.json()
        recs = data["recommendations"]
        assert isinstance(recs, list)
        assert len(recs) <= 5  # default top_n

    def test_recommend_with_max_rent(self):
        response = client.get("/api/recommend?max_rent=2500&top_n=5")
        data = response.json()
        recs = data["recommendations"]
        for r in recs:
            assert r["rent"] <= 2500

    def test_recommend_with_min_rent(self):
        response = client.get("/api/recommend?min_rent=2000&max_rent=5000&top_n=5")
        data = response.json()
        recs = data["recommendations"]
        for r in recs:
            assert r["rent"] >= 2000

    def test_recommend_with_budget_range(self):
        response = client.get("/api/recommend?min_rent=2500&max_rent=3500&top_n=10")
        data = response.json()
        recs = data["recommendations"]
        for r in recs:
            assert 2500 <= r["rent"] <= 3500

    def test_recommend_with_restaurant_importance(self):
        response = client.get("/api/recommend?max_rent=5000&top_n=5&restaurant_importance=100")
        data = response.json()
        recs = data["recommendations"]
        assert len(recs) > 0
        # At 100% importance, results should be sorted by restaurant count
        counts = [r["restaurant_count"] for r in recs]
        assert counts == sorted(counts, reverse=True)

    def test_recommend_top_n_respected(self):
        response = client.get("/api/recommend?max_rent=5000&top_n=3")
        data = response.json()
        assert len(data["recommendations"]) <= 3

    def test_recommend_no_results_for_low_budget(self):
        response = client.get("/api/recommend?max_rent=100&top_n=5")
        data = response.json()
        assert data["recommendations"] == []

    def test_recommend_invalid_restaurant_importance_handled(self):
        """Values outside 0-100 should not crash the API."""
        response = client.get("/api/recommend?max_rent=5000&restaurant_importance=999")
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data

    def test_recommend_results_have_all_fields(self):
        response = client.get("/api/recommend?max_rent=4000&top_n=3")
        data = response.json()
        for r in data["recommendations"]:
            assert "areaName" in r
            assert "Borough" in r
            assert "rent" in r
            assert "restaurant_count" in r
            assert "combined_score" in r


class TestStaticFiles:
    """Tests for static file serving."""

    def test_geojson_served(self):
        response = client.get("/static/nyc-neighborhoods.geojson")
        assert response.status_code == 200
        assert "FeatureCollection" in response.text
