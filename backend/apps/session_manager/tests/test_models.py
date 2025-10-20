# backend/apps/session_manager/tests/test_models.py

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from apps.session_manager.models import Session, Speaker
from apps.events.models import Event
from apps.tracks.models import Track
from apps.users.models import User


@pytest.mark.django_db
class TestSpeakerModel:
    """Test cases for Speaker model"""
    
    @pytest.fixture
    def speaker_user(self):
        return User.objects.create_user(
            username='speaker',
            email='speaker@test.com',
            password='testpass123',
            role='speaker'
        )
    
    def test_create_speaker_success(self, speaker_user):
        """Test creating a speaker with valid data"""
        speaker = Speaker.objects.create(
            user=speaker_user,
            name='John Speaker',
            email='john@test.com',
            bio='Experienced speaker',
            title='Senior Engineer',
            company='TechCorp'
        )
        
        assert speaker.name == 'John Speaker'
        assert speaker.email == 'john@test.com'
        assert speaker.user == speaker_user
    
    def test_speaker_str_representation(self):
        """Test speaker string representation"""
        speaker = Speaker.objects.create(
            name='Jane Doe',
            email='jane@test.com'
        )
        
        assert str(speaker) == 'Jane Doe'
    
    def test_speaker_without_user(self):
        """Test creating speaker without linked user"""
        speaker = Speaker.objects.create(
            name='External Speaker',
            email='external@test.com',
            bio='External guest speaker'
        )
        
        assert speaker.user is None
        assert speaker.name == 'External Speaker'


@pytest.mark.django_db
class TestSessionModel:
    """Test cases for Session model"""
    
    @pytest.fixture
    def organizer(self):
        return User.objects.create_user(
            username='organizer',
            email='organizer@test.com',
            password='testpass123',
            role='organizer'
        )
    
    @pytest.fixture
    def event(self, organizer):
        now = timezone.now()
        return Event.objects.create(
            title='Test Conference',
            slug='test-conference',
            description='A test conference',
            event_type='conference',
            status='published',
            start_date=now + timedelta(days=30),
            end_date=now + timedelta(days=32),
            registration_start=now,
            registration_end=now + timedelta(days=25),
            venue_name='Test Venue',
            venue_address='123 Test St',
            city='Test City',
            country='Test Country',
            capacity=100,
            organizer=organizer
        )
    
    @pytest.fixture
    def track(self, event):
        return Track.objects.create(
            event=event,
            name='Backend Track',
            description='Backend development sessions',
            color='#3B82F6'
        )
    
    @pytest.fixture
    def speaker(self):
        return Speaker.objects.create(
            name='Test Speaker',
            email='speaker@test.com',
            bio='Test bio'
        )
    
    def test_create_session_success(self, event, track, speaker):
        """Test creating a session with valid data"""
        start_time = event.start_date + timedelta(hours=2)
        end_time = start_time + timedelta(hours=1, minutes=30)
        
        session = Session.objects.create(
            event=event,
            track=track,
            title='Django Best Practices',
            slug='django-best-practices',
            description='Learn Django best practices',
            session_format='talk',
            level='intermediate',
            start_time=start_time,
            end_time=end_time,
            duration_minutes=90,
            room='Hall A'
        )
        session.speakers.add(speaker)
        
        assert session.title == 'Django Best Practices'
        assert session.event == event
        assert session.track == track
        assert session.duration_minutes == 90
    
    def test_session_str_representation(self, event, speaker):
        """Test session string representation"""
        start_time = event.start_date + timedelta(hours=2)
        end_time = start_time + timedelta(hours=1)
        
        session = Session.objects.create(
            event=event,
            title='Test Session',
            slug='test-session',
            description='Test description',
            session_format='talk',
            level='all',
            start_time=start_time,
            end_time=end_time,
            duration_minutes=60
        )
        
        expected = f"Test Session - {start_time.strftime('%Y-%m-%d %H:%M')}"
        assert str(session) == expected
    
    def test_session_end_before_start(self, event, track):
        """Test that end_time must be after start_time"""
        start_time = event.start_date + timedelta(hours=2)
        end_time = start_time - timedelta(hours=1)
        
        with pytest.raises(ValidationError) as exc_info:
            session = Session(
                event=event,
                track=track,
                title='Invalid Session',
                slug='invalid-session',
                description='Test',
                session_format='talk',
                level='all',
                start_time=start_time,
                end_time=end_time,
                duration_minutes=60
            )
            session.full_clean()
        
        assert 'end_time' in exc_info.value.message_dict
    
    def test_session_outside_event_dates(self, event, track):
        """Test that session must be within event dates"""
        # Session before event starts
        start_time = event.start_date - timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        with pytest.raises(ValidationError) as exc_info:
            session = Session(
                event=event,
                track=track,
                title='Early Session',
                slug='early-session',
                description='Test',
                session_format='talk',
                level='all',
                start_time=start_time,
                end_time=end_time,
                duration_minutes=60
            )
            session.full_clean()
        
        assert 'start_time' in exc_info.value.message_dict
    
    def test_session_conflict_detection(self, event, track, speaker):
        """Test that sessions in same track cannot overlap"""
        start_time = event.start_date + timedelta(hours=2)
        
        # Create first session
        session1 = Session.objects.create(
            event=event,
            track=track,
            title='Session 1',
            slug='session-1',
            description='First session',
            session_format='talk',
            level='all',
            start_time=start_time,
            end_time=start_time + timedelta(hours=1, minutes=30),
            duration_minutes=90,
            room='Hall A'
        )
        
        # Try to create overlapping session in same track
        overlapping_start = start_time + timedelta(minutes=30)
        
        with pytest.raises(ValidationError) as exc_info:
            session2 = Session(
                event=event,
                track=track,
                title='Session 2',
                slug='session-2',
                description='Overlapping session',
                session_format='talk',
                level='all',
                start_time=overlapping_start,
                end_time=overlapping_start + timedelta(hours=1),
                duration_minutes=60,
                room='Hall A'
            )
            session2.full_clean()
        
        assert 'start_time' in exc_info.value.message_dict
    
    def test_sessions_in_different_tracks_no_conflict(self, event, organizer, speaker):
        """Test that sessions in different tracks can overlap"""
        track1 = Track.objects.create(
            event=event,
            name='Track 1',
            description='First track'
        )
        track2 = Track.objects.create(
            event=event,
            name='Track 2',
            description='Second track'
        )
        
        start_time = event.start_date + timedelta(hours=2)
        
        # Create session in track 1
        session1 = Session.objects.create(
            event=event,
            track=track1,
            title='Session 1',
            slug='session-1-track1',
            description='First session',
            session_format='talk',
            level='all',
            start_time=start_time,
            end_time=start_time + timedelta(hours=1),
            duration_minutes=60,
            room='Hall A'
        )
        
        # Create overlapping session in track 2 (should succeed)
        session2 = Session.objects.create(
            event=event,
            track=track2,
            title='Session 2',
            slug='session-2-track2',
            description='Second session',
            session_format='talk',
            level='all',
            start_time=start_time,
            end_time=start_time + timedelta(hours=1),
            duration_minutes=60,
            room='Hall B'
        )
        
        assert session1.start_time == session2.start_time
        assert session1.track != session2.track
    
    def test_track_must_belong_to_same_event(self, event, organizer):
        """Test that track must belong to the same event"""
        # Create another event
        now = timezone.now()
        other_event = Event.objects.create(
            title='Other Event',
            slug='other-event',
            description='Another event',
            event_type='conference',
            status='published',
            start_date=now + timedelta(days=60),
            end_date=now + timedelta(days=62),
            registration_start=now,
            registration_end=now + timedelta(days=55),
            venue_name='Other Venue',
            venue_address='456 Other St',
            city='Other City',
            country='Other Country',
            capacity=50,
            organizer=organizer
        )
        
        other_track = Track.objects.create(
            event=other_event,
            name='Other Track',
            description='Track from different event'
        )
        
        start_time = event.start_date + timedelta(hours=2)
        
        with pytest.raises(ValidationError) as exc_info:
            session = Session(
                event=event,
                track=other_track,  # Track from different event
                title='Invalid Session',
                slug='invalid-session',
                description='Test',
                session_format='talk',
                level='all',
                start_time=start_time,
                end_time=start_time + timedelta(hours=1),
                duration_minutes=60
            )
            session.full_clean()
        
        assert 'track' in exc_info.value.message_dict
    
    def test_duration_auto_calculated(self, event, track):
        """Test that duration is auto-calculated if not provided"""
        start_time = event.start_date + timedelta(hours=2)
        end_time = start_time + timedelta(hours=2)  # 2 hours = 120 minutes
        
        session = Session.objects.create(
            event=event,
            track=track,
            title='Auto Duration Session',
            slug='auto-duration',
            description='Test auto duration',
            session_format='workshop',
            level='all',
            start_time=start_time,
            end_time=end_time
            # duration_minutes not provided
        )
        
        assert session.duration_minutes == 120
    
    def test_speaker_names_property(self, event, track):
        """Test speaker_names property"""
        speaker1 = Speaker.objects.create(name='Alice', email='alice@test.com')
        speaker2 = Speaker.objects.create(name='Bob', email='bob@test.com')
        
        start_time = event.start_date + timedelta(hours=2)
        
        session = Session.objects.create(
            event=event,
            track=track,
            title='Multi-Speaker Session',
            slug='multi-speaker',
            description='Session with multiple speakers',
            session_format='panel',
            level='all',
            start_time=start_time,
            end_time=start_time + timedelta(hours=1),
            duration_minutes=60
        )
        session.speakers.add(speaker1, speaker2)
        
        assert session.speaker_names == 'Alice, Bob'
             
    
    def test_max_attendees_for_workshop(self, event, track, speaker):
        """Test max_attendees field for workshops"""
        start_time = event.start_date + timedelta(hours=2)
        
        workshop = Session.objects.create(
            event=event,
            track=track,
            title='Django Workshop',
            slug='django-workshop',
            description='Hands-on Django workshop',
            session_format='workshop',
            level='beginner',
            start_time=start_time,
            end_time=start_time + timedelta(hours=3),
            duration_minutes=180,
            room='Workshop Room',
            max_attendees=30
        )
        
        assert workshop.max_attendees == 30
        assert workshop.session_format == 'workshop'
    
    def test_is_ongoing_property(self, event, track):
        """
        Test the is_ongoing and has_ended properties of Session.
        Ensures sessions are validated within event range.
        """

        now = timezone.now()

        # Adjust event so registration_end < start_date
        event.registration_start = now - timedelta(days=10)
        event.registration_end = now - timedelta(days=2)
        event.start_date = now - timedelta(days=1)
        event.end_date = now + timedelta(days=1)
        event.save()

        # Past session (ended already)
        past_start = now - timedelta(hours=3)
        past_session = Session.objects.create(
            event=event,
            track=track,
            title="Past Session",
            slug="past-session",
            description="Session that has ended",
            session_format="talk",
            level="all",
            start_time=past_start,
            end_time=past_start + timedelta(hours=1),
            duration_minutes=60,
        )
        assert past_session.is_ongoing is False
        assert past_session.has_ended is True

        # Current session (ongoing right now)
        current_start = now - timedelta(minutes=30)
        live_session = Session.objects.create(
            event=event,
            track=track,
            title="Live Session",
            slug="live-session",
            description="Currently ongoing session",
            session_format="workshop",
            level="beginner",
            start_time=current_start,
            end_time=current_start + timedelta(hours=1),
            duration_minutes=60,
        )
        assert live_session.is_ongoing is True
        assert live_session.has_ended is False

        # Future session (not started yet)
        future_start = now + timedelta(hours=2)
        future_session = Session.objects.create(
            event=event,
            track=track,
            title="Future Session",
            slug="future-session",
            description="Will start later",
            session_format="panel",
            level="intermediate",
            start_time=future_start,
            end_time=future_start + timedelta(hours=1),
            duration_minutes=60,
        )
        assert future_session.is_ongoing is False
        assert future_session.has_ended is False


   