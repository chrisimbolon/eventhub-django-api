# ============================================
# apps/tracks/serializers.py
# ============================================

from rest_framework import serializers
from .models import Track


class TrackSerializer(serializers.ModelSerializer):
    """Track serializer"""
    session_count = serializers.IntegerField(read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)
    
    class Meta:
        model = Track
        fields = [
            'id', 'event', 'event_title', 'name', 'description',
            'color', 'room', 'session_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate unique track name per event"""
        event = data.get('event')
        name = data.get('name')
        
        if event and name:
            queryset = Track.objects.filter(event=event, name=name)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError({
                    'name': f'Track "{name}" already exists for this event'
                })
        
        return data


class TrackDetailSerializer(serializers.ModelSerializer):
    """Detailed track serializer with sessions"""
    from apps.sessions.serializers import SessionListSerializer
    
    sessions = SessionListSerializer(many=True, read_only=True)
    session_count = serializers.IntegerField(read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)
    
    class Meta:
        model = Track
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']