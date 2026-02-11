# ============================================
# backend/eventmaster/urls.py
# ============================================

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.events.urls')),
    path('api/v1/', include('apps.session_manager.urls')),
    path('api/v1/', include('apps.tracks.urls')),
    path('api/v1/', include('apps.users.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Development: Django serves static files
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ✅ Always serve media (dev AND production)
# WhiteNoise handles /static/, Django handles /media/
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)