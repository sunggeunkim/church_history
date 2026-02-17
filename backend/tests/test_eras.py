"""Tests for eras app models, serializers, and API endpoints."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.content.models import ContentTag
from apps.eras.models import Era, KeyEvent, KeyFigure
from apps.eras.serializers import (
    EraDetailSerializer,
    EraListSerializer,
    KeyEventSerializer,
    KeyFigureSerializer,
)


@pytest.fixture
def api_client():
    """Provide API client for testing."""
    return APIClient()


@pytest.fixture
def sample_era():
    """Create a sample era for testing."""
    return Era.objects.create(
        name="Reformation",
        slug="reformation",
        start_year=1517,
        end_year=1648,
        description="The Protestant Reformation era.",
        summary="Recovery of the gospel through the five solas.",
        color="#15803D",
        order=4,
    )


@pytest.fixture
def sample_era_with_relations(sample_era):
    """Create a sample era with events and figures."""
    # Add key events
    KeyEvent.objects.create(
        era=sample_era,
        year=1517,
        title="Luther's 95 Theses",
        description="Martin Luther posts 95 theses.",
        order=1,
    )
    KeyEvent.objects.create(
        era=sample_era,
        year=1536,
        title="Calvin Publishes Institutes",
        description="First edition of Institutes.",
        order=2,
    )

    # Add key figures
    KeyFigure.objects.create(
        era=sample_era,
        name="Martin Luther",
        birth_year=1483,
        death_year=1546,
        title="German Reformer",
        description="Father of the Protestant Reformation.",
        order=1,
    )
    KeyFigure.objects.create(
        era=sample_era,
        name="John Calvin",
        birth_year=1509,
        death_year=1564,
        title="French Reformer",
        description="Influential Reformed theologian.",
        order=2,
    )

    return sample_era


@pytest.mark.django_db
class TestEraModel:
    """Test Era model."""

    def test_era_creation(self, sample_era):
        """Test creating an era."""
        assert sample_era.name == "Reformation"
        assert sample_era.slug == "reformation"
        assert sample_era.start_year == 1517
        assert sample_era.end_year == 1648
        assert sample_era.color == "#15803D"

    def test_era_str_with_end_year(self, sample_era):
        """Test string representation with end year."""
        assert str(sample_era) == "Reformation (1517-1648)"

    def test_era_str_without_end_year(self):
        """Test string representation for current era."""
        era = Era.objects.create(
            name="Contemporary",
            slug="contemporary",
            start_year=1900,
            end_year=None,
            description="Modern era",
            color="#475569",
            order=6,
        )
        assert str(era) == "Contemporary (1900-present)"

    def test_era_ordering(self):
        """Test that eras are ordered correctly."""
        era1 = Era.objects.create(
            name="Early Church",
            slug="early-church",
            start_year=30,
            end_year=325,
            description="Early church",
            color="#C2410C",
            order=1,
        )
        era2 = Era.objects.create(
            name="Medieval",
            slug="medieval",
            start_year=590,
            end_year=1517,
            description="Medieval period",
            color="#7C3AED",
            order=3,
        )

        eras = list(Era.objects.all())
        assert eras[0] == era1
        assert eras[1] == era2


@pytest.mark.django_db
class TestKeyEventModel:
    """Test KeyEvent model."""

    def test_key_event_creation(self, sample_era):
        """Test creating a key event."""
        event = KeyEvent.objects.create(
            era=sample_era,
            year=1517,
            title="Luther's 95 Theses",
            description="Posted on church door.",
            order=1,
        )
        assert event.year == 1517
        assert event.title == "Luther's 95 Theses"
        assert event.era == sample_era

    def test_key_event_str(self, sample_era):
        """Test string representation."""
        event = KeyEvent.objects.create(
            era=sample_era,
            year=1517,
            title="Luther's 95 Theses",
            order=1,
        )
        assert str(event) == "1517: Luther's 95 Theses"

    def test_key_event_ordering(self, sample_era):
        """Test that events are ordered correctly."""
        event1 = KeyEvent.objects.create(
            era=sample_era, year=1536, title="Event B", order=2
        )
        event2 = KeyEvent.objects.create(
            era=sample_era, year=1517, title="Event A", order=1
        )

        events = list(sample_era.key_events.all())
        assert events[0] == event2
        assert events[1] == event1


@pytest.mark.django_db
class TestKeyFigureModel:
    """Test KeyFigure model."""

    def test_key_figure_creation(self, sample_era):
        """Test creating a key figure."""
        figure = KeyFigure.objects.create(
            era=sample_era,
            name="Martin Luther",
            birth_year=1483,
            death_year=1546,
            title="German Reformer",
            description="Father of Reformation.",
            order=1,
        )
        assert figure.name == "Martin Luther"
        assert figure.birth_year == 1483
        assert figure.death_year == 1546
        assert figure.era == sample_era

    def test_key_figure_str_with_both_years(self, sample_era):
        """Test string representation with birth and death years."""
        figure = KeyFigure.objects.create(
            era=sample_era,
            name="Martin Luther",
            birth_year=1483,
            death_year=1546,
            order=1,
        )
        assert str(figure) == "Martin Luther (1483-1546)"

    def test_key_figure_str_with_birth_only(self, sample_era):
        """Test string representation with only birth year."""
        figure = KeyFigure.objects.create(
            era=sample_era,
            name="John Piper",
            birth_year=1946,
            death_year=None,
            order=1,
        )
        assert str(figure) == "John Piper (b. 1946)"

    def test_key_figure_str_without_years(self, sample_era):
        """Test string representation without years."""
        figure = KeyFigure.objects.create(
            era=sample_era, name="Unknown Saint", order=1
        )
        assert str(figure) == "Unknown Saint"


@pytest.mark.django_db
class TestSerializers:
    """Test era serializers."""

    def test_key_event_serializer(self, sample_era):
        """Test KeyEventSerializer."""
        event = KeyEvent.objects.create(
            era=sample_era,
            year=1517,
            title="Luther's 95 Theses",
            description="Posted on church door.",
            order=1,
        )
        serializer = KeyEventSerializer(event)
        data = serializer.data

        assert data["year"] == 1517
        assert data["title"] == "Luther's 95 Theses"
        assert data["description"] == "Posted on church door."
        assert data["order"] == 1

    def test_key_figure_serializer(self, sample_era):
        """Test KeyFigureSerializer."""
        figure = KeyFigure.objects.create(
            era=sample_era,
            name="Martin Luther",
            birth_year=1483,
            death_year=1546,
            title="German Reformer",
            description="Father of Reformation.",
            order=1,
        )
        serializer = KeyFigureSerializer(figure)
        data = serializer.data

        assert data["name"] == "Martin Luther"
        assert data["birth_year"] == 1483
        assert data["death_year"] == 1546
        assert data["title"] == "German Reformer"

    def test_era_list_serializer(self, sample_era):
        """Test EraListSerializer."""
        serializer = EraListSerializer(sample_era)
        data = serializer.data

        assert data["name"] == "Reformation"
        assert data["slug"] == "reformation"
        assert data["start_year"] == 1517
        assert data["end_year"] == 1648
        assert data["color"] == "#15803D"
        assert data["summary"] == "Recovery of the gospel through the five solas."
        assert data["order"] == 4
        # Should not include description or related objects
        assert "description" not in data
        assert "key_events" not in data

    def test_era_detail_serializer(self, sample_era_with_relations):
        """Test EraDetailSerializer includes related objects."""
        serializer = EraDetailSerializer(sample_era_with_relations)
        data = serializer.data

        assert data["name"] == "Reformation"
        assert data["description"] == "The Protestant Reformation era."
        assert len(data["key_events"]) == 2
        assert len(data["key_figures"]) == 2

        # Check first event
        assert data["key_events"][0]["year"] == 1517
        assert data["key_events"][0]["title"] == "Luther's 95 Theses"

        # Check first figure
        assert data["key_figures"][0]["name"] == "Martin Luther"
        assert data["key_figures"][0]["birth_year"] == 1483


@pytest.mark.django_db
class TestEraAPI:
    """Test era API endpoints."""

    def test_list_eras(self, api_client, sample_era):
        """Test listing all eras."""
        url = reverse("eras:era-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        assert len(results) == 1
        assert results[0]["name"] == "Reformation"
        assert results[0]["slug"] == "reformation"

    def test_retrieve_era_by_slug(self, api_client, sample_era_with_relations):
        """Test retrieving a single era by slug."""
        url = reverse("eras:era-detail", kwargs={"slug": "reformation"})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Reformation"
        assert len(response.data["key_events"]) == 2
        assert len(response.data["key_figures"]) == 2

    def test_retrieve_nonexistent_era(self, api_client):
        """Test retrieving a nonexistent era returns 404."""
        url = reverse("eras:era-detail", kwargs={"slug": "nonexistent"})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_timeline_endpoint(self, api_client):
        """Test timeline endpoint returns all eras with events."""
        # Create multiple eras
        era1 = Era.objects.create(
            name="Early Church",
            slug="early-church",
            start_year=30,
            end_year=325,
            description="Early church",
            summary="Apostolic age",
            color="#C2410C",
            order=1,
        )
        era2 = Era.objects.create(
            name="Reformation",
            slug="reformation",
            start_year=1517,
            end_year=1648,
            description="Reformation",
            summary="Protestant Reformation",
            color="#15803D",
            order=4,
        )

        # Add events
        KeyEvent.objects.create(
            era=era1, year=30, title="Pentecost", order=1
        )
        KeyEvent.objects.create(
            era=era2, year=1517, title="95 Theses", order=1
        )

        url = reverse("eras:era-timeline")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        # Check that events are included
        assert len(response.data[0]["key_events"]) >= 1
        assert len(response.data[1]["key_events"]) >= 1

    def test_era_ordering_in_list(self, api_client):
        """Test that eras are returned in correct order."""
        Era.objects.create(
            name="Medieval",
            slug="medieval",
            start_year=590,
            end_year=1517,
            description="Medieval",
            color="#7C3AED",
            order=3,
        )
        Era.objects.create(
            name="Early Church",
            slug="early-church",
            start_year=30,
            end_year=325,
            description="Early",
            color="#C2410C",
            order=1,
        )

        url = reverse("eras:era-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        # Should be ordered by order field
        assert results[0]["name"] == "Early Church"
        assert results[1]["name"] == "Medieval"


@pytest.mark.django_db
class TestSeedErasCommand:
    """Test the seed_eras management command."""

    def test_seed_command_creates_all_eras(self):
        """Test that seed command creates all 6 eras."""
        from django.core.management import call_command

        # Run the seed command
        call_command("seed_eras")

        # Verify all 6 eras were created
        assert Era.objects.count() == 6

        # Verify era names
        era_names = set(Era.objects.values_list("name", flat=True))
        expected_names = {
            "Early Church",
            "Nicene & Post-Nicene",
            "Medieval",
            "Reformation",
            "Post-Reformation",
            "Contemporary",
        }
        assert era_names == expected_names

    def test_seed_command_creates_content_tags(self):
        """Test that seed command creates ContentTag records."""
        from django.core.management import call_command

        call_command("seed_eras")

        # Verify ContentTags were created
        era_tags = ContentTag.objects.filter(tag_type=ContentTag.TagType.ERA)
        assert era_tags.count() == 6

    def test_seed_command_creates_events(self):
        """Test that seed command creates key events."""
        from django.core.management import call_command

        call_command("seed_eras")

        # Verify events were created
        assert KeyEvent.objects.count() > 0

        # Check that Reformation era has expected events
        reformation = Era.objects.get(slug="reformation")
        events = reformation.key_events.all()
        assert events.count() >= 5

        # Check for specific event
        assert events.filter(title="Luther's 95 Theses").exists()

    def test_seed_command_creates_figures(self):
        """Test that seed command creates key figures."""
        from django.core.management import call_command

        call_command("seed_eras")

        # Verify figures were created
        assert KeyFigure.objects.count() > 0

        # Check that Reformation era has expected figures
        reformation = Era.objects.get(slug="reformation")
        figures = reformation.key_figures.all()
        assert figures.count() >= 4

        # Check for specific figures
        assert figures.filter(name="Martin Luther").exists()
        assert figures.filter(name="John Calvin").exists()

    def test_seed_command_is_idempotent(self):
        """Test that running seed command multiple times is safe."""
        from django.core.management import call_command

        # Run twice
        call_command("seed_eras")
        call_command("seed_eras")

        # Should still only have 6 eras
        assert Era.objects.count() == 6
        assert ContentTag.objects.filter(tag_type=ContentTag.TagType.ERA).count() == 6
