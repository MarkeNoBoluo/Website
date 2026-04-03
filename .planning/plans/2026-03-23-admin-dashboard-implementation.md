# Blog Admin Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a unified admin dashboard for managing Articles, Todos, and Users with a modern clean UI.

**Architecture:** 
- Reuse existing admin blueprint at `/admin`
- Add new route files for todos and users admin
- Create modern CSS stylesheet
- Build modular templates with shared base layout

**Tech Stack:** Flask, SQLAlchemy, Jinja2, modern CSS

---

## File Structure

```
app/
├── admin/
│   ├── __init__.py              # Blueprint registration (modify)
│   ├── routes.py                # Article routes (enhance)
│   ├── todo_admin.py            # Todo admin routes (new)
│   ├── user_admin.py            # User admin routes (new)
│   ├── utils.py                 # Utility functions (modify)
│   └── templates/
│       └── admin/
│           ├── base.html        # Base admin layout (new)
│           ├── dashboard.html   # Dashboard page (new)
│           ├── index.html       # Redirect to dashboard (new)
│           ├── articles/
│           │   ├── list.html    # Articles list (enhance)
│           │   ├── create.html  # Create article (enhance)
│           │   └── edit.html    # Edit article (enhance)
│           ├── todos/
│           │   ├── list.html    # Todos list (new)
│           │   ├── create.html  # Create todo (new)
│           │   └── edit.html    # Edit todo (new)
│           └── users/
│               ├── list.html    # Users list (new)
│               ├── create.html  # Create user (new)
│               ├── edit.html    # Edit user (new)
│               └── password.html # Change password (new)
app/static/css/
└── admin.css                    # Admin styles (replace existing)
```

---

## Task 1: Create Modern Admin CSS

**Files:**
- Create: `app/static/css/admin.css`

- [ ] **Step 1: Create admin.css with modern styles**

```css
/* Modern Admin Dashboard Styles */

:root {
    --bg-primary: #ffffff;
    --bg-secondary: #f8f9fa;
    --bg-sidebar: #f1f3f5;
    --text-primary: #212529;
    --text-secondary: #6c757d;
    --border-color: #dee2e6;
    --primary: #007bff;
    --success: #28a745;
    --warning: #ffc107;
    --danger: #dc3545;
    --sidebar-width: 250px;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
}

/* Layout */
.admin-layout {
    display: flex;
    min-height: 100vh;
}

/* Sidebar */
.sidebar {
    width: var(--sidebar-width);
    background: var(--bg-sidebar);
    border-right: 1px solid var(--border-color);
    padding: 1.5rem 0;
    position: fixed;
    height: 100vh;
    overflow-y: auto;
}

.sidebar-logo {
    padding: 0 1.5rem 1.5rem;
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 1rem;
}

.sidebar-logo h1 {
    font-size: 1.25rem;
    font-weight: 600;
}

.sidebar-nav {
    list-style: none;
}

.sidebar-nav li {
    margin: 0.25rem 0;
}

.sidebar-nav a {
    display: flex;
    align-items: center;
    padding: 0.75rem 1.5rem;
    color: var(--text-secondary);
    text-decoration: none;
    transition: all 0.2s;
}

.sidebar-nav a:hover {
    background: var(--bg-secondary);
    color: var(--text-primary);
}

.sidebar-nav a.active {
    background: var(--primary);
    color: white;
    border-radius: 0 8px 8px 0;
    margin-right: 0.5rem;
}

/* Main Content */
.main-content {
    flex: 1;
    margin-left: var(--sidebar-width);
    padding: 2rem;
}

/* Top Bar */
.top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border-color);
}

.breadcrumbs {
    display: flex;
    gap: 0.5rem;
    color: var(--text-secondary);
}

.breadcrumbs span {
    color: var(--text-primary);
}

.user-info {
    display: flex;
    align-items: center;
    gap: 1rem;
}

/* Cards */
.card {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: var(--bg-secondary);
    border-radius: 8px;
    padding: 1.5rem;
}

.stat-card h3 {
    font-size: 0.875rem;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
}

.stat-card .value {
    font-size: 2rem;
    font-weight: 600;
    color: var(--text-primary);
}

/* Tables */
.data-table {
    width: 100%;
    border-collapse: collapse;
    background: var(--bg-primary);
    border-radius: 8px;
    overflow: hidden;
}

.data-table th,
.data-table td {
    padding: 1rem;
    text-align: left;
    border-bottom: 1px solid var(--border-color);
}

.data-table th {
    background: var(--bg-secondary);
    font-weight: 600;
    font-size: 0.875rem;
    color: var(--text-secondary);
}

.data-table tr:hover {
    background: var(--bg-secondary);
}

/* Buttons */
.btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 6px;
    font-size: 0.875rem;
    cursor: pointer;
    text-decoration: none;
    transition: all 0.2s;
}

.btn-primary {
    background: var(--primary);
    color: white;
}

.btn-success {
    background: var(--success);
    color: white;
}

.btn-danger {
    background: var(--danger);
    color: white;
}

.btn-secondary {
    background: var(--bg-secondary);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
}

.btn:hover {
    opacity: 0.9;
    transform: translateY(-1px);
}

/* Badges */
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
}

.badge-draft {
    background: #fff3cd;
    color: #856404;
}

.badge-published {
    background: #d4edda;
    color: #155724;
}

/* Forms */
.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
}

.form-control {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    font-size: 1rem;
}

.form-control:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

/* Toolbar */
.toolbar {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}

.search-box {
    flex: 1;
    min-width: 200px;
}

.search-box input {
    width: 100%;
    padding: 0.5rem 1rem;
    border: 1px solid var(--border-color);
    border-radius: 6px;
}

/* Pagination */
.pagination {
    display: flex;
    gap: 0.5rem;
    margin-top: 1.5rem;
    justify-content: center;
}

.pagination a,
.pagination span {
    padding: 0.5rem 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    text-decoration: none;
    color: var(--text-primary);
}

.pagination a:hover {
    background: var(--bg-secondary);
}

.pagination .active {
    background: var(--primary);
    color: white;
    border-color: var(--primary);
}

/* Actions */
.actions {
    display: flex;
    gap: 0.5rem;
}

.actions .btn {
    padding: 0.35rem 0.75rem;
    font-size: 0.8rem;
}

/* Quadrant badges */
.quadrant-1 { background: #ff6b6b; color: white; }
.quadrant-2 { background: #4ecdc4; color: white; }
.quadrant-3 { background: #ffe66d; color: #333; }
.quadrant-4 { background: #95a5a6; color: white; }

/* Priority indicator */
.priority-high { color: var(--danger); font-weight: bold; }
.priority-medium { color: var(--warning); }
.priority-low { color: var(--success); }
```

---

## Task 2: Create Base Admin Template

**Files:**
- Create: `app/admin/templates/admin/base.html`

- [ ] **Step 1: Create base admin template**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Admin Dashboard{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/admin.css') }}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <div class="admin-layout">
        <!-- Sidebar -->
        <aside class="sidebar">
            <div class="sidebar-logo">
                <h1>Admin Panel</h1>
            </div>
            <ul class="sidebar-nav">
                <li>
                    <a href="{{ url_for('admin.index') }}" class="{% if request.endpoint == 'admin.index' %}active{% endif %}">
                        Dashboard
                    </a>
                </li>
                <li>
                    <a href="{{ url_for('admin.articles') }}" class="{% if request.endpoint and 'admin.article' in request.endpoint %}active{% endif %}">
                        Articles
                    </a>
                </li>
                <li>
                    <a href="{{ url_for('admin.todos') }}" class="{% if request.endpoint and 'admin.todo' in request.endpoint %}active{% endif %}">
                        Todos
                    </a>
                </li>
                <li>
                    <a href="{{ url_for('admin.users') }}" class="{% if request.endpoint and 'admin.user' in request.endpoint %}active{% endif %}">
                        Users
                    </a>
                </li>
            </ul>
        </aside>

        <!-- Main Content -->
        <main class="main-content">
            <!-- Top Bar -->
            <div class="top-bar">
                <div class="breadcrumbs">
                    <a href="{{ url_for('admin.index') }}">Dashboard</a>
                    {% block breadcrumbs %}{% endblock %}
                </div>
                <div class="user-info">
                    <span>{{ session.get('username', 'User') }}</span>
                    <a href="{{ url_for('auth.logout') }}" class="btn btn-secondary">Logout</a>
                </div>
            </div>

            <!-- Flash Messages -->
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                <div class="flash-messages">
                    {% for category, message in messages %}
                    <div class="flash flash-{{ category }}">{{ message }}</div>
                    {% endfor %}
                </div>
                {% endif %}
            {% endwith %}

            <!-- Page Content -->
            {% block content %}{% endblock %}
        </main>
    </div>

    {% block extra_js %}{% endblock %}
</body>
</html>
```

---

## Task 3: Create Dashboard Page

**Files:**
- Create: `app/admin/templates/admin/dashboard.html`
- Modify: `app/admin/__init__.py` (add index route)

- [ ] **Step 1: Create dashboard template**

```html
{% extends "admin/base.html" %}

{% block title %}Dashboard - Admin{% endblock %}

{% block breadcrumbs %}
    <span>&gt;</span>
    <span>Dashboard</span>
{% endblock %}

{% block content %}
<h2 style="margin-bottom: 1.5rem;">Dashboard</h2>

<!-- Statistics Cards -->
<div class="stats-grid">
    <div class="stat-card">
        <h3>Total Articles</h3>
        <div class="value">{{ stats.total_articles }}</div>
    </div>
    <div class="stat-card">
        <h3>Published</h3>
        <div class="value">{{ stats.published_articles }}</div>
    </div>
    <div class="stat-card">
        <h3>Total Todos</h3>
        <div class="value">{{ stats.total_todos }}</div>
    </div>
    <div class="stat-card">
        <h3>Total Users</h3>
        <div class="value">{{ stats.total_users }}</div>
    </div>
</div>

<!-- Recent Activity -->
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
    <!-- Recent Articles -->
    <div class="card">
        <h3 style="margin-bottom: 1rem;">Recent Drafts</h3>
        {% if recent_drafts %}
        <table class="data-table">
            <thead>
                <tr>
                    <th>Title</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for article in recent_drafts %}
                <tr>
                    <td>{{ article.title }}</td>
                    <td><span class="badge badge-draft">{{ article.status }}</span></td>
                    <td class="actions">
                        <a href="{{ url_for('admin.edit_article', id=article.id) }}" class="btn btn-secondary">Edit</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p style="color: var(--text-secondary);">No draft articles.</p>
        {% endif %}
    </div>

    <!-- Recent Todos -->
    <div class="card">
        <h3 style="margin-bottom: 1rem;">Recent Todos</h3>
        {% if recent_todos %}
        <table class="data-table">
            <thead>
                <tr>
                    <th>Title</th>
                    <th>Quadrant</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for todo in recent_todos %}
                <tr>
                    <td>{{ todo.title }}</td>
                    <td><span class="badge quadrant-{{ todo.quadrant }}">Q{{ todo.quadrant }}</span></td>
                    <td class="actions">
                        <a href="{{ url_for('admin.edit_todo', id=todo.id) }}" class="btn btn-secondary">Edit</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p style="color: var(--text-secondary);">No todos.</p>
        {% endif %}
    </div>
</div>

<div style="margin-top: 1.5rem;">
    <a href="{{ url_for('admin.articles') }}" class="btn btn-primary">Manage Articles</a>
    <a href="{{ url_for('admin.todos') }}" class="btn btn-primary">Manage Todos</a>
    <a href="{{ url_for('admin.users') }}" class="btn btn-primary">Manage Users</a>
</div>
{% endblock %}
```

- [ ] **Step 2: Add dashboard route to __init__.py**

```python
# Add to app/admin/__init__.py after existing imports:

@bp.route("/")
@bp.route("/index")
@login_required
def index():
    """Dashboard page with statistics."""
    from ..models import Article, Todo, User
    
    stats = {
        'total_articles': Article.query.count(),
        'published_articles': Article.query.filter_by(status='published').count(),
        'total_todos': Todo.query.count(),
        'total_users': User.query.count(),
    }
    
    recent_drafts = Article.query.filter_by(status='draft').order_by(Article.updated_at.desc()).limit(5).all()
    recent_todos = Todo.query.order_by(Todo.updated_at.desc()).limit(5).all()
    
    return render_template("dashboard.html", stats=stats, recent_drafts=recent_drafts, recent_todos=recent_todos)
```

---

## Task 4: Create Article Admin Routes

**Files:**
- Modify: `app/admin/routes.py` (enhance with search/pagination)
- Create: `app/admin/templates/admin/articles/list.html`
- Create: `app/admin/templates/admin/articles/create.html`
- Create: `app/admin/templates/admin/articles/edit.html`

- [ ] **Step 1: Enhance article routes with search/pagination**

```python
# Add to app/admin/routes.py

@bp.route("/articles")
@login_required
def articles():
    """List articles with search/filter/sort/pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    search = request.args.get('search', '')
    status = request.args.get('status', 'all')
    sort_by = request.args.get('sort', 'updated_at')
    sort_order = request.args.get('order', 'desc')
    
    query = Article.query
    
    # Search
    if search:
        query = query.filter(
            db.or_(
                Article.title.contains(search),
                Article.content.contains(search)
            )
        )
    
    # Status filter
    if status != 'all':
        query = query.filter_by(status=status)
    
    # Sort
    sort_column = getattr(Article, sort_by, Article.updated_at)
    if sort_order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template(
        "articles/list.html",
        articles=pagination.items,
        pagination=pagination,
        search=search,
        status=status,
        sort_by=sort_by,
        sort_order=sort_order
    )
```

- [ ] **Step 2: Create articles list template**

```html
{% extends "admin/base.html" %}

{% block title %}Articles - Admin{% endblock %}

{% block breadcrumbs %}
    <span>&gt;</span>
    <span>Articles</span>
{% endblock %}

{% block content %}
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
    <h2>Articles</h2>
    <a href="{{ url_for('admin.create_article') }}" class="btn btn-primary">New Article</a>
</div>

<!-- Toolbar -->
<form method="GET" class="toolbar">
    <div class="search-box">
        <input type="text" name="search" placeholder="Search title or content..." value="{{ search }}">
    </div>
    <select name="status" class="form-control" style="width: auto;">
        <option value="all">All Status</option>
        <option value="published" {% if status == 'published' %}selected{% endif %}>Published</option>
        <option value="draft" {% if status == 'draft' %}selected{% endif %}>Draft</option>
    </select>
    <select name="sort" class="form-control" style="width: auto;">
        <option value="updated_at" {% if sort_by == 'updated_at' %}selected{% endif %}>Updated</option>
        <option value="created_at" {% if sort_by == 'created_at' %}selected{% endif %}>Created</option>
        <option value="title" {% if sort_by == 'title' %}selected{% endif %}>Title</option>
    </select>
    <button type="submit" class="btn btn-secondary">Filter</button>
    <a href="{{ url_for('admin.articles') }}" class="btn btn-secondary">Reset</a>
</form>

<!-- Articles Table -->
<table class="data-table">
    <thead>
        <tr>
            <th>Title</th>
            <th>Status</th>
            <th>Created</th>
            <th>Updated</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {% for article in articles %}
        <tr>
            <td><a href="{{ url_for('admin.edit_article', id=article.id) }}">{{ article.title }}</a></td>
            <td><span class="badge badge-{{ article.status }}">{{ article.status }}</span></td>
            <td>{{ article.created_at.strftime('%Y-%m-%d') }}</td>
            <td>{{ article.updated_at.strftime('%Y-%m-%d') }}</td>
            <td class="actions">
                <a href="{{ url_for('admin.edit_article', id=article.id) }}" class="btn btn-secondary">Edit</a>
                {% if article.status == 'draft' %}
                <form method="POST" action="{{ url_for('admin.publish_article', id=article.id) }}" style="display: inline;">
                    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
                    <button type="submit" class="btn btn-success">Publish</button>
                </form>
                {% else %}
                <form method="POST" action="{{ url_for('admin.unpublish_article', id=article.id) }}" style="display: inline;">
                    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
                    <button type="submit" class="btn btn-secondary">Unpublish</button>
                </form>
                {% endif %}
                <form method="POST" action="{{ url_for('admin.delete_article', id=article.id) }}" style="display: inline;" onsubmit="return confirm('Delete this article?');">
                    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
                    <button type="submit" class="btn btn-danger">Delete</button>
                </form>
            </td>
        </tr>
        {% else %}
        <tr>
            <td colspan="5" style="text-align: center; color: var(--text-secondary);">No articles found.</td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<!-- Pagination -->
{% if pagination.pages > 1 %}
<div class="pagination">
    {% if pagination.has_prev %}
    <a href="{{ url_for('admin.articles', page=pagination.prev_num, search=search, status=status, sort=sort_by) }}">&laquo; Prev</a>
    {% endif %}
    {% for p in range(1, pagination.pages + 1) %}
    <a href="{{ url_for('admin.articles', page=p, search=search, status=status, sort=sort_by) }}" class="{% if p == pagination.page %}active{% endif %}">{{ p }}</a>
    {% endfor %}
    {% if pagination.has_next %}
    <a href="{{ url_for('admin.articles', page=pagination.next_num, search=search, status=status, sort=sort_by) }}">Next &raquo;</a>
    {% endif %}
</div>
{% endif %}
{% endblock %}
```

- [ ] **Step 3: Update article create/edit routes to use new templates**

```python
# Update create route to use new template path
@bp.route("/articles/new", methods=["GET", "POST"])
@login_required
@csrf_protected
def create_article():
    """Create a new article."""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        status = request.form.get("status", "draft")

        if not title:
            flash("Title is required", "error")
            return render_template("articles/create.html", form_data=request.form)

        slug = generate_slug(title)

        article = Article(
            title=title,
            content=content,
            slug=slug,
            status=status if status in ("draft", "published") else "draft",
        )
        db.session.add(article)
        db.session.commit()

        get_db_articles.cache_clear()
        get_db_article_by_slug.cache_clear()

        flash(f'Article "{title}" created successfully', "success")
        return redirect(url_for("admin.articles"))

    return render_template("articles/create.html")

# Update edit route to use new template path
@bp.route("/articles/<int:id>/edit", methods=["GET", "POST"])
@login_required
@csrf_protected
def edit_article(id):
    """Edit an existing article."""
    article = Article.query.get_or_404(id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        status = request.form.get("status", "draft")

        if not title:
            flash("Title is required", "error")
            return render_template("articles/edit.html", article=article, form_data=request.form)

        if title != article.title:
            article.slug = generate_slug(title)

        article.title = title
        article.content = content
        article.status = status if status in ("draft", "published") else "draft"

        db.session.commit()

        get_db_articles.cache_clear()
        get_db_article_by_slug.cache_clear()

        flash(f'Article "{title}" updated successfully', "success")
        return redirect(url_for("admin.articles"))

    return render_template("articles/edit.html", article=article)
```

---

## Task 5: Create Todo Admin Routes

**Files:**
- Create: `app/admin/todo_admin.py`
- Create: `app/admin/templates/admin/todos/list.html`
- Create: `app/admin/templates/admin/todos/create.html`
- Create: `app/admin/templates/admin/todos/edit.html`

- [ ] **Step 1: Create todo_admin.py**

```python
"""Todo admin routes for managing all todos."""

from flask import render_template, redirect, url_for, flash, request
from . import bp
from ..auth.utils import login_required
from ..utils import csrf_protected
from ..extensions import db
from ..models import Todo


@bp.route("/todos")
@login_required
def todos():
    """List all todos with search/filter/sort/pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    search = request.args.get('search', '')
    quadrant = request.args.get('quadrant', 'all')
    priority = request.args.get('priority', 'all')
    
    query = Todo.query
    
    # Search
    if search:
        query = query.filter(Todo.title.contains(search))
    
    # Quadrant filter
    if quadrant != 'all':
        query = query.filter_by(quadrant=int(quadrant))
    
    # Priority filter
    if priority != 'all':
        query = query.filter_by(priority=int(priority))
    
    # Sort by updated
    query = query.order_by(Todo.updated_at.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template(
        "todos/list.html",
        todos=pagination.items,
        pagination=pagination,
        search=search,
        quadrant=quadrant,
        priority=priority
    )


@bp.route("/todos/new", methods=["GET", "POST"])
@login_required
@csrf_protected
def create_todo():
    """Create a new todo."""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        quadrant = request.form.get("quadrant", 2, type=int)
        priority = request.form.get("priority", 3, type=int)
        
        if not title:
            flash("Title is required", "error")
            return render_template("todos/create.html", form_data=request.form)
        
        todo = Todo(
            user_id=session.get('user_id'),
            title=title,
            description=description,
            quadrant=quadrant,
            priority=priority
        )
        db.session.add(todo)
        db.session.commit()
        
        flash(f'Todo "{title}" created successfully', "success")
        return redirect(url_for("admin.todos"))
    
    return render_template("todos/create.html")


@bp.route("/todos/<int:id>/edit", methods=["GET", "POST"])
@login_required
@csrf_protected
def edit_todo(id):
    """Edit an existing todo."""
    todo = Todo.query.get_or_404(id)
    
    if request.method == "POST":
        todo.title = request.form.get("title", "").strip()
        todo.description = request.form.get("description", "").strip()
        todo.quadrant = request.form.get("quadrant", 2, type=int)
        todo.priority = request.form.get("priority", 3, type=int)
        todo.completed = 'completed' in request.form
        
        db.session.commit()
        
        flash(f'Todo "{todo.title}" updated successfully', "success")
        return redirect(url_for("admin.todos"))
    
    return render_template("todos/edit.html", todo=todo)


@bp.route("/todos/<int:id>/delete", methods=["POST"])
@login_required
@csrf_protected
def delete_todo(id):
    """Delete a todo."""
    todo = Todo.query.get_or_404(id)
    title = todo.title
    
    db.session.delete(todo)
    db.session.commit()
    
    flash(f'Todo "{title}" deleted successfully', "success")
    return redirect(url_for("admin.todos"))


@bp.route("/todos/<int:id>/complete", methods=["POST"])
@login_required
@csrf_protected
def complete_todo(id):
    """Toggle todo completion."""
    todo = Todo.query.get_or_404(id)
    todo.completed = not todo.completed
    db.session.commit()
    
    flash(f'Todo marked as {"completed" if todo.completed else "pending"}', "success")
    return redirect(url_for("admin.todos"))


@bp.route("/todos/<int:id>/move", methods=["POST"])
@login_required
@csrf_protected
def move_todo(id):
    """Move todo to another quadrant."""
    todo = Todo.query.get_or_404(id)
    quadrant = request.form.get("quadrant", type=int)
    
    if quadrant in (1, 2, 3, 4):
        todo.quadrant = quadrant
        db.session.commit()
        flash(f'Todo moved to Quadrant {quadrant}', "success")
    
    return redirect(url_for("admin.todos"))
```

- [ ] **Step 2: Create todos list template**

```html
{% extends "admin/base.html" %}

{% block title %}Todos - Admin{% endblock %}

{% block breadcrumbs %}
    <span>&gt;</span>
    <span>Todos</span>
{% endblock %}

{% block content %}
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
    <h2>Todos</h2>
    <a href="{{ url_for('admin.create_todo') }}" class="btn btn-primary">New Todo</a>
</div>

<!-- Toolbar -->
<form method="GET" class="toolbar">
    <div class="search-box">
        <input type="text" name="search" placeholder="Search title..." value="{{ search }}">
    </div>
    <select name="quadrant" class="form-control" style="width: auto;">
        <option value="all">All Quadrants</option>
        <option value="1" {% if quadrant == '1' %}selected{% endif %}>Q1 - Urgent & Important</option>
        <option value="2" {% if quadrant == '2' %}selected{% endif %}>Q2 - Important</option>
        <option value="3" {% if quadrant == '3' %}selected{% endif %}>Q3 - Urgent</option>
        <option value="4" {% if quadrant == '4' %}selected{% endif %}>Q4 - Neither</option>
    </select>
    <select name="priority" class="form-control" style="width: auto;">
        <option value="all">All Priorities</option>
        {% for p in range(1, 6) %}
        <option value="{{ p }}" {% if priority == p|string %}selected{% endif %}>Priority {{ p }}</option>
        {% endfor %}
    </select>
    <button type="submit" class="btn btn-secondary">Filter</button>
    <a href="{{ url_for('admin.todos') }}" class="btn btn-secondary">Reset</a>
</form>

<!-- Todos Table -->
<table class="data-table">
    <thead>
        <tr>
            <th>Title</th>
            <th>Quadrant</th>
            <th>Priority</th>
            <th>Status</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {% for todo in todos %}
        <tr>
            <td>{{ todo.title }}</td>
            <td><span class="badge quadrant-{{ todo.quadrant }}">Q{{ todo.quadrant }}</span></td>
            <td class="priority-{% if todo.priority <= 2 %}high{% elif todo.priority == 3 %}medium{% else %}low{% endif %}">
                {{ todo.priority }}
            </td>
            <td>
                {% if todo.completed %}
                <span class="badge badge-published">Completed</span>
                {% else %}
                <span class="badge badge-draft">Pending</span>
                {% endif %}
            </td>
            <td class="actions">
                <a href="{{ url_for('admin.edit_todo', id=todo.id) }}" class="btn btn-secondary">Edit</a>
                <form method="POST" action="{{ url_for('admin.complete_todo', id=todo.id) }}" style="display: inline;">
                    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
                    <button type="submit" class="btn btn-success">{{ 'Uncomplete' if todo.completed else 'Complete' }}</button>
                </form>
                <form method="POST" action="{{ url_for('admin.delete_todo', id=todo.id) }}" style="display: inline;" onsubmit="return confirm('Delete this todo?');">
                    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
                    <button type="submit" class="btn btn-danger">Delete</button>
                </form>
            </td>
        </tr>
        {% else %}
        <tr>
            <td colspan="5" style="text-align: center; color: var(--text-secondary);">No todos found.</td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<!-- Pagination -->
{% if pagination.pages > 1 %}
<div class="pagination">
    {% if pagination.has_prev %}
    <a href="{{ url_for('admin.todos', page=pagination.prev_num, search=search, quadrant=quadrant, priority=priority) }}">&laquo; Prev</a>
    {% endif %}
    {% for p in range(1, pagination.pages + 1) %}
    <a href="{{ url_for('admin.todos', page=p, search=search, quadrant=quadrant, priority=priority) }}" class="{% if p == pagination.page %}active{% endif %}">{{ p }}</a>
    {% endfor %}
    {% if pagination.has_next %}
    <a href="{{ url_for('admin.todos', page=pagination.next_num, search=search, quadrant=quadrant, priority=priority) }}">Next &raquo;</a>
    {% endif %}
</div>
{% endif %}
{% endblock %}
```

---

## Task 6: Create User Admin Routes

**Files:**
- Create: `app/admin/user_admin.py`
- Create: `app/admin/templates/admin/users/list.html`
- Create: `app/admin/templates/admin/users/create.html`
- Create: `app/admin/templates/admin/users/edit.html`
- Create: `app/admin/templates/admin/users/password.html`

- [ ] **Step 1: Create user_admin.py**

```python
"""User admin routes for managing users."""

from flask import render_template, redirect, url_for, flash, request, session
from . import bp
from ..auth.utils import login_required
from ..auth.utils import hash_password, check_password
from ..utils import csrf_protected
from ..extensions import db
from ..models import User


@bp.route("/users")
@login_required
def users():
    """List all users with search/sort/pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    search = request.args.get('search', '')
    sort_by = request.args.get('sort', 'created_at')
    
    query = User.query
    
    # Search
    if search:
        query = query.filter(User.username.contains(search))
    
    # Sort
    sort_column = getattr(User, sort_by, User.created_at)
    query = query.order_by(sort_column.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template(
        "users/list.html",
        users=pagination.items,
        pagination=pagination,
        search=search,
        sort_by=sort_by
    )


@bp.route("/users/new", methods=["GET", "POST"])
@login_required
def create_user():
    """Create a new user."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        if not username or not password:
            flash("Username and password are required", "error")
            return render_template("users/create.html", form_data=request.form)
        
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template("users/create.html", form_data=request.form)
        
        if User.query.filter_by(username=username).first():
            flash("Username already exists", "error")
            return render_template("users/create.html", form_data=request.form)
        
        user = User(username=username, password_hash=hash_password(password))
        db.session.add(user)
        db.session.commit()
        
        flash(f'User "{username}" created successfully', "success")
        return redirect(url_for("admin.users"))
    
    return render_template("users/create.html")


@bp.route("/users/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_user(id):
    """Edit an existing user."""
    user = User.query.get_or_404(id)
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        
        if not username:
            flash("Username is required", "error")
            return render_template("users/edit.html", user=user, form_data=request.form)
        
        # Check if username is taken by another user
        existing = User.query.filter(User.username == username, User.id != id).first()
        if existing:
            flash("Username already exists", "error")
            return render_template("users/edit.html", user=user, form_data=request.form)
        
        user.username = username
        db.session.commit()
        
        flash(f'User "{username}" updated successfully', "success")
        return redirect(url_for("admin.users"))
    
    return render_template("users/edit.html", user=user)


@bp.route("/users/<int:id>/password", methods=["GET", "POST"])
@login_required
def change_password(id):
    """Change user password."""
    user = User.query.get_or_404(id)
    
    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        # Verify current user or admin
        if not check_password(user.password_hash, current_password):
            flash("Current password is incorrect", "error")
            return render_template("users/password.html", user=user)
        
        if new_password != confirm_password:
            flash("New passwords do not match", "error")
            return render_template("users/password.html", user=user)
        
        if len(new_password) < 6:
            flash("Password must be at least 6 characters", "error")
            return render_template("users/password.html", user=user)
        
        user.password_hash = hash_password(new_password)
        db.session.commit()
        
        flash("Password changed successfully", "success")
        return redirect(url_for("admin.users"))
    
    return render_template("users/password.html", user=user)


@bp.route("/users/<int:id>/delete", methods=["POST"])
@login_required
@csrf_protected
def delete_user(id):
    """Delete a user."""
    user = User.query.get_or_404(id)
    
    # Prevent self-deletion
    if user.id == session.get('user_id'):
        flash("You cannot delete yourself", "error")
        return redirect(url_for("admin.users"))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User "{username}" deleted successfully', "success")
    return redirect(url_for("admin.users"))
```

- [ ] **Step 2: Create users list template**

```html
{% extends "admin/base.html" %}

{% block title %}Users - Admin{% endblock %}

{% block breadcrumbs %}
    <span>&gt;</span>
    <span>Users</span>
{% endblock %}

{% block content %}
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
    <h2>Users</h2>
    <a href="{{ url_for('admin.create_user') }}" class="btn btn-primary">New User</a>
</div>

<!-- Toolbar -->
<form method="GET" class="toolbar">
    <div class="search-box">
        <input type="text" name="search" placeholder="Search username..." value="{{ search }}">
    </div>
    <select name="sort" class="form-control" style="width: auto;">
        <option value="created_at" {% if sort_by == 'created_at' %}selected{% endif %}>Joined Date</option>
        <option value="username" {% if sort_by == 'username' %}selected{% endif %}>Username</option>
    </select>
    <button type="submit" class="btn btn-secondary">Filter</button>
    <a href="{{ url_for('admin.users') }}" class="btn btn-secondary">Reset</a>
</form>

<!-- Users Table -->
<table class="data-table">
    <thead>
        <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Joined</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {% for user in users %}
        <tr>
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.created_at.strftime('%Y-%m-%d') }}</td>
            <td class="actions">
                <a href="{{ url_for('admin.edit_user', id=user.id) }}" class="btn btn-secondary">Edit</a>
                <a href="{{ url_for('admin.change_password', id=user.id) }}" class="btn btn-secondary">Password</a>
                {% if user.id != session.get('user_id') %}
                <form method="POST" action="{{ url_for('admin.delete_user', id=user.id) }}" style="display: inline;" onsubmit="return confirm('Delete this user?');">
                    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
                    <button type="submit" class="btn btn-danger">Delete</button>
                </form>
                {% endif %}
            </td>
        </tr>
        {% else %}
        <tr>
            <td colspan="4" style="text-align: center; color: var(--text-secondary);">No users found.</td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<!-- Pagination -->
{% if pagination.pages > 1 %}
<div class="pagination">
    {% if pagination.has_prev %}
    <a href="{{ url_for('admin.users', page=pagination.prev_num, search=search, sort=sort_by) }}">&laquo; Prev</a>
    {% endif %}
    {% for p in range(1, pagination.pages + 1) %}
    <a href="{{ url_for('admin.users', page=p, search=search, sort=sort_by) }}" class="{% if p == pagination.page %}active{% endif %}">{{ p }}</a>
    {% endfor %}
    {% if pagination.has_next %}
    <a href="{{ url_for('admin.users', page=pagination.next_num, search=search, sort=sort_by) }}">Next &raquo;</a>
    {% endif %}
</div>
{% endif %}
{% endblock %}
```

---

## Task 7: Update Blueprint Registration

**Files:**
- Modify: `app/admin/__init__.py`

- [ ] **Step 1: Update __init__.py to import new routes**

```python
"""Admin blueprint."""

from flask import Blueprint

bp = Blueprint("admin", __name__, url_prefix="/admin", template_folder="templates")

from . import routes
from . import todo_admin
from . import user_admin
```

---

## Task 8: Create Form Templates

**Files:**
- Create: `app/admin/templates/admin/articles/create.html`
- Create: `app/admin/templates/admin/articles/edit.html`
- Create: `app/admin/templates/admin/todos/create.html`
- Create: `app/admin/templates/admin/todos/edit.html`
- Create: `app/admin/templates/admin/users/create.html`
- Create: `app/admin/templates/admin/users/edit.html`
- Create: `app/admin/templates/admin/users/password.html`

- [ ] **Step 1: Create article create template (simplified)**

```html
{% extends "admin/base.html" %}

{% block title %}New Article - Admin{% endblock %}

{% block breadcrumbs %}
    <span>&gt;</span>
    <span>Articles</span>
    <span>&gt;</span>
    <span>New</span>
{% endblock %}

{% block content %}
<h2 style="margin-bottom: 1.5rem;">New Article</h2>

<form method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    
    <div class="form-group">
        <label>Title</label>
        <input type="text" name="title" class="form-control" required value="{{ form_data.title if form_data else '' }}">
    </div>
    
    <div class="form-group">
        <label>Content (Markdown)</label>
        <textarea name="content" class="form-control" rows="15">{{ form_data.content if form_data else '' }}</textarea>
    </div>
    
    <div class="form-group">
        <label>Status</label>
        <select name="status" class="form-control" style="width: auto;">
            <option value="draft">Draft</option>
            <option value="published">Published</option>
        </select>
    </div>
    
    <div style="display: flex; gap: 1rem;">
        <button type="submit" class="btn btn-primary">Create Article</button>
        <a href="{{ url_for('admin.articles') }}" class="btn btn-secondary">Cancel</a>
    </div>
</form>
{% endblock %}
```

- [ ] **Step 2: Create article edit template**

```html
{% extends "admin/base.html" %}

{% block title %}Edit Article - Admin{% endblock %}

{% block breadcrumbs %}
    <span>&gt;</span>
    <span>Articles</span>
    <span>&gt;</span>
    <span>Edit</span>
{% endblock %}

{% block content %}
<h2 style="margin-bottom: 1.5rem;">Edit Article</h2>

<form method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    
    <div class="form-group">
        <label>Title</label>
        <input type="text" name="title" class="form-control" required value="{{ article.title }}">
    </div>
    
    <div class="form-group">
        <label>Content (Markdown)</label>
        <textarea name="content" class="form-control" rows="15">{{ article.content }}</textarea>
    </div>
    
    <div class="form-group">
        <label>Status</label>
        <select name="status" class="form-control" style="width: auto;">
            <option value="draft" {% if article.status == 'draft' %}selected{% endif %}>Draft</option>
            <option value="published" {% if article.status == 'published' %}selected{% endif %}>Published</option>
        </select>
    </div>
    
    <div style="display: flex; gap: 1rem;">
        <button type="submit" class="btn btn-primary">Save Changes</button>
        <a href="{{ url_for('admin.articles') }}" class="btn btn-secondary">Cancel</a>
    </div>
</form>
{% endblock %}
```

(Remaining form templates follow similar patterns - create for todos and users)

---

## Task 9: Test the Implementation

- [ ] **Step 1: Run database migrations if needed**

```bash
flask --app app db upgrade
```

- [ ] **Step 2: Start development server**

```bash
flask --app app run --debug
```

- [ ] **Step 3: Test access to admin dashboard**

1. Navigate to `/admin`
2. Verify dashboard loads with statistics
3. Navigate to Articles, Todos, Users sections
4. Test CRUD operations

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Admin CSS | `app/static/css/admin.css` |
| 2 | Base Template | `app/admin/templates/admin/base.html` |
| 3 | Dashboard | `app/admin/templates/admin/dashboard.html`, `__init__.py` |
| 4 | Article Admin | `app/admin/routes.py` (enhanced), templates |
| 5 | Todo Admin | `app/admin/todo_admin.py`, templates |
| 6 | User Admin | `app/admin/user_admin.py`, templates |
| 7 | Blueprint Update | `app/admin/__init__.py` |
| 8 | Form Templates | Various create/edit templates |
| 9 | Testing | Manual verification |

---

_Plan created: 2026-03-23_
_Version: 1.0_
