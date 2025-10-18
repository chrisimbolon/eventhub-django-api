# ============================================
# apps/session_manager/models.py
# ============================================

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Q
from apps.events.models import Event
from apps.tracks.models import Track

User = get_user_model()


class Speaker(models.Model):
    """
    Speaker model for managing session speakers
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='speaker_profile',
        blank=True,
        null=True
    )
    
    # Basic Information
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    
    # Professional Information
    title = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=200, blank=True)
    
    # Social Links
    website = models.URLField(blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    linkedin = models.URLField(blank=True)
    github = models.CharField(max_length=100, blank=True)
    
    # Profile
    profile_picture = models.ImageField(
        upload_to='speakers/profiles/',
        blank=True,
        null=True
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Speaker'
        verbose_name_plural = 'Speakers'
    
    def __str__(self):
        return self.name


class Session(models.Model):
    """
    Session model representing a talk/workshop within an event
    """
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('all', 'All Levels'),
    ]
    
    FORMAT_CHOICES = [
        ('talk', 'Talk'),
        ('workshop', 'Workshop'),
        ('panel', 'Panel Discussion'),
        ('lightning', 'Lightning Talk'),
        ('keynote', 'Keynote'),
    ]
    
    # Relationships
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    track = models.ForeignKey(
        Track,
        on_delete=models.SET_NULL,
        related_name='sessions',
        blank=True,
        null=True
    )
    speakers = models.ManyToManyField(
        Speaker,
        related_name='sessions'
    )
    
    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    
    # Session Details
    session_format = models.CharField(
        max_length=20,
        choices=FORMAT_CHOICES,
        default='talk'
    )
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='all'
    )
    
    # Timing
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(db_index=True)
    duration_minutes = models.PositiveIntegerField(
        help_text='Session duration in minutes'
    )
    
    # Location
    room = models.CharField(max_length=100, blank=True)
    
    # Capacity (for workshops)
    max_attendees = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='Maximum attendees (for workshops)'
    )
    
    # Additional Information
    tags = models.CharField(
        max_length=200,
        blank=True,
        help_text='Comma-separated tags'
    )
    slides_url = models.URLField(blank=True)
    recording_url = models.URLField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_time']
        verbose_name = 'Session'
        verbose_name_plural = 'Sessions'
        indexes = [
            models.Index(fields=['event', 'start_time']),
            models.Index(fields=['track', 'start_time']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    def clean(self):
        """Validate session data and check for conflicts"""
        errors = {}
        
        # Validate times
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                errors['end_time'] = 'End time must be after start time'
            
            # Validate duration
            actual_duration = (self.end_time - self.start_time).total_seconds() / 60
            if self.duration_minutes and abs(actual_duration - self.duration_minutes) > 1:
                errors['duration_minutes'] = f'Duration does not match time range (actual: {actual_duration:.0f} minutes)'
        
        # Validate session is within event dates
        if self.event and self.start_time and self.end_time:
            if self.start_time < self.event.start_date or self.end_time > self.event.end_date:
                errors['start_time'] = 'Session must be within event dates'
        
        # Check for scheduling conflicts within the same track
        if self.track and self.start_time and self.end_time:
            conflicts = Session.objects.filter(
                track=self.track,
                event=self.event
            ).exclude(pk=self.pk).filter(
                Q(start_time__lt=self.end_time, end_time__gt=self.start_time)
            )
            
            if conflicts.exists():
                conflicting_session = conflicts.first()
                errors['start_time'] = (
                    f'Time conflict with "{conflicting_session.title}" '
                    f'({conflicting_session.start_time.strftime("%H:%M")} - '
                    f'{conflicting_session.end_time.strftime("%H:%M")})'
                )
        
        # Validate track belongs to same event
        if self.track and self.event:
            if self.track.event != self.event:
                errors['track'] = 'Track must belong to the same event'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        # Calculate duration if not provided
        if not self.duration_minutes and self.start_time and self.end_time:
            self.duration_minutes = int((self.end_time - self.start_time).total_seconds() / 60)
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def speaker_names(self):
        """Get comma-separated speaker names"""
        return ', '.join([speaker.name for speaker in self.speakers.all()])
    
    @property
    def is_ongoing(self):
        """Check if session is currently ongoing"""
        from django.utils import timezone
        now = timezone.now()
        return self.start_time <= now <= self.end_time
    
    @property
    def has_ended(self):
        """Check if session has ended"""
        from django.utils import timezone
        return timezone.now() > self.end_time