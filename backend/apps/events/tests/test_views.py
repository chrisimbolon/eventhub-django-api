# backend/apps/events/tests/test_views.py

import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from apps.users.models import User
from apps.events.models import Event, Registration

@pytest.mark.django_db
class TestEventViewSet:
    """Integration tests for Event API endpoints"""

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def organizer(self):
        return User.objects.create_user(
            username="organizer",
            email="organizer@test.com",
            password="testpass123",
            role="organizer",
        )

    @pytest.fixture
    def attendee(self):
        return User.objects.create_user(
            username="attendee",
            email="attendee@test.com",
            password="testpass123",
            role="attendee",
        )

    @pytest.fixture
    def sample_event(self, organizer):
        now = timezone.now()
        return Event.objects.create(
            title="Sample Event",
            slug="sample-event",
            description="A test event",
            event_type="conference",
            status="draft",
            start_date=now + timedelta(days=10),
            end_date=now + timedelta(days=11),
            registration_start=now - timedelta(days=1),
            registration_end=now + timedelta(days=5),
            venue_name="Test Hall",
            venue_address="123 Test St",
            city="Test City",
            country="Testland",
            capacity=100,
            organizer=organizer,
        )

    def test_list_events(self, api_client, sample_event):
        response = api_client.get("/api/v1/events/")
        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"] if isinstance(response.data, dict) and "results" in response.data else response.data
        assert isinstance(results, list)
        assert len(results) >= 1
        assert "title" in results[0]

    # def test_list_events(self, api_client, sample_event):
    #     response = api_client.get("/api/v1/events/")
    #     assert response.status_code == status.HTTP_200_OK
    #     assert len(response.data) >= 1
    #     assert "title" in response.data[0]

    def test_create_event_requires_authentication(self, api_client):
        payload = {"title": "Unauth Event", "slug": "unauth-event"}
        response = api_client.post("/api/v1/events/", payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_event_success(self, api_client, organizer):
        api_client.force_authenticate(user=organizer)
        now = timezone.now()
        payload = {
            "title": "Organizer Event",
            "slug": "organizer-event",
            "description": "Organized by test user",
            "event_type": "conference",
            "status": "draft",
            "start_date": (now + timedelta(days=5)).isoformat(),
            "end_date": (now + timedelta(days=7)).isoformat(),
            "registration_start": (now - timedelta(days=1)).isoformat(),
            "registration_end": (now + timedelta(days=3)).isoformat(),
            "venue_name": "Main Hall",
            "venue_address": "123 Avenue",
            "city": "Metropolis",
            "country": "Freedonia",
            "capacity": 200,
        }
        response = api_client.post("/api/v1/events/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        event = Event.objects.get(slug="organizer-event")
        assert event.organizer == organizer

    # def test_create_event_success(self, api_client, organizer):
    #     api_client.force_authenticate(user=organizer)
    #     now = timezone.now()
    #     payload = {
    #         "title": "Organizer Event",
    #         "slug": "organizer-event",
    #         "description": "Organized by test user",
    #         "event_type": "conference",
    #         "status": "draft",
    #         "start_date": (now + timedelta(days=5)).isoformat(),
    #         "end_date": (now + timedelta(days=7)).isoformat(),
    #         "registration_start": (now - timedelta(days=1)).isoformat(),
    #         "registration_end": (now + timedelta(days=3)).isoformat(),
    #         "venue_name": "Main Hall",
    #         "venue_address": "123 Avenue",
    #         "city": "Metropolis",
    #         "country": "Freedonia",
    #         "capacity": 200,
    #     }
    #     response = api_client.post("/api/v1/events/", payload, format="json")
    #     assert response.status_code == status.HTTP_201_CREATED
    #     assert response.data["organizer"] == organizer.id or "id" in response.data

    def test_update_event_as_organizer(self, api_client, organizer, sample_event):
        api_client.force_authenticate(user=organizer)
        url = f"/api/v1/events/{sample_event.slug}/"
        response = api_client.patch(url, {"title": "Updated Title"}, format="json")
        assert response.status_code == status.HTTP_200_OK
        sample_event.refresh_from_db()
        assert sample_event.title == "Updated Title"

    def test_update_event_as_non_organizer_forbidden(self, api_client, attendee, sample_event):
        api_client.force_authenticate(user=attendee)
        url = f"/api/v1/events/{sample_event.slug}/"
        response = api_client.patch(url, {"title": "Hack Attempt"}, format="json")
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]

    def test_publish_event_success(self, api_client, organizer, sample_event):
        api_client.force_authenticate(user=organizer)
        url = f"/api/v1/events/{sample_event.slug}/publish/"
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        sample_event.refresh_from_db()
        assert sample_event.status == "published"

    def test_publish_event_forbidden_for_non_organizer(self, api_client, attendee, sample_event):
        api_client.force_authenticate(user=attendee)
        url = f"/api/v1/events/{sample_event.slug}/publish/"
        response = api_client.post(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_upcoming_and_ongoing_views(self, api_client, sample_event):
        now = timezone.now()
        Event.objects.create(
            title="Ongoing Event",
            slug="ongoing-event",
            description="Now running",
            event_type="conference",
            status="published",
            start_date=now - timedelta(hours=1),
            end_date=now + timedelta(hours=1),
            registration_start=now - timedelta(days=10),
            registration_end=now - timedelta(days=1),
            venue_name="Arena",
            venue_address="Downtown",
            city="LiveCity",
            country="Nowhere",
            capacity=50,
            organizer=sample_event.organizer,
        )
        upcoming_response = api_client.get("/api/v1/events/upcoming/")
        assert upcoming_response.status_code == status.HTTP_200_OK
        ongoing_response = api_client.get("/api/v1/events/ongoing/")
        assert ongoing_response.status_code == status.HTTP_200_OK
        assert any("Ongoing" in e["title"] or "Sample" in e["title"] for e in upcoming_response.data + ongoing_response.data)
