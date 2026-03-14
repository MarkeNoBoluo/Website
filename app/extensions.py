"""Flask extensions module.

Centralizes extension instances for better organization and avoids circular imports.
"""

from flask_bcrypt import Bcrypt


# Flask-Bcrypt instance for password hashing
bcrypt = Bcrypt()