# Phase 3: Blog Articles + Dark Theme - Research

**Researched:** 2026-03-15
**Domain:** Flask blog implementation with Markdown rendering, syntax highlighting, and dark theme
**Confidence:** HIGH

## Summary

This phase implements core blog functionality with Markdown file-based content management, dark theme styling, and custom error pages. The implementation uses mistune for Markdown parsing, python-frontmatter for metadata extraction, Pygments for syntax highlighting, and a modern dark theme CSS with system font stack. Articles are stored as flat files with YYYY-MM-DD-slug.md naming convention, scanned from disk with LRU caching for performance on Raspberry Pi 4B.

**Primary recommendation:** Use mistune 3.2.0 + python-frontmatter for Markdown processing, Pygments for server-side syntax highlighting with pre-generated CSS, and implement file scanning with `functools.lru_cache` for performance on Raspberry Pi.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Article List Layout & Content**: Card style with subtle shadows and rounded corners, title + publication date + short excerpt (first 2-3 lines), newest first sorting, medium spacing, no pagination for v1, excerpt from first paragraph or 200 characters
- **Markdown Processing & Syntax Highlighting**: mistune parser, YAML frontmatter with python-frontmatter library, server-side Pygments with dark theme stylesheet, LRU in-memory cache for rendered Markdown, auto-detection of code block languages, basic Markdown extensions only
- **Dark Theme Design System**: Dark gray background (#1a1a1a), system font stack (SF Pro, Segoe UI, Roboto, sans-serif), simple mobile/desktop breakpoint at 768px, modern styling with subtle shadows and rounded corners, dark background with light text, WCAG AA compliance
- **Article File Structure & 404 Page**: Flat structure (all articles in single directory), YYYY-MM-DD-slug.md naming, custom 404 page with navigation and 3 random article recommendations, link back to home and blog index, custom 404 template not Nginx default

### Claude's Discretion
- Exact LRU cache size and invalidation strategy
- Pygments style selection and CSS generation
- Card layout implementation (CSS Grid vs Flexbox)
- Excerpt extraction algorithm
- File system scanning interval and mechanism
- Frontmatter field validation and defaults
- Responsive design details beyond basic breakpoint
- 404 page copy and styling

### Deferred Ideas (OUT OF SCOPE)
- Article tags/categories — Deferred until pattern emerges with 20+ articles
- Full-text search — Deferred until browser Ctrl+F becomes insufficient
- Pagination — Deferred until >200 articles
- RSS feed — Scheduled for v1.x (post-v1)
- Sitemap and robots.txt — Scheduled for v1.x (post-v1)
- Open Graph meta tags — Scheduled for v1.x (post-v1)
- Comment system — Scheduled for v2
- Article edit history — Out of scope (Git provides version control)
- Article drafts — Out of scope (use Git branches)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| BLOG-01 | 用户访问首页可看到所有文章列表，按发布时间倒序排列，显示标题和日期 | mistune + python-frontmatter for parsing, file system scanning with sorting by date, template rendering with card layout |
| BLOG-02 | 用户点击文章可查看详情，Markdown 内容完整渲染为 HTML | mistune Markdown to HTML conversion, frontmatter extraction, template integration |
| BLOG-03 | 代码块有语法高亮（Pygments，适配暗色主题） | Pygments for syntax highlighting, dark theme style selection, CSS generation |
| BLOG-04 | 全站使用暗色技术风格视觉主题，布局在移动端和桌面端均可正常显示 | Dark theme CSS with system font stack, responsive design with 768px breakpoint, WCAG AA compliance |
| BLOG-05 | 访问不存在的 URL 显示自定义 404 页面 | Flask error handler for 404, custom template with article recommendations, integration with existing base template |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| mistune | 3.2.0 | Fast Markdown parser with HTML output | Lightweight, fast, actively maintained (Dec 2025 release), simpler API than markdown2 |
| python-frontmatter | 1.1.0 | YAML frontmatter extraction from Markdown files | Jekyll-style frontmatter support, handles multiple formats, clean separation of metadata and content |
| Pygments | 2.18.0 | Syntax highlighting for code blocks | Supports 500+ languages, generates HTML with CSS classes, server-side rendering avoids client-side JS |
| Flask | 3.1.3 | Web framework (already in use) | WSGI-sync, template-first, low memory footprint (~15MB) suitable for Raspberry Pi |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| functools.lru_cache | stdlib | In-memory caching for rendered Markdown | Cache parsed articles to avoid re-parsing on every request, configurable maxsize |
| os.path + glob | stdlib | File system scanning for Markdown files | Scan posts/ directory for .md files, filter by extension, read file metadata |
| datetime | stdlib | Date parsing and formatting | Parse dates from frontmatter and filenames, format for display (e.g., "March 15, 2026") |
| random | stdlib | Random article selection for 404 page | Select 3 random articles from available posts for 404 page recommendations |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| mistune | markdown2 | markdown2 has more extensions but heavier API, mistune is faster and simpler |
| python-frontmatter | manual YAML parsing | Manual parsing is error-prone, python-frontmatter handles edge cases and multiple formats |
| Pygments | highlight.js (client-side) | Client-side adds JS dependency and FOUC, Pygments is server-side and works without JS |
| LRU cache | Redis/Memcached | External cache adds complexity, LRU cache is sufficient for <200 articles on single server |

**Installation:**
```bash
pip install mistune==3.2.0 python-frontmatter==1.1.0 Pygments==2.18.0
```

## Architecture Patterns

### Recommended Project Structure
```
app/
├── blog/
│   ├── __init__.py           # Blueprint definition
│   ├── routes.py             # Blog routes and view functions
│   ├── utils.py              # Markdown parsing, caching, file scanning
│   └── templates/blog/       # Blog-specific templates
│       ├── index.html        # Article list
│       ├── article.html      # Single article view
│       └── 404.html          # Blog-specific 404 page
├── static/
│   └── css/
│       ├── theme.css         # Dark theme styles
│       └── pygments.css      # Generated Pygments CSS
└── templates/
    ├── base.html             # Base template (already exists)
    └── errors/
        └── 404.html          # Global 404 page
posts/                        # At project root
├── 2026-03-15-hello-world.md
└── 2026-03-16-markdown-guide.md
```

### Pattern 1: File-Based Article Storage with Caching
**What:** Store articles as Markdown files on disk, scan directory on app startup and cache results
**When to use:** Simple content management without database overhead, Git-based version control
**Example:**
```python
# Source: Flask patterns + python-frontmatter documentation
from functools import lru_cache
import frontmatter
from pathlib import Path

POSTS_DIR = Path("posts")

@lru_cache(maxsize=128)
def get_article(slug):
    """Get article by slug with LRU caching."""
    filepath = POSTS_DIR / f"{slug}.md"
    if not filepath.exists():
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)

    return {
        'title': post.metadata.get('title', 'Untitled'),
        'date': post.metadata.get('date'),
        'content': post.content,
        'slug': slug
    }
```

### Pattern 2: Markdown Rendering Pipeline
**What:** Parse Markdown → Extract frontmatter → Convert to HTML → Apply syntax highlighting
**When to use:** Rendering user-authored content with metadata and code blocks
**Example:**
```python
# Source: mistune + Pygments documentation
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter

markdown = mistune.create_markdown(renderer=mistune.HTMLRenderer())

def render_markdown_with_highlighting(content):
    """Render Markdown with syntax highlighted code blocks."""
    # Custom renderer for code blocks
    class HighlightRenderer(mistune.HTMLRenderer):
        def block_code(self, code, info=None):
            if info:
                try:
                    lexer = get_lexer_by_name(info.strip())
                except:
                    lexer = guess_lexer(code)
            else:
                lexer = guess_lexer(code)

            formatter = HtmlFormatter(style='monokai')
            return highlight(code, lexer, formatter)

    renderer = HighlightRenderer()
    md = mistune.create_markdown(renderer=renderer)
    return md(content)
```

### Anti-Patterns to Avoid
- **Direct file inclusion in templates:** Never use `{{ content|safe }}` without proper sanitization - use dedicated Markdown rendering functions
- **Re-parsing on every request:** Avoid parsing Markdown files for each page view - implement caching
- **Blocking file operations in request handlers:** Don't scan filesystem synchronously - cache article list and update periodically
- **Hardcoded file paths:** Use `Path` objects and configurable directories, not string concatenation

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Markdown parsing | Custom regex/parser | mistune | Handles edge cases, safe HTML escaping, extensible |
| Frontmatter extraction | Manual YAML parsing | python-frontmatter | Handles multiple formats, encoding issues, metadata validation |
| Syntax highlighting | Custom regex coloring | Pygments | Supports 500+ languages, theme system, accessibility |
| LRU cache | Custom cache dict | functools.lru_cache | Thread-safe, memory-efficient, battle-tested standard library |
| File system watching | Polling with sleep | Periodic cache refresh | Simpler, no filesystem event dependencies, works on all platforms |

**Key insight:** Markdown parsing and syntax highlighting are deceptively complex problems with many edge cases (nesting, escaping, language detection). Using established libraries prevents security vulnerabilities and rendering bugs.

## Common Pitfalls

### Pitfall 1: XSS via Unsafe HTML Rendering
**What goes wrong:** Raw Markdown output includes script tags or malicious HTML that executes in browser
**Why it happens:** Using `| safe` filter in templates without proper sanitization
**How to avoid:** Always use Markdown library's HTML output (properly escaped), never render raw user content
**Warning signs:** `{{ content|safe }}` in templates, custom rendering functions without escaping

### Pitfall 2: File System Performance on Raspberry Pi
**What goes wrong:** Scanning directory on every request causes high I/O, slow page loads
**Why it happens:** No caching, synchronous file operations in request handlers
**How to avoid:** Use `@lru_cache` with reasonable TTL, scan once at startup, refresh on signal
**Warning signs:** `os.listdir()` in view functions, file reads in template rendering

### Pitfall 3: Pygments CSS Bloat
**What goes wrong:** Generating Pygments CSS per-request or including unused styles
**Why it happens:** Creating new `HtmlFormatter` for each request, not reusing CSS
**How to avoid:** Generate CSS once at startup, save to static file, reference in templates
**Warning signs:** `HtmlFormatter().get_style_defs()` called in view functions, inline style tags

### Pitfall 4: Date Parsing Inconsistency
**What goes wrong:** Different date formats in frontmatter vs filenames cause sorting errors
**Why it happens:** Mixing string dates, datetime objects, and timestamps
**How to avoid:** Standardize on ISO format (YYYY-MM-DD), parse once with `datetime.fromisoformat()`
**Warning signs:** String comparison for dates, multiple date formats in code

### Pitfall 5: 404 Page Interference with Nginx
**What goes wrong:** Custom Flask 404 handler conflicts with Nginx error_page directive
**Why it happens:** Both Flask and Nginx try to handle 404 errors
**How to avoid:** Configure Nginx to pass 404 errors to Flask, not handle them internally
**Warning signs:** Nginx shows default error page instead of custom Flask 404

## Code Examples

Verified patterns from official sources:

### Markdown Processing with Frontmatter
```python
# Source: python-frontmatter PyPI documentation
import frontmatter
import mistune

def load_article(filepath):
    """Load and parse Markdown article with frontmatter."""
    with open(filepath, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)

    # Render Markdown to HTML
    html_content = mistune.markdown(post.content)

    return {
        'metadata': post.metadata,
        'content': html_content,
        'excerpt': extract_excerpt(post.content)
    }
```

### Pygments CSS Generation
```python
# Source: Pygments documentation - Styles API
from pygments.formatters import HtmlFormatter
from pygments.styles import get_all_styles

def generate_pygments_css(style_name='monokai'):
    """Generate CSS for Pygments syntax highlighting."""
    formatter = HtmlFormatter(style=style_name)
    css = formatter.get_style_defs('.highlight')

    # Save to static file
    with open('app/static/css/pygments.css', 'w') as f:
        f.write(css)

    return css

# List available styles
available_styles = list(get_all_styles())
# ['default', 'emacs', 'friendly', 'colorful', 'autumn', 'monokai', ...]
```

### Flask 404 Error Handler with Recommendations
```python
# Source: Flask error handling documentation
from flask import render_template, request
import random

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 page with article recommendations."""
    # Get all articles for recommendations
    articles = get_all_articles()  # Your article scanning function

    # Select 3 random articles
    if articles:
        recommendations = random.sample(articles, min(3, len(articles)))
    else:
        recommendations = []

    # Check if it's a blog URL
    if request.path.startswith('/blog/'):
        template = 'blog/404.html'
    else:
        template = 'errors/404.html'

    return render_template(template,
                         recommendations=recommendations), 404
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| markdown2 (2010s) | mistune 3.x (2025) | 2023-2025 | Faster parsing, cleaner API, active maintenance |
| Client-side syntax highlighting | Server-side Pygments | Always | Better performance, no FOUC, works without JS |
| Database-driven CMS | File-based with Git | Modern static sites | Simpler deployment, version control, no DB migrations |
| Manual cache management | functools.lru_cache | Python 3.2+ | Standard library, thread-safe, efficient LRU algorithm |

**Deprecated/outdated:**
- **Flask-Cache:** Superseded by Flask-Caching, simpler cache types available in standard library
- **Custom Markdown parsers:** Security risks, edge case bugs, maintenance burden
- **Polling filesystem watchers:** High I/O on Raspberry Pi SD card, use cached scanning instead

## Open Questions

1. **LRU cache size optimization**
   - What we know: Raspberry Pi 4B has 4GB RAM, typical article ~10KB
   - What's unclear: Optimal maxsize for 128MB allocation vs performance
   - Recommendation: Start with maxsize=100 (covers ~1MB), monitor memory usage

2. **Pygments style selection for dark theme**
   - What we know: monokai, solarized-dark, vs are popular dark styles
   - What's unclear: Which has best contrast for WCAG AA on dark background
   - Recommendation: Test monokai first, provide style config option

3. **File scanning refresh strategy**
   - What we know: Need to detect new articles without restart
   - What's unclear: Optimal interval (5min vs 15min) vs cache invalidation
   - Recommendation: Cache with 300s TTL, refresh on cache miss after timeout

## Sources

### Primary (HIGH confidence)
- PyPI mistune 3.2.0 - Markdown parser features and API
- PyPI python-frontmatter 1.1.0 - Frontmatter extraction API
- Pygments documentation - Styles API and CSS generation
- Flask documentation - Error handling patterns and file operations

### Secondary (MEDIUM confidence)
- MDN Web Docs - System font stack and CSS best practices
- Flask patterns documentation - Caching recommendations

### Tertiary (LOW confidence)
- Web search for dark theme Pygments styles (needs validation with actual testing)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Libraries well-documented, versions current
- Architecture: HIGH - Patterns align with Flask best practices and project constraints
- Pitfalls: HIGH - Based on documented security concerns and Raspberry Pi performance characteristics

**Research date:** 2026-03-15
**Valid until:** 2026-04-15 (30 days - stable libraries)
