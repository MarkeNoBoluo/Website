"""Todo routes for Eisenhower matrix functionality."""

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    abort,
    jsonify,
    session,
)
from . import bp
from ..auth.utils import login_required
from ..utils import csrf_protected
from ..extensions import db
from ..models import Todo, User, Quadrant
from .utils import (
    get_current_user_id,
    get_todo_or_404,
    validate_todo_form,
    get_todos_by_quadrant,
)
from datetime import datetime


@bp.route("/")
@login_required
def index():
    """Display Eisenhower matrix with todos grouped by quadrant."""
    user_id = get_current_user_id()
    if not user_id:
        flash("Please log in to access this page.", "warning")
        return redirect(url_for("auth.login"))

    quadrant_todos = get_todos_by_quadrant(user_id)

    return render_template("todo/index.html", quadrant_todos=quadrant_todos)


@bp.route("/add", methods=["GET", "POST"])
@login_required
@csrf_protected
def add():
    """Add a new todo item."""
    user_id = get_current_user_id()

    if request.method == "POST":
        try:
            validated = validate_todo_form(request.form)

            # Create new todo
            todo = Todo(
                user_id=user_id,
                title=validated["title"],
                description=validated["description"],
                quadrant=validated["quadrant"],
                priority=validated["priority"],
                due_date=validated["due_date"],
            )

            db.session.add(todo)
            db.session.commit()

            flash("Todo added successfully", "success")
            return redirect(url_for("todo.index"))

        except ValueError as e:
            flash(str(e), "error")
            # Re-render form with submitted data
            return render_template("add.html", form_data=request.form)

    # GET request - render form
    return render_template("add.html")


@bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
@csrf_protected
def edit(id):
    """Edit an existing todo item."""
    todo = get_todo_or_404(id)

    if request.method == "POST":
        try:
            validated = validate_todo_form(request.form)

            # Update todo
            todo.title = validated["title"]
            todo.description = validated["description"]
            todo.quadrant = validated["quadrant"]
            todo.priority = validated["priority"]
            todo.due_date = validated["due_date"]
            todo.completed = "completed" in request.form

            db.session.commit()

            flash("Todo updated successfully", "success")
            return redirect(url_for("todo.index"))

        except ValueError as e:
            flash(str(e), "error")
            # Re-render form with submitted data
            return render_template("edit.html", todo=todo, form_data=request.form)

    # GET request - render form
    return render_template("edit.html", todo=todo)


@bp.route("/<int:id>/delete", methods=["POST"])
@login_required
@csrf_protected
def delete(id):
    """Delete a todo item."""
    todo = get_todo_or_404(id)

    db.session.delete(todo)
    db.session.commit()

    flash("Todo deleted successfully", "success")
    return redirect(url_for("todo.index"))


@bp.route("/<int:id>/toggle", methods=["POST"])
@login_required
@csrf_protected
def toggle(id):
    """Toggle completion status of a todo item."""
    todo = get_todo_or_404(id)

    todo.completed = not todo.completed
    db.session.commit()

    flash("Todo status updated", "success")

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True, "completed": todo.completed})

    return redirect(url_for("todo.index"))


@bp.route("/<int:id>/move", methods=["POST"])
@login_required
@csrf_protected
def move(id):
    """Update quadrant of a todo item (drag and drop)."""
    todo = get_todo_or_404(id)

    quadrant = request.form.get("quadrant", type=int)
    if quadrant not in tuple(q.value for q in Quadrant):
        abort(400, "Invalid quadrant")

    todo.quadrant = quadrant
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True})

    return redirect(url_for("todo.index"))


@bp.route("/<int:id>/reorder", methods=["POST"])
@login_required
@csrf_protected
def reorder(id):
    """Update priority/order of a todo item (drag and drop sorting)."""
    todo = get_todo_or_404(id)

    priority = request.form.get("priority", type=int)
    if priority not in (1, 2, 3, 4, 5):
        abort(400, "Invalid priority")

    todo.priority = priority
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True})

    return redirect(url_for("todo.index"))
