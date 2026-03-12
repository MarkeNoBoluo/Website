# Architecture Research

**Domain:** Python personal blog on Raspberry Pi 4B (Flask + SQLite + Markdown files)
**Researched:** 2026-03-12
**Confidence:** HIGH

---

## Standard Architecture

### System Overview

```
Internet / frp tunnel
        |
        v
+-------------------+
|      Nginx        |  ← reverse proxy, static file serving, TLS termination
|  (port 80 / 443)  |
+--------+----------+
         | Unix socket (/tmp/blog.sock)
         v
+-------------------+
|    Gunicorn       |  ← WSGI server, 2 sync workers, managed by systemd
|  (2 workers)      |
+--------+----------+
         |
         v
+---------------------------------------------------+
|              Flask Application                    |
|                                                   |
|  +-----------+  +------------+  +-------------+  |
|  |  blog bp  |  |  todo bp   |  |  auth bp    |  |
|  | (public)  |  | (private)  |  | (login)     |  |
|  +-----------+  +------------+  +-------------+  |
|        |              |                |          |
|  +-----v--------------v----------------v------+  |
|  |              Application Core              |  |
|  |  - config.py   - db.py   - utils.py       |  |
|  +---------------------------------------------+  |
+---------------------------------------------------+
         |                          |
         v                          v
+------------------+    +----------------------+
|   /posts/*.md    |    |    blog.db (SQLite)  |
| (Markdown files  |    |  - comments table    |
|  on filesystem)  |    |  - todos table       |
+------------------+    +----------------------+
```

**Deployment path (Git push to deploy):**

```
Developer machine
    | git push origin main
    v
Git bare repo (/home/pi/blog.git)
    | post-receive hook triggers
    v
Working directory (/home/pi/blog)
    | git checkout -f
    | pip install -r requirements.txt (if changed)
    | systemctl restart blog
    v
Running application (updated)
```

### Component Responsibilities

| Component | Responsibility | Notes |
|-----------|---------------|-------|
| Nginx | Accept external connections; serve static files directly; forward dynamic requests to Gunicorn via Unix socket; terminate TLS if certificate added later | Configured via `/etc/nginx/sites-available/blog` |
| Gunicorn | Run Flask app with 2 pre-fork workers; bind to Unix socket; restart on crash is handled by systemd | Pure Python, no ARM64 compilation needed |
| systemd unit | Start Gunicorn on boot; restart on crash; inject environment variables from `.env` file | `/etc/systemd/system/blog.service` |
| Flask app | Route HTTP requests; render Jinja2 templates; read Markdown files; read/write SQLite; manage session auth | Entry point: `wsgi.py` → `app/__init__.py` |
| blog blueprint | Article list, article detail, comments POST endpoint — all public, no auth required | |
| todo blueprint | Eisenhower matrix CRUD — all routes behind `@login_required` decorator | |
| auth blueprint | Login GET/POST, logout — manages `session['authenticated']` | |
| Markdown layer | Parse `.md` files from `/posts` directory using mistune; extract frontmatter metadata (title, date, slug) | Called at request time; cache parsed HTML in-process dict if needed |
| SQLite db | Persist comments (per article) and todos (four quadrants); no ORM, raw `sqlite3` stdlib | Single file: `blog.db` in working directory |
| Git bare repo | Receives `git push`; `post-receive` hook orchestrates deploy | Located at `/home/pi/blog.git` (separate from working dir) |
| frp/ngrok | Tunnel external traffic to RPi on local network; sits in front of Nginx | Configured independently; Nginx doesn't know about it |

---

## Recommended Project Structure

```
/home/pi/
├── blog.git/                    # Git bare repo — receives git push
│   └── hooks/
│       └── post-receive         # Deploy hook (executable)
└── blog/                        # Working directory — the live application
    ├── wsgi.py                  # Gunicorn entry point: from app import create_app; app = create_app()
    ├── .env                     # Secrets: SECRET_KEY, ADMIN_PASSWORD_HASH (never committed)
    ├── .env.example             # Template for .env, committed to git
    ├── requirements.txt         # Pinned dependencies
    ├── blog.db                  # SQLite database (gitignored)
    ├── posts/                   # Markdown article files
    │   ├── 2026-03-01-hello-world.md
    │   └── 2026-03-10-raspberry-pi-setup.md
    └── app/
        ├── __init__.py          # create_app() factory, register blueprints, init db
        ├── config.py            # Config class: SECRET_KEY, POSTS_DIR, DB_PATH from env
        ├── db.py                # get_db(), close_db(), init_db(), schema migration helpers
        ├── auth.py              # login_required decorator, /login, /logout routes
        ├── blog/
        │   ├── __init__.py      # Blueprint definition: bp = Blueprint('blog', __name__)
        │   ├── routes.py        # /, /post/<slug>, /post/<slug>/comment (POST)
        │   └── markdown.py      # parse_post(filepath) → {title, date, slug, html}
        ├── todo/
        │   ├── __init__.py      # Blueprint definition
        │   └── routes.py        # /todo (GET/POST), /todo/<id>/done, /todo/<id>/delete
        ├── static/
        │   ├── css/
        │   │   └── main.css     # Dark technical theme, Pygments code highlighting CSS
        │   ├── js/
        │   │   └── main.js      # Minimal JS: quadrant drag/drop for todo (optional)
        │   └── fonts/           # Self-hosted fonts if needed (no external CDN dependency)
        └── templates/
            ├── base.html        # Layout, nav, dark theme wrapper
            ├── blog/
            │   ├── index.html   # Article list
            │   └── post.html    # Article detail + comments
            ├── todo/
            │   └── index.html   # Eisenhower matrix four-quadrant view
            └── auth/
                └── login.html   # Single-field password form
```

### Structure Rationale

- **`app/__init__.py` as factory:** `create_app()` pattern allows testing with different configs without importing a module-level app instance. Gunicorn calls `wsgi.py` which calls `create_app()`.
- **Blueprints by feature (`blog/`, `todo/`, `auth`):** Each feature is self-contained. Routes, templates, and any feature-specific helpers stay together. Easier to build and test one feature at a time.
- **`app/db.py` as shared data layer:** Both `blog` and `todo` blueprints need database access. Centralizing `get_db()` / `close_db()` avoids connection duplication and ensures proper teardown via `app.teardown_appcontext`.
- **`posts/` at project root (not inside `app/`):** Markdown files are content, not code. They live alongside `wsgi.py` and `blog.db`. The `POSTS_DIR` config points to this directory. Makes it simple to add new articles without touching any Python.
- **`blog.git/` separate from `blog/`:** The bare repo and working directory are separate. The `post-receive` hook does `git --work-tree=/home/pi/blog --git-dir=/home/pi/blog.git checkout -f` to update the working directory from the bare repo.
- **`.env` gitignored, `.env.example` committed:** Secrets never enter git. `python-dotenv` loads `.env` at startup. The systemd unit also references `EnvironmentFile=/home/pi/blog/.env` as a backup.

---

## Database Schema

Single SQLite file (`blog.db`). Three tables. No ORM.

```sql
-- Comments submitted by visitors on individual articles
CREATE TABLE IF NOT EXISTS comments (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    post_slug  TEXT    NOT NULL,          -- matches filename slug, e.g. "hello-world"
    author     TEXT    NOT NULL DEFAULT 'Anonymous',
    body       TEXT    NOT NULL,
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_comments_post_slug ON comments(post_slug);

-- Eisenhower matrix todos (four quadrants)
CREATE TABLE IF NOT EXISTS todos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    body        TEXT    NOT NULL,
    quadrant    INTEGER NOT NULL CHECK (quadrant IN (1, 2, 3, 4)),
    -- 1 = Important + Urgent   (Do)
    -- 2 = Important + Not Urgent (Schedule)
    -- 3 = Not Important + Urgent (Delegate)
    -- 4 = Not Important + Not Urgent (Eliminate)
    done        INTEGER NOT NULL DEFAULT 0,  -- 0 = open, 1 = done
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_todos_quadrant ON todos(quadrant);
```

**No posts table.** Articles are Markdown files on the filesystem. The slug is derived from the filename (`2026-03-01-hello-world.md` → slug `hello-world`). Frontmatter metadata (title, date) is parsed from the file header at request time. This avoids any sync problem between files and a database index.

**No users table.** There is one admin. The password hash lives in `.env` as `ADMIN_PASSWORD_HASH`. A session flag `session['authenticated'] = True` is set on successful login.

---

## Markdown Article Format Convention

Each `.md` file in `posts/` uses a simple frontmatter block at the top:

```markdown
---
title: Hello World
date: 2026-03-01
---

Article content starts here...
```

The `markdown.py` parser reads files, splits on the `---` delimiter, extracts title and date, then passes the body through mistune. The slug is derived from the filename (strip date prefix and `.md` extension), not from frontmatter — this keeps slugs stable and predictable.

---

## Data Flow

### Public: Article List Page (`GET /`)

```
Browser GET /
    |
    v
Nginx (check: is this /static/? if yes, serve directly)
    | no → forward to Gunicorn via Unix socket
    v
Flask blog blueprint → routes.py index()
    |
    v
markdown.py: scan posts/ directory
    for each .md file:
        - read file
        - parse frontmatter (title, date)
        - derive slug from filename
    sort by date descending
    |
    v
Jinja2 render: templates/blog/index.html
    |
    v
HTTP 200 → Nginx → Browser
```

### Public: Article Detail + Comments (`GET /post/<slug>`)

```
Browser GET /post/hello-world
    |
    v
Flask blog blueprint → routes.py post_detail(slug)
    |
    +-- markdown.py: find posts/<date>-<slug>.md → parse frontmatter + render HTML
    |
    +-- db.py get_db(): SELECT * FROM comments WHERE post_slug = ? ORDER BY created_at ASC
    |
    v
Jinja2 render: templates/blog/post.html (article HTML + comments list + comment form)
    |
    v
HTTP 200 → Browser
```

### Public: Submit Comment (`POST /post/<slug>/comment`)

```
Browser POST /post/hello-world/comment
    (form fields: author, body + CSRF token from Flask-WTF)
    |
    v
Flask-WTF: validate CSRF token → reject if invalid (403)
    |
    v
Flask blog blueprint → routes.py submit_comment(slug)
    |
    +-- validate: body not empty, author trimmed
    +-- db.py: INSERT INTO comments (post_slug, author, body) VALUES (?, ?, ?)
    |
    v
redirect to GET /post/<slug> (Post-Redirect-Get pattern)
```

### Private: Todo Access (auth check)

```
Browser GET /todo
    |
    v
Flask todo blueprint → @login_required decorator
    |
    +-- check session['authenticated']
    |       |
    |   NOT SET → redirect to GET /login
    |       |
    |     SET = True → continue
    |
    v
db.py: SELECT * FROM todos ORDER BY quadrant, done, created_at
    |
    v
Jinja2 render: templates/todo/index.html (four-quadrant grid)
```

### Auth: Login Flow

```
Browser GET /login → render login form (empty)

Browser POST /login (password field + CSRF token)
    |
    v
Flask-WTF: validate CSRF
    |
    v
auth.py: check_password_hash(app.config['ADMIN_PASSWORD_HASH'], form.password.data)
    |
    +-- MATCH   → session['authenticated'] = True → redirect to /todo
    +-- NO MATCH → re-render login form with error message
```

### Deployment Flow (Git push)

```
Developer: git push rpi main
    |
    v
RPi bare repo /home/pi/blog.git receives pack
    |
    v
hooks/post-receive executes:
    git --work-tree=/home/pi/blog --git-dir=/home/pi/blog.git checkout -f
    |
    v
(if requirements.txt changed):
    /home/pi/blog/.venv/bin/pip install -r /home/pi/blog/requirements.txt -q
    |
    v
    sudo systemctl restart blog
    |
    v
systemd stops old Gunicorn, starts new Gunicorn workers
    |
    v
New code is live (downtime: ~1-2 seconds during worker restart)
```

---

## Infrastructure Configuration Architecture

### Nginx Configuration

File: `/etc/nginx/sites-available/blog`

```nginx
server {
    listen 80;
    server_name _;        # catch-all; replace with domain if frp gives a hostname

    # Serve static files directly — Nginx is ~10x faster than Gunicorn for static
    location /static/ {
        alias /home/pi/blog/app/static/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    # All other requests go to Gunicorn via Unix socket
    location / {
        proxy_pass http://unix:/tmp/blog.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
    }
}
```

**Key decision:** Nginx serves `/static/` directly from the filesystem rather than forwarding to Gunicorn. This bypasses Python entirely for CSS/JS/font requests and unloads the Gunicorn workers.

### systemd Unit

File: `/etc/systemd/system/blog.service`

```ini
[Unit]
Description=Personal Blog (Gunicorn)
After=network.target

[Service]
User=pi
Group=www-data
WorkingDirectory=/home/pi/blog
EnvironmentFile=/home/pi/blog/.env
ExecStart=/home/pi/blog/.venv/bin/gunicorn \
    --workers 2 \
    --bind unix:/tmp/blog.sock \
    --timeout 30 \
    --access-logfile /var/log/blog/access.log \
    --error-logfile /var/log/blog/error.log \
    wsgi:app
Restart=always
RestartSec=3
RuntimeDirectory=blog
RuntimeDirectoryMode=0755

[Install]
WantedBy=multi-user.target
```

**Notes:**
- `User=pi Group=www-data`: Gunicorn runs as `pi`; `www-data` group allows Nginx to read the Unix socket.
- `EnvironmentFile`: systemd injects `.env` variables before `ExecStart`; this means `SECRET_KEY` and `ADMIN_PASSWORD_HASH` are available as env vars even if `python-dotenv` fails to load.
- `RuntimeDirectory=blog`: systemd creates `/run/blog/` automatically; alternatively the socket goes in `/tmp/` which is world-writable and simpler.
- Unix socket permissions: Gunicorn creates the socket; the `pi` user owns it; Nginx's `www-data` user needs read access, which the `Group=www-data` line enables.

### Git Bare Repo + post-receive Hook

Setup (run once on RPi):

```bash
# Create bare repo
git init --bare /home/pi/blog.git

# Create working directory
mkdir /home/pi/blog

# On developer machine, add RPi as remote
git remote add rpi pi@raspberrypi.local:/home/pi/blog.git
```

Hook file: `/home/pi/blog.git/hooks/post-receive` (must be executable: `chmod +x`)

```bash
#!/bin/bash
set -e

WORK_TREE=/home/pi/blog
GIT_DIR=/home/pi/blog.git
VENV=/home/pi/blog/.venv
LOG=/var/log/blog/deploy.log

echo "[deploy] $(date) — push received" >> "$LOG"

# Checkout latest code into working directory
git --work-tree="$WORK_TREE" --git-dir="$GIT_DIR" checkout -f main

# Install/update Python dependencies if requirements changed
"$VENV/bin/pip" install -r "$WORK_TREE/requirements.txt" -q >> "$LOG" 2>&1

# Restart the application
sudo systemctl restart blog

echo "[deploy] done" >> "$LOG"
```

**Requirement:** The `pi` user needs passwordless sudo for `systemctl restart blog`. Add to `/etc/sudoers.d/blog`:

```
pi ALL=(ALL) NOPASSWD: /bin/systemctl restart blog
```

### frp / ngrok External Access

frp and ngrok operate at the TCP/HTTP tunnel layer — they forward external traffic to `localhost:80` on the RPi. Nginx receives this traffic exactly as if it came directly. No changes to Nginx, Flask, or any application code are needed.

```
External user → frp server (public IP) → TCP tunnel → RPi frp client → localhost:80 → Nginx
```

**frp client config** (`/home/pi/frpc.toml`):

```toml
serverAddr = "your-frp-server-ip"
serverPort = 7000

[[proxies]]
name   = "blog"
type   = "http"
localPort = 80
customDomains = ["your-domain.example.com"]
```

frp client should also be managed by systemd (separate unit file).

---

## Architectural Patterns

### Pattern 1: Application Factory with Blueprint Registration

**What:** `create_app()` function in `app/__init__.py` instantiates Flask, loads config, registers blueprints, and sets up `db.close_db` as a teardown function. Blueprints are imported inside the factory to avoid circular imports.

**When to use:** Always. This is standard Flask structure for any multi-blueprint app.

**Trade-offs:** Slightly more setup than a single-file app, but it enables proper testing (call `create_app(testing_config)` in tests) and avoids circular import issues.

```python
# app/__init__.py
from flask import Flask
from .config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from .db import close_db, init_db_command
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

    from .blog import bp as blog_bp
    app.register_blueprint(blog_bp)

    from .todo import bp as todo_bp
    app.register_blueprint(todo_bp, url_prefix='/todo')

    from . import auth
    app.register_blueprint(auth.bp)

    return app
```

### Pattern 2: Flask `g` Object for Per-Request DB Connection

**What:** `db.py` uses `flask.g` to hold a single SQLite connection per request. `get_db()` creates the connection on first call within a request; `close_db()` closes it at teardown. All blueprints call `get_db()` — they never open connections themselves.

**When to use:** Always for SQLite in Flask. Creates exactly one connection per request regardless of how many database calls a route makes.

**Trade-offs:** The `g` pattern is Flask-specific. The code is not portable to other frameworks, but that is not a concern for this project.

```python
# app/db.py
import sqlite3
import flask

def get_db():
    if 'db' not in flask.g:
        flask.g.db = sqlite3.connect(
            flask.current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        flask.g.db.row_factory = sqlite3.Row
    return flask.g.db

def close_db(e=None):
    db = flask.g.pop('db', None)
    if db is not None:
        db.close()
```

### Pattern 3: Post-Redirect-Get for All Form Submissions

**What:** After a successful POST (comment submission, todo creation), always redirect to a GET URL rather than rendering a template directly.

**When to use:** Every form submission that modifies state.

**Trade-offs:** One extra HTTP round-trip, but prevents the browser "resubmit on refresh" problem and makes the URL bookmarkable.

```python
# blog/routes.py
@bp.route('/post/<slug>/comment', methods=['POST'])
def submit_comment(slug):
    # ... validate and insert ...
    return redirect(url_for('blog.post_detail', slug=slug))
    # NOT: return render_template(...)
```

### Pattern 4: Filesystem-First Article Discovery

**What:** Articles are discovered by scanning the `posts/` directory at request time, not by querying a database table. The filesystem is the source of truth.

**When to use:** When articles are managed as files (the blog author pushes `.md` files via git). No sync step between filesystem and database is needed.

**Trade-offs:** Slightly slower article list on large post counts (each request scans the directory). For a personal blog with <500 posts this is imperceptible on RPi 4B. If scanning becomes a problem, add an in-process dict cache (`{slug: parsed_post}`) that is populated on first request and invalidated by the post-receive hook touching a sentinel file.

---

## Build Order (Phase Dependencies)

The components have clear dependencies that dictate build order:

```
Phase 1: Infrastructure Foundation
    systemd unit + Gunicorn + Nginx config + Git bare repo + post-receive hook
    |
    └── Dependency: Nothing. This is the deployment pipeline itself.
        Build this first so all subsequent phases deploy via git push.

Phase 2: Flask Application Skeleton
    create_app() factory + config.py + db.py + wsgi.py + .env pattern
    |
    └── Dependency: Phase 1 (deploy pipeline must exist to run the app)

Phase 3: Blog — Article List + Detail
    posts/ directory + markdown.py parser + blog blueprint + templates
    |
    └── Dependency: Phase 2 (app skeleton, db.py for future use)

Phase 4: Blog — Comments
    SQLite comments table + comment form + Flask-WTF CSRF + submit route
    |
    └── Dependency: Phase 3 (need article detail page to attach comments to)

Phase 5: Auth + Todo
    .env password hash + auth blueprint + login_required decorator + todo blueprint + SQLite todos table
    |
    └── Dependency: Phase 2 (app skeleton, session config)
        Note: Auth and Todo are a single unit — the todo page is meaningless without auth.

Phase 6: Dark Theme + Static Assets
    main.css (dark theme) + Pygments CSS (code highlighting) + base.html layout
    |
    └── Dependency: Phase 3 (need templates to style). Can be developed alongside Phase 3.
        Separate phase because visual polish is independent of functionality.
```

**Recommended order summary:**

| Phase | What to Build | Why This Order |
|-------|--------------|----------------|
| 1 | Nginx + Gunicorn + systemd + Git hook | Sets up the deploy pipeline; everything after deploys via git push |
| 2 | Flask factory + config + db.py + wsgi.py | Skeleton that Phase 3-5 build on top of |
| 3 | Markdown parsing + article list + article detail | Core blog value; validates the full deploy pipeline end-to-end |
| 4 | Comments table + comment form + CSRF | Visitor interaction; depends on article detail page existing |
| 5 | Auth + Todo (together) | Todo is gated by auth; build them as one unit |
| 6 | Dark theme CSS + code highlighting | Can overlap Phase 3, but finalise last when templates are stable |

---

## Component Boundaries

| Boundary | Communication | Direction | Notes |
|----------|---------------|-----------|-------|
| Nginx ↔ Gunicorn | Unix socket HTTP/1.1 | Nginx → Gunicorn | Gunicorn creates socket; Nginx connects to it |
| Gunicorn ↔ Flask | WSGI callable | Gunicorn calls Flask | `wsgi.py` exposes `app = create_app()` |
| Flask blueprints ↔ db.py | `get_db()` function call | Blueprint calls db | Blueprints never open their own connections |
| Flask blueprints ↔ markdown.py | Function call | blog blueprint calls markdown | `parse_post(filepath)` returns dict |
| auth.py ↔ todo blueprint | `login_required` decorator | Decorator wraps route function | Decorator reads `flask.session` |
| post-receive hook ↔ systemd | `systemctl restart blog` | Hook calls systemd | Requires passwordless sudo for `pi` user |
| frp/ngrok ↔ Nginx | TCP proxy to port 80 | frp forwards to Nginx | Nginx sees remote IP as tunnel server IP |

---

## Anti-Patterns

### Anti-Pattern 1: Storing Article Content in the Database

**What people do:** Create a `posts` table with `title`, `slug`, `content`, `created_at` columns; write a CMS admin panel to insert rows.

**Why it's wrong:** For this project, articles are authored in VSCode as `.md` files and deployed via git. Adding a database table creates a sync problem: the filesystem and the database can diverge. It also adds an admin panel (explicitly out-of-scope).

**Do this instead:** Treat the `posts/` directory as the database. Derive the slug from the filename. Parse metadata from frontmatter. The filesystem is always in sync because git manages it.

### Anti-Pattern 2: Opening a DB Connection Per Query

**What people do:** `sqlite3.connect(DB_PATH)` at the top of each route function or helper, then closing it after each query.

**Why it's wrong:** Connection setup has overhead; opening multiple connections in one request wastes it. `sqlite3` in WAL mode handles concurrent reads well but opening many short-lived connections under load creates contention.

**Do this instead:** Use the `flask.g` pattern in `db.py`. One connection per request, opened lazily on first use, closed at teardown.

### Anti-Pattern 3: Rendering HTML After POST

**What people do:** After a comment is submitted (POST), render the article page directly from the POST handler.

**Why it's wrong:** If the user refreshes the page, the browser re-submits the POST, submitting the comment again.

**Do this instead:** Post-Redirect-Get. After insert, `return redirect(url_for('blog.post_detail', slug=slug))`. The browser then does a GET, which is safe to refresh.

### Anti-Pattern 4: Storing SECRET_KEY or Password Hash in Source Code

**What people do:** `app.config['SECRET_KEY'] = 'my-secret'` in `config.py`, which is committed to git.

**Why it's wrong:** Even in a private repo, the secret is in git history forever. If the repo becomes public, sessions are compromisable.

**Do this instead:** Always load from environment: `app.config['SECRET_KEY'] = os.environ['SECRET_KEY']`. Store the value in `.env` (gitignored). The systemd `EnvironmentFile` injects it at process start as a backup.

### Anti-Pattern 5: Running as Root on the RPi

**What people do:** Start Gunicorn or Nginx under the `root` user to avoid permission headaches.

**Why it's wrong:** A vulnerability in the web app or Nginx would give an attacker root access to the RPi, including the local network.

**Do this instead:** Run Gunicorn as `pi` (or a dedicated `blog` user). Nginx runs as `www-data` (default). Use `Group=www-data` in the systemd unit so Nginx can read the Unix socket.

---

## Scaling Considerations

This is a personal blog on a single RPi. "Scaling" means handling traffic spikes, not distributed systems.

| Scenario | Architecture Impact |
|----------|-------------------|
| Normal (0-100 daily visitors) | 2 Gunicorn workers is sufficient; SQLite handles reads easily; no changes needed |
| Traffic spike (blog post goes viral, 1k simultaneous) | Gunicorn queue will back up; Nginx keeps accepting but workers are busy; solution: increase `--workers` to 4 if RPi RAM allows (~60MB total); SQLite WAL mode handles concurrent reads without locking |
| Many articles (100+ posts) | `posts/` directory scan on every request adds up; add a simple in-process dict cache in `markdown.py`; populated on first request, reset when post-receive hook touches a sentinel file |
| Large comments volume | Comments table with slug index handles thousands of rows efficiently; no change needed until tens of thousands of comments on a single post |

**First bottleneck on RPi 4B:** RAM, not CPU. Each Gunicorn worker holds the full Flask app in memory (~15-20MB per worker). With 2 workers, the app uses ~40MB. RPi 4B has 2-8GB RAM, so this is not a concern.

**What never needs to change for a personal blog:** SQLite database (single-file, WAL mode, >100k rows fine), Nginx configuration, systemd unit.

---

## Sources

- Flask application factory pattern: https://flask.palletsprojects.com/en/stable/patterns/appfactories/
- Flask `g` object and database connections: https://flask.palletsprojects.com/en/stable/patterns/sqlite3/
- Flask blueprints: https://flask.palletsprojects.com/en/stable/blueprints/
- Gunicorn Unix socket configuration: https://docs.gunicorn.org/en/stable/deploy.html
- Nginx + Gunicorn Unix socket proxy: https://docs.gunicorn.org/en/stable/deploy.html#nginx-configuration
- systemd service file for Python/Gunicorn: https://blog.miguelgrinberg.com/post/running-a-flask-application-as-a-service-with-systemd
- Git bare repo + post-receive deployment pattern: https://git-scm.com/book/en/v2/Git-on-the-Server-Setting-Up-the-Server
- Flask session-based auth pattern: https://flask.palletsprojects.com/en/stable/quickstart/#sessions
- Post-Redirect-Get pattern: https://en.wikipedia.org/wiki/Post/Redirect/Get
- SQLite WAL mode for concurrent reads: https://www.sqlite.org/wal.html

---

*Architecture research for: Python personal blog on Raspberry Pi 4B (Flask + SQLite + Markdown files)*
*Researched: 2026-03-12*
