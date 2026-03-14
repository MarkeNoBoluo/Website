"""Gunicorn WSGI entry point for Flask blog application."""
from app import create_app

app = create_app()

# This file provides the 'app' object that Gunicorn will use
# Gunicorn command: gunicorn --bind unix:/tmp/blog.sock wsgi:app