# Terminal Theme — Public Pages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the generic dark-gray blog theme with a lightweight terminal aesthetic (no CRT effects) across all public-facing pages: blog list, article detail, login, and error pages.

**Architecture:** Rewrite `static/css/style.css` with terminal CSS variables and component styles; update `templates/base.html` to add Google Fonts and a terminal-style nav/footer; update each public-page template to use the new class naming convention. The standalone `templates/errors/404.html` requires a full rewrite (it has no Jinja `{% extends %}` so nav/footer must be inlined). The only Python change is a new `@app.errorhandler(500)` so the 500 template receives `error` context.

**Tech Stack:** Flask/Jinja2, CSS custom properties, Google Fonts (Share Tech Mono, VT323), existing Pygments monokai (unchanged)

---

## File Map

| File | Change |
|---|---|
| `app/__init__.py` | Add `@app.errorhandler(500)` handler |
| `static/css/style.css` | **Full rewrite** — terminal variables, fonts, nav, footer, flash, forms, blog list, article detail, error pages, auth login |
| `templates/base.html` | Add Google Fonts `<link>`; rewrite `<nav>` (terminal prompt style, no Todo link); rewrite `<footer>` |
| `app/blog/templates/blog/index.html` | Replace card grid with flat `.t-article-row` layout |
| `app/blog/templates/blog/article.html` | Add `.t-prompt` breadcrumb before `h1`; update back-link text |
| `app/auth/templates/auth/login.html` | Remove `admin.css` extra_css block; remove duplicate flash block; swap admin class names for terminal class names |
| `app/blog/templates/blog/404.html` | Update markup to terminal error style |
| `templates/errors/500.html` | Update markup to terminal debug panel style |
| `templates/errors/404.html` | **Full standalone rewrite** — add `<head>` fonts, inline nav/footer, terminal error layout |

**Not touched:** `static/css/home.css`, `templates/home.html`, `static/css/admin.css`, `static/css/todo.css`, `static/css/pygments.css`, all admin/todo templates, all Python route/model code (except the 500 handler).

---

## Task 1: Add 500 Error Handler

**Files:**
- Modify: `app/__init__.py`
- Test: `test_app.py`

This is the only Python change. The 500 template already renders `{{ error }}` but there's no handler that passes the `error` variable — so in DEBUG mode the debug panel would show nothing.

- [ ] **Step 1: Write failing test in `test_app.py`**

Add at the bottom of `test_app.py`:

```python
def test_500_handler_passes_error_to_template():
    """500 handler renders errors/500.html with error context."""
    from app import create_app

    app = create_app(config_class=TestConfig)
    app.config["DEBUG"] = True  # Enable debug panel

    @app.route("/trigger-500")
    def trigger_500():
        raise RuntimeError("test error message")

    with app.test_client() as client:
        response = client.get("/trigger-500")
        assert response.status_code == 500
        body = response.data.decode("utf-8")
        assert "test error message" in body
```

- [ ] **Step 2: Run test to confirm it fails**

```bash
python -m pytest test_app.py::test_500_handler_passes_error_to_template -v
```

Expected: FAIL (500 currently returns Werkzeug default debug page, not our template)

- [ ] **Step 3: Add 500 handler to `app/__init__.py`**

Inside `create_app()`, after the `@app.errorhandler(404)` block (line ~127), add:

```python
@app.errorhandler(500)
def internal_server_error(error):
    """500 Internal Server Error handler."""
    return render_template("errors/500.html", error=str(error)), 500
```

- [ ] **Step 4: Run test to confirm it passes**

```bash
python -m pytest test_app.py::test_500_handler_passes_error_to_template -v
```

Expected: PASS

- [ ] **Step 5: Run full test suite**

```bash
python -m pytest test_app.py -v
```

Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add app/__init__.py test_app.py
git commit -m "feat: add 500 error handler that passes error context to template"
```

---

## Task 2: Rewrite `static/css/style.css`

**Files:**
- Modify: `static/css/style.css`

Full replacement of the generic dark-gray theme with terminal CSS. This is the foundation — all subsequent template tasks depend on these class names being defined.

- [ ] **Step 1: Replace the entire contents of `static/css/style.css`**

```css
/* Terminal theme — public blog pages
 * Lightweight terminal aesthetic (no CRT effects — those are home.css only)
 * Primary: #00ff41 green / #ffb300 amber on #080808 near-black
 */

/* ── Variables ── */
:root {
  --bg:            #080808;
  --bg2:           #0d0d0d;
  --green:         #00ff41;
  --green-dim:     #00c832;
  --green-faint:   #003d10;
  --green-bg:      rgba(0,255,65,0.03);
  --amber:         #ffb300;
  --red:           #ff2244;
  --nav-link:      #00a830;
  --comment:       #2a6e3e;
  --divider:       #1a4a25;
  --text-body:     #cccccc;
  --text-dim:      #1a5c28;
}

/* ── Reset ── */
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

html { font-size: 16px; scroll-behavior: smooth; }

/* ── Base ── */
body {
  font-family: 'Share Tech Mono', 'Courier New', monospace;
  background: var(--bg);
  color: var(--text-body);
  line-height: 1.6;
  min-height: 100vh;
}

a { color: var(--nav-link); text-decoration: none; }
a:hover { color: var(--green); }

/* ── Layout ── */
main {
  max-width: 860px;
  margin: 0 auto;
  padding: 2rem 1rem;
  min-height: calc(100vh - 100px);
}

/* ── Navigation ── */
nav {
  background: var(--green-bg);
  border-bottom: 1px solid var(--green-faint);
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.nav-logo {
  font-family: 'VT323', 'Courier New', monospace;
  font-size: 1.4rem;
  color: var(--green);
  text-shadow: 0 0 8px var(--green);
  text-decoration: none;
}

.nav-links {
  display: flex;
  list-style: none;
  gap: 0.25rem;
  align-items: center;
  flex-wrap: wrap;
}

.nav-links li a,
.nav-links li span {
  color: var(--nav-link);
  text-decoration: none;
  padding: 0.3rem 0.5rem;
  font-size: 0.9rem;
  position: relative;
  transition: color 0.15s;
}

.nav-links li a:hover { color: var(--green); }

.nav-links li a::before {
  content: '> ';
  color: var(--amber);
  opacity: 0;
  transition: opacity 0.15s;
}

.nav-links li a:hover::before { opacity: 1; }

.nav-user {
  color: var(--amber);
  padding: 0.3rem 0.5rem;
  font-size: 0.9rem;
}

/* ── Footer ── */
footer {
  border-top: 1px solid #0a2010;
  padding: 1rem 1.5rem;
  text-align: center;
  font-size: 0.72rem;
  color: var(--divider);
  margin-top: 2rem;
}

/* ── Flash messages ── */
.flash-messages {
  max-width: 860px;
  margin: 1rem auto 0;
  padding: 0 1rem;
}

.flash {
  border-left: 2px solid var(--green-dim);
  background: rgba(0, 200, 50, 0.05);
  color: var(--green-dim);
  padding: 0.6rem 1rem;
  margin-bottom: 0.5rem;
  font-size: 0.82rem;
}

.flash.success {
  border-left-color: var(--green);
  background: rgba(0, 255, 65, 0.05);
  color: var(--green);
}

.flash.error {
  border-left-color: var(--red);
  background: rgba(255, 34, 68, 0.05);
  color: var(--red);
}

.flash.warning {
  border-left-color: var(--amber);
  background: rgba(255, 179, 0, 0.05);
  color: var(--amber);
}

/* ── Section header ── */
.t-section-header {
  font-family: 'VT323', 'Courier New', monospace;
  font-size: 1.3rem;
  color: var(--amber);
  margin-bottom: 1.5rem;
  padding-bottom: 0.4rem;
  position: relative;
}

.t-section-header::after {
  content: '';
  display: block;
  height: 1px;
  margin-top: 0.4rem;
  background: linear-gradient(to right, var(--green-faint), transparent);
}

/* ── Blog article list ── */
.t-article-list {
  display: flex;
  flex-direction: column;
}

.t-article-row {
  display: grid;
  grid-template-columns: 140px 1fr auto;
  align-items: center;
  gap: 1rem;
  padding: 0.6rem 0.5rem 0.6rem 0;
  border-bottom: 1px solid #0f2e17;
  text-decoration: none;
  transition: background 0.15s, padding-left 0.15s;
}

.t-article-row:hover {
  background: rgba(0,255,65,0.04);
  padding-left: 0.4rem;
}

.t-article-date {
  font-size: 0.82rem;
  color: var(--text-dim);
  white-space: nowrap;
}

.t-article-date span { color: var(--amber); }

.t-article-title {
  color: var(--green-dim);
  font-size: 0.95rem;
  transition: color 0.15s, text-shadow 0.15s;
}

.t-article-row:hover .t-article-title {
  color: var(--green);
  text-shadow: 0 0 6px rgba(0,255,65,0.4);
}

.t-article-tag {
  font-size: 0.72rem;
  color: var(--comment);
  border: 1px solid var(--divider);
  padding: 0.1rem 0.4rem;
  white-space: nowrap;
}

/* Empty state */
.t-empty {
  color: var(--comment);
  font-size: 0.9rem;
  padding: 2rem 0;
}

/* ── Article detail ── */
.article-detail {
  max-width: 780px;
  margin: 0 auto;
}

.t-prompt {
  font-size: 0.82rem;
  color: var(--text-dim);
  margin-bottom: 0.75rem;
}

h1.article-title {
  font-family: 'VT323', 'Courier New', monospace;
  font-size: clamp(1.8rem, 5vw, 2.8rem);
  color: var(--green);
  text-shadow: 0 0 12px var(--green);
  line-height: 1.1;
  margin-bottom: 0.75rem;
}

.article-header {
  margin-bottom: 2rem;
  border-bottom: 1px solid var(--green-faint);
  padding-bottom: 1rem;
}

.article-meta {
  font-size: 0.85rem;
  color: var(--text-dim);
}

.article-meta .meta-bracket { color: var(--amber); }

/* Article body */
.article-content {
  color: var(--text-body);
  line-height: 1.8;
  font-size: 1rem;
}

.article-content h2 {
  font-family: 'VT323', 'Courier New', monospace;
  font-size: 1.6rem;
  color: var(--green-dim);
  margin: 2rem 0 0.75rem;
}

.article-content h2::before { content: '## '; color: var(--amber); }

.article-content h3 {
  font-family: 'VT323', 'Courier New', monospace;
  font-size: 1.3rem;
  color: var(--nav-link);
  margin: 1.5rem 0 0.5rem;
}

.article-content h3::before { content: '### '; color: var(--amber); }

.article-content p { margin: 0.9rem 0; }

.article-content a { color: var(--green-dim); }
.article-content a:hover { color: var(--green); }

.article-content code {
  background: var(--bg2);
  color: var(--amber);
  padding: 0.1rem 0.35rem;
  font-family: 'Share Tech Mono', 'Courier New', monospace;
  font-size: 0.9em;
}

.article-content pre {
  background: var(--bg2);
  border-left: 2px solid var(--green-faint);
  padding: 1rem;
  overflow-x: auto;
  margin: 1.5rem 0;
}

.article-content pre code {
  background: none;
  color: var(--green-dim);
  padding: 0;
  font-size: 0.88rem;
}

.article-content ul, .article-content ol {
  margin: 0.75rem 0 0.75rem 1.5rem;
}

.article-content li { margin: 0.3rem 0; }

.article-content blockquote {
  border-left: 2px solid var(--amber);
  margin: 1rem 0;
  padding: 0.5rem 1rem;
  color: var(--comment);
  font-style: italic;
}

.article-footer {
  margin-top: 3rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--green-faint);
}

.back-to-blog {
  color: var(--nav-link);
  font-size: 0.9rem;
}
.back-to-blog:hover { color: var(--green); }

/* ── Auth / Login ── */
.t-auth-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 3rem 1rem;
}

.t-auth-box {
  border: 1px solid var(--green-faint);
  background: rgba(0,255,65,0.02);
  padding: 2rem;
  width: 100%;
  max-width: 420px;
}

.t-auth-box .t-section-header { margin-bottom: 1.5rem; }

.t-auth-box .form-group { margin-bottom: 1.25rem; }

.t-auth-box label {
  display: block;
  color: var(--nav-link);
  font-size: 0.8rem;
  margin-bottom: 0.35rem;
}

.t-auth-box input[type="text"],
.t-auth-box input[type="password"] {
  width: 100%;
  background: var(--bg2);
  border: 1px solid var(--green-faint);
  color: var(--green-dim);
  font-family: 'Share Tech Mono', 'Courier New', monospace;
  font-size: 0.95rem;
  padding: 0.6rem 0.75rem;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.t-auth-box input:focus {
  border-color: var(--green-dim);
  box-shadow: 0 0 6px rgba(0,255,65,0.25);
}

.t-auth-box input:invalid { border-color: var(--red); }

.t-btn {
  display: inline-block;
  border: 1px solid var(--green);
  color: var(--green);
  background: transparent;
  font-family: 'Share Tech Mono', 'Courier New', monospace;
  font-size: 0.95rem;
  padding: 0.6rem 1.5rem;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
  width: 100%;
  text-align: center;
}

.t-btn:hover {
  background: var(--green);
  color: var(--bg);
}

.t-auth-hint {
  margin-top: 1.25rem;
  font-size: 0.8rem;
  color: var(--text-dim);
}

/* ── Error pages ── */
.t-error-page {
  text-align: center;
  padding: 4rem 1rem;
}

.t-error-code {
  font-family: 'VT323', 'Courier New', monospace;
  font-size: clamp(5rem, 20vw, 8rem);
  color: var(--green);
  text-shadow: 0 0 20px rgba(0,255,65,0.5);
  line-height: 1;
  display: block;
}

.t-error-msg {
  color: var(--text-body);
  font-size: 1rem;
  margin: 0.5rem 0 2rem;
}

.t-error-actions { display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }

.t-btn-outline {
  display: inline-block;
  border: 1px solid var(--green-faint);
  color: var(--nav-link);
  background: transparent;
  font-family: 'Share Tech Mono', 'Courier New', monospace;
  font-size: 0.9rem;
  padding: 0.5rem 1.25rem;
  text-decoration: none;
  transition: border-color 0.15s, color 0.15s;
}

.t-btn-outline:hover {
  border-color: var(--green);
  color: var(--green);
}

/* 500 debug panel */
.t-debug-panel {
  margin-top: 2rem;
  border: 1px solid var(--red);
  background: rgba(255,34,68,0.04);
  padding: 1rem;
  text-align: left;
}

.t-debug-header {
  font-family: 'VT323', 'Courier New', monospace;
  color: var(--red);
  font-size: 1.1rem;
  margin-bottom: 0.75rem;
}

.t-debug-panel pre {
  color: var(--red);
  font-family: 'Share Tech Mono', 'Courier New', monospace;
  font-size: 0.78rem;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

/* ── Utility ── */
.text-center { text-align: center; }
```

- [ ] **Step 2: Start Flask dev server and load `/blog/`**

```bash
flask --app app run --debug
```

Navigate to `http://localhost:5000/blog/` — page should load without JS errors.

- [ ] **Step 3: Run tests to confirm nothing broken**

```bash
python -m pytest test_app.py -v
```

Expected: All tests PASS (style.css change has no backend impact)

- [ ] **Step 4: Commit**

```bash
git add static/css/style.css
git commit -m "feat: rewrite style.css with terminal theme variables and component styles"
```

---

## Task 3: Update `templates/base.html`

**Files:**
- Modify: `templates/base.html`

Add Google Fonts; rewrite nav with terminal prompt style (remove `./matrix` Todo link); rewrite footer with system tagline.

- [ ] **Step 1: Replace entire `templates/base.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token }}">
    <title>{% block title %}Blog{% endblock %}</title>
    <!-- Terminal fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=VT323&display=swap" rel="stylesheet">
    <!-- Styles -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/pygments.css') }}">
    {% if request.endpoint and request.endpoint.startswith('todo.') %}
    <link rel="stylesheet" href="{{ url_for('static', filename='css/todo.css') }}">
    {% endif %}
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav>
        <a href="{{ url_for('index') }}" class="nav-logo">~/blog<span style="color:var(--amber)">$</span></a>
        <ul class="nav-links">
            <li><a href="{{ url_for('blog.index') }}">./articles</a></li>
            {% if session.get('user_id') %}
                <li><a href="{{ url_for('admin.dashboard') }}">[admin]</a></li>
                <li><span class="nav-user">[{{ session.get('username', 'admin') }}]</span></li>
                <li><a href="{{ url_for('auth.logout') }}">./logout</a></li>
            {% else %}
                <li><a href="{{ url_for('auth.login') }}">./login</a></li>
            {% endif %}
        </ul>
    </nav>

    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="flash-messages">
                {% for category, message in messages %}
                    <div class="flash {{ category }}">{{ message }}</div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

    <main>
        {% block content %}{% endblock %}
    </main>

    <footer>
        [system] &copy; {{ now.year if now else '2026' }} // running on Raspberry Pi 4B // Flask + SQLite // Cloudflare Tunnel
    </footer>

    {% block extra_js %}{% endblock %}
</body>
</html>
```

- [ ] **Step 2: Visual check**

Navigate to `http://localhost:5000/blog/` — confirm:
- Logo shows `~/blog$` in green with amber `$`
- Nav shows `./articles` and `./login` (no `./matrix`)
- Footer shows system tagline

- [ ] **Step 3: Run tests**

```bash
python -m pytest test_app.py -v
```

Expected: All PASS

- [ ] **Step 4: Commit**

```bash
git add templates/base.html
git commit -m "feat: update base.html with terminal nav (remove todo link), Google Fonts, and terminal footer"
```

---

## Task 4: Update Blog Article List (`app/blog/templates/blog/index.html`)

**Files:**
- Modify: `app/blog/templates/blog/index.html`

Replace `.articles-grid` / `.article-card` card layout with flat `.t-article-row` terminal list.

- [ ] **Step 1: Replace entire `app/blog/templates/blog/index.html`**

```html
{% extends "base.html" %}

{% block title %}Articles{% endblock %}

{% block content %}
<div class="t-section-header">// ARTICLES</div>

{% if articles %}
<div class="t-article-list">
  {% for article in articles %}
  <a href="{{ url_for('blog.article_detail', slug=article.slug) }}" class="t-article-row">
    <span class="t-article-date"><span>[</span>{{ article.date.strftime('%Y-%m-%d') }}<span>]</span></span>
    <span class="t-article-title">{{ article.title }}</span>
    <span class="t-article-tag">md</span>
  </a>
  {% endfor %}
</div>
{% else %}
<p class="t-empty">// no articles yet — check back soon</p>
{% endif %}
{% endblock %}
```

- [ ] **Step 2: Visual check**

Navigate to `http://localhost:5000/blog/` — confirm:
- Article rows show date in `[YYYY-MM-DD]` format with amber brackets
- Title is green-dim, turns bright green on hover
- `md` tag appears at right
- No card grid, no rounded corners

- [ ] **Step 3: Run tests**

```bash
python -m pytest test_app.py -v
```

Expected: All PASS

- [ ] **Step 4: Commit**

```bash
git add app/blog/templates/blog/index.html
git commit -m "feat: rewrite blog index template with terminal flat-row article list"
```

---

## Task 5: Update Blog Article Detail (`app/blog/templates/blog/article.html`)

**Files:**
- Modify: `app/blog/templates/blog/article.html`

Add `.t-prompt` breadcrumb before `h1`; update back-link text; add amber bracket wrapper for date.

- [ ] **Step 1: Replace entire `app/blog/templates/blog/article.html`**

```html
{% extends "base.html" %}

{% block title %}{{ article.title }} - Blog{% endblock %}

{% block content %}
<article class="article-detail">
    <header class="article-header">
        <div class="t-prompt">[root@raspberrypi articles]$</div>
        <h1 class="article-title">{{ article.title }}</h1>
        <div class="article-meta">
            <span class="meta-bracket">[</span>{{ article.date.strftime('%Y-%m-%d') }}<span class="meta-bracket">]</span>
        </div>
    </header>

    <div class="article-content">
        {{ article.content|safe }}
    </div>

    <footer class="article-footer">
        <a href="{{ url_for('blog.index') }}" class="back-to-blog">
            ← back to ./articles
        </a>
    </footer>
</article>
{% endblock %}
```

- [ ] **Step 2: Visual check**

Navigate to an article at `http://localhost:5000/blog/articles/<slug>` — confirm:
- `[root@raspberrypi articles]$` prompt appears above title
- Title is large VT323 green with glow
- Date shows `[YYYY-MM-DD]` with amber brackets
- Body text is `#cccccc` (readable, not green)
- Code blocks have `border-left` and dark background
- Back link reads `← back to ./articles`

- [ ] **Step 3: Run tests**

```bash
python -m pytest test_app.py -v
```

Expected: All PASS

- [ ] **Step 4: Commit**

```bash
git add app/blog/templates/blog/article.html
git commit -m "feat: update article detail template with terminal breadcrumb and meta styling"
```

---

## Task 6: Update Login Page (`app/auth/templates/auth/login.html`)

**Files:**
- Modify: `app/auth/templates/auth/login.html`

Three changes: (1) remove `admin.css` import; (2) remove duplicate flash messages block; (3) swap admin class names for terminal class names.

- [ ] **Step 1: Replace entire `app/auth/templates/auth/login.html`**

```html
{% extends "base.html" %}

{% block title %}Login{% endblock %}

{% block content %}
<div class="t-auth-container">
    <div class="t-auth-box">
        <div class="t-section-header">// AUTH_LOGIN</div>

        <form method="POST" action="{{ url_for('auth.login') }}">
            <div class="form-group">
                <label for="username">username</label>
                <input type="text" id="username" name="username"
                       value="{{ username or '' }}"
                       required autofocus
                       autocomplete="username">
            </div>

            <div class="form-group">
                <label for="password">password</label>
                <input type="password" id="password" name="password"
                       required
                       autocomplete="current-password">
            </div>

            <button type="submit" class="t-btn">[ AUTHENTICATE ]</button>
        </form>

        <div class="t-auth-hint">// access restricted — admin only</div>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 2: Visual check**

Navigate to `http://localhost:5000/auth/login` — confirm:
- Dark background, green bordered box, no white admin panel appearance
- `// AUTH_LOGIN` section header in amber
- Input fields have terminal styling (dark bg, green-faint border, green text on focus)
- Submit button reads `[ AUTHENTICATE ]`
- Flash messages from `base.html` appear above the form box if present

- [ ] **Step 3: Test login flow**

Submit the form with wrong credentials — confirm flash error message appears in red terminal style.

- [ ] **Step 4: Run tests**

```bash
python -m pytest test_app.py -v
```

Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add app/auth/templates/auth/login.html
git commit -m "feat: replace login page with terminal auth style, remove admin.css dependency"
```

---

## Task 7: Update Blog 404 Page (`app/blog/templates/blog/404.html`)

**Files:**
- Modify: `app/blog/templates/blog/404.html`

Update markup to terminal error style. Extends `base.html`, so nav/footer come for free.

- [ ] **Step 1: Replace entire `app/blog/templates/blog/404.html`**

```html
{% extends "base.html" %}

{% block title %}404 – Page Not Found{% endblock %}

{% block content %}
<div class="t-error-page">
    <span class="t-error-code">404</span>
    <p class="t-error-msg">// page not found</p>
    <div class="t-error-actions">
        <a href="{{ url_for('blog.index') }}" class="t-btn-outline">[ → ARTICLES ]</a>
        <a href="{{ url_for('index') }}" class="t-btn-outline">[ → HOME ]</a>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 2: Visual check**

Trigger a blog 404 at `http://localhost:5000/blog/articles/nonexistent-slug` — confirm:
- Large `404` in VT323 green with glow
- `// page not found` in body text colour
- Two outline buttons

- [ ] **Step 3: Run tests**

```bash
python -m pytest test_app.py -v
```

Expected: All PASS

- [ ] **Step 4: Commit**

```bash
git add app/blog/templates/blog/404.html
git commit -m "feat: update blog 404 template to terminal error style"
```

---

## Task 8: Update Global 500 Page (`templates/errors/500.html`)

**Files:**
- Modify: `templates/errors/500.html`

Update markup to terminal style with conditional debug panel.

- [ ] **Step 1: Replace entire `templates/errors/500.html`**

```html
{% extends "base.html" %}

{% block title %}500 – Server Error{% endblock %}

{% block content %}
<div class="t-error-page">
    <span class="t-error-code">500</span>
    <p class="t-error-msg">// internal server error</p>
    <div class="t-error-actions">
        <a href="{{ url_for('index') }}" class="t-btn-outline">[ → HOME ]</a>
        <a href="javascript:history.back()" class="t-btn-outline">[ ← BACK ]</a>
    </div>

    {% if config.DEBUG %}
    <div class="t-debug-panel">
        <div class="t-debug-header">// ERROR_TRACE</div>
        <pre>{{ error }}</pre>
    </div>
    {% endif %}
</div>
{% endblock %}
```

- [ ] **Step 2: Visual check (optional — requires triggering a 500)**

In DEBUG mode, navigate to `/trigger-500` if you added that test route, or temporarily add an error route. Confirm the red debug panel appears with error text.

- [ ] **Step 3: Run tests**

```bash
python -m pytest test_app.py -v
```

Expected: All PASS (including the 500 handler test from Task 1)

- [ ] **Step 4: Commit**

```bash
git add templates/errors/500.html
git commit -m "feat: update global 500 template to terminal style with conditional debug panel"
```

---

## Task 9: Rewrite Global 404 Page (`templates/errors/404.html`)

**Files:**
- Modify: `templates/errors/404.html`

This is a **standalone** full HTML document (no Jinja `{% extends %}`). Must manually add Google Fonts, nav markup, and footer.

- [ ] **Step 1: Replace entire `templates/errors/404.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 – Page Not Found</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=VT323&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav>
        <a href="{{ url_for('index') }}" class="nav-logo">~/blog<span style="color:var(--amber)">$</span></a>
        <ul class="nav-links">
            <li><a href="{{ url_for('blog.index') }}">./articles</a></li>
            <li><a href="{{ url_for('auth.login') }}">./login</a></li>
        </ul>
    </nav>

    <main>
        <div class="t-error-page">
            <span class="t-error-code">404</span>
            <p class="t-error-msg">// page not found</p>
            <div class="t-error-actions">
                <a href="{{ url_for('index') }}" class="t-btn-outline">[ → HOME ]</a>
                <a href="{{ url_for('blog.index') }}" class="t-btn-outline">[ → ARTICLES ]</a>
            </div>
        </div>
    </main>

    <footer>
        [system] &copy; 2026 // running on Raspberry Pi 4B // Flask + SQLite // Cloudflare Tunnel
    </footer>
</body>
</html>
```

- [ ] **Step 2: Visual check**

Navigate to `http://localhost:5000/nonexistent-path` — confirm:
- Terminal nav with logo and links appears
- Large 404 code with glow
- Terminal footer appears
- Consistent with the rest of the site

- [ ] **Step 3: Run full test suite**

```bash
python -m pytest test_app.py -v
```

Expected: All PASS

- [ ] **Step 4: Final commit**

```bash
git add templates/errors/404.html
git commit -m "feat: rewrite standalone global 404 template with terminal nav, error style, and footer"
```

---

## Final Verification Checklist

After all 9 tasks are complete, do a full visual walkthrough:

- [ ] `/` — home page unchanged (no CRT effects should be removed)
- [ ] `/blog/` — flat article row list with terminal styling
- [ ] `/blog/articles/<slug>` — article readable with `#cccccc` body text, green heading, amber brackets
- [ ] `/auth/login` — terminal auth box, no white admin panel
- [ ] `/blog/articles/nonexistent` — blog 404 with nav/footer
- [ ] `/nonexistent` — global 404 with inline nav/footer
- [ ] Logged in as admin: nav shows `[admin]` link and `[username]`, no `./matrix` link
- [ ] Not logged in: nav shows `./articles` and `./login` only
- [ ] Flash message on failed login appears in red terminal style
- [ ] Admin pages (`/admin/`) retain white UI — **not** affected by style.css
- [ ] Todo pages (`/todo/`) retain their existing style — **not** affected

```bash
python -m pytest test_app.py -v
```

All tests PASS.
