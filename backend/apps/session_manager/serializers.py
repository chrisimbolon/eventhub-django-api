# ============================================
# apps/sessions/serializers.py
# ============================================

from rest_framework import serializers
from .models import Session, Speaker


class SpeakerSerializer(serializers.ModelSerializer):
    """Speaker serializer"""
    
    class Meta:
        model = Speaker
        fields = [
            'id', 'name', 'email', 'bio', 'title', 'company',
            'website', 'twitter', 'linkedin', 'github',
            'profile_picture', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SessionListSerializer(serializers.ModelSerializer):
    """Serializer for session list"""
    speakers = SpeakerSerializer(many=True, read_only=True)
    track_name = serializers.CharField(source='track.name', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    has_ended = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Session
        fields = [
            'id', 'title', 'slug', 'description', 'session_format', 'level',
            'start_time', 'end_time', 'duration_minutes', 'room',
            'event', 'event_title', 'track', 'track_name',
            'speakers', 'max_attendees', 'tags',
            'is_ongoing', 'has_ended', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SessionDetailSerializer(serializers.ModelSerializer):
    """Detailed session serializer"""
    speakers = SpeakerSerializer(many=True, read_only=True)
    speaker_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Speaker.objects.all(),
        source='speakers'
    )
    track_name = serializers.CharField(source='track.name', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    has_ended = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Session
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Custom validation for sessions"""
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        event = data.get('event')
        track = data.get('track')
        duration = data.get('duration_minutes')
        
        # Validate times
        if start_time and end_time:
            if end_time <= start_time:
                raise serializers.ValidationError({
                    'end_time': 'End time must be after start time'
                })
            
            # Check duration
            actual_duration = (end_time - start_time).total_seconds() / 60
            if duration and abs(actual_duration - duration) > 1:
                raise serializers.ValidationError({
                    'duration_minutes': f'Duration does not match time range (actual: {actual_duration:.0f} minutes)'
                })
        
        # Validate session is within event dates
        if event and start_time and end_time:
            if start_time < event.start_date or end_time > event.end_date:
                raise serializers.ValidationError({
                    'start_time': 'Session must be within event dates'
                })
        
        # Validate track belongs to event
        if track and event:
            if track.event != event:
                raise serializers.ValidationError({
                    'track': 'Track must belong to the same event'
                })
        
        # Check for scheduling conflicts
        if track and start_time and end_time:
            from django.db.models import Q
            
            conflicts = Session.objects.filter(
                track=track,
                event=event
            ).exclude(pk=self.instance.pk if self.instance else None).filter(
                Q(start_time__lt=end_time, end_time__gt=start_time)
            )
            
            if conflicts.exists():
                conflicting = conflicts.first()
                raise serializers.ValidationError({
                    'start_time': f'Time conflict with "{conflicting.title}" '
                                 f'({conflicting.start_time.strftime("%H:%M")} - '
                                 f'{conflicting.end_time.strftime("%H:%M")})'
                })
        
        return data


class SessionCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating sessions"""
    speaker_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Speaker.objects.all(),
        source='speakers',
        required=False
    )
    
    class Meta:
        model = Session
        fields = [
            'event', 'track', 'title', 'slug', 'description',
            'session_format', 'level', 'start_time', 'end_time',
            'duration_minutes', 'room', 'max_attendees', 'tags',
            'slides_url', 'recording_url', 'speaker_ids'
        ]
    
    def validate(self, data):
        """Custom validation"""
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        event = data.get('event')
        track = data.get('track')
        
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({
                'end_time': 'End time must be after start time'
            })
        
        if event and start_time and end_time:
            if start_time < event.start_date or end_time > event.end_date:
                raise serializers.ValidationError({
                    'start_time': 'Session must be within event dates'
                })
        
        if track and event and track.event != event:
            raise serializers.ValidationError({
                'track': 'Track must belong to the same event'
            })
        
        return data
