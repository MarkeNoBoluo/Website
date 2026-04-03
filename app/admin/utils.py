"""Admin utility functions."""

import re
from datetime import date
from app.models import Article


def generate_slug(title: str, suffix: int = 0) -> str:
    """Generate URL-friendly slug from title.

    Chinese characters are transliterated to pinyin. The slug is prefixed
    with the current date (YYYY-MM-DD) so URLs look like /blog/2026-03-24-title.

    Args:
        title: Article title
        suffix: Optional numeric suffix for disambiguation

    Returns:
        URL-safe slug string, e.g. "2026-03-24-yuan-dui-xiang-xi-tong"
    """
    from pypinyin import lazy_pinyin

    pinyin_parts = lazy_pinyin(title)
    slug = "-".join(pinyin_parts).lower().strip()

    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")

    today = date.today().strftime("%Y-%m-%d")
    slug = f"{today}-{slug}" if slug else today

    if suffix > 0:
        slug = f"{slug}-{suffix}"

    return slug
