"""
MakuUP Studio — Management Command
Run: python manage.py setup_dev
Sets up a local .env from .env.example with dev-friendly defaults.
"""
from django.core.management.base import BaseCommand
import os
import shutil


class Command(BaseCommand):
    help = 'Copy .env.example to .env for local development'

    def handle(self, *args, **options):
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        env_example = os.path.join(backend_dir, '.env.example')
        env_file    = os.path.join(backend_dir, '.env')

        if os.path.exists(env_file):
            self.stdout.write(self.style.WARNING('.env already exists. Skipping.'))
        else:
            shutil.copy(env_example, env_file)
            self.stdout.write(self.style.SUCCESS('.env created from .env.example'))
            self.stdout.write(self.style.WARNING('IMPORTANT: Fill in your real values in .env before running the server.'))
