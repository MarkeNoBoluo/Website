# Phase 2: Flask Application Skeleton - Context

**Gathered:** 2026-03-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish Flask application skeleton with configuration loading, database connection (WAL mode), blueprint structure, and user authentication functionality. Includes application factory `create_app()` that initializes three blueprints (blog, todo, auth), SQLite connection with WAL mode, password-based authentication with session management, and protected routes.

</domain>

<decisions>
## Implementation Decisions

### Authentication Implementation
- Password hashing: Flask-Bcrypt extension
- Session management: Session expires on browser close (no "remember me" feature)
- Login form fields: Username + password (allow multiple admin accounts in future)
- Error display: Inline error below form field (user-friendly, points to incorrect field)
- Protected routes: Use `@login_required` decorator; unauthenticated users redirected to login page
- Logout: Simple session destruction

### Database Connection Management
- WAL mode configuration: Default settings (`PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;`)
- Connection handling: Raw sqlite3 with connection per request (using Flask's `g` object and teardown)
- Error handling: Show generic error page (500) with logged details; no automatic retry
- Database initialization: Create only auth-related tables (users table); comments and todos tables deferred to later phases

### Blueprint Structure and Organization
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

</decisions>

<specifics>
## Specific Ideas

- Inline error display below form fields for login errors
- Username+password login (not single password field)
- SQLite WAL mode with default synchronous=NORMAL
- Blueprint templates in subdirectories matching blueprint name

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app.py` — Environment variable validation logic, Flask app configuration
- `CONFIGURATION.md` — Environment variable documentation pattern
- `app/static/` — Existing static folder (Nginx serves directly)
- `wsgi.py` — Gunicorn entry point (references `app` object)
- `test_app.py` — Testing patterns for Flask routes

### Established Patterns
- Environment variable validation at startup (fail-fast with clear error messages)
- Configuration via `.env` file (excluded from git, `.env.example` as template)
- Systemd service uses `EnvironmentFile` directive for production variables
- Nginx serves static files directly from `app/static/`
- Gunicorn communicates via Unix socket (`/tmp/blog.sock`)

### Integration Points
- Application factory must integrate with existing `wsgi.py` (Gunicorn entry)
- Database connection must use validated `DATABASE_URL` from environment
- Authentication sessions must use `SECRET_KEY` from environment (already validated)
- Blueprint templates extend from base template (to be created in `app/templates/`)
- Static files continue to be served by Nginx from `app/static/`

</code_context>

<deferred>
## Deferred Ideas

- Configuration extensibility for auth-specific variables (e.g., password hash rounds, session duration) — not selected for discussion
- Comments and todos tables creation — deferred to later phases
- Password reset functionality — out of scope for v1
- "Remember me" feature — explicitly not included

</deferred>

---

*Phase: 02-flask-application-skeleton*
*Context gathered: 2026-03-13*