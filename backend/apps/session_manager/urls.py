# ============================================
# apps/session_manager/urls.py
# ============================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SessionViewSet, SpeakerViewSet

router = DefaultRouter()
router.register(r'sessions', SessionViewSet, basename='session')
router.register(r'speakers', SpeakerViewSet, basename='speaker')

urlpatterns = [
    path('', include(router.urls)),
]