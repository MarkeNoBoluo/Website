# Pitfalls Research

**Domain:** Python personal blog on Raspberry Pi 4B (Flask + SQLite + Gunicorn + Nginx + systemd + frp)
**Researched:** 2026-03-12
**Confidence:** HIGH

---

## Critical Pitfalls

### Pitfall 1: Markdown Rendering XSS via User Comments

**What goes wrong:**
Comments are plain text, but if Markdown is ever enabled for them (or if the render pipeline is accidentally applied to comment content), user-submitted `<script>` tags or JavaScript URIs in link attributes survive the conversion and execute in other visitors' browsers. Even without Markdown, if the Jinja2 template uses `{{ comment.body | safe }}` instead of `{{ comment.body }}`, the escaping is bypassed entirely.

**Why it happens:**
Developers prototype by passing article Markdown through the renderer and then accidentally reuse the same render call for comment content. The `| safe` filter gets added during debugging to "fix" double-encoding and is never removed.

**How to avoid:**
- Article content (trusted, written by you) can be rendered through mistune with `escape=False` on the renderer.
- Comment body (untrusted, written by visitors) must use one of two strategies: (a) store and display as plain text only — never run through mistune — and rely on Jinja2's default auto-escaping; or (b) if rich comment text is desired, run through mistune AND then sanitize the resulting HTML with `nh3` (not the deprecated `bleach`).
- Never use `| safe` on user-submitted content. Audit all templates for this filter.
- mistune's `HTMLRenderer(escape=True)` only escapes raw HTML blocks, not injected JavaScript in attributes — it is NOT a substitute for sanitization.

```python
# For article content (trusted):
renderer = HTMLRenderer(escape=False)
md = mistune.create_markdown(renderer=renderer, plugins=[table, strikethrough, url])
article_html = md(article.body)  # safe — you wrote this

# For comment display (untrusted):
# Option A (recommended): plain text, Jinja2 auto-escapes
# In template: {{ comment.body }}  — no | safe

# Option B (if Markdown comments are wanted):
import nh3
raw_html = md(comment.body)
safe_html = nh3.clean(raw_html, tags={"p", "strong", "em", "code", "pre", "a"},
                       attributes={"a": ["href"]})
```

**Warning signs:**
- Template has `{{ comment.body | safe }}` anywhere
- A single `md_render()` function is used for both articles and comments
- Comments containing `<b>test</b>` display as bold (means HTML is not being escaped)

**Phase to address:** Core blog features phase (when comment submission is built). Must be correct from day one — retroactive sanitization of stored comments is possible but risky.

---

### Pitfall 2: SQLite "Database Is Locked" Under Gunicorn Multi-Worker

**What goes wrong:**
With `--workers 2`, two Gunicorn workers can attempt simultaneous writes (e.g., two visitors submitting comments at the same instant). SQLite in default journal mode queues these with a 5-second timeout, returning `sqlite3.OperationalError: database is locked` when the timeout expires. The error surfaces as a 500 to the user.

**Why it happens:**
SQLite allows only one writer at a time. The default journal mode has a very short implicit timeout. Flask's `sqlite3.connect()` call without an explicit `timeout` argument defaults to 5 seconds, which can expire under load or if a transaction is held open too long.

**How to avoid:**
Enable WAL mode and set an explicit connection timeout. WAL mode allows readers and a writer to co-exist (readers never block writers and writers never block readers). Set `timeout=15` on the connection.

```python
# In db.py or flask.g connection setup
import sqlite3

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(
            current_app.config['DATABASE'],
            timeout=15,           # wait up to 15s for lock instead of 5s
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL;")
        db.execute("PRAGMA synchronous=NORMAL;")  # safe with WAL, reduces write IOPS
    return db
```

Keep transactions short: never hold a write transaction open while waiting on an external operation (e.g., sending an email). For a personal blog with low concurrent traffic, WAL + 15s timeout is sufficient — no need for a connection pool or PostgreSQL.

**Warning signs:**
- 500 errors during comment submission under modest load
- Log line: `sqlite3.OperationalError: database is locked`
- PRAGMA journal_mode returns `delete` (not `wal`) — means WAL was never set

**Phase to address:** Infrastructure / database setup phase. Set WAL mode in the `init_db()` schema script so it is applied once and persisted in the database file.

---

### Pitfall 3: SD Card Wear from Excessive SQLite Writes

**What goes wrong:**
SQLite's default journal mode (`DELETE`) writes a separate journal file for every transaction, causing two write operations per commit plus fsync calls. On an SD card, this matters: consumer SD cards are rated for 10,000–100,000 write cycles per cell. High-frequency logging (access logs written to SQLite, every-request session updates, etc.) can wear a card in months. Documented cases on RPi forums show 100M+ writes in 7 days from poorly tuned database-heavy apps.

**Why it happens:**
Developers treat the RPi like a server with an SSD. They add access logging to SQLite, store ephemeral data in the database, or forget that Nginx and Gunicorn also write access logs to the SD card continuously.

**How to avoid:**
1. `PRAGMA synchronous=NORMAL` with WAL mode — safe and halves write IOPS vs. `FULL`.
2. Do NOT use `PRAGMA synchronous=OFF` — risks corruption on power loss.
3. Route Gunicorn access logs to `/dev/null` in production (or to a `tmpfs` mount) rather than an SD card file. Nginx access logs are higher value — keep those but rotate with logrotate.
4. Do NOT store ephemeral data (rate-limit counters, session data) in SQLite — use Python's in-memory structures or a `tmpfs`-backed file.
5. Do NOT run `VACUUM` on a schedule — it rewrites the entire database file, causing massive write amplification.
6. Consider moving the SQLite file to a USB drive or SSD plugged into the RPi's USB 3.0 port if the blog grows in write volume.

**Warning signs:**
- SD card health tools (e.g., `f3probe`) showing errors
- System suddenly very slow — often the first sign of SD card degradation
- `df -h` shows `/` usage growing unexpectedly (WAL file not checkpointing)

**Phase to address:** Infrastructure phase. Set `synchronous=NORMAL` in init script. Configure Gunicorn log paths in the systemd unit file at setup time.

---

### Pitfall 4: Flask SECRET_KEY Committed to Git

**What goes wrong:**
The Flask `SECRET_KEY` signs session cookies. An attacker with the key can forge the `session['authenticated'] = True` cookie, bypassing the todo login entirely. A hardcoded key in `app.py` or `config.py` will end up in the git repo — and if that repo is ever public or the RPi is compromised, all sessions are forfeit.

**Why it happens:**
Developers set `app.secret_key = "mysecret"` in a tutorial, ship it, and forget. The `.env` file is added to the project but not to `.gitignore` before the first commit.

**How to avoid:**
1. Generate the key offline: `python -c "import secrets; print(secrets.token_hex(32))"`.
2. Store in `.env`: `SECRET_KEY=<generated value>`.
3. Add `.env` to `.gitignore` **before** the first `git add`.
4. Load with `python-dotenv` in the app factory — never in `app.py` directly.
5. Also store `ADMIN_PASSWORD_HASH` in `.env`, not in source code.

```
# .gitignore
.env
*.pyc
__pycache__/
.venv/
*.db
*.db-wal
*.db-shm
```

**Warning signs:**
- `grep -r "secret_key" app/` returns a string literal (not a config lookup)
- `.env` file appears in `git status` as untracked without `.gitignore` entry
- `git log --all --full-history -- .env` shows .env was ever committed

**Phase to address:** Project initialization / first commit. This must be correct before any code is pushed.

---

### Pitfall 5: Post-Receive Hook Breaks on Venv or Permissions

**What goes wrong:**
The post-receive hook runs as the git repository's owner (e.g., `pi`). If the hook uses `source .venv/bin/activate` (a bash shell builtin that does not work in `/bin/sh`), or references relative paths that differ from the bare repo's working directory, or tries to `systemctl restart blog` without sudo, the deployment silently fails or half-completes: the code is updated but the running process serves stale code.

**Why it happens:**
The hook is written and tested interactively as the `pi` user, then forgotten. The hook's shebang defaults to `/bin/sh` on Debian/Bookworm (which is `dash`, not `bash`), breaking `source`. The hook has no error handling — if `pip install` fails, it still tries to restart the service.

**How to avoid:**

```bash
#!/bin/bash  # Must be bash, not /bin/sh, for 'source' to work
set -e       # Exit on any error — prevents silent partial deploys

REPO_DIR="/home/pi/blog-bare"
WORK_DIR="/home/pi/blog"
VENV_DIR="$WORK_DIR/.venv"

git --work-tree="$WORK_DIR" --git-dir="$REPO_DIR" checkout -f

cd "$WORK_DIR"

# Use the venv's pip directly — no need to 'source activate'
"$VENV_DIR/bin/pip" install -q -r requirements.txt

# systemctl requires sudo — configure sudoers for this specific command
sudo /bin/systemctl restart blog
```

Configure passwordless sudo for exactly this one command:
```
# /etc/sudoers.d/blog-deploy (mode 0440)
pi ALL=(ALL) NOPASSWD: /bin/systemctl restart blog
```

**Warning signs:**
- `git push` succeeds but the live site shows old code
- Hook file starts with `#!/bin/sh` and contains `source`
- `systemctl status blog` shows the service was last restarted days ago after a recent push
- Hook has no `set -e` and subsequent steps run despite earlier failures

**Phase to address:** Deployment infrastructure phase. Test the hook end-to-end with a trivial change before building any application features.

---

### Pitfall 6: Nginx Unix Socket 502 Bad Gateway

**What goes wrong:**
Nginx returns `502 Bad Gateway` because it cannot read the Gunicorn Unix socket at `/tmp/blog.sock`. This happens even though the service is running. The root cause is almost always a file permission mismatch: the `pi` user owns the socket, but Nginx runs as `www-data` and cannot access it.

**Why it happens:**
Developers configure the socket path correctly but do not align the user accounts. On Bookworm, Nginx defaults to `www-data`. Gunicorn (running as `pi` via systemd) creates the socket with `0600` permissions. `www-data` cannot read it.

**How to avoid:**
Option A (simplest): Run Gunicorn with `--umask 007` so the socket is group-readable, and add `www-data` to the `pi` group:
```bash
sudo usermod -aG pi www-data
```

Option B (cleanest): Run both Nginx and Gunicorn as the same non-root user by setting `user pi pi;` in Nginx's `nginx.conf` (uncommon but valid for a single-purpose RPi).

Option C: Place the socket in a directory owned by a shared group:
```bash
sudo mkdir /run/blog
sudo chown pi:www-data /run/blog
sudo chmod 770 /run/blog
# In gunicorn: --bind unix:/run/blog/blog.sock
```

Also ensure the `/tmp/blog.sock` parent directory is accessible — `/tmp` is world-accessible but verify with `ls -la /tmp`.

**Warning signs:**
- `sudo nginx -t` passes but browser returns 502
- `sudo journalctl -u blog` shows Gunicorn is running and bound
- `ls -la /tmp/blog.sock` shows `-rw-------` (no group/other read)
- Nginx error log shows `(13: Permission denied) while connecting to upstream`

**Phase to address:** Infrastructure phase. Verify the full Nginx → Gunicorn → Flask chain returns 200 before any application features are built.

---

### Pitfall 7: frp/ngrok Tunnel Drops Without Detection

**What goes wrong:**
The tunnel process (frp client or ngrok agent) crashes or loses connection to the relay server. The RPi is still running, the blog is still running, but the public URL returns nothing. Since there is no alerting, the outage is only discovered by manually checking the URL — potentially hours later.

**Why it happens:**
frp and ngrok are run in a terminal session or a `nohup` background command, not under systemd. When the SSH session drops or the system reboots, the tunnel process dies. frp's `tcp` keepalive defaults are also too conservative for some NAT configurations.

**How to avoid:**
Run the tunnel client as a systemd service so it auto-restarts and starts on boot:

```ini
# /etc/systemd/system/frpc.service
[Unit]
Description=frp Client
After=network.target

[Service]
User=pi
ExecStart=/usr/local/bin/frpc -c /home/pi/frpc.toml
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

For frp, set keepalive in `frpc.toml`:
```toml
[common]
heartbeat_interval = 10
heartbeat_timeout = 30
```

For ngrok: the free tier assigns a random URL on each reconnect — use ngrok's static domain feature (free tier allows one) or use frp with a self-controlled relay server to get a stable URL.

**Warning signs:**
- Public URL times out but `curl localhost` on RPi succeeds
- `systemctl status frpc` does not exist (tunnel not managed by systemd)
- frp/ngrok started with `nohup` or in a terminal multiplexer session

**Phase to address:** Deployment / external access phase. Configure tunnel-as-service before declaring the site "live."

---

### Pitfall 8: Comment Spam Without Rate Limiting

**What goes wrong:**
The anonymous comment endpoint (`POST /article/<id>/comment`) receives hundreds of automated spam submissions. Each submission writes to SQLite. The blog's article pages fill with spam. The RPi's modest CPU is saturated handling form validation and database writes.

**Why it happens:**
Public POST endpoints without rate limiting are discovered and exploited within hours of a site going live, even low-traffic personal blogs. CSRF protection (Flask-WTF) stops browser-based CSRF attacks but does NOT stop bots that parse the CSRF token from the HTML form before submitting.

**How to avoid:**
Apply rate limiting at the Nginx layer — this is the correct place because it stops requests before they reach Gunicorn:

```nginx
# In nginx.conf http block:
limit_req_zone $binary_remote_addr zone=comments:10m rate=2r/m;

# In the server block location:
location /article {
    limit_req zone=comments burst=3 nodelay;
    proxy_pass http://unix:/tmp/blog.sock;
}
```

This allows 2 comment submissions per minute per IP with a burst of 3. Adjust to taste. The `10m` shared memory zone holds ~160,000 IP addresses and is negligible for the RPi.

Also add a honeypot field (a hidden form field that bots fill in but humans leave empty) as a secondary layer.

**Warning signs:**
- Nginx access log shows repeated `POST /article/*/comment` from same IP
- Comments table has rows with gibberish content or URL-spam bodies
- SQLite file growing unexpectedly fast

**Phase to address:** Comment feature phase. Add rate limiting when the comment endpoint is built, not as an afterthought.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| `app.run(debug=True)` in production | Easy debugging | Exposes interactive debugger PIN — full code execution for anyone who triggers an error | Never in production; use `FLASK_ENV=production` and `app.config['DEBUG'] = False` |
| Gunicorn logs to SD card file without rotation | Simple log setup | SD card fills or wears out; logs grow unboundedly | Never without `logrotate` configured |
| SQLite file in `/home/pi/blog/blog.db` | Obvious location | Gets committed to git if `.gitignore` is incomplete | Acceptable location if `*.db` is in `.gitignore` |
| `PRAGMA synchronous=OFF` | Fastest writes | Data loss on power failure (SD card loses power mid-write, database corrupted) | Never on RPi — power loss is common |
| No `set -e` in post-receive hook | Hook never aborts | Partial deploy: new code checked out but old venv, service restart fails silently | Never — always `set -e` in deploy scripts |
| Storing admin password in plaintext in `.env` | Simple to set up | If `.env` is leaked, password is immediately usable | Never — always store the hash, generate with `generate_password_hash()` |
| `mistune.html()` shorthand instead of configured renderer | One line | Uses defaults that may not sanitize; no plugin control; behavior changes between mistune versions | Never for production; always configure the renderer explicitly |

---

## Integration Gotchas

Common mistakes when connecting components in this specific stack.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Nginx → Gunicorn (Unix socket) | `proxy_pass http://localhost:8000` (TCP) | `proxy_pass http://unix:/tmp/blog.sock` — Unix socket is faster and avoids port conflicts |
| Nginx → Gunicorn | Missing `proxy_set_header Host $host` | Without this, Flask's `request.host` and `url_for()` generate wrong URLs |
| Nginx → Gunicorn | Missing `proxy_set_header X-Forwarded-For $remote_addr` | Flask sees all requests as coming from `127.0.0.1`; rate-limiting by IP in Flask is ineffective; use `ProxyFix` middleware |
| frp → Nginx | frp exposes port 80 directly, bypassing Nginx | Always route frp's public port to Nginx, not directly to Gunicorn — Nginx handles static files, security headers, and rate limiting |
| systemd → Gunicorn | `ExecStart` uses `gunicorn` (not venv path) | Must use `/home/pi/blog/.venv/bin/gunicorn` — system PATH does not include the venv |
| Flask-WTF CSRF → Gunicorn multi-worker | CSRF token validation fails intermittently | Ensure `SECRET_KEY` is identical across workers (loaded from `.env`, not generated at runtime per-process) |
| python-dotenv → systemd | `.env` not loaded because systemd clears environment | Use `EnvironmentFile=/home/pi/blog/.env` in the `[Service]` section, not python-dotenv's `load_dotenv()` as primary mechanism |

---

## Performance Traps

Patterns that work at small scale but degrade on a 1GB-RAM ARM Cortex-A72.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Rendering Markdown on every request | Article pages slow under concurrent load | Pre-render `.md` files to HTML at deploy time (in post-receive hook), store in a `rendered/` cache directory or in SQLite `articles.html_cache` column | At ~50 concurrent requests on RPi |
| Gunicorn `--workers 9` (formula: 2×cores+1) | OOM kill; all workers crash; service restarts; site down | Use exactly 2 workers for RPi 4B (1GB model) or 3 for 4GB model; the formula is for servers, not ARM SBCs | Immediately on 1GB RPi — each worker holds ~50-80MB |
| Pygments syntax highlighting on every request | Slow article rendering | Cache rendered HTML; Pygments is the slowest part of the pipeline | At ~20 concurrent requests |
| Loading entire SQLite `articles` table to display list | Memory spike when many articles exist | `SELECT id, title, date, slug FROM articles ORDER BY date DESC LIMIT 20` — never `SELECT *` or fetch all rows | At ~500 articles |
| `pip install -r requirements.txt` on every push in post-receive hook | Deploys take 2-3 minutes, service is restarted during install | Check if requirements.txt changed before running pip: `git diff HEAD@{1} HEAD -- requirements.txt` | Every deploy — annoying from day 1 |

---

## Security Mistakes

Domain-specific security issues for this stack and deployment target.

| Mistake | Risk | Prevention |
|---------|------|------------|
| frp/ngrok exposes Gunicorn directly (bypasses Nginx) | No security headers, no rate limiting, no static file optimization | Always proxy through Nginx; frp's `local_port` should point to Nginx (80), not Gunicorn |
| Session cookie without `Secure` and `HttpOnly` flags | Session token readable by JavaScript or transmitted over HTTP | Set `SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SAMESITE='Lax'` in Flask config |
| No `X-Content-Type-Options`, `X-Frame-Options` headers | Clickjacking, MIME sniffing attacks | Add security headers in Nginx: `add_header X-Frame-Options DENY; add_header X-Content-Type-Options nosniff; add_header Referrer-Policy strict-origin-when-cross-origin;` |
| Weak or guessable admin password | Todo list accessible to anyone who tries common passwords | Use a long random passphrase; store only the hash in `.env`; add a login attempt delay (`time.sleep(1)` after failed attempt) |
| Comment body stored without length limit | Database row bloat; potential DoS via very long comments | Validate `len(body) <= 2000` server-side (not just client-side) before inserting |
| frp server running on a cheap VPS with default credentials | Third party can hijack the tunnel | Set a strong `token` in frpc.toml / frps.toml; use TLS between frpc and frps if the VPS is untrusted |
| Markdown article files committed with sensitive content | Blog posts with TODOs like `<!-- password: xyz -->` become public | Review all `.md` files before first push; add pre-commit hook to scan for secrets |

---

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Comment form:** CSRF token present in HTML — verify with `curl -s http://yoursite/article/1 | grep csrf_token` returns a value
- [ ] **Comment display:** HTML is escaped — submit `<script>alert(1)</script>` as a comment body and verify it appears as literal text, not an alert
- [ ] **Login form:** Password is hashed — verify `ADMIN_PASSWORD_HASH` in `.env` starts with `pbkdf2:sha256:` (Werkzeug hash prefix), not a plaintext string
- [ ] **Session security:** `SESSION_COOKIE_HTTPONLY` is True — verify with browser DevTools → Application → Cookies that the session cookie has the HttpOnly flag
- [ ] **SQLite WAL mode:** Verify after first `init_db` run: `sqlite3 blog.db "PRAGMA journal_mode;"` returns `wal`
- [ ] **Deployment hook:** Push a trivial change and verify `systemctl status blog` shows a restart timestamp matching the push time
- [ ] **Nginx static files:** Static assets served by Nginx (not Gunicorn) — verify with `curl -I http://yoursite/static/style.css` shows `Server: nginx`, not via Gunicorn access log
- [ ] **Rate limiting active:** Nginx `limit_req_zone` defined and applied — verify by checking `nginx -T | grep limit_req`
- [ ] **Tunnel as service:** `systemctl status frpc` (or ngrok service) shows `active (running)` and `Restart=always` — not running in a tmux/screen session
- [ ] **Secret key not in git:** `git log --all -p | grep SECRET_KEY` returns nothing

---

## Recovery Strategies

When pitfalls occur despite prevention.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| XSS injected via comment (if `\| safe` was used) | MEDIUM | 1. Remove `\| safe` from template. 2. Sanitize existing comment rows: `UPDATE comments SET body = sanitized_body`. 3. Deploy fix. 4. Review other templates for `\| safe`. |
| SECRET_KEY committed to git | HIGH | 1. Rotate immediately: generate new key, update `.env`. 2. All existing sessions are invalidated (users logged out — only affects you). 3. `git filter-repo` or BFG to purge key from history. 4. If repo was public, assume key was captured and rotate immediately. |
| SQLite "database is locked" errors in production | LOW | 1. Enable WAL mode: `sqlite3 blog.db "PRAGMA journal_mode=WAL;"`. 2. Increase connection timeout in `get_db()`. 3. Deploy. No data loss. |
| SD card corruption (database file damaged) | HIGH | 1. Restore from most recent SQLite backup (`sqlite3 backup.db ".restore blog.db"`). 2. Assess data loss window (time since last backup). 3. Replace SD card. 4. Improve backup frequency and WAL settings. |
| Post-receive hook partial deploy (stale code running) | LOW | 1. SSH to RPi. 2. `cd /home/pi/blog && git pull` (or re-run checkout manually). 3. `pip install -r requirements.txt`. 4. `sudo systemctl restart blog`. 5. Fix hook with `set -e`. |
| frp tunnel dead, site unreachable | LOW | 1. SSH to RPi (via local network). 2. `sudo systemctl restart frpc`. 3. If systemd service was not set up, create it now. |
| Nginx 502 after deploy | LOW | 1. `sudo journalctl -u blog -n 50` to check if Gunicorn is running. 2. `ls -la /tmp/blog.sock` to check socket existence and permissions. 3. `sudo nginx -t && sudo systemctl reload nginx` to rule out config error. |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| SECRET_KEY committed to git | Phase 1: Project init (before first commit) | `git log --all -p \| grep SECRET_KEY` returns nothing |
| SQLite WAL mode + synchronous setting | Phase 2: Database schema setup | `PRAGMA journal_mode;` returns `wal`; `PRAGMA synchronous;` returns `1` |
| SD card wear (log paths, no VACUUM) | Phase 2: Infrastructure setup | Gunicorn logs point to `/dev/null` or tmpfs; no scheduled VACUUM |
| Nginx Unix socket permissions (502) | Phase 3: Infrastructure wiring | `curl --unix-socket /tmp/blog.sock http://localhost/` returns 200 |
| Nginx security headers | Phase 3: Infrastructure wiring | `curl -I http://yoursite/` shows `X-Frame-Options` and `X-Content-Type-Options` |
| frp/ngrok as systemd service | Phase 3: External access setup | `systemctl status frpc` shows `active (running)` and `Restart=always` |
| Post-receive hook permissions + bash shebang | Phase 3: Deployment pipeline | Push trivial change; verify service restarts and new code is live |
| Markdown XSS in comments | Phase 4: Comment feature | Submit `<script>` comment; verify it displays as escaped text |
| Comment spam / rate limiting | Phase 4: Comment feature | `nginx -T \| grep limit_req` shows zone and rate configured |
| Flask debug mode off in production | Phase 4: First production deploy | `FLASK_DEBUG=0` in `.env`; 500 errors show generic page, not traceback |
| Gunicorn worker count (2, not 9) | Phase 2: Process manager setup | `systemctl status blog` shows 2 worker processes; `free -m` shows acceptable RAM usage |
| SQLite backup strategy | Phase 5: Operations hardening | `crontab -l` shows daily `sqlite3 blog.db ".backup /home/pi/backups/blog-$(date +%Y%m%d).db"` |
| ProxyFix for correct remote IP | Phase 3: Nginx config | Flask's `request.remote_addr` returns visitor IP, not `127.0.0.1` |

---

## Sources

- https://sqlite.org/wal.html — SQLite WAL mode official documentation (HIGH confidence)
- https://tenthousandmeters.com/blog/sqlite-concurrent-writes-and-database-is-locked-errors/ — SQLite database locked error analysis (MEDIUM confidence)
- https://linuxpi.ca/the-pitfalls-of-long-term-sd-card-usage-in-raspberry-pi-projects/ — SD card wear on Raspberry Pi (MEDIUM confidence)
- https://forums.raspberrypi.com/viewtopic.php?t=255573 — SQLite on RPi SD card community discussion (MEDIUM confidence)
- https://litestream.io/alternatives/cron/ — SQLite cron backup vs. Litestream comparison (HIGH confidence)
- https://github.com/messense/nh3 — nh3 HTML sanitizer (bleach replacement), Python Rust binding (HIGH confidence)
- https://pypi.org/project/bleach/ — bleach deprecation notice (HIGH confidence)
- https://github.com/lepture/mistune/issues/87 — mistune XSS link bypass issue (MEDIUM confidence, fixed in 3.x)
- https://www.datadoghq.com/blog/nginx-502-bad-gateway-errors-gunicorn/ — Nginx/Gunicorn 502 root causes (HIGH confidence)
- https://www.acunetix.com/vulnerabilities/web/flask-weak-secret-key/ — Flask SECRET_KEY attack surface (HIGH confidence)
- https://blog.miguelgrinberg.com/post/running-a-flask-application-as-a-service-with-systemd — systemd + Gunicorn unit file (HIGH confidence)
- https://turndevopseasier.com/real-use-case-nginx-rate-limit-fail2ban-to-prevent-massive-spam-post-requests/ — Nginx rate limiting for POST spam (MEDIUM confidence)
- https://www.getpagespeed.com/server-setup/nginx/nginx-rate-limiting — Nginx rate limiting complete guide (HIGH confidence)
- https://hub.corgea.com/articles/flask-security-best-practices-2025 — Flask security best practices 2025 (MEDIUM confidence)
- https://xtom.com/blog/frp-rathole-ngrok-comparison-best-reverse-tunneling-solution/ — frp vs. ngrok comparison (MEDIUM confidence)
- https://dev.to/blazselih/slightly-more-advanced-deployment-with-git-4ikm — git post-receive hook deployment patterns (MEDIUM confidence)

---

*Pitfalls research for: Python personal blog on Raspberry Pi 4B (Flask + SQLite + Gunicorn + Nginx + systemd + frp)*
*Researched: 2026-03-12*
