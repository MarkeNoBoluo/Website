# Stack Research

**Domain:** Personal blog on Raspberry Pi 4B (Python, SQLite, Markdown, ARM64)
**Researched:** 2026-03-12
**Confidence:** HIGH

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.11 (system, Bookworm) | Runtime | Ships with RPi OS Bookworm; 3.11 is stable and well-supported; avoid 3.12+ until ecosystem catches up on ARM |
| Flask | 3.1.3 | Web framework | Lightweight WSGI framework with minimal memory footprint (~15MB idle vs Django's ~50MB+); pure-Python wheel installs cleanly on ARM64; sync/template-first design matches a blog's request pattern |
| SQLite | 3 (stdlib) | Database | Zero-config, single-file, ships with Python — no separate DB service consuming RAM; perfect for single-machine RPi deployment with low concurrent write volume |
| Gunicorn | 25.1.0 | WSGI production server | Pure-Python `py3-none-any` wheel — installs on ARM64 with no native compilation; pre-fork worker model is battle-tested for Flask; run 2 workers on RPi to limit RAM use |
| Nginx | system apt | Reverse proxy | Handles static files, TLS termination, and frp tunnel forwarding before requests hit Gunicorn; extremely low idle RAM (~5MB); apt-installable, no pip dependency |
| systemd | system | Process manager | Built into RPi OS Bookworm; no additional install; `systemctl` restarts Gunicorn on crash, starts on boot — preferred over Supervisor which adds a Python daemon |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| mistune | 3.2.0 | Markdown → HTML parsing | At article-read time or at deploy time; use for all `.md` file rendering; fastest Python MD parser, pure Python, installs on ARM64 without issues |
| Werkzeug | 3.1.x (Flask dep) | Password hashing, request utilities | Already included as Flask dependency; use `generate_password_hash` / `check_password_hash` for the todo password — no extra install needed |
| Jinja2 | 3.1.x (Flask dep) | HTML templating | Already included as Flask dependency; use for all server-side rendered pages |
| Flask-WTF | 1.2.x | CSRF protection on comment/login forms | Required whenever you accept POST form data from unauthenticated users; prevents comment-spam attacks |
| python-dotenv | 1.0.x | Environment variable management | Store `SECRET_KEY`, `ADMIN_PASSWORD_HASH` outside source code; loads `.env` file at startup |
| Pygments | 2.18.x | Syntax highlighting in code blocks | Integrate with mistune's `HighlightRenderer` for technical blog posts; pure Python, ARM64-safe |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| venv (stdlib) | Virtual environment isolation | **Required on Bookworm** — RPi OS 12 enforces PEP 668, blocking system-wide `pip install`; create with `python -m venv .venv` |
| VSCode Remote SSH | Editor + debugger | Connect from Windows host to RPi; run Flask dev server directly on RPi via SSH tunnel |
| Git bare repo + post-receive hook | Deployment pipeline | On RPi: `git init --bare`; hook does `git checkout -f`, `pip install -r requirements.txt`, `systemctl restart blog`; push-to-deploy from dev machine |

---

## Flask vs FastAPI: Decision

**Use Flask.** Here is the specific reasoning for this project:

| Criterion | Flask 3.1 | FastAPI |
|-----------|-----------|---------|
| Primary use case | Server-rendered HTML websites | JSON API backends |
| Template rendering | First-class (Jinja2 built-in) | Bolted on (Jinja2 optional) |
| Session/cookie auth | Built-in `flask.session` | Manual implementation |
| Sync SQLite access | Natural (no async complexity) | Forces `run_in_executor` or async driver to avoid blocking the event loop |
| Memory footprint | ~15MB idle | ~20MB idle (includes pydantic, starlette) |
| WSGI server | Gunicorn (pure Python, ARM64 clean) | Uvicorn (also pure Python, but adds async overhead for sync work) |
| Appropriate for blog | YES — designed for HTML-first apps | Overkill — async throughput irrelevant at personal blog scale |

FastAPI excels at high-throughput async JSON APIs. A personal blog serves HTML pages with SQLite reads — Flask's synchronous model is simpler, lighter, and more idiomatic for this workload. FastAPI's speed advantage only matters at 1000+ concurrent requests.

---

## Markdown Library: Decision

**Use mistune 3.2.0.** Reasoning:

| Criterion | mistune 3.2 | python-markdown 3.x | marko 2.x |
|-----------|-------------|---------------------|-----------|
| Performance | Fastest (by large margin) | Moderate | 3x slower than python-markdown |
| CommonMark compliance | Yes | Partial | Strict |
| GitHub Flavored Markdown | Via plugin | Via extension | Native |
| Code highlighting integration | `HighlightRenderer` built-in | Via extension | Via plugin |
| Pure Python / ARM64 | Yes | Yes | Yes |
| Active maintenance | Yes (3.2.0 Dec 2025) | Yes | Yes |

mistune is the correct choice here: a technical blog needs code block highlighting and tables (GFM), mistune's plugin system handles both, and its speed advantage is real when parsing many articles on a 4-core ARM Cortex-A72.

**Integration pattern:**
```python
import mistune
from mistune.renderers.html import HTMLRenderer
from mistune.plugins.formatting import strikethrough
from mistune.plugins.table import table
from mistune.plugins.url import url

renderer = HTMLRenderer(escape=False)
md = mistune.create_markdown(
    renderer=renderer,
    plugins=[strikethrough, table, url]
)
html = md(article_markdown_content)
```

---

## WSGI/ASGI Server: Decision

**Use Gunicorn 25.1.0 with 2 sync workers, bound to a Unix socket.**

- Gunicorn ships as `py3-none-any` — pure Python, no C extensions to compile on ARM64
- Unix socket (`--bind unix:/tmp/blog.sock`) avoids TCP overhead for Nginx → Gunicorn communication on the same machine
- **2 workers** is the right number for RPi 4B: `(2 × CPU_cores) + 1` would be 9, but that wastes RAM; 2 workers consume ~30MB total and handle all realistic personal blog traffic
- Do NOT use `--worker-class gevent` or `uvicorn.workers.UvicornWorker` — both add dependencies with C extensions that complicate ARM64 builds; default `sync` workers are sufficient

**Production command:**
```bash
gunicorn \
  --workers 2 \
  --bind unix:/tmp/blog.sock \
  --timeout 30 \
  --access-logfile /var/log/blog/access.log \
  wsgi:app
```

---

## Process Manager: Decision

**Use systemd. Do not use Supervisor.**

Supervisor is a Python daemon that runs alongside your app — it adds ~15MB RAM overhead and must itself be managed. systemd is built into RPi OS Bookworm, has zero overhead, and is the community-standard for RPi services.

**Example unit file** (`/etc/systemd/system/blog.service`):
```ini
[Unit]
Description=Personal Blog (Gunicorn)
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/blog
EnvironmentFile=/home/pi/blog/.env
ExecStart=/home/pi/blog/.venv/bin/gunicorn --workers 2 --bind unix:/tmp/blog.sock wsgi:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

---

## Auth Approach: Decision

**Use Flask's built-in `session` + Werkzeug's password hashing. Do NOT add Flask-Login.**

Flask-Login adds user model abstraction, `@login_required` decorators, and `UserMixin` — all designed for multi-user auth. This project has exactly one user (the blog owner) with one password. Flask-Login is architectural overkill.

**Simple pattern:**
```python
from werkzeug.security import check_password_hash
from flask import session, redirect, url_for

# In login route:
if check_password_hash(app.config['ADMIN_PASSWORD_HASH'], form.password.data):
    session['authenticated'] = True
    return redirect(url_for('todo'))

# Guard decorator:
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated
```

Store `ADMIN_PASSWORD_HASH` in `.env` (generated offline with `werkzeug.security.generate_password_hash`). Never store plaintext passwords.

---

## ARM64 Compatibility Notes

**Critical context:** piwheels.org does NOT support aarch64/ARM64 as of 2026. If using 64-bit Raspberry Pi OS (Bookworm 64-bit), all pip installs come from PyPI directly.

**Good news:** Every library in this stack ships as a pure-Python wheel (`py3-none-any`). No C extension compilation is needed at install time.

| Library | Wheel Type | ARM64 Install Risk |
|---------|------------|-------------------|
| Flask 3.1.3 | `py3-none-any` | None |
| Werkzeug 3.1.x | `py3-none-any` | None |
| Jinja2 3.1.x | `py3-none-any` | None |
| Gunicorn 25.1.0 | `py3-none-any` | None |
| mistune 3.2.0 | `py3-none-any` | None |
| Flask-WTF 1.2.x | `py3-none-any` | None |
| python-dotenv 1.0.x | `py3-none-any` | None |
| Pygments 2.18.x | `py3-none-any` | None |

**Bookworm venv requirement:** RPi OS Bookworm (Python 3.11) enforces PEP 668 — `pip install` outside a virtualenv is blocked. Always use:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Django | 50MB+ baseline RAM, ORM/migration overhead for a project that has 3 database tables | Flask |
| FastAPI | Built for async JSON APIs; server-rendering HTML requires extra setup; pydantic adds 5MB+ RAM | Flask |
| Flask-SQLAlchemy | ORM abstraction overhead for 3 simple tables; SQLAlchemy's connection pool wastes RAM on single-machine SQLite | `sqlite3` stdlib directly, or `flask.g` pattern |
| Flask-Login | Multi-user auth system for a single-admin blog; adds complexity without benefit | `flask.session` + Werkzeug |
| Supervisor | Extra Python daemon to manage another Python daemon; systemd already does this natively on Bookworm | systemd |
| uvicorn | ASGI server for async frameworks; Flask is WSGI-sync; mixing them adds complexity with no benefit | Gunicorn |
| celery / redis | Task queue for a personal blog — extreme overkill; no async workloads exist | Synchronous request handling |
| SQLAlchemy (standalone) | Same ORM overhead concern; 3 tables (articles, comments, todos) do not need a query builder | `sqlite3` stdlib |

---

## Installation

```bash
# On Raspberry Pi — create venv first (required on Bookworm)
python -m venv .venv
source .venv/bin/activate

# Core application
pip install Flask==3.1.3 mistune==3.2.0 Flask-WTF==1.2.2 python-dotenv==1.0.1 Pygments==2.18.0

# Production server (already included in pip install above as Flask dep, but pin it)
pip install gunicorn==25.1.0

# Freeze
pip freeze > requirements.txt
```

```bash
# System packages (via apt, no venv needed)
sudo apt install nginx
```

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Flask | FastAPI | If the project becomes an API-first service with async I/O, type-validated schemas, and auto-generated OpenAPI docs |
| Flask | Django | If the project grows to multi-user CMS with admin panel, complex ORM relations, and built-in email/auth needs |
| mistune | python-markdown | If you need maximum extension ecosystem (there are hundreds of python-markdown extensions) and don't care about parse speed |
| mistune | marko | If strict CommonMark spec compliance is a hard requirement and GFM is needed natively |
| sqlite3 stdlib | Flask-SQLAlchemy | If the project scales to PostgreSQL or needs complex multi-table queries with ORM convenience |
| systemd | Supervisor | If running a non-systemd Linux distro (Alpine, some containers) |
| Gunicorn sync workers | gunicorn + uvicorn workers | Only if migrating to FastAPI/Starlette later |

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| Flask 3.1.3 | Python 3.9–3.13 | Bookworm ships Python 3.11 — fully compatible |
| Flask 3.1.3 | Werkzeug 3.1.x | Flask pins Werkzeug; install Flask and Werkzeug version is managed automatically |
| Flask-WTF 1.2.x | Flask 3.x | Flask-WTF 1.2 added Flask 3.x support; do not use Flask-WTF < 1.2 with Flask 3 |
| mistune 3.2.0 | Python 3.8+ | No conflicts with Flask stack |
| Gunicorn 25.1.0 | Python 3.7+ | No conflicts; pure Python |
| Pygments 2.18.x | mistune 3.x | Use `mistune.renderers.html.HTMLRenderer` with Pygments as separate highlight step |

---

## Sources

- https://pypi.org/project/Flask/ — Flask 3.1.3 confirmed current version (Feb 2026)
- https://flask.palletsprojects.com/en/stable/changes/ — Flask 3.x changelog, Python version support
- https://www.piwheels.org/project/flask/ — Flask 3.1.3 piwheels build confirmed; ARM Bookworm support verified
- https://www.piwheels.org/faq.html — Confirmed piwheels does NOT support aarch64; all installs via PyPI (pure Python wheels are fine)
- https://pypi.org/project/mistune/ — mistune 3.2.0 confirmed current (Dec 2025)
- https://mistune.lepture.com/ — mistune plugin API (table, GFM, highlight renderer)
- https://pypi.org/project/gunicorn/ — Gunicorn 25.1.0 confirmed; `py3-none-any` wheel
- https://blog.miguelgrinberg.com/post/running-a-flask-application-as-a-service-with-systemd — systemd unit file pattern for Flask/Gunicorn
- https://strapi.io/blog/fastapi-vs-flask-python-framework-comparison — Flask vs FastAPI comparison (MEDIUM confidence, verified against official docs)
- https://forums.raspberrypi.com/viewtopic.php?t=358063 — Bookworm PEP 668 venv requirement confirmed from RPi forums
- https://umatechnology.org/how-to-install-python-packages-in-raspberry-pi-os-bookworm/ — venv pattern for Bookworm confirmed

---

*Stack research for: Personal blog on Raspberry Pi 4B (Python/Flask/SQLite/Markdown)*
*Researched: 2026-03-12*
