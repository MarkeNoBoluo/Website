"""Tests for blog article scanning and caching utilities.

Regression tests for Phase 05: Blog Management.
Tests the database-backed article system (get_db_articles, get_db_article_by_slug).
"""

import pytest
import uuid
from datetime import date


@pytest.fixture
def app():
    """Create application fixture with a unique temp file database."""
    import os
    from app import create_app
    from app.config import Config
    from app.extensions import db

    # Unique temp file per test to avoid SQLite in-memory sharing
    db_path = f"test_blog_{uuid.uuid4().hex}.db"

    class TestConfig(Config):
        TESTING = True
        DATABASE_URL = f"sqlite:///{db_path}"
        SECRET_KEY = "test-secret-key-" + "x" * 48
        DEBUG = False
        LOG_LEVEL = "INFO"

        @classmethod
        def validate(cls):
            pass

    app = create_app(config_class=TestConfig)
    ctx = app.app_context()
    ctx.push()
    db.create_all()

    yield app, db_path

    db.drop_all()
    db.session.remove()
    ctx.pop()
    try:
        os.unlink(db_path)
    except OSError:
        pass


@pytest.fixture
def seeded_app(app):
    """Seed test data into the database."""
    from app.extensions import db
    from app.models import Article
    from app.blog import utils as blog_utils

    app_obj = app[0]
    article1 = Article(
        title="Hello, World!",
        slug="hello-world",
        content="# Welcome\n\nThis is my first blog post. Welcome to the world of blogging!\n\n## Features\n\n- Markdown support\n- Syntax highlighting",
        status="published",
    )
    article2 = Article(
        title="Markdown Guide",
        slug="markdown-guide",
        content="# Markdown Guide\n\nThis guide covers Markdown basics including **bold**, *italic*, and `code`.\n\n```python\nprint('hello')\n```",
        status="published",
    )
    article3 = Article(
        title="Draft Post",
        slug="draft-post",
        content="# Draft\n\nThis is a draft article that should not appear in public listings.",
        status="draft",
    )
    db.session.add_all([article1, article2, article3])
    db.session.commit()

    # Clear cache to pick up new articles
    blog_utils.get_db_articles.cache_clear()
    blog_utils.get_db_article_by_slug.cache_clear()

    yield app_obj


def test_get_db_articles(seeded_app):
    """Test that database articles are found."""
    from app.blog.utils import get_db_articles

    articles = get_db_articles(status="published")
    assert len(articles) == 2
    for article in articles:
        assert "title" in article
        assert "date" in article
        assert "slug" in article
        assert "excerpt" in article
        assert "content" in article
        assert "raw_content" in article
        assert article["status"] == "published"


def test_get_db_articles_with_status(seeded_app):
    """Test filtering by status."""
    from app.blog.utils import get_db_articles

    published = get_db_articles(status="published")
    assert len(published) == 2
    for a in published:
        assert a["status"] == "published"

    drafts = get_db_articles(status="draft")
    assert len(drafts) == 1
    assert drafts[0]["title"] == "Draft Post"

    all_articles = get_db_articles(status=None)
    assert len(all_articles) == 3


def test_get_db_article_by_slug(seeded_app):
    """Test retrieving article by slug from database."""
    from app.blog.utils import get_db_article_by_slug

    article = get_db_article_by_slug("hello-world")
    assert article is not None
    assert article["title"] == "Hello, World!"
    assert article["slug"] == "hello-world"
    assert article["excerpt"]
    assert article["content"]
    assert "article_id" in article
    assert article["status"] == "published"


def test_get_db_article_by_slug_nonexistent(seeded_app):
    """Test retrieving non-existent article returns None."""
    from app.blog.utils import get_db_article_by_slug

    article = get_db_article_by_slug("nonexistent")
    assert article is None


def test_lru_cache(seeded_app):
    """Test that LRU cache prevents re-querying database."""
    from app.blog.utils import get_db_articles

    articles1 = get_db_articles()
    articles2 = get_db_articles()
    assert articles1 is articles2


def test_excerpt_extraction(seeded_app):
    """Test excerpt extraction from first paragraph or first 200 characters."""
    from app.blog.utils import get_db_article_by_slug

    article = get_db_article_by_slug("hello-world")
    excerpt = article["excerpt"]
    assert excerpt
    assert len(excerpt) <= 250
    assert "Welcome" in excerpt or "blog" in excerpt


def test_date_parsing(seeded_app):
    """Test that dates are returned as date objects."""
    from app.blog.utils import get_db_article_by_slug

    article = get_db_article_by_slug("markdown-guide")
    assert article["date"] is not None
    assert isinstance(article["date"], date)
