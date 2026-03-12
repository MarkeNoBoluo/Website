# Project Research Summary

**Project:** Personal Blog on Raspberry Pi 4B
**Domain:** Self-hosted personal technical blog with private productivity tool
**Researched:** 2026-03-12
**Confidence:** HIGH

## Executive Summary

This is a server-rendered personal blog running on a Raspberry Pi 4B, authored in Markdown, served over a public tunnel, and extended with a private Eisenhower Matrix task manager. The canonical approach for this constraint profile is Flask (WSGI, sync, low RAM) + SQLite (zero-config, single-file) + Gunicorn (2 workers, Unix socket) + Nginx (reverse proxy, static files) + systemd (process management). Every library in this stack ships as a pure-Python wheel (`py3-none-any`), which eliminates ARM64 compilation problems entirely. The full stack fits comfortably within RPi 4B's RAM constraints, with ~40MB for Gunicorn workers and ~5MB for Nginx idle.

The recommended build approach follows a strict dependency order: infrastructure and deploy pipeline first, then Flask application skeleton, then blog content features, then comments, then auth and todo together. This order means every feature after Phase 1 deploys via git push and is immediately testable on live hardware. The Markdown filesystem (not a database table) is the source of truth for articles; SQLite stores only comments and tasks. Password auth is a single-session mechanism shared by the todo tool and comment moderation — build it once in a dedicated blueprint.

The most significant risks fall into two categories: security mistakes made at project initialization (SECRET_KEY in git, plaintext password in .env) and infrastructure wiring mistakes that cause silent failures (Unix socket permissions causing 502, post-receive hook partial deploys, frp tunnel not managed by systemd). Both categories are addressed by getting the infrastructure phase correct before writing any application code. SD card wear from excessive SQLite writes and XSS via comment rendering are the only ongoing operational risks, and both have clear preventions that must be in place from day one.

---

## Key Findings

### Recommended Stack

Flask 3.1.3 is the unambiguous choice over FastAPI for this project. FastAPI is designed for high-throughput async JSON APIs; Flask is designed for synchronous server-rendered HTML websites. Flask's sync/SQLite model is simpler, lighter (~15MB idle vs ~20MB), and more idiomatic for a blog serving HTML pages to a handful of daily visitors. The entire stack avoids native extensions: every pip package is `py3-none-any`, so ARM64 (64-bit RPi OS Bookworm) is a non-issue. The Bookworm PEP 668 venv requirement is critical — `pip install` outside a virtualenv is blocked on Bookworm, so `.venv` is mandatory.

**Core technologies:**
- **Python 3.11** (system, Bookworm) — ships with RPi OS; stable; no upgrade needed
- **Flask 3.1.3** — lightweight WSGI framework; Jinja2 and Werkzeug included; designed for HTML-first apps
- **SQLite 3** (stdlib) — zero-config, single-file, zero RAM overhead as a service; handles all blog/task traffic
- **mistune 3.2.0** — fastest Python Markdown parser; pure Python; GFM table/strikethrough/URL plugins; Pygments integration
- **Gunicorn 25.1.0** — pure-Python WSGI server; 2 sync workers on Unix socket; managed by systemd
- **Nginx** (apt) — static file serving (~10x faster than Gunicorn for assets); reverse proxy; TLS termination; rate limiting
- **systemd** (built-in) — zero-overhead process manager; replaces Supervisor; starts on boot, restarts on crash
- **Flask-WTF 1.2.x** — CSRF protection on comment and login forms; required for any unauthenticated POST
- **python-dotenv 1.0.x** — loads SECRET_KEY and ADMIN_PASSWORD_HASH from .env; keeps secrets out of source

**What to avoid:** Django (50MB+ RAM), FastAPI (async/JSON-first), Flask-SQLAlchemy (ORM overkill for 3 tables), Flask-Login (multi-user abstraction for a single-admin blog), Supervisor (redundant with systemd), Docker (container runtime RAM overhead).

### Expected Features

**Must have (table stakes — v1 launch):**
- Markdown article list page (reverse-chronological, title + date) — core visitor entry point
- Article detail page with rendered Markdown and syntax highlighting — core content delivery
- Dark technical CSS theme + responsive layout — stated aesthetic; table stakes for 2026
- Per-article anonymous comments (name + body) with honeypot spam defense — visitor interaction
- SQLite schema (comments + todos tables) — shared persistence layer
- Password auth (session-based, env-var hash) — gates todo and comment moderation
- Eisenhower Matrix UI (four quadrants: add, complete, delete) — owner productivity tool
- Git post-receive deployment hook — frictionless publish workflow
- 404 page — professionalism baseline

**Should have (v1.x — add after core is working):**
- RSS feed (`/feed.xml`) — high value for tech readers, low implementation cost
- Open Graph meta tags — article links shared in chat/social render with previews
- Sitemap (`/sitemap.xml`) + `robots.txt` — search engine discoverability
- Comment moderation view (approve/delete) — admin view for managing comments
- About page — when there's something to say

**Defer (v2+ — concrete trigger required):**
- Article tags/categories — defer until 20+ articles and content patterns emerge
- Full-text search — defer until browser Ctrl+F is genuinely insufficient
- Pagination — defer until 200+ articles
- Email comment notifications — defer unless comments become high-volume

**Anti-features (do not build):** Web-based CMS/admin panel for articles (VSCode SSH is already the workflow), OAuth/social login for comments (breaks anonymous requirement), real-time comments (WebSocket overkill for personal blog), microservices, Docker.

### Architecture Approach

The architecture is a single Flask application with three blueprints (blog, todo, auth), a shared db.py using the `flask.g` per-request connection pattern, and a markdown.py module that treats the `posts/` filesystem as the article database. Nginx sits in front of Gunicorn via a Unix socket, serving static files directly from the filesystem. systemd manages both Gunicorn and the frp tunnel client. A git bare repo with a post-receive hook provides push-to-deploy from the developer's machine.

**Major components:**
1. **Nginx** — external-facing reverse proxy; serves `/static/` directly; forwards dynamic requests to Gunicorn via Unix socket; enforces rate limits on comment POST endpoints
2. **Gunicorn (2 workers)** — WSGI server; bound to Unix socket `/tmp/blog.sock`; managed by systemd with `Restart=always`
3. **Flask application** — three blueprints: `blog` (public article/comment routes), `todo` (private Eisenhower matrix, `@login_required`), `auth` (login/logout, `session['authenticated']`)
4. **db.py** — `get_db()` via `flask.g`; single SQLite connection per request; WAL mode + `synchronous=NORMAL` set at init; `close_db()` registered as teardown
5. **markdown.py** — scans `posts/` directory; parses YAML-style frontmatter; runs body through mistune with table/strikethrough/URL plugins; slug derived from filename
6. **Git bare repo + post-receive hook** — receives `git push`; checks out to working directory; runs pip if requirements changed; restarts blog service via passwordless sudo
7. **frp/ngrok** — tunnel client managed by systemd; routes external traffic to Nginx port 80; never bypasses Nginx

**Key patterns:** Application factory (`create_app()`) for testability and blueprint registration; Post-Redirect-Get for all form submissions; filesystem-first article discovery (no posts table); secrets only in `.env` (gitignored), loaded via systemd `EnvironmentFile` and python-dotenv.

### Critical Pitfalls

1. **XSS via comment rendering** — Never use `| safe` on user-submitted content; never run comment body through mistune; rely on Jinja2's default auto-escaping (`{{ comment.body }}` without `safe` filter). If Markdown comments are ever desired, sanitize with `nh3` after rendering. Must be correct from day one — retroactive sanitization of stored comments is risky.

2. **SECRET_KEY committed to git** — Add `.env` to `.gitignore` before the first `git add`. Generate key with `secrets.token_hex(32)`. Store only the hash of the admin password (`pbkdf2:sha256:...`), never plaintext. A leaked SECRET_KEY allows session cookie forgery, bypassing todo auth entirely. If ever committed, rotate immediately and purge from git history with `git filter-repo`.

3. **SQLite "database is locked" under Gunicorn multi-worker** — Enable WAL mode and set `timeout=15` in `get_db()`. WAL mode allows concurrent readers and a single writer without blocking. Set in `init_db()` schema script so it persists in the database file. Also set `synchronous=NORMAL` (safe with WAL, halves write IOPS vs FULL — critical for SD card longevity).

4. **Nginx 502 Bad Gateway from Unix socket permission mismatch** — Gunicorn (running as `pi`) creates the socket; Nginx (running as `www-data`) cannot read it by default. Fix: add `www-data` to the `pi` group (`usermod -aG pi www-data`) and run Gunicorn with `--umask 007`. Verify the full chain with `curl --unix-socket /tmp/blog.sock http://localhost/` before building any features.

5. **Post-receive hook partial deploy** — Hook must use `#!/bin/bash` (not `/bin/sh`/dash) and `set -e` (abort on any error). Use venv pip directly (`$VENV/bin/pip`) rather than `source activate`. Configure passwordless sudo for exactly `systemctl restart blog`. Test end-to-end with a trivial push before building application features. Silent partial deploys (code updated, service not restarted) waste hours of debugging time.

6. **frp/ngrok tunnel not managed by systemd** — Tunnel clients started in terminal sessions or with `nohup` die on SSH disconnect and reboot. Run as a systemd service with `Restart=always`. Set frp keepalive (`heartbeat_interval=10`) to survive NAT timeouts. Without this, the site is silently unreachable with no alerting.

7. **Comment spam without rate limiting** — CSRF protection (Flask-WTF) does not stop bots that parse the token before submitting. Add Nginx `limit_req_zone` (2 requests/minute per IP, burst 3) on the comment endpoint at the same time the comment feature is built. Combine with the honeypot hidden field as a secondary layer.

---

## Implications for Roadmap

Based on the component dependency graph from ARCHITECTURE.md and the pitfall-to-phase mapping from PITFALLS.md, the following phase structure is recommended. The architecture research explicitly documents this order with rationale — it should be followed closely.

### Phase 1: Infrastructure Foundation

**Rationale:** The deployment pipeline (Nginx + Gunicorn + systemd + git bare repo + post-receive hook + frp tunnel) must exist before any application code is written. Every subsequent phase deploys via `git push`. Testing on real RPi hardware from the first push eliminates a class of "works on dev, broken on Pi" surprises.

**Delivers:** A working deployment pipeline that accepts `git push`, restarts the service, and serves a placeholder Flask response through the full Nginx → Gunicorn → Flask → Nginx → frp chain.

**Addresses:** Git post-receive deployment hook (FEATURES.md P1); frp/ngrok external access (ARCHITECTURE.md)

**Avoids:** Post-receive hook partial deploy (PITFALLS #5); Nginx 502 socket permission mismatch (PITFALLS #6); frp tunnel not managed by systemd (PITFALLS #7)

**Must verify before proceeding:** `curl --unix-socket /tmp/blog.sock http://localhost/` returns 200; `git push` triggers service restart; `systemctl status frpc` shows `active (running)`.

### Phase 2: Flask Application Skeleton

**Rationale:** The `create_app()` factory, config.py, db.py (with WAL mode), wsgi.py, .env pattern, and blueprint registration are the foundation that Phases 3-5 build on. Getting WAL mode and the .env/gitignore pattern correct here prevents the SQLite locking and SECRET_KEY pitfalls before any feature code is written.

**Delivers:** A deployable Flask app skeleton with proper config loading, database connection management (WAL + synchronous=NORMAL), three registered blueprint stubs, and secrets correctly kept out of git.

**Uses:** Flask 3.1.3, python-dotenv, sqlite3 stdlib, Werkzeug password hashing (STACK.md)

**Implements:** Application factory pattern, `flask.g` per-request DB connection pattern (ARCHITECTURE.md)

**Avoids:** SECRET_KEY committed to git (PITFALLS #4); SQLite locked errors (PITFALLS #2); SD card write wear from synchronous=FULL (PITFALLS #3)

### Phase 3: Blog — Article List and Detail

**Rationale:** This is the core blog value. It validates the full deploy pipeline end-to-end with real content and establishes the Markdown parser that RSS, sitemap, and the article detail page all depend on. Build this before comments because comments attach to article detail pages.

**Delivers:** Working article list (reverse-chronological, title + date + excerpt) and article detail page (rendered Markdown, syntax highlighting, dark theme applied), with 404 handling.

**Uses:** mistune 3.2.0, Pygments 2.18.x, Jinja2 (Flask dep) (STACK.md)

**Implements:** `markdown.py` filesystem-first article discovery, blog blueprint routes (`/` and `/post/<slug>`), `base.html` dark theme layout, Nginx static file serving for CSS/fonts (ARCHITECTURE.md)

**Addresses:** Article list + detail pages (FEATURES.md P1); syntax highlighting (FEATURES.md P1); dark theme + responsive CSS (FEATURES.md P1); 404 page (FEATURES.md P1)

**Avoids:** Storing article content in SQLite (ARCHITECTURE.md anti-pattern #1); rendering Markdown on every request without caching (consider in-process dict cache from the start if the Pi is under load)

### Phase 4: Comments

**Rationale:** Comments depend on the article detail page existing. CSRF protection and the honeypot must ship in the same phase as the comment form — adding them later risks bot accumulation in the database. Nginx rate limiting on the comment endpoint is also part of this phase, not an afterthought.

**Delivers:** Per-article anonymous comment submission (name + body, honeypot field, CSRF token), comment display below article, and Nginx rate limiting on the comment POST endpoint.

**Uses:** Flask-WTF 1.2.x for CSRF; sqlite3 stdlib for comments table; Nginx `limit_req_zone` for rate limiting (STACK.md)

**Implements:** `POST /post/<slug>/comment` with Post-Redirect-Get pattern; comments table in blog.db; submit_comment route in blog blueprint (ARCHITECTURE.md)

**Addresses:** Anonymous comments + honeypot (FEATURES.md P1); comment display (FEATURES.md P1)

**Avoids:** XSS via comment rendering (PITFALLS #1 — never use `| safe` on comment.body, never run through mistune); comment spam (PITFALLS #8 — Nginx rate limiting + honeypot field); POST-without-redirect browser resubmit (ARCHITECTURE.md anti-pattern #3)

### Phase 5: Auth and Eisenhower Matrix Todo

**Rationale:** Auth and todo are a single unit — the todo page is meaningless without auth, and auth is not needed for any public feature. Building them together avoids a half-implemented auth system sitting idle. The session mechanism built here is also reused by the comment moderation view (v1.x).

**Delivers:** Password login (session-based, Werkzeug hash check), `@login_required` decorator, logout route, and a fully functional four-quadrant Eisenhower Matrix UI (add task to quadrant, mark done, delete).

**Uses:** Flask session, Werkzeug `check_password_hash`, sqlite3 todos table, Flask-WTF CSRF on login form (STACK.md)

**Implements:** auth blueprint (login/logout routes, `session['authenticated']`), todo blueprint (`@login_required` on all routes), todos table in blog.db (ARCHITECTURE.md)

**Addresses:** Password auth (FEATURES.md P1); Eisenhower Matrix UI (FEATURES.md P1); SQLite todos table (FEATURES.md P1)

**Avoids:** Flask-Login (overkill for single-admin blog — STACK.md decision); storing plaintext admin password (PITFALLS #4 — store only `ADMIN_PASSWORD_HASH` in .env)

### Phase 6: Polish and Production Hardening

**Rationale:** Visual polish (dark theme finalization, code block styling, responsive tweaks) can overlap Phase 3 but should be finalized when templates are stable. Production hardening (security headers, session cookie flags, log rotation, SQLite backup cron) rounds out the v1 launch.

**Delivers:** Finalized dark theme CSS with Pygments code highlighting styles, security headers in Nginx (X-Frame-Options, X-Content-Type-Options, Referrer-Policy), session cookie flags (HttpOnly, SameSite=Lax), logrotate configuration for Nginx access logs, daily SQLite backup cron job.

**Addresses:** Responsive layout finalization; code block visual styling (FEATURES.md P1 — dark theme)

**Avoids:** Flask debug mode in production (PITFALLS — `FLASK_DEBUG=0` in .env); session cookie without HttpOnly (PITFALLS security); Gunicorn logs to SD card without rotation (PITFALLS #3)

### Phase 7: v1.x Enhancements (Post-Launch)

**Rationale:** These features add significant value for tech-savvy visitors but are not required for the first public launch. Add them once the blog has real content to share.

**Delivers:** RSS feed (`/feed.xml`), Open Graph meta tags, sitemap (`/sitemap.xml`) + robots.txt, comment moderation view (approve/delete, behind `@login_required`), About page.

**Addresses:** RSS feed (FEATURES.md P2); Open Graph tags (FEATURES.md P2); sitemap (FEATURES.md P2); comment moderation (FEATURES.md P2)

### Phase Ordering Rationale

- **Infrastructure before application code** — the post-receive hook and Unix socket permission pitfalls must be resolved before any feature work begins; discovering them during feature development wastes time
- **Skeleton before features** — WAL mode and .env/gitignore must be correct before the first application commit; SECRET_KEY in git is irreversible without history rewriting
- **Articles before comments** — comments are per-article; the article detail page must exist first
- **Auth + todo together** — the todo route with no auth gate is a security hole; they are a single deliverable
- **Polish last** — templates must be stable before CSS is finalized; hardening after features ensures all endpoints exist before security review

### Research Flags

Phases with well-documented patterns (skip research-phase during planning):
- **Phase 1 (Infrastructure):** Nginx + Gunicorn + systemd + git bare repo are extremely well-documented patterns with multiple authoritative sources verified
- **Phase 2 (Flask Skeleton):** Application factory, blueprint registration, `flask.g` DB pattern are official Flask documentation patterns
- **Phase 3 (Blog Articles):** Flask + Markdown filesystem pattern is well-established; mistune API is straightforward
- **Phase 4 (Comments):** Flask-WTF CSRF, Post-Redirect-Get, SQLite insert — all standard patterns

Phases that may benefit from targeted research during planning:
- **Phase 1 (Infrastructure) — frp configuration:** The specific frp version and TOML config syntax may have changed; verify `frpc.toml` format against the installed frp version on the RPi before writing the systemd unit
- **Phase 6 (Production Hardening):** Specific Nginx security header recommendations evolve; verify current best practices for `Content-Security-Policy` header values given the blog's inline styles vs. external font loading decisions

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All library versions verified against PyPI and piwheels as of Feb/Mar 2026; ARM64 wheel availability confirmed; Flask vs FastAPI decision grounded in official docs and authoritative comparisons |
| Features | HIGH | Core blog features are well-established domain knowledge; Eisenhower Matrix UX is simple/custom; honeypot spam defense is documented across multiple sources; no speculative features |
| Architecture | HIGH | Component choices (Unix socket, application factory, `flask.g`, filesystem-first articles) are directly from official Flask documentation and battle-tested RPi deployment guides |
| Pitfalls | HIGH (critical pitfalls); MEDIUM (SD card wear quantification) | SQLite WAL mode, XSS, SECRET_KEY, socket permissions are from authoritative sources; SD card wear cycle numbers are from community sources — treat as directional, not precise |

**Overall confidence:** HIGH

### Gaps to Address

- **Markdown rendering performance at scale:** Research suggests caching parsed HTML in an in-process dict, with cache invalidation via post-receive hook touching a sentinel file. The exact cache invalidation mechanism is not prescribed in the architecture research — design this during Phase 3 planning if post count is expected to grow quickly.

- **frp vs ngrok selection:** Research documents both options but does not make a final selection. frp (self-hosted relay) gives a stable URL and full control; ngrok free tier assigns random URLs on reconnect (ngrok static domain feature mitigates this but adds account dependency). The owner's existing setup preference should drive this decision before Phase 1.

- **TLS/HTTPS:** The architecture documents Nginx TLS termination as "if certificate added later" but does not detail the Let's Encrypt/Certbot setup. If the frp relay server supports HTTPS proxying, TLS can be terminated at the relay. Clarify before Phase 1 whether TLS is in scope for v1.

- **Comment moderation strategy:** The v1 MVP does not include a comment moderation view (deferred to v1.x). Whether comments are auto-published or held in an approval queue is not specified in the research. Decide during Phase 4 planning — the SQLite schema should include an `approved` flag from the start if moderation is planned.

---

## Sources

### Primary (HIGH confidence)
- https://flask.palletsprojects.com/en/stable/ — Flask 3.x official docs (factory pattern, blueprints, session, g object)
- https://pypi.org/project/Flask/ — Flask 3.1.3 confirmed current (Feb 2026)
- https://pypi.org/project/mistune/ — mistune 3.2.0 confirmed current (Dec 2025)
- https://pypi.org/project/gunicorn/ — Gunicorn 25.1.0 confirmed; `py3-none-any` wheel
- https://sqlite.org/wal.html — SQLite WAL mode official documentation
- https://docs.gunicorn.org/en/stable/deploy.html — Gunicorn Unix socket + Nginx configuration
- https://github.com/messense/nh3 — nh3 HTML sanitizer (bleach replacement)
- https://pypi.org/project/bleach/ — bleach deprecation notice

### Secondary (MEDIUM confidence)
- https://blog.miguelgrinberg.com/post/running-a-flask-application-as-a-service-with-systemd — systemd + Gunicorn unit file pattern
- https://www.piwheels.org/faq.html — piwheels does not support aarch64; all installs via PyPI
- https://forums.raspberrypi.com/viewtopic.php?t=358063 — Bookworm PEP 668 venv requirement
- https://www.datadoghq.com/blog/nginx-502-bad-gateway-errors-gunicorn/ — Nginx/Gunicorn 502 root causes
- https://www.getpagespeed.com/server-setup/nginx/nginx-rate-limiting — Nginx rate limiting guide
- https://kinsta.com/blog/wordpress-spam-comments/ — honeypot spam defense pattern
- https://tenthousandmeters.com/blog/sqlite-concurrent-writes-and-database-is-locked-errors/ — SQLite locked error analysis
- https://linuxpi.ca/the-pitfalls-of-long-term-sd-card-usage-in-raspberry-pi-projects/ — SD card wear on RPi
- https://xtom.com/blog/frp-rathole-ngrok-comparison-best-reverse-tunneling-solution/ — frp vs ngrok comparison

### Tertiary (LOW confidence — verify during implementation)
- https://strapi.io/blog/fastapi-vs-flask-python-framework-comparison — Flask vs FastAPI comparison (cross-checked against official docs)
- https://hub.corgea.com/articles/flask-security-best-practices-2025 — Flask security best practices 2025

---

*Research completed: 2026-03-12*
*Ready for roadmap: yes*
