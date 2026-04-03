# AGENTS.md - Personal Blog Repository

## Project Overview

Flask blog app on Raspberry Pi 4B with:
- **Public Blog**: Markdown articles with syntax highlighting (Pygments + mistune)
- **Private Todo**: Eisenhower matrix task manager (login-protected)
- **Auth**: Session-based with bcrypt password hashing
- **External Access**: Cloudflare Tunnel

## Technology Stack

| Component | Technology |
|-----------|------------|
| Web Framework | Flask 3.1.3 |
| WSGI Server | Gunicorn 21.2.0 |
| Database | SQLite 3.x (SQLAlchemy) |
| ORM | Flask-SQLAlchemy 3.1.1 |
| Migrations | Flask-Migrate 4.1.0 |
| Password Hashing | Flask-Bcrypt 1.0.1 |
| Markdown | mistune 3.2.0 + python-frontmatter 1.1.0 |
| Syntax Highlighting | Pygments 2.18.0 |

## Build/Lint/Test Commands

```bash
# Virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Development server
flask --app app run --debug
flask --app app run --host=0.0.0.0 --port=5000 --debug

# Production server
gunicorn -c gunicorn.conf.py

# Database
python init_db.py
python init_db.py --create-admin --username admin --password <password>
flask --app app db migrate -m "Description"
flask --app app db upgrade

# Testing (all tests)
python -m pytest

# Single test file
python -m pytest test_app.py -v
python -m pytest test_auth_routes.py -v

# Single test function
python -m pytest test_app.py::test_health_check_route -v

# With coverage
python -m pytest --cov=app test_*.py
```

## Code Style Guidelines

### Python Version
- Python 3.9+
- Use modern features: f-strings, type hints, match statements

### Imports (PEP 8)
```python
# Standard library first
import os
import re
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

# Third-party
import frontmatter
from flask import Flask, jsonify, render_template

# Local application
from app.extensions import db
from app.models import User
```

### Formatting
- Max line length: 88 characters (Black default)
- 4 spaces per indentation level
- Trailing commas in multi-line structures
- Two blank lines between top-level definitions
- One blank line between method definitions

### Type Hints
Required for all function parameters and return values:
```python
def get_article_by_slug(slug: str) -> Optional[Dict]:
    """Get article by slug.

    Args:
        slug: Article slug from filename

    Returns:
        Article dictionary or None if not found
    """
```

### Naming Conventions
| Type | Convention | Example |
|------|------------|---------|
| Modules | snake_case | `utils.py`, `markdown.py` |
| Classes | PascalCase | `HighlightRenderer`, `User` |
| Functions | snake_case | `generate_csrf_token` |
| Constants | UPPER_CASE | `POSTS_DIR`, `SLUG_PATTERN` |
| Variables | snake_case | `article`, `filepath` |
| Blueprints | snake_case + _bp | `blog_bp`, `todo_bp` |

### Error Handling
- Catch specific exceptions, never bare `except:`
- Log errors before handling when appropriate
- Return `None` or default values for utility functions on failure
- Use proper HTTP error codes in routes (404, 403, 500)
- Don't expose internal error details to users in production

### Documentation
Google-style docstrings:
```python
def parse_article_file(filepath: Path) -> Optional[Dict]:
    """Parse a Markdown article file with frontmatter.

    Args:
        filepath: Path to Markdown file

    Returns:
        Article dictionary or None if parsing fails

    Raises:
        ValueError: If frontmatter is malformed
    """
```

## Architecture

### Application Factory Pattern
```python
from app import create_app
app = create_app()  # Creates and configures Flask app
```

### Blueprint Organization
| Blueprint | URL Prefix | Purpose |
|-----------|------------|---------|
| `blog` | `/blog` | Public article listing and detail |
| `todo` | `/todo` | Eisenhower matrix (login required) |
| `auth` | `/auth` | Login/logout session management |
| `admin` | `/admin` | Admin panel |

### Key Decorators
- `@login_required` - Protects routes requiring authentication
- `@csrf_protected` - Validates CSRF token on POST/PUT/DELETE routes

### CSRF Implementation
- Tokens stored in session (`session['_csrf_token']`)
- Available in templates via `{{ csrf_token }}`
- Include in all mutating forms:
```html
<form method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
</form>
```

### Article Caching
Functions use `@lru_cache(maxsize=100)`. Call `.cache_clear()` to invalidate without restarting.

## Key Constraints

1. **SQLite Only** - `DATABASE_URL` must start with `sqlite:///`
2. **Session Expires on Browser Close** - `SESSION_PERMANENT = False`
3. **Todo/Admin Routes Require Login** - Use `@login_required`
4. **Mutating Routes Require CSRF** - Use `@csrf_protected`
5. **Blog Article Cache** - In-process; restart to pick up new posts

## Project Structure

```
app/
├── __init__.py          # create_app() factory
├── config.py            # Configuration with validation
├── extensions.py        # Flask extensions (db, bcrypt, migrate)
├── models.py            # SQLAlchemy models
├── utils.py             # CSRF, health check utilities
├── markdown.py          # Pygments + mistune rendering
├── templates/           # Jinja2 templates
├── blog/                # Blog blueprint
├── todo/                # Todo blueprint  
├── auth/                # Auth blueprint
└── admin/               # Admin blueprint
posts/                   # Markdown articles (YYYY-MM-DD-slug.md)
tests/                   # Test files
```

## Environment Configuration

```bash
# Required in .env
SECRET_KEY=<min-64-characters>
DATABASE_URL=sqlite:///blog.db
DEBUG=false
LOG_LEVEL=INFO
```

## Troubleshooting

- **App fails to start**: Check `.env` exists with all required variables
- **Database errors**: Run `python init_db.py`
- **CSRF errors**: Ensure form includes `{{ csrf_token }}`
- **Static files 404**: Check `app/static/` exists and Nginx config
