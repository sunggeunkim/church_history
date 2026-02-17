"""Tests for Interactive Canvas backend (P5).

The canvas feature relies on the existing eras API with caching optimization.
"""

import pytest
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.eras.models import Era, KeyEvent, KeyFigure


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_era(db):
    era = Era.objects.create(
        name="Early Church",
        slug="early-church",
        start_year=30,
        end_year=325,
        description="The apostolic age and early Christianity.",
        summary="From Pentecost to the Council of Nicaea.",
        color="#C2410C",
        order=1,
    )
    KeyEvent.objects.create(
        era=era,
        year=30,
        title="Pentecost",
        description="The Holy Spirit descends on the apostles.",
        order=1,
    )
    KeyEvent.objects.create(
        era=era,
        year=70,
        title="Fall of Jerusalem",
        description="The Roman destruction of the Temple.",
        order=2,
    )
    KeyFigure.objects.create(
        era=era,
        name="Apostle Paul",
        birth_year=5,
        death_year=67,
        title="Apostle to the Gentiles",
        description="Missionary and author of many epistles.",
        order=1,
    )
    return era


@pytest.fixture
def second_era(db):
    return Era.objects.create(
        name="Nicene Era",
        slug="nicene-era",
        start_year=325,
        end_year=590,
        description="The age of creeds and councils.",
        summary="From Nicaea to Gregory the Great.",
        color="#7C3AED",
        order=2,
    )


@pytest.mark.django_db
class TestTimelineEndpoint:
    """Tests for the /api/eras/timeline/ endpoint used by the canvas."""

    def test_timeline_returns_all_eras_with_events_and_figures(
        self, api_client, sample_era, second_era
    ):
        """Timeline endpoint returns all eras with nested key_events and key_figures."""
        response = api_client.get("/api/eras/timeline/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        # Find the era with events
        era_data = next(e for e in response.data if e["slug"] == "early-church")
        assert era_data["name"] == "Early Church"
        assert era_data["start_year"] == 30
        assert era_data["end_year"] == 325
        assert era_data["color"] == "#C2410C"
        assert len(era_data["key_events"]) == 2
        assert len(era_data["key_figures"]) == 1

        # Verify event structure
        event = era_data["key_events"][0]
        assert event["year"] == 30
        assert event["title"] == "Pentecost"

        # Verify figure structure
        figure = era_data["key_figures"][0]
        assert figure["name"] == "Apostle Paul"
        assert figure["birth_year"] == 5
        assert figure["death_year"] == 67

    def test_timeline_orders_eras_by_order_field(
        self, api_client, sample_era, second_era
    ):
        """Timeline eras are ordered by the order field."""
        response = api_client.get("/api/eras/timeline/")
        assert response.status_code == status.HTTP_200_OK
        slugs = [e["slug"] for e in response.data]
        assert slugs == ["early-church", "nicene-era"]

    def test_timeline_accessible_without_auth(self, api_client, sample_era):
        """Timeline is public — no authentication required."""
        response = api_client.get("/api/eras/timeline/")
        assert response.status_code == status.HTTP_200_OK

    def test_timeline_empty_when_no_eras(self, api_client, db):
        """Timeline returns empty list when no eras exist."""
        response = api_client.get("/api/eras/timeline/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    @override_settings(
        CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
    )
    def test_timeline_response_is_cached(self, api_client, sample_era):
        """Timeline response is cached (subsequent requests are identical)."""
        response1 = api_client.get("/api/eras/timeline/")
        assert response1.status_code == status.HTTP_200_OK

        response2 = api_client.get("/api/eras/timeline/")
        assert response2.status_code == status.HTTP_200_OK

        # Both responses should have the same data
        assert response1.data == response2.data

    def test_timeline_includes_description_and_summary(self, api_client, sample_era):
        """Timeline returns both description and summary fields."""
        response = api_client.get("/api/eras/timeline/")
        era_data = response.data[0]
        assert "description" in era_data
        assert "summary" in era_data
        assert era_data["description"] == "The apostolic age and early Christianity."
        assert era_data["summary"] == "From Pentecost to the Council of Nicaea."

    def test_timeline_includes_image_url(self, api_client, sample_era):
        """Timeline returns image_url field (even if empty)."""
        response = api_client.get("/api/eras/timeline/")
        era_data = response.data[0]
        assert "image_url" in era_data

    def test_era_with_null_end_year(self, api_client, db):
        """Era with null end_year (current era) is handled properly."""
        Era.objects.create(
            name="Modern Era",
            slug="modern-era",
            start_year=1900,
            end_year=None,
            description="The modern church.",
            summary="Contemporary Christianity.",
            color="#059669",
            order=6,
        )
        response = api_client.get("/api/eras/timeline/")
        assert response.status_code == status.HTTP_200_OK
        era_data = response.data[0]
        assert era_data["end_year"] is None
