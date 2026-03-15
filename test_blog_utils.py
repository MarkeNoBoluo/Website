"""Tests for blog article scanning and caching utilities."""
import pytest
from datetime import datetime, date
from app.blog.utils import get_all_articles, get_article_by_slug


def test_get_all_articles():
    """Test that all articles are found and sorted by date descending."""
    articles = get_all_articles()
    assert len(articles) == 2
    # Should be sorted by date descending (newest first)
    assert articles[0]['date'] > articles[1]['date']
    # Check article structure
    for article in articles:
        assert 'title' in article
        assert 'date' in article
        assert 'slug' in article
        assert 'excerpt' in article
        assert 'content' in article
        assert 'html' in article


def test_get_article_by_slug():
    """Test retrieving article by slug."""
    article = get_article_by_slug("hello-world")
    assert article is not None
    assert article['title'] == "Hello, World!"
    assert article['date'] == datetime(2026, 3, 15).date()
    assert article['slug'] == "hello-world"
    # Should have excerpt extracted
    assert article['excerpt']
    # Should have HTML content
    assert article['html']


def test_get_article_by_slug_nonexistent():
    """Test retrieving non-existent article returns None."""
    article = get_article_by_slug("nonexistent")
    assert article is None


def test_lru_cache():
    """Test that LRU cache prevents re-parsing."""
    # First call should parse
    articles1 = get_all_articles()
    # Second call should use cache
    articles2 = get_all_articles()
    # Should be same object (cached)
    assert articles1 is articles2


def test_excerpt_extraction():
    """Test excerpt extraction from first paragraph or first 200 characters."""
    article = get_article_by_slug("hello-world")
    excerpt = article['excerpt']
    # Excerpt should be extracted from content
    assert excerpt
    # Should not be too long (around 200 chars max)
    assert len(excerpt) <= 250  # Allow some buffer
    # Should contain meaningful text
    assert "Welcome" in excerpt or "first blog post" in excerpt


def test_date_parsing():
    """Test date parsing from ISO format."""
    article = get_article_by_slug("markdown-guide")
    assert article['date'] == datetime(2026, 3, 16).date()
    # Should be datetime.date object
    assert isinstance(article['date'], date)