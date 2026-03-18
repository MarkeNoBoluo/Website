# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal blog website running on a Raspberry Pi 4B. Dark tech-themed blog with Markdown article rendering and visitor comments, plus a private Eisenhower matrix todo tool. Deployed via Git post-receive hook; tunneled externally via Cloudflare Tunnel.

## Development Commands

```bash
# Activate virtualenv (Windows dev machine)
.venv\Scripts\activate

# Run development server
flask --app app run --debug

# Run with gunicorn (production-like)
gunicorn -w 4 "app:create_app()"

# Database migrations
flask --app app db migrate -m "description"
flask --app app db upgrade

# Run tests
python -m pytest

# Run a single test file
python -m pytest tests/test_blog.py -v
```

## Environment Setup

Copy `.env.example` to `.env`. Required variables:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Min 64 chars random string |
| `DATABASE_URL` | `sqlite:///blog.db` |
| `DEBUG` | `true` or `false` |
| `LOG_LEVEL` | `DEBUG`/`INFO`/`WARNING`/`ERROR`/`CRITICAL` |

`Config.validate()` enforces all these at startup and raises `RuntimeError` if misconfigured.

## Architecture

**Application factory** at `app/__init__.py:create_app()` — registers blueprints, extensions, and context processors.

**Blueprints:**
- `/blog` — `app/blog/` — public blog; article list and detail pages
- `/todo` — `app/todo/` — Eisenhower matrix, login-protected
- `/auth` — `app/auth/` — login/logout session management

**Extensions** (`app/extensions.py`): `db` (SQLAlchemy), `bcrypt` (Flask-Bcrypt), `migrate` (Flask-Migrate), plus custom CSRF token helpers. Extension instances are created here to avoid circular imports.

**Database models** (`app/models.py`): `User` and `Todo`. Todos belong to a `User` and have a `quadrant` (1–4) and `priority` (1–5).

**Blog articles** are flat `.md` files in `posts/` with filename format `YYYY-MM-DD-slug.md`. `app/blog/utils.py` scans, parses frontmatter (via `python-frontmatter`), renders to HTML (via `mistune` + Pygments monokai), and caches results with `@lru_cache`. **Important:** article cache is in-process — a server restart is required to pick up new/updated posts.

**Markdown rendering** (`app/markdown.py`): `HighlightRenderer` extends `mistune.HTMLRenderer` for Pygments-based code block highlighting with monokai style.

**CSRF protection**: Session-based tokens generated via `generate_csrf_token()` in `extensions.py`, injected into all templates via context processor, validated by `@csrf_protected` decorator in `app/utils.py`.

**Templates**: Jinja2 templates live in `app/templates/` (blog, errors, auth) and `app/todo/templates/todo/`. A `base.html` defines the dark-theme layout. The `{{ now }}` and `{{ csrf_token }}` variables are available in every template via context processors.

**Health check**: `GET /health` returns JSON with DB and app status (used by Cloudflare Tunnel monitoring).

## Key Constraints

- **SQLite only** — `DATABASE_URL` must start with `sqlite:///`
- **Session expires on browser close** — `SESSION_PERMANENT = False`
- **Todo routes require login** — use `@login_required` from `app/auth/utils.py`
- **All mutating todo routes require CSRF** — use `@csrf_protected` from `app/utils.py`
- **Blog article cache** — call `scan_articles.cache_clear()` / `get_all_articles.cache_clear()` / `get_article_by_slug.cache_clear()` if you need cache invalidation without a restart
