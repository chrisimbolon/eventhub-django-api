# backend/apps/events/tests/test_serializers.py

import pytest
from datetime import timedelta
from django.utils import timezone
from apps.events.models import Event, Registration
from apps.users.models import User
from types import SimpleNamespace
from apps.events.serializers import (
EventCreateUpdateSerializer,
EventListSerializer,
EventDetailSerializer,
RegistrationSerializer,
)

@pytest.mark.django_db
class TestEventSerializers:
    """Tests for Event serializers (create, list, detail)"""

    @pytest.fixture
    def organizer(self):
        return User.objects.create_user(
            username="organizer",
            email="organizer@test.com",
            password="testpass123",
            role="organizer",
        )

    def test_valid_data_creates_event(self, organizer):
        now = timezone.now()
        data = {
            "title": "AI Summit 2025",
            "slug": "ai-summit-2025",
            "description": "The next generation of AI innovation",
            "event_type": "conference",
            "status": "draft",
            "start_date": now + timedelta(days=10),
            "end_date": now + timedelta(days=12),
            "registration_start": now - timedelta(days=1),
            "registration_end": now + timedelta(days=5),
            "venue_name": "Tech Convention Hall",
            "venue_address": "123 Innovation Road",
            "city": "Jakarta",
            "country": "Indonesia",
            "capacity": 100,
        }

        serializer = EventCreateUpdateSerializer(data=data, context={"request": None})
        assert serializer.is_valid(), serializer.errors

        event = serializer.save(organizer=organizer)
        assert event.title == data["title"]
        assert event.organizer == organizer
        assert Event.objects.count() == 1

    def test_invalid_missing_required_fields(self):
        data = {"title": "Incomplete Event"}  
        serializer = EventCreateUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert "start_date" in serializer.errors
        assert "end_date" in serializer.errors
        assert "venue_address" in serializer.errors

    def test_list_serializer_returns_expected_fields(self, organizer):
        event = Event.objects.create(
            title="DataConf 2025",
            slug="dataconf-2025",
            description="AI and ML conference",
            event_type="conference",
            status="published",
            start_date=timezone.now() + timedelta(days=5),
            end_date=timezone.now() + timedelta(days=6),
            registration_start=timezone.now() - timedelta(days=1),
            registration_end=timezone.now() + timedelta(days=4),
            venue_name="Hall A",
            venue_address="123 Main St",
            city="Jakarta",
            country="Indonesia",
            capacity=300,
            organizer=organizer,
        )

        serializer = EventListSerializer(event)
        data = serializer.data
        assert "title" in data
        assert "slug" in data
        assert "start_date" in data
        assert "organizer_name" in data

    def test_detail_serializer_includes_related_data(self, organizer):
        event = Event.objects.create(
            title="AI Meetup",
            slug="ai-meetup",
            description="Testing detail serializer",
            event_type="meetup",
            status="published",
            start_date=timezone.now() + timedelta(days=2),
            end_date=timezone.now() + timedelta(days=3),
            registration_start=timezone.now() - timedelta(days=1),
            registration_end=timezone.now() + timedelta(days=1),
            venue_name="Innovation Hub",
            venue_address="456 Future St",
            city="Bandung",
            country="Indonesia",
            capacity=50,
            organizer=organizer,
        )

        serializer = EventDetailSerializer(event)
        data = serializer.data
        assert data["slug"] == event.slug
        assert data["venue_name"] == "Innovation Hub"
        assert "organizer" in data
        organizer_data = data["organizer"]
        assert isinstance(organizer_data, dict)
        assert organizer_data["email"] == "organizer@test.com"
        assert organizer_data["id"] == organizer.id
        assert "name" in organizer_data  # optional field (can be blank)



@pytest.mark.django_db
class TestRegistrationSerializer:
    """Tests for Registration serializer"""

    @pytest.fixture
    def organizer(self):
        return User.objects.create_user(
            username="org",
            email="org@test.com",
            password="testpass123",
            role="organizer",
        )

    @pytest.fixture
    def attendee(self):
        return User.objects.create_user(
            username="att",
            email="att@test.com",
            password="testpass123",
            role="attendee",
        )

    @pytest.fixture
    def event(self, organizer):
        now = timezone.now()
        return Event.objects.create(
            title="ML Bootcamp",
            slug="ml-bootcamp",
            description="Intro to ML",
            event_type="workshop",
            status="published",
            start_date=now + timedelta(days=5),
            end_date=now + timedelta(days=7),
            registration_start=now - timedelta(days=1),
            registration_end=now + timedelta(days=3),
            venue_name="Learning Hall",
            venue_address="789 Knowledge Ave",
            city="Jakarta",
            country="Indonesia",
            capacity=100,
            organizer=organizer,
        )
    
    def test_valid_registration(self, attendee, event):
        data = {"event": event.id}
        fake_request = SimpleNamespace(user=attendee)
        serializer = RegistrationSerializer(data=data, context={"request": fake_request})
        assert serializer.is_valid(), serializer.errors
        reg = serializer.save(attendee=attendee)
        assert reg.event == event
        assert reg.attendee == attendee
        assert reg.status == "pending"

    def test_invalid_registration_missing_event(self):
        serializer = RegistrationSerializer(data={})
        assert not serializer.is_valid()
        assert "event" in serializer.errors
