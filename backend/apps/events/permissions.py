# ============================================
# apps/events/permissions.py
# ============================================

from rest_framework import permissions


class IsOrganizerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow organizers to edit events/sessions
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the organizer
        if hasattr(obj, 'organizer'):
            return obj.organizer == request.user
        elif hasattr(obj, 'event'):
            return obj.event.organizer == request.user
        
        return False


class IsAttendeeOrOrganizer(permissions.BasePermission):
    """
    Permission for registrations - attendee or event organizer
    """
    
    def has_object_permission(self, request, view, obj):
        # Allow if user is the attendee
        if obj.attendee == request.user:
            return True
        
        # Allow if user is the event organizer
        if obj.event.organizer == request.user:
            return True
        
        return False
