# =============================================================================
# apps/mice/permissions.py
# =============================================================================

from rest_framework import permissions


class IsMICEProjectOrganizer(permissions.BasePermission):
    """Allow access only to the organizer of the MICE project."""

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'organizer'):
            return obj.organizer == request.user
        if hasattr(obj, 'mice_project'):
            return obj.mice_project.organizer == request.user
        if hasattr(obj, 'section'):
            return obj.section.quotation.mice_project.organizer == request.user
        if hasattr(obj, 'quotation'):
            return obj.quotation.mice_project.organizer == request.user
        return False
