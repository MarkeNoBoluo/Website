"""Admin utility functions."""

import re
from app.models import Article


def generate_slug(title: str) -> str:
    """Generate URL-friendly slug from title.

    Args:
        title: Article title

    Returns:
        URL-safe slug string
    """
    # Convert to lowercase and replace spaces with hyphens
    slug = title.lower().strip()
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    slug = re.sub(r"-+", "-", slug)  # Collapse multiple hyphens
    slug = slug.strip("-")

    # Handle empty slug
    if not slug:
        slug = "untitled"

    # Check for duplicates and append suffix
    base_slug = slug
    counter = 1
    while Article.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug
