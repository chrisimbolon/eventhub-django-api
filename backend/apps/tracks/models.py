# ============================================
# apps/tracks/models.py
# ============================================

from django.db import models
from django.core.exceptions import ValidationError
from apps.events.models import Event


class Track(models.Model):
    """
    Track for organizing sessions (e.g., Backend Track, Frontend Track)
    """
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='tracks'
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text='Hex color code for UI display'
    )
    
    # Room/Location information
    room = models.CharField(max_length=100, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['event', 'name']
        ordering = ['event', 'name']
        verbose_name = 'Track'
        verbose_name_plural = 'Tracks'
    
    def __str__(self):
        return f"{self.event.title} - {self.name}"
    
    @property
    def session_count(self):
        """Get number of sessions in this track"""
        return self.sessions.count()
