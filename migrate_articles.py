#!/usr/bin/env python
"""One-time migration script to import posts/ files into database.

Usage:
    python migrate_articles.py [--archive]

The --archive flag moves posts/ to posts-archive/ after successful import.
"""

import os
import re
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app
from app.extensions import db
from app.models import Article
from app.admin.utils import generate_slug
import frontmatter


def extract_slug_from_filename(filename: str) -> str | None:
    """Extract slug from YYYY-MM-DD-slug.md format."""
    pattern = re.compile(r"(\d{4}-\d{2}-\d{2})-(.+)\.md$")
    match = pattern.match(filename)
    return match.group(2) if match else None


def migrate_articles(archive: bool = True) -> int:
    """Migrate articles from posts/ to database.

    Args:
        archive: If True, move posts/ to posts-archive/ after migration

    Returns:
        Number of articles migrated
    """
    app = create_app()

    with app.app_context():
        posts_dir = Path("posts")
        if not posts_dir.exists():
            print("No posts/ directory found. Nothing to migrate.")
            return 0

        # Get existing slugs to avoid duplicates
        existing_slugs = set(a.slug for a in Article.query.all())

        migrated = 0
        for filepath in sorted(posts_dir.glob("*.md")):
            # Extract slug from filename (use existing slug mapping)
            slug = extract_slug_from_filename(filepath.name)
            if not slug:
                print(f"Skipping {filepath.name}: invalid filename format")
                continue

            # Handle duplicate slugs (add suffix if needed)
            original_slug = slug
            counter = 1
            while slug in existing_slugs:
                slug = f"{original_slug}-{counter}"
                counter += 1
                existing_slugs.add(slug)

            try:
                post = frontmatter.load(filepath)
                title = post.get("title", slug.replace("-", " ").title())

                article = Article(
                    title=title,
                    content=post.content,
                    slug=slug,
                    status="published",  # Migrate all as published
                )
                db.session.add(article)
                migrated += 1
                print(f"Migrated: {title} (slug: {slug})")

            except Exception as e:
                print(f"Error migrating {filepath.name}: {e}")

        db.session.commit()
        print(f"\nMigrated {migrated} articles.")

        # Archive original posts
        if archive and migrated > 0:
            archive_dir = Path("posts-archive")
            archive_dir.mkdir(exist_ok=True)

            for filepath in posts_dir.glob("*.md"):
                archive_path = archive_dir / filepath.name
                filepath.rename(archive_path)

            print(
                f"Archived {len(list(archive_dir.glob('*.md')))} files to posts-archive/"
            )

        return migrated


if __name__ == "__main__":
    archive = "--no-archive" not in sys.argv
    migrate_articles(archive=archive)
