
# ============================================
# apps/sessions/views.py
# ============================================

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Session, Speaker
from .serializers import (
    SessionListSerializer, SessionDetailSerializer,
    SessionCreateUpdateSerializer, SpeakerSerializer
)
from apps.events.permissions import IsOrganizerOrReadOnly


class SessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Session CRUD operations
    """
    queryset = Session.objects.select_related('event', 'track').prefetch_related('speakers').all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsOrganizerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event', 'track', 'session_format', 'level']
    search_fields = ['title', 'description', 'speakers__name', 'tags']
    ordering_fields = ['start_time', 'end_time', 'created_at']
    ordering = ['start_time']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SessionListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SessionCreateUpdateSerializer
        return SessionDetailSerializer
    
    @action(detail=False, methods=['get'])
    def ongoing(self, request):
        """Get currently ongoing sessions"""
        now = timezone.now()
        sessions = self.queryset.filter(
            start_time__lte=now,
            end_time__gte=now
        )
        serializer = SessionListSerializer(sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming sessions"""
        now = timezone.now()
        sessions = self.queryset.filter(
            start_time__gte=now
        ).order_by('start_time')[:20]
        serializer = SessionListSerializer(sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def conflicts(self, request, slug=None):
        """Check for potential scheduling conflicts"""
        session = self.get_object()
        
        from django.db.models import Q
        conflicts = Session.objects.filter(
            track=session.track,
            event=session.event
        ).exclude(pk=session.pk).filter(
            Q(start_time__lt=session.end_time, end_time__gt=session.start_time)
        )
        
        serializer = SessionListSerializer(conflicts, many=True)
        return Response({
            'has_conflicts': conflicts.exists(),
            'conflicts': serializer.data
        })


class SpeakerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Speaker CRUD operations
    """
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'company', 'bio']
    ordering_fields = ['name', 'company', 'created_at']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def sessions(self, request, pk=None):
        """Get all sessions for a speaker"""
        speaker = self.get_object()
        sessions = speaker.sessions.select_related('event', 'track').all()
        from .serializers import SessionListSerializer
        serializer = SessionListSerializer(sessions, many=True)
        return Response(serializer.data)