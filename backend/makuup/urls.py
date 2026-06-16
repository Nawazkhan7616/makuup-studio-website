"""
MakuUP Studio — Root URL Configuration
"""
from django.urls import path, include


urlpatterns = [
    path('api/', include('app.urls')),
    path('api/glow-guide/', include('glow_guide.urls')),
]
