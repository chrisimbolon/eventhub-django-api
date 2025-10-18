# ============================================
# apps/tracks/views.py
# ============================================

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import Track
from .serializers import TrackSerializer, TrackDetailSerializer
from apps.events.permissions import IsOrganizerOrReadOnly


class TrackViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Track CRUD operations
    """
    queryset = Track.objects.select_related('event').all()
    serializer_class = TrackSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOrganizerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['event']
    search_fields = ['name', 'description']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TrackDetailSerializer
        return TrackSerializer
    
    @action(detail=True, methods=['get'])
    def sessions(self, request, pk=None):
        """Get all sessions in this track"""
        track = self.get_object()
        sessions = track.sessions.select_related('event').prefetch_related('speakers').all()
        from apps.sessions.serializers import SessionListSerializer
        serializer = SessionListSerializer(sessions, many=True)
        return Response(serializer.data)