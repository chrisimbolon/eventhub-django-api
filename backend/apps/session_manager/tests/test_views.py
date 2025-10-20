# backend/apps/session_manager/tests/test_views.py

import pytest
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from apps.session_manager.models import Session, Speaker 
from apps.events.models import Event
from apps.tracks.models import Track
from apps.users.models import User


@pytest.mark.django_db
class TestSessionViewSet:
    """Test cases for Session API endpoints"""
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    @pytest.fixture
    def organizer(self):
        return User.objects.create_user(
            username='organizer',
            email='organizer@test.com',
            password='testpass123',
            role='organizer'
        )
    
    @pytest.fixture
    def speaker_user(self):
        return User.objects.create_user(
            username='speaker',
            email='speaker@test.com',
            password='testpass123',
            role='speaker'
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
            description='Backend sessions',
            color='#3B82F6'
        )
    
    @pytest.fixture
    def speaker(self, speaker_user):
        return Speaker.objects.create(
            user=speaker_user,
            name='Test Speaker',
            email='speaker@test.com',
            bio='Test speaker bio',
            title='Senior Engineer',
            company='TechCorp'
        )
    
    @pytest.fixture
    def session(self, event, track, speaker):
        start_time = event.start_date + timedelta(hours=2)
        session = Session.objects.create(
            event=event,
            track=track,
            title='Django Best Practices',
            slug='django-best-practices',
            description='Learn Django best practices',
            session_format='talk',
            level='intermediate',
            start_time=start_time,
            end_time=start_time + timedelta(hours=1, minutes=30),
            duration_minutes=90,
            room='Hall A'
        )
        session.speakers.add(speaker)
        return session
    
    def test_list_sessions_unauthenticated(self, api_client, session):
        """Test listing sessions without authentication"""
        url = '/api/v1/sessions/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
    
    def test_retrieve_session_unauthenticated(self, api_client, session):
        """Test retrieving a single session without authentication"""
        # FIX: Use session.slug for lookup
        url = f'/api/v1/sessions/{session.slug}/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Django Best Practices'
    
    def test_create_session_as_organizer(self, api_client, event, track, speaker, organizer):
        """Test creating a session as event organizer"""
        api_client.force_authenticate(user=organizer)
        
        start_time = event.start_date + timedelta(hours=4)
        url = '/api/v1/sessions/'
        data = {
            'event': event.id,
            'track': track.id,
            'title': 'New Session',
            'slug': 'new-session',
            'description': 'A new session',
            'session_format': 'workshop',
            'level': 'beginner',
            'start_time': start_time.isoformat(),
            'end_time': (start_time + timedelta(hours=2)).isoformat(),
            'duration_minutes': 120,
            'room': 'Hall B',
            'speakers': [speaker.id]
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Session.objects.filter(slug='new-session').exists()
    
    def test_create_session_unauthenticated(self, api_client, event, track):
        """Test that unauthenticated users cannot create sessions"""
        start_time = event.start_date + timedelta(hours=4)
        url = '/api/v1/sessions/'
        data = {
            'event': event.id,
            'track': track.id,
            'title': 'Unauthorized Session',
            'slug': 'unauthorized-session',
            'description': 'Should fail',
            'session_format': 'talk',
            'level': 'all',
            'start_time': start_time.isoformat(),
            'end_time': (start_time + timedelta(hours=1)).isoformat(),
            'duration_minutes': 60,
            'room': 'Hall C'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_session_as_organizer(self, api_client, session, organizer):
        """Test updating a session as event organizer"""
        api_client.force_authenticate(user=organizer)
        
        # FIX: Use session.slug for lookup
        url = f'/api/v1/sessions/{session.slug}/'
        data = {
            'title': 'Updated Session Title',
            'level': 'advanced'
        }
        
        response = api_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        session.refresh_from_db()
        assert session.title == 'Updated Session Title'
        assert session.level == 'advanced'
    
    def test_delete_session_as_organizer(self, api_client, session, organizer):
        """Test deleting a session as event organizer"""
        api_client.force_authenticate(user=organizer)
        
        # FIX: Use session.slug for lookup
        url = f'/api/v1/sessions/{session.slug}/'
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Session.objects.filter(id=session.id).exists()
    
    def test_filter_sessions_by_event(self, api_client, session, organizer):
        """Test filtering sessions by event"""
        # Create another event with a session
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
        
        # Assumes Track model is accessible for creation
        track2 = Track.objects.create(
            event=other_event,
            name='Other Track',
            description='Other track'
        )
        
        start_time = other_event.start_date + timedelta(hours=2)
        Session.objects.create(
            event=other_event,
            track=track2,
            title='Other Session',
            slug='other-session',
            description='Session in other event',
            session_format='talk',
            level='all',
            start_time=start_time,
            end_time=start_time + timedelta(hours=1),
            duration_minutes=60,
            room='Hall A'
        )
        
        # Filter by first event
        url = f'/api/v1/sessions/?event={session.event.id}'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['title'] == 'Django Best Practices'
    
    def test_search_sessions(self, api_client, session):
        """Test searching sessions by title"""
        url = '/api/v1/sessions/?search=Django'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1


@pytest.mark.django_db
class TestSpeakerViewSet:
    """Test cases for Speaker API endpoints"""
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    @pytest.fixture
    def organizer(self):
        return User.objects.create_user(
            username='organizer',
            email='organizer@test.com',
            password='testpass123',
            role='organizer'
        )
    
    @pytest.fixture
    def speaker(self):
        # Assumes Speaker is correctly imported from apps.session_manager.models
        return Speaker.objects.create(
            name='John Speaker',
            email='john@speaker.com',
            bio='Experienced speaker',
            title='Senior Engineer',
            company='TechCorp'
        )
    
    def test_list_speakers_unauthenticated(self, api_client, speaker):
        """Test listing speakers without authentication"""
        url = '/api/v1/speakers/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
    
    def test_retrieve_speaker_unauthenticated(self, api_client, speaker):
        """Test retrieving a single speaker without authentication"""
        # SpeakerViewSet defaults to 'pk' (ID)
        url = f'/api/v1/speakers/{speaker.id}/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'John Speaker'
    
    def test_create_speaker_as_organizer(self, api_client, organizer):
        """Test creating a speaker as organizer"""
        api_client.force_authenticate(user=organizer)
        
        url = '/api/v1/speakers/'
        data = {
            'name': 'Jane Speaker',
            'email': 'jane@speaker.com',
            'bio': 'Python expert',
            'title': 'Tech Lead',
            'company': 'DevCorp'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Speaker.objects.filter(email='jane@speaker.com').exists()
    
    def test_update_speaker_as_organizer(self, api_client, speaker, organizer):
        """Test updating a speaker"""
        api_client.force_authenticate(user=organizer)
        
        url = f'/api/v1/speakers/{speaker.id}/'
        data = {'bio': 'Updated bio'}
        
        response = api_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        speaker.refresh_from_db()
        assert speaker.bio == 'Updated bio'
    
    def test_search_speakers(self, api_client, speaker):
        """Test searching speakers by name"""
        url = '/api/v1/speakers/?search=John'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1
