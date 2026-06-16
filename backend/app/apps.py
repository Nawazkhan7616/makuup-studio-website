"""
MakuUP Studio — app/apps.py
"""
from django.apps import AppConfig


class AppConfig(AppConfig):
    name = 'app'
    verbose_name = 'MakuUP Studio API'

    def ready(self):
        """Connect to MongoDB after Django settings are fully loaded."""
        try:
            import mongoengine
            from django.conf import settings
            mongoengine.connect(
                db=settings.MONGODB_DB_NAME,
                host=settings.MONGODB_URI,
                tlsAllowInvalidCertificates=True,
            )
        except Exception as e:
            import warnings
            warnings.warn(f"MongoDB connection failed: {e}. Check MONGODB_URI in .env")
