"""Admin utility functions."""

import re
from datetime import date
from app.models import Article


def generate_slug(title: str) -> str:
    """Generate URL-friendly slug from title.

    Chinese characters are transliterated to pinyin. The slug is prefixed
    with the current date (YYYY-MM-DD) so URLs look like /blog/2026-03-24-title.

    Args:
        title: Article title

    Returns:
        URL-safe slug string, e.g. "2026-03-24-yuan-dui-xiang-xi-tong"
    """
    from pypinyin import lazy_pinyin

    # Transliterate Chinese characters to pinyin, then lowercase
    pinyin_parts = lazy_pinyin(title)
    slug = "-".join(pinyin_parts).lower().strip()

    # Keep only alphanumeric and hyphens
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    slug = re.sub(r"-+", "-", slug)  # Collapse multiple hyphens
    slug = slug.strip("-")

    # Prefix with today's date
    today = date.today().strftime("%Y-%m-%d")
    slug = f"{today}-{slug}" if slug else today

    # Check for duplicates and append suffix
    base_slug = slug
    counter = 1
    while Article.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug
