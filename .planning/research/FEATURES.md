# Feature Research

**Domain:** Personal technical blog with private productivity tool
**Researched:** 2026-03-12
**Confidence:** HIGH (core blog features well-established; Eisenhower matrix scope is custom/simple)

## Feature Landscape

### Table Stakes (Users Expect These)

Features visitors assume exist. Missing these = blog feels broken or untrustworthy.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Article list page (reverse-chronological) | Every blog shows this; it's the homepage contract | LOW | Sort by date desc; show title + date + excerpt |
| Article detail page with rendered Markdown | The core content delivery mechanism | LOW | Use python-markdown or mistune; code syntax highlighting matters for technical blog |
| Page title and meta description per article | SEO and browser tab legibility | LOW | `<title>` and `<meta name="description">`; derive from frontmatter |
| Readable typography and dark theme | Visitors read text; dark theme is the stated aesthetic | LOW | CSS-only; no JS required for theme itself |
| Responsive layout (mobile-readable) | 60%+ of web traffic is mobile; broken mobile = broken blog | LOW | CSS flexbox/grid; media queries; test on phone |
| Fast page load | Slow load causes abandonment; Raspberry Pi is constrained hardware | MEDIUM | Serve static assets with cache headers; avoid heavy JS bundles |
| Code block syntax highlighting | Technical blog readers expect readable code; this is table stakes for dev blogs | LOW | Pygments (Python-native) or highlight.js client-side |
| 404 page | Broken links happen; missing 404 = unprofessional | LOW | Single template with back-to-home link |
| About page or author byline | Visitors want to know who wrote this | LOW | Static page or frontmatter author field |

### Differentiators (Serve the Owner Well or Stand Out)

Features that make this blog distinctively useful — either to visitors or to the owner.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Per-article anonymous comments | Enables visitor interaction without requiring accounts; rare on self-hosted blogs | MEDIUM | Name + content fields; store in SQLite; moderation queue or simple approval flag |
| Comment spam defense (honeypot field) | Anonymous comments attract bots; invisible honeypot field stops 90%+ of spam without CAPTCHA friction | LOW | Add hidden `<input>` field; reject any submission where it's filled; no third-party dependency |
| Eisenhower Matrix todo tool (password-protected) | Personal productivity embedded in personal site; accessible from anywhere on the network | MEDIUM | Four quadrants; add/complete/delete tasks; session-based password auth; SQLite storage |
| Git push deployment (post-receive hook) | Zero-friction publish workflow: write → commit → push → live | MEDIUM | Bare repo on Pi + hook script; requires initial server-side setup; one-time cost |
| RSS feed | Tech-savvy readers use RSS readers; shows the blog is "serious" | LOW | Generate `/feed.xml` from article list; well-established format |
| `<meta og:*>` open graph tags | Article links shared on social/chat platforms render with title + description previews | LOW | Add to article template; no external service needed |
| Sitemap (`/sitemap.xml`) | Helps search engines discover all articles | LOW | Auto-generate from article list on each request or on deploy |

### Anti-Features (Over-Engineering Traps)

Features that seem useful but create disproportionate complexity for a personal blog at this scale.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Web-based CMS / admin panel for articles | "Edit posts in the browser" sounds convenient | Duplicates VSCode; adds auth surface, file-write logic, and a whole UI to build and maintain; VSCode SSH is already the workflow | Write `.md` files in VSCode over SSH — it's faster and already works |
| Email notifications for new comments | "Know when someone comments" | Requires SMTP config, credentials storage, email templating, and handling delivery failures; high complexity for occasional personal blog comments | Check the admin view periodically; add notifications only if comments become active |
| OAuth / social login for comments | "Reduce spam with real identities" | Adds third-party OAuth dependency, token handling, and user account management; breaks anonymity which is the stated design | Use honeypot field + manual moderation for spam; anonymous commenting is the explicit requirement |
| Full-text search | "Search my posts" | Requires index, query UI, and relevance tuning; adds significant complexity for a blog that may have <100 articles | Browser Ctrl+F on article list; or add later with a simple SQLite FTS query if needed |
| Pagination on article list | "Handle lots of posts" | Adds state management and query complexity before it's needed | Show all articles (reverse-chron) — acceptable until 200+ posts; add pagination then |
| Tag / category taxonomy | "Organize content" | Tag management UI, tag index pages, filtering logic; premature for a fresh blog | Add article tags as plain text in frontmatter; build index pages only when 20+ articles exist and patterns emerge |
| Real-time comment updates (WebSocket/polling) | "Comments appear live" | Requires persistent connection or polling loop; adds server complexity on constrained Pi hardware | Standard page reload on submit is completely adequate for a low-traffic personal blog |
| PostgreSQL or MySQL | "Proper database" | Requires a running database service consuming memory on the Pi; adds operational overhead | SQLite is the right choice: zero-config, single file, handles thousands of concurrent readers |
| Microservices / separate comment service | "Clean architecture" | Distributed systems complexity with no scaling benefit at personal-blog traffic levels | Single Flask/FastAPI app with clear module boundaries |
| Docker / container orchestration | "Reproducible deployment" | Adds container runtime overhead on the Pi's limited RAM; systemd unit file is simpler | Use a Python virtualenv + systemd service unit for process management |

## Feature Dependencies

```
Article List Page
    └──requires──> Markdown File Parser (frontmatter + body)
                       └──requires──> Article Storage Convention (.md files in /content)

Article Detail Page
    └──requires──> Markdown File Parser
    └──requires──> Syntax Highlighting (Pygments or highlight.js)

Comment Section
    └──requires──> Article Detail Page (comments are per-article)
    └──requires──> SQLite Database (comment storage)
    └──requires──> Spam Defense (honeypot) [should ship together]

Comment Moderation View
    └──requires──> Comment Section
    └──requires──> Password Auth (same session system as Eisenhower Matrix)

Eisenhower Matrix Tool
    └──requires──> Password Auth (session-based, simple)
    └──requires──> SQLite Database (task storage, can share same DB file)

RSS Feed
    └──requires──> Markdown File Parser (to generate feed entries)
    └──enhances──> Article List Page (parallel output format)

Sitemap
    └──requires──> Markdown File Parser (to enumerate articles)
    └──enhances──> Article List Page (parallel output format)

Git Push Deployment
    └──requires──> Bare git repo on Pi (one-time setup)
    └──enhances──> All features (makes publishing frictionless)

Password Auth (session)
    └──shared by──> Eisenhower Matrix Tool
    └──shared by──> Comment Moderation View
```

### Dependency Notes

- **Comments require spam defense:** Honeypot should ship in the same phase as the comment form — adding it later risks bot accumulation in the database.
- **Password auth is shared infrastructure:** Eisenhower Matrix and comment moderation both need the same session mechanism. Build it once.
- **SQLite is shared:** Comments and tasks can live in the same `.db` file with separate tables. No multi-DB complexity.
- **Markdown parser is the foundation:** Article list, detail, RSS, and sitemap all depend on parsing `.md` frontmatter. Get this right first.
- **Deployment hook enhances everything:** It doesn't block any feature but should be set up early so the workflow is smooth from the first push.

## MVP Definition

### Launch With (v1)

Minimum viable product — fully functional personal blog that visitors can read and comment on, and owner can use for task management.

- [ ] Markdown article parser (frontmatter: title, date, slug) — all other content features depend on this
- [ ] Article list page (reverse-chronological, title + date) — core visitor entry point
- [ ] Article detail page (rendered Markdown, syntax highlighting) — core content delivery
- [ ] Dark technical CSS theme — stated aesthetic requirement; do once, do right
- [ ] Responsive layout — table stakes for any 2026 web property
- [ ] Per-article comment form (anonymous: name + content) with honeypot — visitor interaction
- [ ] Comment display below article — close the feedback loop
- [ ] SQLite schema (comments + tasks tables) — shared persistence layer
- [ ] Password auth (simple session, env-var password) — gate for protected features
- [ ] Eisenhower Matrix UI (four quadrants, add/complete/delete) — owner's productivity tool
- [ ] 404 page — professionalism baseline
- [ ] Git post-receive deployment hook — frictionless publish workflow

### Add After Validation (v1.x)

Features to add once core is working and the blog has real content.

- [ ] RSS feed (`/feed.xml`) — add when sharing articles; low cost, high value for tech readers
- [ ] Open Graph meta tags — add when sharing links on social/chat platforms
- [ ] Sitemap (`/sitemap.xml`) + `robots.txt` — add when wanting search engine indexing
- [ ] Comment moderation view (approve/delete) — add when first real comments appear
- [ ] About page — add when there's something to say

### Future Consideration (v2+)

Features to defer until there's a concrete need.

- [ ] Article tags / categories — defer until 20+ articles and clear content patterns emerge
- [ ] Full-text search — defer until Ctrl+F on article list is genuinely insufficient
- [ ] Pagination — defer until 200+ articles
- [ ] Email comment notifications — defer unless comments become high-volume

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Article list + detail pages | HIGH | LOW | P1 |
| Markdown parsing with frontmatter | HIGH | LOW | P1 |
| Syntax highlighting | HIGH (tech blog) | LOW | P1 |
| Dark theme + responsive CSS | HIGH | LOW | P1 |
| Anonymous comments + honeypot | HIGH | MEDIUM | P1 |
| Eisenhower Matrix + password auth | HIGH (owner) | MEDIUM | P1 |
| Git deploy hook | HIGH (owner) | MEDIUM | P1 |
| SQLite persistence | HIGH | LOW | P1 |
| 404 page | MEDIUM | LOW | P1 |
| RSS feed | MEDIUM | LOW | P2 |
| Open Graph meta tags | MEDIUM | LOW | P2 |
| Sitemap + robots.txt | MEDIUM | LOW | P2 |
| Comment moderation view | MEDIUM | LOW | P2 |
| About page | LOW | LOW | P2 |
| Article tags / categories | LOW | MEDIUM | P3 |
| Full-text search | LOW | MEDIUM | P3 |
| Pagination | LOW | LOW | P3 |
| Email notifications | LOW | HIGH | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when core is working
- P3: Nice to have, add when there's a concrete trigger

## Competitor Feature Analysis

Reference: what comparable self-hosted personal blogs typically provide.

| Feature | Typical WordPress Blog | Typical Static Site (Hugo/Jekyll) | This Blog's Approach |
|---------|----------------------|----------------------------------|----------------------|
| Article rendering | Server-rendered PHP | Pre-built HTML | Flask renders Markdown at request time (or at deploy) |
| Comments | Akismet + accounts optional | Disqus (third-party) or none | SQLite, anonymous, honeypot spam defense — no third party |
| CMS | Web admin panel | None (local files) | None — VSCode over SSH, same as static site approach |
| Deployment | FTP / hosting panel | CI/CD or manual | Git post-receive hook — same simplicity as static sites |
| Task management | Plugin (WP Planner, etc.) | N/A (separate tool) | Built-in Eisenhower Matrix — unique, personal, owned |
| Search | Plugin (ElasticPress, etc.) | Client-side JS index | Deferred — browser Ctrl+F sufficient initially |
| Theme | Theme marketplace | Template files | Custom CSS — dark technical aesthetic, no theme bloat |

## Sources

- General blog feature research: web search survey of blog platform comparisons (Medium, blogging guides)
- Comment spam prevention: [WordPress spam comments guide — Kinsta](https://kinsta.com/blog/wordpress-spam-comments/) (methods generalize to any platform)
- Spam prevention: [Stop spam comments — wp-rocket](https://wp-rocket.me/blog/stop-spam-comments/) (honeypot pattern documented here)
- SEO basics: [Google Search Central — Build and Submit a Sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- SEO basics: [Google Search Central — XML sitemaps and RSS/Atom best practices](https://developers.google.com/search/blog/2014/10/best-practices-for-xml-sitemaps-rssatom)
- Eisenhower Matrix UX patterns: [eisenhower.me](https://www.eisenhower.me/eisenhower-matrix-apps/) and [appfluence.com](https://appfluence.com/eisenhower-matrix-app/)
- Flask + Markdown blog patterns: [simple-flask-blog (LowbrowLabs)](https://github.com/LowbrowLabs/simple-flask-blog), [James Harding's post](https://jameshard.ing/posts/simple-static-markdown-blog-in-flask/)

---
*Feature research for: Personal technical blog (Python, Raspberry Pi 4B, Markdown articles, anonymous comments, Eisenhower Matrix todo)*
*Researched: 2026-03-12*
