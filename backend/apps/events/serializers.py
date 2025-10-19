# backend/apps/events/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Event, Registration

User = get_user_model()


class EventListSerializer(serializers.ModelSerializer):
    """Serializer for event list view"""
    organizer_name = serializers.CharField(source='organizer.get_full_name', read_only=True)
    is_registration_open = serializers.BooleanField(read_only=True)
    available_spots = serializers.IntegerField(read_only=True)
    duration_days = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'description', 'event_type', 'status',
            'start_date', 'end_date', 'city', 'country', 'venue_name',
            'capacity', 'current_attendees', 'available_spots',
            'is_registration_open', 'banner_image', 'organizer_name',
            'duration_days', 'created_at'
        ]
        read_only_fields = ['id', 'current_attendees', 'created_at']


class EventDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for event detail view"""
    organizer = serializers.SerializerMethodField()
    is_registration_open = serializers.BooleanField(read_only=True)
    available_spots = serializers.IntegerField(read_only=True)
    duration_days = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    track_count = serializers.SerializerMethodField()
    session_count = serializers.SerializerMethodField()
    registration_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['id', 'slug', 'current_attendees', 'created_at', 'updated_at']
    
    def get_organizer(self, obj):
        return {
            'id': obj.organizer.id,
            'name': obj.organizer.get_full_name(),
            'email': obj.organizer.email
        }
    
    def get_track_count(self, obj):
        return obj.tracks.count()
    
    def get_session_count(self, obj):
        return obj.sessions.count()
    
    def get_registration_count(self, obj):
        return obj.registrations.filter(status__in=['pending', 'confirmed']).count()
    
    def validate(self, data):
        """Custom validation for event dates"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        reg_start = data.get('registration_start')
        reg_end = data.get('registration_end')
        
        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date'
            })
        
        if reg_start and reg_end and reg_end <= reg_start:
            raise serializers.ValidationError({
                'registration_end': 'Registration end must be after registration start'
            })
        
        if reg_end and start_date and reg_end > start_date:
            raise serializers.ValidationError({
                'registration_end': 'Registration must end before event starts'
            })
        
        return data


class EventCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating events"""
    
    class Meta:
        model = Event
        fields = [
            'title', 'slug', 'description', 'event_type', 'status',
            'start_date', 'end_date', 'registration_start', 'registration_end',
            'venue_name', 'venue_address', 'city', 'country',
            'capacity', 'website', 'banner_image'
        ]
    
    def validate(self, data):
        """Custom validation"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        reg_start = data.get('registration_start')
        reg_end = data.get('registration_end')
        
        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date'
            })
        
        if reg_start and reg_end and reg_end <= reg_start:
            raise serializers.ValidationError({
                'registration_end': 'Registration end must be after registration start'
            })
        
        if reg_end and start_date and reg_end > start_date:
            raise serializers.ValidationError({
                'registration_end': 'Registration must end before event starts'
            })
        
        return data



class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for registration"""
    attendee_name = serializers.CharField(source='attendee.get_full_name', read_only=True)
    attendee_email = serializers.CharField(source='attendee.email', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = Registration
        fields = [
            'id', 'event', 'event_title', 'attendee', 'attendee_name',
            'attendee_email', 'status', 'registration_date',
            'confirmation_date', 'dietary_requirements', 'special_requests',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'attendee', 'registration_date', 'confirmation_date',
            'created_at', 'updated_at'
        ]

    def validate(self, data):
        """Validate registration rules"""
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        event = data.get('event')

        if not user or not user.is_authenticated:
            raise serializers.ValidationError({'attendee': 'Authentication required.'})

        #  Check role
        if user.role != 'attendee':
            raise serializers.ValidationError({'attendee': 'Only attendees can register for events.'})

        #  Check duplicates
        if Registration.objects.filter(event=event, attendee=user).exists():
            raise serializers.ValidationError({'event': 'You are already registered for this event.'})

        #  Check event status
        if event.is_full:
            raise serializers.ValidationError({'event': 'This event has reached maximum capacity.'})

        if not event.is_registration_open:
            raise serializers.ValidationError({'event': 'Registration is not currently open for this event.'})

        return data

    def create(self, validated_data):
        validated_data['attendee'] = self.context['request'].user
        return super().create(validated_data)



class RegistrationDetailSerializer(serializers.ModelSerializer):
    """Detailed registration serializer"""
    attendee = serializers.SerializerMethodField()
    event = EventListSerializer(read_only=True)
    
    class Meta:
        model = Registration
        fields = '__all__'
    
    def get_attendee(self, obj):
        return {
            'id': obj.attendee.id,
            'name': obj.attendee.get_full_name(),
            'email': obj.attendee.email
        }