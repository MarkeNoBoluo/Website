"""Article scanning, caching, and utility functions."""
import os
import re
from datetime import datetime, date
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

import frontmatter
from app.markdown import render_markdown

# Directory containing blog posts
POSTS_DIR = Path("posts")

# Regex to extract slug from filename: YYYY-MM-DD-slug.md
SLUG_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2})-(.+)\.md$")


def extract_slug_from_filename(filename: str) -> Optional[str]:
    """Extract slug from filename in YYYY-MM-DD-slug.md format.

    Args:
        filename: Filename to parse

    Returns:
        Slug string or None if pattern doesn't match
    """
    match = SLUG_PATTERN.match(filename)
    if match:
        return match.group(2)
    return None


def parse_article_file(filepath: Path) -> Optional[Dict]:
    """Parse a Markdown article file with frontmatter.

    Args:
        filepath: Path to Markdown file

    Returns:
        Article dictionary or None if parsing fails
    """
    try:
        # Parse frontmatter and content
        post = frontmatter.load(filepath)

        # Extract slug from filename
        slug = extract_slug_from_filename(filepath.name)
        if not slug:
            return None

        # Parse date from frontmatter (expects YYYY-MM-DD format)
        date_value = post.get('date')
        if isinstance(date_value, str):
            date_obj = datetime.fromisoformat(date_value).date()
        elif isinstance(date_value, datetime):
            date_obj = date_value.date()
        elif isinstance(date_value, date):
            date_obj = date_value
        else:
            # Default to file modification date
            date_obj = datetime.fromtimestamp(filepath.stat().st_mtime).date()

        # Extract excerpt: use frontmatter excerpt or generate from content
        excerpt = post.get('excerpt')
        if not excerpt:
            # Get first paragraph or first 200 characters
            content_text = post.content.strip()
            # Split by double newline (paragraphs)
            paragraphs = content_text.split('\n\n')
            if paragraphs:
                first_para = paragraphs[0].strip()
                # Remove Markdown headers and code blocks for excerpt
                first_para = re.sub(r'^#+\s+', '', first_para)  # Remove headers
                first_para = re.sub(r'`.*?`', '', first_para)  # Remove inline code
                first_para = re.sub(r'\s+', ' ', first_para)  # Normalize whitespace
                excerpt = first_para[:200].strip()
                if len(first_para) > 200:
                    excerpt += "..."
            else:
                excerpt = ""

        # Render Markdown to HTML
        html_content = render_markdown(post.content)

        return {
            'title': post.get('title', 'Untitled'),
            'date': date_obj,
            'slug': slug,
            'excerpt': excerpt,
            'content': html_content,  # Rendered HTML (per plan specification)
            'raw_content': post.content,  # Raw markdown for internal use
            'filepath': str(filepath),
        }
    except Exception as e:
        # Log error and skip file
        print(f"Error parsing {filepath}: {e}")
        return None


@lru_cache(maxsize=100)
def scan_articles() -> List[Dict]:
    """Scan posts directory for articles and parse them.

    Returns:
        List of article dictionaries
    """
    articles = []
    if not POSTS_DIR.exists():
        return articles

    for filepath in POSTS_DIR.glob("*.md"):
        article = parse_article_file(filepath)
        if article:
            articles.append(article)

    return articles


@lru_cache(maxsize=100)
def get_all_articles() -> List[Dict]:
    """Get all articles sorted by date descending (newest first).

    Returns:
        Sorted list of article dictionaries
    """
    articles = scan_articles()
    # Sort by date descending (newest first)
    articles.sort(key=lambda x: x['date'], reverse=True)
    return articles


@lru_cache(maxsize=100)
def get_article_by_slug(slug: str) -> Optional[Dict]:
    """Get article by slug.

    Args:
        slug: Article slug (from filename)

    Returns:
        Article dictionary or None if not found
    """
    articles = scan_articles()
    for article in articles:
        if article['slug'] == slug:
            return article
    return None