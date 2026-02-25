"""
URL configuration for vpulse_backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# Customize admin site
admin.site.site_header = "VPulse Admin"
admin.site.site_title = "VPulse Administration"
admin.site.index_title = "Welcome to VPulse Admin Panel"

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation (must come before api/ to avoid conflicts)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API endpoints
    path('api/', include('accounts.urls')),
    
    # Root redirect to docs
    path('', lambda request: redirect('/api/docs/'), name='api-root'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

