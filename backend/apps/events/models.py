# backend/apps/events/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

User = get_user_model()


class Event(models.Model):
    """
    Main Event model representing a conference or technical event
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    # Basic Information
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, db_index=True)
    description = models.TextField()
    
    # Event Details
    event_type = models.CharField(
        max_length=50,
        choices=[
            ('conference', 'Conference'),
            ('workshop', 'Workshop'),
            ('seminar', 'Seminar'),
            ('meetup', 'Meetup'),
            ('hackathon', 'Hackathon'),
        ],
        default='conference'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True
    )
    
    # Dates
    start_date = models.DateTimeField(db_index=True)
    end_date = models.DateTimeField(db_index=True)
    registration_start = models.DateTimeField()
    registration_end = models.DateTimeField()
    
    # Venue Information
    venue_name = models.CharField(max_length=200)
    venue_address = models.TextField()
    city = models.CharField(max_length=100, db_index=True)
    country = models.CharField(max_length=100, db_index=True)
    
    # Capacity Management
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Maximum number of attendees"
    )
    current_attendees = models.PositiveIntegerField(
        default=0,
        help_text="Current number of registered attendees"
    )
    
    # Organizer
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organized_events'
    )
    
    # Additional Information
    website = models.URLField(blank=True, null=True)
    banner_image = models.ImageField(
        upload_to='events/banners/',
        blank=True,
        null=True
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        indexes = [
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['city', 'country']),
            models.Index(fields=['status', 'start_date']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.start_date.strftime('%Y-%m-%d')})"
    
    def clean(self):
        """Validate model data"""
        errors = {}
        
        # Validate dates
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                errors['end_date'] = 'End date must be after start date'
        
        if self.registration_start and self.registration_end:
            if self.registration_end <= self.registration_start:
                errors['registration_end'] = 'Registration end must be after registration start'
        
        if self.registration_end and self.start_date:
            if self.registration_end > self.start_date:
                errors['registration_end'] = 'Registration must end before event starts'
        
        # Validate capacity
        if self.current_attendees > self.capacity:
            errors['current_attendees'] = f'Current attendees ({self.current_attendees}) cannot exceed capacity ({self.capacity})'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def is_full(self):
        """Check if event has reached capacity"""
        return self.current_attendees >= self.capacity
    
    @property
    def available_spots(self):
        """Get number of available spots"""
        return max(0, self.capacity - self.current_attendees)
    
    @property
    def is_registration_open(self):
        """Check if registration is currently open"""
        now = timezone.now()
        return (
            self.status == 'published' and
            self.registration_start <= now <= self.registration_end and
            not self.is_full
        )
    
    @property
    def duration_days(self):
        """Calculate event duration in days"""
        return (self.end_date - self.start_date).days + 1


class Registration(models.Model):
    """
    Attendee registration for events
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('attended', 'Attended'),
    ]
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    attendee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='event_registrations'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Registration details
    registration_date = models.DateTimeField(auto_now_add=True)
    confirmation_date = models.DateTimeField(blank=True, null=True)
    
    # Additional information
    dietary_requirements = models.TextField(blank=True)
    special_requests = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['event', 'attendee']
        ordering = ['-registration_date']
        verbose_name = 'Registration'
        verbose_name_plural = 'Registrations'
        indexes = [
            models.Index(fields=['event', 'status']),
            models.Index(fields=['attendee', 'status']),
        ]
    
    def __str__(self):
        return f"{self.attendee.get_full_name()} - {self.event.title}"
    
    def clean(self):
        """Validate registration"""
        errors = {}
        
        # Check if event is full
        if self.event.is_full and not self.pk:
            errors['event'] = 'Event has reached maximum capacity'
        
        # Check if registration is open
        if not self.event.is_registration_open and not self.pk:
            errors['event'] = 'Registration is not open for this event'
        
        # Check for duplicate registration
        if not self.pk:  # Only for new registrations
            existing = Registration.objects.filter(
                event=self.event,
                attendee=self.attendee
            ).exclude(status='cancelled').exists()
            
            if existing:
                errors['attendee'] = 'Already registered for this event'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        self.full_clean()
        
        # Update event attendee count
        if is_new and self.status in ['pending', 'confirmed']:
            self.event.current_attendees += 1
            self.event.save()
        
        super().save(*args, **kwargs)
    
    def confirm(self):
        """Confirm registration"""
        self.status = 'confirmed'
        self.confirmation_date = timezone.now()
        self.save()
    
    def cancel(self):
        """Cancel registration"""
        if self.status in ['pending', 'confirmed']:
            self.status = 'cancelled'
            self.event.current_attendees = max(0, self.event.current_attendees - 1)
            self.event.save()
            self.save()