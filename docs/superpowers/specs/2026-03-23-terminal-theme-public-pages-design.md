# Terminal Theme — Public Pages Design Spec

**Date:** 2026-03-23
**Author:** Claude (brainstorming session)
**Status:** Approved

---

## Summary

Apply the terminal/CRT aesthetic from the home page (`templates/home.html` + `static/css/home.css`) to all public-facing pages of the blog. Admin pages and the Todo (Eisenhower matrix) tool are excluded — both retain the white admin UI theme. The Todo entry point is hidden from the nav and only accessible when logged in as admin (or via the admin panel).

---

## Scope

**In scope (terminal theme applied):**
- Blog article list — `app/blog/templates/blog/index.html`
- Blog article detail — `app/blog/templates/blog/article.html`
- Auth login — `app/auth/templates/auth/login.html`
- Blog 404 — `app/blog/templates/blog/404.html` (extends `base.html`)
- Global 404 — `templates/errors/404.html` (**standalone** full-HTML document — requires adding font imports, nav, and footer from scratch, unlike other pages)
- Global 500 — `templates/errors/500.html` (extends `base.html`)
- Base template — `templates/base.html`

**Out of scope (unchanged or using white admin theme):**
- All admin pages (`app/admin/templates/admin/**`) — white admin theme
- Todo pages (`app/todo/templates/todo/**`) — keep current dark style (admin.css variables), **not** terminal theme
- `static/css/admin.css` — untouched
- `static/css/todo.css` — untouched
- `static/css/home.css` — untouched
- `templates/home.html` — untouched
- `static/css/pygments.css` — untouched

---

## Visual Design

### Theme: Lightweight Terminal (no CRT scanlines)

Distinct from the home page in one key way: **no CRT effects** (no scanlines, no phosphor flicker, no custom cursor). These effects are home-page-only to create a "boot → enter" narrative. Content pages prioritize readability.

### Color Palette

All values match `home.css`. Additional palette entries (`--nav-link`, `--comment`, `--divider`) are taken from literal values already used in `home.css`.

```css
/* Core */
--bg:            #080808    /* near-black background */
--bg2:           #0d0d0d    /* slightly lighter surface */
--green:         #00ff41    /* primary: headings, logo glow, active */
--green-dim:     #00c832    /* secondary: links, hover targets */
--green-faint:   #003d10    /* borders, dividers */
--green-bg:      rgba(0,255,65,0.03)   /* subtle tinted backgrounds */
--amber:         #ffb300    /* accents: brackets, dates, section labels */
--red:           #ff2244    /* errors, Q1 quadrant */

/* Extended (from home.css literals) */
--nav-link:      #00a830    /* nav link base colour, back-link */
--comment:       #2a6e3e    /* empty states, secondary button, comment text */
--divider:       #1a4a25    /* footer text, tag borders, dividers */

/* Body text — content pages */
--text-body:     #cccccc    /* article body, form body text — readable on #080808 */
--text-dim:      #1a5c28    /* decorative metadata: timestamps in lists only */
```

> **Accessibility note:** `--text-dim` (`#1a5c28`) has a contrast ratio of ~2.8:1 on `#080808`, below WCAG AA. It is intentionally used *only* for decorative timestamps and metadata in list views (consistent with home page treatment), never for primary body text. All primary body copy uses `--text-body` (`#cccccc`, ~12:1 contrast ratio).

### Typography

- **Body font:** `'Share Tech Mono', 'Courier New', monospace` — applied to `body` in `style.css`
- **Heading font:** `'VT323', 'Courier New', monospace` — applied to `h1`, section headers
- **Google Fonts import:** Added to `base.html` and to the standalone `templates/errors/404.html`

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=VT323&display=swap" rel="stylesheet">
```

### Navigation (shared via `base.html`)

```
# 未登录：
~/blog$                    ./articles  ./login

# 已登录（管理员）：
~/blog$                    ./articles  [admin]  ./logout
```

- **Logo:** `~/blog<span style="color:var(--amber)">$</span>`, VT323 font, `text-shadow: 0 0 8px var(--green)`
- **Nav links:** `./articles`, `./login` / `./logout` — `color: var(--nav-link)`, hover `color: var(--green)`
- **Todo 入口（`./matrix`）完全从 nav 中移除**，改为仅在管理员后台提供入口链接
- **Hover prefix:** `::before { content: '> '; color: var(--amber) }` (same convention as home page)
- **Logged-in state:** `[username]` in `var(--amber)`, `[admin]` link to admin panel shown; no `./matrix` link
- **Border:** `border-bottom: 1px solid var(--green-faint)`
- **Background:** `var(--green-bg)`

### Footer (shared via `base.html`)

```
[system] © 2026 // running on Raspberry Pi 4B // Flask + SQLite // Cloudflare Tunnel
```

`font-size: 0.72rem`, `color: var(--divider)`, `border-top: 1px solid #0a2010`

### Flash Messages

Replaces the current `style.css` `.flash` definitions. Terminal-style, rendered in `base.html`:

```
border-left: 2px solid <category-colour>
background: rgba(<category-colour-rgb>, 0.05)
color: <category-colour>
font-size: 0.82rem
```

| Category | Colour |
|---|---|
| default / info | `var(--green-dim)` `#00c832` |
| success | `var(--green)` `#00ff41` |
| error | `var(--red)` `#ff2244` |
| warning | `var(--amber)` `#ffb300` |

### Form States

For the login page form inputs:

```css
input, textarea, select {
  background: var(--bg2);
  border: 1px solid var(--green-faint);
  color: var(--green-dim);
  font-family: 'Share Tech Mono', monospace;
}
input:focus, textarea:focus, select:focus {
  outline: none;
  border-color: var(--green-dim);
  box-shadow: 0 0 6px rgba(0, 255, 65, 0.25);
}
input:invalid {
  border-color: var(--red);
}
```

---

## Page-by-Page Design

### Blog Article List (`app/blog/templates/blog/index.html`)

**Template markup changes required** — replace `.articles-grid` / `.article-card` structure with flat row layout:

```html
<div class="t-section-header">// ARTICLES</div>
<div class="t-article-list">
  <a href="..." class="t-article-row">
    <span class="t-article-date"><span>[</span>YYYY-MM-DD<span>]</span></span>
    <span class="t-article-title">Title</span>
    <span class="t-article-tag">md</span>
  </a>
</div>
```

- `t-article-date`: `color: var(--text-dim)`, bracket `span` → `color: var(--amber)`
- `t-article-title`: `color: var(--green-dim)`, hover → `color: var(--green)` + `text-shadow`
- `t-article-tag`: always static string `"md"` (all articles are Markdown — no dynamic tag field exists), `border: 1px solid var(--divider)`, `color: var(--comment)`
- Row: `grid-template-columns: 140px 1fr auto`, `border-bottom: 1px solid #0f2e17`
- Hover: `background: rgba(0,255,65,0.04)`, `padding-left: 0.4rem`
- `t-section-header`: VT323, `color: var(--amber)`, underline via `::after` gradient

### Blog Article Detail (`app/blog/templates/blog/article.html`)

Template markup kept as-is; CSS class styles change:

- Breadcrumb: `[root@raspberrypi articles]$` rendered via `.t-prompt` before `h1`; `color: var(--text-dim)`
- `h1.article-title`: VT323, `font-size: clamp(1.8rem, 5vw, 2.8rem)`, `color: var(--green)`, `text-shadow: 0 0 12px var(--green)`
- `.article-meta` date: amber brackets, `color: var(--text-dim)`
- **`.article-content` body text: `color: var(--text-body)` (`#cccccc`)** — primary readability requirement
- `.article-content h2`: VT323, `color: var(--green-dim)`, prefixed `## ` via `::before`
- `.article-content h3`: VT323, `color: var(--nav-link)`, prefixed `### ` via `::before`
- `.article-content code` (inline): `background: var(--bg2)`, `color: var(--amber)`
- `.article-content pre` (block): `background: var(--bg2)`, `border-left: 2px solid var(--green-faint)`, green text
- `.back-to-blog`: `color: var(--nav-link)`, text `← back to ./articles`

### Auth Login (`app/auth/templates/auth/login.html`)

**Two changes to the template:**

1. **Remove `admin.css` import** (the `{% block extra_css %}` block that loads `admin.css`)
2. **Fix duplicate flash messages** — remove the inline `{% with messages = get_flashed_messages(...) %}` block in the login template; rely on the `base.html` flash block only
3. **Replace markup** — swap admin-CSS class names for terminal class names:

Old → New class mapping:
```
.login-container   → .t-auth-container
.login-card        → .t-auth-box
.login-form        → (no class needed, styled via .t-auth-box form)
.login-help        → .t-auth-hint
.btn.btn-primary.btn-block → .t-btn (terminal button style)
```

Terminal form layout:
```
section header:  // AUTH_LOGIN
container:       border: 1px solid var(--green-faint), background: rgba(0,255,65,0.02), max-width: 420px, centered
labels:          color: var(--nav-link), font-size: 0.8rem, display: block
inputs:          full-width, terminal input styles (see Form States above)
submit button:   [ AUTHENTICATE ] — border: 1px solid var(--green), color: var(--green), hover: fill green
hint text:       // access restricted — admin only, color: var(--text-dim)
```

### Error Pages

**`app/blog/templates/blog/404.html`** and **`templates/errors/500.html`** — extend `base.html`, get nav/footer automatically:
- Error code (e.g. `404`): VT323, large, `color: var(--green)`, glow
- Message: `// page not found`, `color: var(--text-body)`
- Back buttons: terminal `[ → HOME ]` style

**`templates/errors/404.html`** — standalone `<!DOCTYPE html>` document:
- Must manually add Google Fonts `<link>` tags
- Must add terminal nav markup (same as `base.html` nav, but static — no Jinja session check needed since it's a global error page)
- Must add terminal footer markup
- Same error code / message / button styling as above

**`templates/errors/500.html`** debug panel:

`{{ error }}` is already passed by the existing error handler — no backend change needed. Only style the existing `<pre>` block:

```html
{% if config.DEBUG %}
<div class="t-debug-panel">
  <div class="t-debug-header">// ERROR_TRACE</div>
  <pre>{{ error }}</pre>
</div>
{% endif %}
```

`.t-debug-panel`: `border: 1px solid var(--red)`, `background: rgba(255,34,68,0.04)`, `padding: 1rem`; inner `pre`: `color: var(--red)`, monospace, `overflow-x: auto`, `font-size: 0.78rem`

---

## Files Changed

| File | Change type |
|---|---|
| `templates/base.html` | Add Google Fonts; rewrite nav + footer to terminal style |
| `static/css/style.css` | Full rewrite: terminal color vars, monospace fonts, all component styles |
| `app/blog/templates/blog/index.html` | Restructure article list markup (card grid → flat row layout) |
| `app/blog/templates/blog/404.html` | Update error markup to terminal style (extends base.html) |
| `app/auth/templates/auth/login.html` | Remove `admin.css` import; remove duplicate flash block; swap class names |
| `templates/errors/404.html` | Standalone rewrite: add fonts, nav, footer, terminal error layout |
| `templates/errors/500.html` | Update error markup + debug panel to terminal style (extends base.html) |

---

## What Does NOT Change

- `static/css/home.css` — untouched
- `templates/home.html` — untouched
- CRT scanlines, phosphor flicker, boot screen, custom cursor — home page only
- `static/css/admin.css` — untouched
- All admin page templates — untouched
- `static/css/pygments.css` — untouched (code syntax highlighting colours unchanged)
- `static/css/todo.css` — untouched
- All todo page templates — untouched
- All Python/Flask route and model code — no backend changes
  - **Exception 1:** `templates/errors/500.html` debug panel requires a 500 error handler in `app/__init__.py`. Add `@app.errorhandler(500)` → `render_template("errors/500.html", error=str(e)), 500`.
  - **Exception 2:** The `./matrix` nav link is removed from `base.html`. The todo feature remains accessible via the admin panel only — no route changes needed.
