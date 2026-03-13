# Phase 2: Flask Application Skeleton - Research

**Researched:** 2026-03-13
**Domain:** Flask application architecture with authentication and SQLite WAL mode
**Confidence:** HIGH

## Summary

This phase establishes the Flask application skeleton with configuration loading, database connection (WAL mode), blueprint structure, and user authentication functionality. The application will use Flask 3.1.3 with an application factory pattern, Flask-Bcrypt for password hashing, SQLite with WAL mode for concurrent access, and blueprint-based modular organization.

**Primary recommendation:** Implement Flask application factory with three blueprints (auth, blog, todo), SQLite WAL mode configuration, and password-based authentication using Flask-Bcrypt with session management.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Password hashing: Flask-Bcrypt extension
- Session management: Session expires on browser close (no "remember me" feature)
- Login form fields: Username + password (allow multiple admin accounts in future)
- Error display: Inline error below form field (user-friendly, points to incorrect field)
- Protected routes: Use `@login_required` decorator; unauthenticated users redirected to login page
- Logout: Simple session destruction
- WAL mode configuration: Default settings (`PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;`)
- Connection handling: Raw sqlite3 with connection per request (using Flask's `g` object and teardown)
- Error handling: Show generic error page (500) with logged details; no automatic retry
- Database initialization: Create only auth-related tables (users table); comments and todos tables deferred to later phases
- Package structure: Full package per blueprint (`auth/`, `blog/`, `todo/` each with `__init__.py`, `routes.py`, etc.)
- Template organization: Blueprint-specific subdirectories (`auth/templates/auth/login.html`)
- Static files: Global static folder only (`app/static`) — matches existing Nginx configuration
- Application factory migration: Claude's discretion (clean refactoring of existing `app.py` into `app/__init__.py` factory)

### Claude's Discretion
- Application factory migration approach
- Exact Flask-Bcrypt configuration (work factor)
- Session cookie settings (secure, httponly flags)
- Database connection teardown implementation
- Template styling and form layout
- Error page design (generic 500 page)
- Logging configuration for authentication events

### Deferred Ideas (OUT OF SCOPE)
- Configuration extensibility for auth-specific variables (e.g., password hash rounds, session duration) — not selected for discussion
- Comments and todos tables creation — deferred to later phases
- Password reset functionality — out of scope for v1
- "Remember me" feature — explicitly not included
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| AUTH-01 | 博主可通过密码登录进入后台功能（session 认证，密码哈希存 .env） | Flask-Bcrypt for password hashing, session management, login form with username/password fields |
| AUTH-02 | 未登录时无法访问后台路由（`@login_required` 保护） | `@login_required` decorator implementation, session validation, redirect to login page |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Flask | 3.1.3 | Web framework | WSGI-sync, template-first, low RAM (~15MB), established ecosystem |
| Flask-Bcrypt | Latest | Password hashing | Flask extension for bcrypt, handles password hashing/verification |
| python-dotenv | 1.0.1 | Environment loading | Loads `.env` files, already in use from Phase 1 |
| SQLite3 | Built-in | Database | Zero-config, single-file, WAL mode handles concurrent access |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | Latest | Testing framework | Already used in existing test_app.py, maintain consistency |
| Werkzeug | Flask dep | WSGI utilities | Provides secure password hashing utilities if needed |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Flask-Bcrypt | Werkzeug security | Flask-Bcrypt is Flask-specific, cleaner integration |
| SQLite WAL mode | SQLite default | WAL mode prevents "database is locked" with Gunicorn workers |
| Application factory | Global app | Factory enables testing, multiple instances, better structure |

**Installation:**
```bash
pip install flask-bcrypt
# Flask 3.1.3, python-dotenv 1.0.1 already installed from Phase 1
```

## Architecture Patterns

### Recommended Project Structure
```
app/
├── __init__.py              # Application factory create_app()
├── config.py               # Configuration class
├── db.py                   # Database connection with WAL mode
├── templates/
│   ├── base.html          # Base template skeleton
│   └── errors/
│       └── 500.html       # Generic error page
├── auth/                   # Authentication blueprint
│   ├── __init__.py        # Blueprint creation
│   ├── routes.py          # Login/logout routes
│   ├── utils.py           # Password hash/verify utilities
│   └── templates/
│       └── auth/
│           ├── login.html # Login form
│           └── logout.html # Logout confirmation
├── blog/                   # Blog blueprint (placeholder)
│   ├── __init__.py
│   └── routes.py
└── todo/                   # Todo blueprint (placeholder)
    ├── __init__.py
    └── routes.py
```

### Pattern 1: Application Factory
**What:** Create Flask app instance through `create_app()` factory function
**When to use:** Always for production Flask apps
**Example:**
```python
# app/__init__.py
from flask import Flask
from .config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    from .extensions import bcrypt
    bcrypt.init_app(app)

    # Register blueprints
    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    return app
```

### Pattern 2: Database Connection per Request with WAL Mode
**What:** SQLite connection stored in Flask's `g` object, enabled with WAL mode
**When to use:** SQLite databases with concurrent Flask workers
**Example:**
```python
# app/db.py
import sqlite3
from flask import g, current_app

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE_PATH'])
        # Enable WAL mode for concurrent access
        g.db.execute('PRAGMA journal_mode=WAL;')
        g.db.execute('PRAGMA synchronous=NORMAL;')
        g.db.execute('PRAGMA busy_timeout=5000;')
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

### Pattern 3: Blueprint-based Modular Organization
**What:** Organize features into blueprints with own routes, templates, utilities
**When to use:** All Flask applications with multiple features
**Example:**
```python
# app/auth/__init__.py
from flask import Blueprint

bp = Blueprint('auth', __name__, template_folder='templates/auth')

from . import routes
```

### Anti-Patterns to Avoid
- **Global app instance:** Use application factory instead of global `app = Flask(__name__)`
- **Hardcoded configuration:** Load from environment variables, not hardcoded values
- **Direct SQLite connections:** Use connection per request with teardown, not global connection
- **Plain text passwords:** Always hash with bcrypt, never store plain text

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Password hashing | Custom hash algorithm | Flask-Bcrypt | Security vulnerabilities, timing attacks, salt management |
| Session management | Custom session storage | Flask sessions | Secure cookie handling, expiration, serialization |
| Database connection pooling | Custom connection pool | SQLite WAL mode | Concurrency issues, connection leaks, race conditions |
| Configuration validation | Manual validation | python-dotenv + Flask config | Missing validation, type errors, security issues |
| Form validation | Manual form parsing | Flask request handling + templates | XSS vulnerabilities, CSRF, input sanitization |

**Key insight:** Security components (password hashing, sessions) and concurrency solutions (database locking) have subtle edge cases that libraries handle correctly.

## Common Pitfalls

### Pitfall 1: SQLite Connection Leaks
**What goes wrong:** Database connections not closed, leading to "too many connections" errors
**Why it happens:** Missing `teardown_appcontext` handler
**How to avoid:** Register `close_db` function with `app.teardown_appcontext`
**Warning signs:** Database file locks, increasing memory usage

### Pitfall 2: WAL Mode Not Persistent
**What goes wrong:** WAL mode resets to default on application restart
**Why it happens:** PRAGMA settings not saved to database file
**How to avoid:** Execute WAL PRAGMAs on every connection (they persist)
**Warning signs:** "database is locked" errors with concurrent requests

### Pitfall 3: Weak Password Hashing
**What goes wrong:** Passwords vulnerable to brute force attacks
**Why it happens:** Insufficient bcrypt work factor or custom hash
**How to avoid:** Use Flask-Bcrypt with work factor 12 (default)
**Warning signs:** Fast password verification, no salt in hash

### Pitfall 4: Insecure Session Cookies
**What goes wrong:** Session hijacking, XSS attacks
**Why it happens:** Missing secure/httponly flags
**How to avoid:** Configure `SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_HTTPONLY=True`
**Warning signs:** JavaScript can access session cookie, cookies sent over HTTP

### Pitfall 5: Blueprint Template Conflicts
**What goes wrong:** Template not found errors
**Why it happens:** Incorrect template folder paths
**How to avoid:** Use `template_folder='templates/auth'` in blueprint, reference as `auth/login.html`
**Warning signs:** "TemplateNotFound" errors, templates loading from wrong blueprint

## Code Examples

Verified patterns from official sources:

### Flask-Bcrypt Configuration
```python
# app/extensions.py
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# In create_app():
bcrypt.init_app(app)
```

### Password Hashing and Verification
```python
# app/auth/utils.py
from ..extensions import bcrypt

def hash_password(password):
    # For Python 3, decode to string
    return bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(password_hash, password):
    return bcrypt.check_password_hash(password_hash, password)
```

### Login Route with Session
```python
# app/auth/routes.py
from flask import render_template, redirect, url_for, flash, session, request
from . import bp

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Validate credentials
        if validate_credentials(username, password):
            session['user_id'] = username
            flash('Login successful', 'success')
            return redirect(url_for('blog.index'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('auth/login.html')
```

### Login Required Decorator
```python
# app/auth/utils.py
from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Global app instance | Application factory | Flask 0.11+ | Better testing, multiple instances |
| MD5/SHA-256 passwords | Bcrypt/Argon2 | ~2010 | Resistance to GPU/ASIC attacks |
| SQLite rollback journal | WAL mode | SQLite 3.7.0 (2010) | Concurrent reads/writes |
| Manual configuration | Environment variables + .env | Modern DevOps | Security, deployment flexibility |

**Deprecated/outdated:**
- **MD5/SHA-1 password hashing:** Vulnerable to rainbow tables, use bcrypt
- **Global Flask app:** Prevents testing isolation, use factory pattern
- **SQLite without WAL:** "database is locked" with concurrent access

## Open Questions

1. **Flask-Bcrypt work factor optimization for Raspberry Pi**
   - What we know: Default work factor is 12 (2^12 iterations)
   - What's unclear: Optimal work factor for Raspberry Pi 4B performance
   - Recommendation: Start with default 12, measure login time (< 500ms acceptable)

2. **Session cookie SameSite policy**
   - What we know: `SESSION_COOKIE_SAMESITE` can be 'Lax', 'Strict', or 'None'
   - What's unclear: Best setting for local network blog
   - Recommendation: Use 'Lax' for balance of security and functionality

## Sources

### Primary (HIGH confidence)
- Flask-Bcrypt documentation - Installation, configuration, usage patterns
- SQLite WAL documentation - WAL mode configuration, PRAGMA settings, best practices
- Flask 3.1.x documentation - Application factories, blueprints, configuration management

### Secondary (MEDIUM confidence)
- Existing project patterns (app.py, test_app.py) - Configuration validation, testing approach

### Tertiary (LOW confidence)
- Web search limitations prevented verification of some Flask session configuration details

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Flask 3.1.3 already installed, Flask-Bcrypt well-documented
- Architecture: HIGH - Application factory and blueprint patterns are standard Flask practices
- Pitfalls: MEDIUM - Based on known Flask/SQLite issues, some session details need verification

**Research date:** 2026-03-13
**Valid until:** 2026-04-13 (30 days for stable Flask ecosystem)
