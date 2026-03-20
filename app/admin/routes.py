"""Admin routes for article CRUD."""

from flask import render_template, redirect, url_for, flash, request, abort
from . import bp
from ..auth.utils import login_required
from ..utils import csrf_protected
from ..extensions import db
from ..models import Article
from ..markdown import render_markdown
from .utils import generate_slug
from ..blog.utils import get_db_articles, get_db_article_by_slug


@bp.route("/preview", methods=["POST"])
@login_required
def preview():
    """Render markdown preview for admin editor."""
    content = request.form.get("content", "")
    if content:
        html = render_markdown(content)
        return html
    return '<p class="placeholder-text">Start typing to see preview...</p>'


@bp.route("/articles")
@login_required
def list():
    """List all articles (admin view - shows all statuses)."""
    status_filter = request.args.get("status", "all")
    if status_filter == "all":
        articles = Article.query.order_by(Article.updated_at.desc()).all()
    else:
        articles = (
            Article.query.filter_by(status=status_filter)
            .order_by(Article.updated_at.desc())
            .all()
        )
    return render_template("list.html", articles=articles, status_filter=status_filter)


@bp.route("/articles/new", methods=["GET", "POST"])
@login_required
@csrf_protected
def create():
    """Create a new article."""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        status = request.form.get("status", "draft")

        if not title:
            flash("Title is required", "error")
            return render_template("create.html", form_data=request.form)

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
        return redirect(url_for("admin.list"))

    return render_template("create.html")


@bp.route("/articles/<int:id>/edit", methods=["GET", "POST"])
@login_required
@csrf_protected
def edit(id):
    """Edit an existing article."""
    article = Article.query.get_or_404(id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        status = request.form.get("status", "draft")

        if not title:
            flash("Title is required", "error")
            return render_template("edit.html", article=article, form_data=request.form)

        # Regenerate slug if title changed
        if title != article.title:
            article.slug = generate_slug(title)

        article.title = title
        article.content = content
        article.status = status if status in ("draft", "published") else "draft"

        db.session.commit()

        get_db_articles.cache_clear()
        get_db_article_by_slug.cache_clear()

        flash(f'Article "{title}" updated successfully', "success")
        return redirect(url_for("admin.list"))

    return render_template("edit.html", article=article)


@bp.route("/articles/<int:id>/delete", methods=["POST"])
@login_required
@csrf_protected
def delete(id):
    """Delete an article."""
    article = Article.query.get_or_404(id)
    title = article.title

    db.session.delete(article)
    db.session.commit()

    get_db_articles.cache_clear()
    get_db_article_by_slug.cache_clear()

    flash(f'Article "{title}" deleted successfully', "success")
    return redirect(url_for("admin.list"))


@bp.route("/articles/<int:id>/publish", methods=["POST"])
@login_required
@csrf_protected
def publish(id):
    """Publish an article (set status to published)."""
    article = Article.query.get_or_404(id)
    article.status = "published"
    db.session.commit()

    get_db_articles.cache_clear()
    get_db_article_by_slug.cache_clear()

    flash(f'Article "{article.title}" published', "success")
    return redirect(url_for("admin.list"))


@bp.route("/articles/<int:id>/unpublish", methods=["POST"])
@login_required
@csrf_protected
def unpublish(id):
    """Unpublish an article (set status to draft)."""
    article = Article.query.get_or_404(id)
    article.status = "draft"
    db.session.commit()

    get_db_articles.cache_clear()
    get_db_article_by_slug.cache_clear()

    flash(f'Article "{article.title}" unpublished', "success")
    return redirect(url_for("admin.list"))


@bp.route("/articles/<int:id>/toggle-status", methods=["POST"])
@login_required
@csrf_protected
def toggle_status(id):
    """Toggle article status between draft and published."""
    article = Article.query.get_or_404(id)

    article.status = "published" if article.status == "draft" else "draft"
    db.session.commit()

    get_db_articles.cache_clear()
    get_db_article_by_slug.cache_clear()

    flash(f'Article status changed to "{article.status}"', "success")
    return redirect(url_for("admin.list"))
