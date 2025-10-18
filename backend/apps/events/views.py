from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Event, Registration
from .serializers import (
    EventListSerializer, EventDetailSerializer, 
    EventCreateUpdateSerializer, RegistrationSerializer,
    RegistrationDetailSerializer
)
from .filters import EventFilter
from .permissions import IsOrganizerOrReadOnly


class EventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Event CRUD operations
    
    list: Get all events
    retrieve: Get single event
    create: Create new event (authenticated users)
    update: Update event (organizer only)
    destroy: Delete event (organizer only)
    """
    queryset = Event.objects.select_related('organizer').prefetch_related('tracks', 'sessions')
    permission_classes = [IsAuthenticatedOrReadOnly, IsOrganizerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EventFilter
    search_fields = ['title', 'description', 'city', 'country', 'venue_name']
    ordering_fields = ['start_date', 'end_date', 'created_at', 'capacity', 'current_attendees']
    ordering = ['-start_date']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EventCreateUpdateSerializer
        return EventDetailSerializer
    
    def perform_create(self, serializer):
        """Set organizer to current user"""
        serializer.save(organizer=self.request.user)
    
    @action(detail=True, methods=['get'])
    def registrations(self, request, slug=None):
        """Get all registrations for an event"""
        event = self.get_object()
        
        # Only organizer can see all registrations
        if event.organizer != request.user:
            return Response(
                {'detail': 'Only event organizer can view registrations'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        registrations = event.registrations.select_related('attendee').all()
        serializer = RegistrationSerializer(registrations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def sessions(self, request, slug=None):
        """Get all sessions for an event"""
        event = self.get_object()
        from apps.sessions.serializers import SessionListSerializer
        
        sessions = event.sessions.select_related('track', 'event').prefetch_related('speakers').all()
        serializer = SessionListSerializer(sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def tracks(self, request, slug=None):
        """Get all tracks for an event"""
        event = self.get_object()
        from apps.tracks.serializers import TrackSerializer
        
        tracks = event.tracks.all()
        serializer = TrackSerializer(tracks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, slug=None):
        """Publish an event"""
        event = self.get_object()
        
        if event.organizer != request.user:
            return Response(
                {'detail': 'Only event organizer can publish event'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if event.status == 'published':
            return Response(
                {'detail': 'Event is already published'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        event.status = 'published'
        event.save()
        
        serializer = self.get_serializer(event)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming events"""
        now = timezone.now()
        events = self.queryset.filter(
            start_date__gte=now,
            status='published'
        ).order_by('start_date')[:10]
        
        serializer = EventListSerializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def ongoing(self, request):
        """Get currently ongoing events"""
        now = timezone.now()
        events = self.queryset.filter(
            start_date__lte=now,
            end_date__gte=now,
            status__in=['published', 'ongoing']
        )
        
        serializer = EventListSerializer(events, many=True)
        return Response(serializer.data)


class RegistrationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Registration operations
    
    list: Get user's registrations
    retrieve: Get single registration
    create: Register for an event
    update: Update registration details
    destroy: Cancel registration
    """
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Users can only see their own registrations"""
        user = self.request.user
        if user.is_staff:
            return Registration.objects.select_related('event', 'attendee').all()
        return Registration.objects.filter(attendee=user).select_related('event')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RegistrationDetailSerializer
        return RegistrationSerializer
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a registration"""
        registration = self.get_object()
        
        # Only event organizer can confirm
        if registration.event.organizer != request.user:
            return Response(
                {'detail': 'Only event organizer can confirm registrations'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        registration.confirm()
        serializer = self.get_serializer(registration)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a registration"""
        registration = self.get_object()
        
        # User can cancel own registration, organizer can cancel any
        if registration.attendee != request.user and registration.event.organizer != request.user:
            return Response(
                {'detail': 'You cannot cancel this registration'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        registration.cancel()
        serializer = self.get_serializer(registration)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get user's upcoming event registrations"""
        now = timezone.now()
        registrations = self.get_queryset().filter(
            event__start_date__gte=now,
            status__in=['pending', 'confirmed']
        ).order_by('event__start_date')
        
        serializer = self.get_serializer(registrations, many=True)
        return Response(serializer.data)