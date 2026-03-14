"""Authentication blueprint.

Provides user authentication functionality including login, logout,
password hashing, and user management.
"""

from flask import Blueprint

# Create authentication blueprint
bp = Blueprint('auth', __name__, template_folder='templates/auth')

# Import routes
from . import routes