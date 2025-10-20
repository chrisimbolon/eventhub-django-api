# backend/apps/events/tests/test_models.py

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from apps.events.models import Event, Registration
from apps.users.models import User


@pytest.mark.django_db
class TestEventModel:
    """Test cases for Event model"""
    
    @pytest.fixture
    def organizer(self):
        """Create a test organizer"""
        return User.objects.create_user(
            username='organizer',
            email='organizer@test.com',
            password='testpass123',
            role='organizer'
        )
    
    @pytest.fixture
    def attendee(self):
        """Create a test attendee"""
        return User.objects.create_user(
            username='attendee',
            email='attendee@test.com',
            password='testpass123',
            role='attendee'
        )
    
    @pytest.fixture
    def valid_event_data(self, organizer):
        """Create valid event data"""
        now = timezone.now()
        return {
            'title': 'Test Conference',
            'slug': 'test-conference',
            'description': 'A test conference',
            'event_type': 'conference',
            'status': 'published',
            'start_date': now + timedelta(days=30),
            'end_date': now + timedelta(days=32),
            'registration_start': now,
            'registration_end': now + timedelta(days=25),
            'venue_name': 'Test Venue',
            'venue_address': '123 Test St',
            'city': 'Test City',
            'country': 'Test Country',
            'capacity': 100,
            'organizer': organizer
        }
    
    def test_create_event_success(self, valid_event_data):
        """Test creating an event with valid data"""
        event = Event.objects.create(**valid_event_data)
        
        assert event.title == 'Test Conference'
        assert event.slug == 'test-conference'
        assert event.capacity == 100
        assert event.current_attendees == 0
        assert event.status == 'published'
    
    def test_event_str_representation(self, valid_event_data):
        """Test event string representation"""
        event = Event.objects.create(**valid_event_data)
        expected = f"Test Conference ({event.start_date.strftime('%Y-%m-%d')})"
        assert str(event) == expected
    
    def test_event_end_date_before_start_date(self, valid_event_data):
        """Test that end_date must be after start_date"""
        valid_event_data['end_date'] = valid_event_data['start_date'] - timedelta(days=1)
        
        with pytest.raises(ValidationError) as exc_info:
            event = Event(**valid_event_data)
            event.full_clean()
        
        assert 'end_date' in exc_info.value.message_dict
    
    def test_registration_end_before_start(self, valid_event_data):
        """Test that registration_end must be after registration_start"""
        valid_event_data['registration_end'] = valid_event_data['registration_start'] - timedelta(days=1)
        
        with pytest.raises(ValidationError) as exc_info:
            event = Event(**valid_event_data)
            event.full_clean()
        
        assert 'registration_end' in exc_info.value.message_dict
    
    def test_registration_end_after_event_start(self, valid_event_data):
        """Test that registration must end before event starts"""
        valid_event_data['registration_end'] = valid_event_data['start_date'] + timedelta(days=1)
        
        with pytest.raises(ValidationError) as exc_info:
            event = Event(**valid_event_data)
            event.full_clean()
        
        assert 'registration_end' in exc_info.value.message_dict

    def test_is_full_property(self, valid_event_data):
        """Test is_full and capacity validation"""
    # Create event with capacity 100
        event = Event.objects.create(**valid_event_data)

    # Valid: exactly equal to capacity => should be full but still valid
        event.current_attendees = 100
        event.save()
        event.refresh_from_db()
        assert event.is_full is True
        assert event.available_spots == 0

    # Invalid: above capacity => should raise ValidationError
        event.current_attendees = 101
        with pytest.raises(ValidationError):
            event.full_clean() 
    
    def test_available_spots_property(self, valid_event_data):
        """Test available_spots property"""
        event = Event.objects.create(**valid_event_data)
        
        assert event.available_spots == 100
        
        event.current_attendees = 30
        event.save()
        assert event.available_spots == 70
        
        event.current_attendees = 100
        event.save()
        assert event.available_spots == 0
    
    def test_is_registration_open_property(self, valid_event_data):
        """Test is_registration_open property"""
        now = timezone.now()
        
        # Registration is open (status=published, within registration period, not full)
        valid_event_data['registration_start'] = now - timedelta(days=1)
        valid_event_data['registration_end'] = now + timedelta(days=10)
        event = Event.objects.create(**valid_event_data)
        assert event.is_registration_open is True
        
        # Registration closed - draft status
        event.status = 'draft'
        event.save()
        assert event.is_registration_open is False
        
        # Registration closed - before registration start
        event.status = 'published'
        event.registration_start = now + timedelta(days=1)
        event.save()
        assert event.is_registration_open is False
        
        # Registration closed - after registration end
        event.registration_start = now - timedelta(days=20)
        event.registration_end = now - timedelta(days=1)
        event.save()
        assert event.is_registration_open is False
        
        # Registration closed - event is full
        event.registration_start = now - timedelta(days=1)
        event.registration_end = now + timedelta(days=10)
        event.current_attendees = event.capacity
        event.save()
        assert event.is_registration_open is False
    
    def test_duration_days_property(self, valid_event_data):
        """Test duration_days property"""
        event = Event.objects.create(**valid_event_data)
        assert event.duration_days == 3  # 30th, 31st, 32nd = 3 days


@pytest.mark.django_db
class TestRegistrationModel:
    """Test cases for Registration model"""
    
    @pytest.fixture
    def organizer(self):
        return User.objects.create_user(
            username='organizer',
            email='organizer@test.com',
            password='testpass123',
            role='organizer'
        )
    
    @pytest.fixture
    def attendee(self):
        return User.objects.create_user(
            username='attendee',
            email='attendee@test.com',
            password='testpass123',
            role='attendee'
        )
    
    @pytest.fixture
    def event(self, organizer):
        now = timezone.now()
        return Event.objects.create(
            title='Test Event',
            slug='test-event',
            description='Test description',
            event_type='conference',
            status='published',
            start_date=now + timedelta(days=30),
            end_date=now + timedelta(days=32),
            registration_start=now - timedelta(days=1),
            registration_end=now + timedelta(days=25),
            venue_name='Test Venue',
            venue_address='123 Test St',
            city='Test City',
            country='Test Country',
            capacity=100,
            organizer=organizer
        )
    
    def test_create_registration_success(self, event, attendee):
        """Test creating a registration with valid data"""
        registration = Registration.objects.create(
            event=event,
            attendee=attendee,
            status='pending'
        )
        
        assert registration.event == event
        assert registration.attendee == attendee
        assert registration.status == 'pending'
        
        # Check that event attendee count increased
        event.refresh_from_db()
        assert event.current_attendees == 1
    
    def test_registration_str_representation(self, event, attendee):
        """Test registration string representation"""
        registration = Registration.objects.create(
            event=event,
            attendee=attendee
        )
        
        expected = f"{attendee.get_full_name()} - {event.title}"
        assert str(registration) == expected
    
    def test_duplicate_registration_prevented(self, event, attendee):
        """Test that duplicate registrations are prevented"""
        # Create first registration
        Registration.objects.create(
            event=event,
            attendee=attendee,
            status='confirmed'
        )
        
        # Try to create duplicate
        with pytest.raises(ValidationError) as exc_info:
            registration = Registration(
                event=event,
                attendee=attendee
            )
            registration.full_clean()
        
        assert 'attendee' in exc_info.value.message_dict
    
    def test_registration_when_event_full(self, event, attendee):
        """Test that registration fails when event is full"""
        # Fill the event
        event.current_attendees = event.capacity
        event.save()
        
        with pytest.raises(ValidationError) as exc_info:
            registration = Registration(
                event=event,
                attendee=attendee
            )
            registration.full_clean()
        
        assert 'event' in exc_info.value.message_dict
    
    def test_registration_when_closed(self, event, attendee):
        """Test that registration fails when registration is closed"""
        # Set event to draft
        event.status = 'draft'
        event.save()
        
        with pytest.raises(ValidationError) as exc_info:
            registration = Registration(
                event=event,
                attendee=attendee
            )
            registration.full_clean()
        
        assert 'event' in exc_info.value.message_dict
    
    def test_confirm_registration(self, event, attendee):
        """Test confirming a registration"""
        registration = Registration.objects.create(
            event=event,
            attendee=attendee,
            status='pending'
        )
        
        registration.confirm()
        
        assert registration.status == 'confirmed'
        assert registration.confirmation_date is not None
    
    def test_cancel_registration(self, event, attendee):
        """Test canceling a registration"""
        registration = Registration.objects.create(
            event=event,
            attendee=attendee,
            status='confirmed'
        )
        
        event.refresh_from_db()
        initial_count = event.current_attendees
        
        registration.cancel()
        
        assert registration.status == 'cancelled'
        event.refresh_from_db()
        assert event.current_attendees == initial_count - 1
    
    def test_unique_together_constraint(self, event, attendee):
        """Test that event + attendee must be unique"""
        Registration.objects.create(
            event=event,
            attendee=attendee
        )
        
        from django.db import IntegrityError
        with pytest.raises((IntegrityError, ValidationError)):
            Registration.objects.create(
                event=event,
                attendee=attendee
            )