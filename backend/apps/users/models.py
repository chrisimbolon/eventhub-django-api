from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model - can be attendee, organizer, or speaker
    """
    ROLE_CHOICES = [
        ('attendee', 'Attendee'),      # ← Regular user attending events
        ('organizer', 'Organizer'),    # ← User organizing events
        ('speaker', 'Speaker'),        # ← User speaking at events
        ('admin', 'Admin'),            # ← System admin
    ]
    
    # The role field determines what they can do!
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='attendee'  # ← Most users are attendees!
    )
    
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    company = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=200, blank=True)
    
    # Social links
    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    github = models.CharField(max_length=100, blank=True)
    
    # Profile picture
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return self.email