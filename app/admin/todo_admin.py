"""Todo admin routes for managing all todos."""

from flask import render_template, redirect, url_for, flash, request, session
from . import bp
from ..auth.utils import login_required
from ..utils import csrf_protected
from ..extensions import db
from ..models import Todo


@bp.route("/todos")
@login_required
def todos():
    """List all todos with search/filter/sort/pagination."""
    page = request.args.get("page", 1, type=int)
    per_page = 10

    search = request.args.get("search", "")
    quadrant = request.args.get("quadrant", "all")
    priority = request.args.get("priority", "all")

    query = Todo.query

    if search:
        query = query.filter(Todo.title.contains(search))

    if quadrant != "all":
        query = query.filter_by(quadrant=int(quadrant))

    if priority != "all":
        query = query.filter_by(priority=int(priority))

    query = query.order_by(Todo.updated_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        "admin/todos/list.html",
        todos=pagination.items,
        pagination=pagination,
        search=search,
        quadrant=quadrant,
        priority=priority,
    )


@bp.route("admin//todos/new", methods=["GET", "POST"])
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
            flash("标题不能为空", "error")
            return render_template("admin/todos/create.html", form_data=request.form)

        todo = Todo(
            user_id=session.get("user_id"),
            title=title,
            description=description,
            quadrant=quadrant,
            priority=priority,
        )
        db.session.add(todo)
        db.session.commit()

        flash(f'待办《{title}》创建成功', "success")
        return redirect(url_for("admin.todos"))

    return render_template("admin/todos/create.html")


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
        todo.completed = "completed" in request.form

        db.session.commit()

        flash(f'待办《{todo.title}》更新成功', "success")
        return redirect(url_for("admin.todos"))

    return render_template("admin/todos/edit.html", todo=todo)


@bp.route("/todos/<int:id>/delete", methods=["POST"])
@login_required
@csrf_protected
def delete_todo(id):
    """Delete a todo."""
    todo = Todo.query.get_or_404(id)
    title = todo.title

    db.session.delete(todo)
    db.session.commit()

    flash(f'待办《{title}》已删除', "success")
    return redirect(url_for("admin.todos"))


@bp.route("/todos/<int:id>/complete", methods=["POST"])
@login_required
@csrf_protected
def complete_todo(id):
    """Toggle todo completion."""
    todo = Todo.query.get_or_404(id)
    todo.completed = not todo.completed
    db.session.commit()

    if todo.completed:
        flash("待办已标记为完成", "success")
    else:
        flash("待办已标记为未完成", "success")
    return redirect(url_for("admin.todos"))
