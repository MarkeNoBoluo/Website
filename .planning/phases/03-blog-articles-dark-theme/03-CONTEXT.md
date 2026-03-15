# Phase 3: Blog Articles + Dark Theme - Context

**Gathered:** 2026-03-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement core blog functionality — article list, detail pages, Markdown rendering, syntax highlighting, dark theme, and 404 page. Includes scanning Markdown files from disk, rendering with frontmatter extraction, implementing responsive dark theme with system font stack, and providing custom 404 page with article recommendations.

</domain>

<decisions>
## Implementation Decisions

### Article List Layout & Content
- **Card style**: Article cards with subtle shadows and rounded corners
- **Content per card**: Title, publication date, short excerpt (first 2-3 lines of content)
- **Sorting**: Newest first (by date descending)
- **Spacing**: Medium spacing between cards (comfortable visual separation)
- **Pagination**: None for v1 (assumes < 200 articles)
- **Excerpt source**: First paragraph or 200 characters from article content (excluding frontmatter)

### Markdown Processing & Syntax Highlighting
- **Markdown parser**: mistune (as planned in requirements)
- **Frontmatter handling**: YAML frontmatter with python-frontmatter library
- **Syntax highlighting**: Server-side Pygments with dark theme stylesheet
- **Caching strategy**: LRU in-memory cache for rendered Markdown (performance optimization)
- **Code block language detection**: Auto-detection via Pygments with fallback to plain text
- **Markdown extensions**: Basic only (no tables, footnotes in v1)

### Dark Theme Design System
- **Background color**: Dark gray (#1a1a1a) for main background
- **Font stack**: System font stack (SF Pro, Segoe UI, Roboto, sans-serif)
- **Responsive breakpoint**: Simple mobile/desktop breakpoint at 768px
- **Component styling**: Modern styling with subtle shadows, rounded corners, clean typography
- **Color scheme**: Dark background with light text, accent color for links and interactive elements
- **Accessibility**: Sufficient color contrast for WCAG AA compliance

### Article File Structure & 404 Page
- **Directory structure**: Flat structure (all articles in single directory)
- **File naming**: YYYY-MM-DD-slug.md (e.g., 2026-03-15-hello-world.md)
- **404 page design**: Simple "Not Found" page with navigation and recommendations
- **Article recommendations**: Show 3 random articles on 404 page
- **Navigation**: 404 page includes link back to home and blog index
- **Error handling**: Custom 404 template, not Nginx default error page

### Claude's Discretion
- Exact LRU cache size and invalidation strategy
- Pygments style selection and CSS generation
- Card layout implementation (CSS Grid vs Flexbox)
- Excerpt extraction algorithm
- File system scanning interval and mechanism
- Frontmatter field validation and defaults
- Responsive design details beyond basic breakpoint
- 404 page copy and styling

</decisions>

<specifics>
## Specific Ideas

- Article cards with hover effect (slight elevation change)
- Date formatted as "March 15, 2026" in article list
- Excerpt truncated with ellipsis if too long
- Code block copy-to-clipboard button (Claude's discretion)
- Pygments CSS generated once at startup and cached
- Random article selection for 404 page uses simple shuffle
- All articles stored in `posts/` directory at project root
- Frontmatter includes: title (required), date (required), excerpt (optional)

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/__init__.py` — Application factory pattern with blueprint registration
- `app/config.py` — Configuration loading from .env file
- `app/db.py` — SQLite connection management (WAL mode)
- `app/auth/` — Authentication blueprint with session management
- `app/blog/__init__.py` — Blog blueprint placeholder
- `app/todo/__init__.py` — Todo blueprint placeholder
- `app/templates/base.html` — Base template structure
- `app/static/` — Static folder served directly by Nginx
- `wsgi.py` — Gunicorn entry point

### Established Patterns
- Environment variable validation at startup
- Blueprint-based modular architecture
- SQLite with WAL mode for concurrent access
- Session-based authentication with Flask-Bcrypt
- Systemd service management with automatic restarts
- Git push deployment via post-receive hook
- Nginx static file serving from `app/static/`
- Unix socket communication between Nginx and Gunicorn

### Integration Points
- Blog routes must integrate with existing authentication system
- Markdown rendering must work within Flask template context
- Static CSS files must be served by Nginx from `app/static/css/`
- Article scanning must be efficient for Raspberry Pi 4B (limited memory)
- Dark theme CSS must integrate with existing base template
- 404 page must use custom template, not interfere with Nginx error pages

### Performance Considerations
- LRU cache essential for Markdown rendering (prevents re-parsing on every request)
- File system scanning should be cached with reasonable TTL
- Pygments CSS should be pre-generated, not per-request
- Article list should load quickly even with many posts (no pagination in v1)

</code_context>

<deferred>
## Deferred Ideas

- **Article tags/categories** — Deferred until pattern emerges with 20+ articles
- **Full-text search** — Deferred until browser Ctrl+F becomes insufficient
- **Pagination** — Deferred until >200 articles
- **RSS feed** — Scheduled for v1.x (post-v1)
- **Sitemap and robots.txt** — Scheduled for v1.x (post-v1)
- **Open Graph meta tags** — Scheduled for v1.x (post-v1)
- **Comment system** — Scheduled for v2
- **Article edit history** — Out of scope (Git provides version control)
- **Article drafts** — Out of scope (use Git branches)

</deferred>

---

*Phase: 03-blog-articles-dark-theme*
*Context gathered: 2026-03-15*