"""User admin routes for managing users."""

from flask import render_template, redirect, url_for, flash, request, session
from . import bp
from ..auth.utils import login_required, hash_password, check_password
from ..utils import csrf_protected
from ..extensions import db
from ..models import User


@bp.route("/users")
@login_required
def users():
    """List all users with search/sort/pagination."""
    page = request.args.get("page", 1, type=int)
    per_page = 10

    search = request.args.get("search", "")
    sort_by = request.args.get("sort", "created_at")

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
        sort_by=sort_by,
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
    if user.id == session.get("user_id"):
        flash("You cannot delete yourself", "error")
        return redirect(url_for("admin.users"))

    username = user.username
    db.session.delete(user)
    db.session.commit()

    flash(f'User "{username}" deleted successfully', "success")
    return redirect(url_for("admin.users"))
