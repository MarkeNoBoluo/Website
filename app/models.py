"""SQLAlchemy data models for the application."""

from .extensions import db
from datetime import datetime


class User(db.Model):
    """User model for authentication and ownership."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    todos = db.relationship("Todo", backref="user", lazy="dynamic")


class Todo(db.Model):
    """Todo item model for Eisenhower matrix."""

    __tablename__ = "todos"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    quadrant = db.Column(db.Integer, nullable=False)  # 1-4
    priority = db.Column(db.Integer, default=3)  # 1-5, 1最高
    due_date = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        db.CheckConstraint("quadrant IN (1, 2, 3, 4)", name="check_quadrant"),
        db.CheckConstraint("priority IN (1, 2, 3, 4, 5)", name="check_priority"),
    )


class Article(db.Model):
    """Article model for blog posts."""

    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)  # Raw markdown content
    slug = db.Column(db.String(200), unique=True, nullable=False)
    status = db.Column(db.String(20), default="draft")  # 'draft' or 'published'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        db.CheckConstraint(
            "status IN ('draft', 'published')", name="check_article_status"
        ),
    )
