"""Admin blueprint."""

from flask import Blueprint, render_template

from ..auth.utils import login_required

bp = Blueprint(
    "admin", __name__, url_prefix="/admin", template_folder="templates"
)


@bp.route("/")
@bp.route("/index")
@login_required
def index():
    """Dashboard page with statistics."""
    from ..models import Article, Todo, User

    stats = {
        "total_articles": Article.query.count(),
        "published_articles": Article.query.filter_by(status="published").count(),
        "total_todos": Todo.query.count(),
        "total_users": User.query.count(),
    }

    recent_drafts = (
        Article.query.filter_by(status="draft")
        .order_by(Article.updated_at.desc())
        .limit(5)
        .all()
    )
    recent_todos = Todo.query.order_by(Todo.updated_at.desc()).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_drafts=recent_drafts,
        recent_todos=recent_todos,
    )


from . import routes
from . import todo_admin
from . import user_admin
