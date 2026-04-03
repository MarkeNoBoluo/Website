"""Todo utility functions for validation and permission checking."""

from datetime import datetime
from flask import abort, session, request
from ..extensions import db
from ..models import Todo, User, Quadrant


def get_current_user_id():
    """Get current user ID from session."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    return user_id


def get_current_user():
    """Get current user object from session."""
    user_id = get_current_user_id()
    if not user_id:
        return None
    return User.query.get(user_id)


def get_todo_or_404(todo_id):
    """Get todo by ID and verify ownership.

    Args:
        todo_id: Todo item ID

    Returns:
        Todo object if found and owned by current user

    Raises:
        404: If todo not found
        403: If todo belongs to different user
    """
    todo = Todo.query.get_or_404(todo_id)
    user_id = get_current_user_id()

    # Check ownership
    if todo.user_id != user_id:
        abort(403, "You do not have permission to access this todo")

    return todo


def validate_todo_form(form_data):
    """Validate todo form data.

    Args:
        form_data: dict with title, description, quadrant, priority, due_date

    Returns:
        dict with validated data or raises ValueError
    """
    errors = []

    # Title validation
    title = form_data.get("title", "").strip()
    if not title:
        errors.append("Title is required")
    elif len(title) > 200:
        errors.append("Title must be 200 characters or less")

    # Description validation
    description = form_data.get("description", "").strip()
    if len(description) > 5000:
        errors.append("Description must be 5000 characters or less")

    # Quadrant validation
    quadrant = form_data.get("quadrant", type=int)
    if quadrant is None:
        errors.append("Quadrant is required")
    elif quadrant not in tuple(q.value for q in Quadrant):
        errors.append("Quadrant must be 1, 2, 3, or 4")

    # Priority validation
    priority = form_data.get("priority", 3, type=int)
    if priority not in (1, 2, 3, 4, 5):
        errors.append("Priority must be 1-5")

    # Due date validation (optional)
    due_date_str = form_data.get("due_date", "").strip()
    due_date = None
    if due_date_str:
        try:
            # Expecting ISO format or YYYY-MM-DD
            due_date = datetime.fromisoformat(due_date_str)
        except ValueError:
            errors.append("Due date must be in YYYY-MM-DD format")

    if errors:
        raise ValueError("; ".join(errors))

    return {
        "title": title,
        "description": description,
        "quadrant": quadrant,
        "priority": priority,
        "due_date": due_date,
    }


def get_todos_by_quadrant(user_id):
    """Get all todos for a user grouped by quadrant.

    Args:
        user_id: User ID

    Returns:
        dict with quadrant numbers as keys and lists of todos as values
    """
    todos = (
        Todo.query.filter_by(user_id=user_id)
        .order_by(Todo.priority.asc(), Todo.created_at.desc())
        .all()
    )

    # Group by quadrant
    quadrant_todos = {1: [], 2: [], 3: [], 4: []}
    for todo in todos:
        quadrant_todos[todo.quadrant].append(todo)

    return quadrant_todos
