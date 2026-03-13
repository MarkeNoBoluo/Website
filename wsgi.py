"""Gunicorn WSGI entry point for Flask blog application."""
from app import app

# This file provides the 'app' object that Gunicorn will use
# Gunicorn command: gunicorn --bind unix:/tmp/blog.sock wsgi:app