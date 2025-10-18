# ============================================
# apps/events/filters.py
# ============================================

import django_filters
from django.utils import timezone
from .models import Event


class EventFilter(django_filters.FilterSet):
    """
    Advanced filtering for events
    """
    # Date filters
    start_date_after = django_filters.DateTimeFilter(
        field_name='start_date',
        lookup_expr='gte',
        label='Start date after'
    )
    start_date_before = django_filters.DateTimeFilter(
        field_name='start_date',
        lookup_expr='lte',
        label='Start date before'
    )
    end_date_after = django_filters.DateTimeFilter(
        field_name='end_date',
        lookup_expr='gte'
    )
    end_date_before = django_filters.DateTimeFilter(
        field_name='end_date',
        lookup_expr='lte'
    )
    
    # Location filters
    city = django_filters.CharFilter(lookup_expr='iexact')
    country = django_filters.CharFilter(lookup_expr='iexact')
    
    # Status filter
    status = django_filters.MultipleChoiceFilter(choices=Event.STATUS_CHOICES)
    event_type = django_filters.MultipleChoiceFilter(
        choices=[
            ('conference', 'Conference'),
            ('workshop', 'Workshop'),
            ('seminar', 'Seminar'),
            ('meetup', 'Meetup'),
            ('hackathon', 'Hackathon'),
        ]
    )
    
    # Capacity filters
    has_available_spots = django_filters.BooleanFilter(
        method='filter_available_spots',
        label='Has available spots'
    )
    
    # Registration status
    registration_open = django_filters.BooleanFilter(
        method='filter_registration_open',
        label='Registration currently open'
    )
    
    # Time-based filters
    is_upcoming = django_filters.BooleanFilter(
        method='filter_upcoming',
        label='Upcoming events'
    )
    is_ongoing = django_filters.BooleanFilter(
        method='filter_ongoing',
        label='Currently ongoing'
    )
    
    class Meta:
        model = Event
        fields = {
            'title': ['exact', 'icontains'],
            'city': ['exact', 'icontains'],
            'country': ['exact', 'icontains'],
            'status': ['exact'],
            'event_type': ['exact'],
            'organizer': ['exact'],
        }
    
    def filter_available_spots(self, queryset, name, value):
        """Filter events with available spots"""
        if value:
            return queryset.filter(current_attendees__lt=models.F('capacity'))
        return queryset.filter(current_attendees__gte=models.F('capacity'))
    
    def filter_registration_open(self, queryset, name, value):
        """Filter events with open registration"""
        from django.db.models import F, Q
        now = timezone.now()
        
        if value:
            return queryset.filter(
                status='published',
                registration_start__lte=now,
                registration_end__gte=now,
                current_attendees__lt=F('capacity')
            )
        return queryset
    
    def filter_upcoming(self, queryset, name, value):
        """Filter upcoming events"""
        now = timezone.now()
        if value:
            return queryset.filter(start_date__gte=now)
        return queryset.filter(start_date__lt=now)
    
    def filter_ongoing(self, queryset, name, value):
        """Filter currently ongoing events"""
        now = timezone.now()
        if value:
            return queryset.filter(
                start_date__lte=now,
                end_date__gte=now
            )
        return queryset.exclude(
            start_date__lte=now,
            end_date__gte=now
        )