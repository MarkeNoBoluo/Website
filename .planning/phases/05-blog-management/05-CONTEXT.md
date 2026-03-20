# Phase 5: Blog Management (CRUD) - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Add article management capabilities (create, edit, delete) with draft/publish workflow. Admin interface at `/admin` with CRUD operations. Import existing file-based articles to database. Unify UI across all pages (login, admin, forms) with consistent dark theme.

</domain>

<decisions>
## Implementation Decisions

### Article Storage
- **Storage**: Database only (SQLite via SQLAlchemy)
- **Model fields**: title, markdown content, status (draft/published), created_at, updated_at
- **No explicit slug field**: Slugs auto-generated from title

### URL Generation
- **Format**: `/blog/{slug}` with date prefix in route `/blog/{year}/{month}/{day}/{slug}`
- **Slug generation**: Convert title to URL-friendly slug (lowercase, hyphens)
- **Duplicate handling**: Add incrementing suffix for conflicts (my-post, my-post-2, my-post-3)

### Status Workflow
- **States**: draft, published (simple two-state system)
- **Behavior**: Draft articles hidden from public listing, visible only to admin

### Admin Interface Structure
- **URL prefix**: `/admin` (e.g., `/admin/articles`, `/admin/articles/new`, `/admin/articles/{id}/edit`)
- **Authentication**: All admin routes require `@login_required`
- **Article list**: Card grid view with status badges and filter buttons (All/Draft/Published)
- **Create/Edit form**: Title field + Markdown textarea with live preview pane (side-by-side)
- **Delete handling**: JavaScript confirmation dialog before deletion

### Migration Strategy
- **Import existing posts**: One-time migration script to import `posts/` folder into database
- **Slug mapping**: Extract slug from filename (e.g., `2026-03-15-hello-world.md` → slug `hello-world`)
- **Archive original**: Move `posts/` to `posts-archive/` after successful import
- **URL compatibility**: Generate matching slugs so existing URLs continue working

### UI Unification
- Apply existing dark theme (#1a1a1a background) consistently to:
  - Login page (already has dark styling, verify consistency)
  - Admin templates (forms, tables, buttons)
  - Flash messages and error states

### Claude's Discretion
- Exact markdown editor implementation (textarea + preview refresh strategy)
- Migration script details (batch size, error handling)
- Admin navigation menu structure
- Filter implementation for article list
- Card grid layout details (spacing, hover effects)

</decisions>

<specifics>
## Specific Ideas

- Use existing dark theme CSS variables from style.css
- Leverage existing Markdown rendering from app/markdown.py
- Reuse card styling from public blog for admin article list
- Preview pane should update on content change (debounced)

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/blog/utils.py`: `get_all_articles()`, `get_article_by_slug()` — update to query DB
- `app/markdown.py`: `render_markdown()` — reuse for preview pane
- `app/models.py`: Existing User/Todo models — add Article model in similar style
- `app/auth/utils.py`: `@login_required` decorator — reuse for admin routes
- `app/static/css/style.css`: Dark theme CSS — reuse variables and patterns

### Established Patterns
- SQLAlchemy models with `db.Model`, columns, timestamps
- Blueprint routes with `@bp.route()` decorator
- Form handling via `request.form.get()`
- Flash messages with category (success, error)
- Template inheritance from `base.html`

### Integration Points
- Blog routes (`app/blog/routes.py`): Update to read from DB instead of file system
- Article listing on homepage: Filter to show only `published` articles
- Markdown rendering: Continue using existing `render_markdown()` function
- Authentication: Continue using existing `@login_required` for admin protection

</code_context>

<deferred>
## Deferred Ideas

- Article tags/categories — deferred until pattern emerges with 20+ articles
- Full-text search — deferred until browser Ctrl+F becomes insufficient
- Article edit history — out of scope (Git provides version control)
- Image upload for articles — out of scope for v1.1

</deferred>

---

*Phase: 05-blog-management*
*Context gathered: 2026-03-20*
