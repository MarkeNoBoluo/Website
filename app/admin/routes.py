"""Admin routes for article CRUD."""

from flask import render_template, redirect, url_for, flash, request
from sqlalchemy.exc import IntegrityError
from . import bp
from ..auth.utils import login_required
from ..utils import csrf_protected
from ..extensions import db
from ..models import Article
from ..markdown import render_markdown
from .utils import generate_slug


@bp.route("/preview", methods=["POST"])
@login_required
def preview():
    """Render markdown preview for admin editor."""
    content = request.form.get("content", "")
    MAX_CONTENT_SIZE = 1 * 1024 * 1024
    if len(content.encode("utf-8")) > MAX_CONTENT_SIZE:
        return "Content too large (max 1MB)", 413
    if content:
        html = render_markdown(content)
        return html
    return '<p class="placeholder-text">Start typing to see preview...</p>'


@bp.route("/articles")
@login_required
def articles():
    """List articles with search/filter/sort/pagination."""
    page = request.args.get("page", 1, type=int)
    per_page = 10

    search = request.args.get("search", "")
    status = request.args.get("status", "all")
    sort_by = request.args.get("sort", "updated_at")
    sort_order = request.args.get("order", "desc")

    query = Article.query

    if search:
        query = query.filter(
            db.or_(Article.title.contains(search), Article.content.contains(search))
        )

    if status != "all":
        query = query.filter_by(status=status)

    sort_column = getattr(Article, sort_by, Article.updated_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        "admin/articles/list.html",
        articles=pagination.items,
        pagination=pagination,
        search=search,
        status=status,
        sort_by=sort_by,
        sort_order=sort_order,
    )


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
            flash("标题不能为空", "error")
            return render_template("admin/articles/create.html", form_data=request.form)

        slug = generate_slug(title)

        article = Article(
            title=title,
            content=content,
            slug=slug,
            status=status if status in ("draft", "published") else "draft",
        )

        max_retries = 5
        for attempt in range(max_retries):
            try:
                db.session.add(article)
                db.session.commit()
                break
            except IntegrityError:
                db.session.rollback()
                if attempt == max_retries - 1:
                    flash("文章创建失败（slug 冲突）", "error")
                    return redirect(url_for("admin.articles"))
                article.slug = generate_slug(title, suffix=attempt + 1)

        flash(f"文章《{title}》创建成功", "success")
        return redirect(url_for("admin.articles"))

    return render_template("admin/articles/create.html")


@bp.route("/articles/import", methods=["GET", "POST"])
@login_required
@csrf_protected
def import_articles():
    """Bulk import Markdown files as published articles."""
    if request.method == "POST":
        files = request.files.getlist("files")
        success, skipped = [], []
        used_slugs = set()
        MAX_FILE_SIZE = 512 * 1024  # 512 KB

        for f in files:
            filename = f.filename or ""
            if not filename.lower().endswith(".md"):
                skipped.append(f"{filename}（非 .md 文件）")
                continue
            try:
                f.seek(0, 2)
                size = f.tell()
                f.seek(0)
                if size > MAX_FILE_SIZE:
                    skipped.append(f"{filename}（文件超过 512KB）")
                    continue
                content = f.read(MAX_FILE_SIZE).decode("utf-8").strip()
            except UnicodeDecodeError:
                skipped.append(f"{filename}（编码错误）")
                continue
            if not content:
                skipped.append(f"{filename}（文件为空）")
                continue

            title = filename[:-3].strip() or filename
            slug = generate_slug(title)
            base_slug = slug
            counter = 1
            while slug in used_slugs:
                slug = f"{base_slug}-{counter}"
                counter += 1
            used_slugs.add(slug)

            article = Article(
                title=title,
                content=content,
                slug=slug,
                status="published",
            )

            max_retries = 5
            for attempt in range(max_retries):
                try:
                    db.session.add(article)
                    db.session.commit()
                    success.append(title)
                    break
                except IntegrityError:
                    db.session.rollback()
                    if attempt == max_retries - 1:
                        skipped.append(f"{filename}（slug 冲突）")
                    else:
                        article.slug = generate_slug(title, suffix=attempt + 1)
                        used_slugs.add(article.slug)

        if success:
            flash(
                f"成功导入 {len(success)} 篇：{'、'.join(success[:3])}{'...' if len(success) > 3 else ''}",
                "success",
            )
        if skipped:
            flash(f"跳过 {len(skipped)} 个：{'、'.join(skipped)}", "warning")
        if not success and not skipped:
            flash("未选择任何文件", "error")

        return redirect(url_for("admin.articles"))

    return render_template("admin/articles/import.html")


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
            flash("标题不能为空", "error")
            return render_template(
                "admin/articles/edit.html", article=article, form_data=request.form
            )

        if title != article.title:
            article.slug = generate_slug(title)

        article.title = title
        article.content = content
        article.status = status if status in ("draft", "published") else "draft"

        max_retries = 5
        for attempt in range(max_retries):
            try:
                db.session.commit()
                break
            except IntegrityError:
                db.session.rollback()
                if attempt == max_retries - 1:
                    flash("文章更新失败（slug 冲突）", "error")
                    return redirect(url_for("admin.articles"))
                article.slug = generate_slug(title, suffix=attempt + 1)

        flash(f"文章《{title}》更新成功", "success")
        return redirect(url_for("admin.articles"))

    return render_template("admin/articles/edit.html", article=article)


@bp.route("/articles/<int:id>/delete", methods=["POST"])
@login_required
@csrf_protected
def delete_article(id):
    """Delete an article."""
    article = Article.query.get_or_404(id)
    title = article.title

    db.session.delete(article)
    db.session.commit()

    flash(f"文章《{title}》已删除", "success")
    return redirect(url_for("admin.articles"))


@bp.route("/articles/<int:id>/publish", methods=["POST"])
@login_required
@csrf_protected
def publish_article(id):
    """Publish an article (set status to published)."""
    article = Article.query.get_or_404(id)
    article.status = "published"
    db.session.commit()

    flash(f"文章《{article.title}》已发布", "success")
    return redirect(url_for("admin.articles"))


@bp.route("/articles/<int:id>/unpublish", methods=["POST"])
@login_required
@csrf_protected
def unpublish_article(id):
    """Unpublish an article (set status to draft)."""
    article = Article.query.get_or_404(id)
    article.status = "draft"
    db.session.commit()

    flash(f"文章《{article.title}》已下线", "success")
    return redirect(url_for("admin.articles"))


@bp.route("/articles/<int:id>/toggle-status", methods=["POST"])
@login_required
@csrf_protected
def toggle_status(id):
    """Toggle article status between draft and published."""
    article = Article.query.get_or_404(id)

    article.status = "published" if article.status == "draft" else "draft"
    db.session.commit()

    flash(f"文章状态已切换为「{article.status}」", "success")
    return redirect(url_for("admin.articles"))
