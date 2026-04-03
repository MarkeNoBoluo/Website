"""Markdown rendering with Pygments syntax highlighting."""

import html
from typing import Optional

import bleach
import mistune
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound

ALLOWED_TAGS = [
    "a",
    "abbr",
    "acronym",
    "address",
    "b",
    "blockquote",
    "br",
    "code",
    "div",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "i",
    "img",
    "li",
    "ol",
    "p",
    "pre",
    "span",
    "strong",
    "sub",
    "sup",
    "table",
    "tbody",
    "td",
    "th",
    "thead",
    "tr",
    "ul",
    # Code highlighting classes (from Pygments)
    ".highlight",
    ".highlight pre",
    ".highlight code",
]

ALLOWED_ATTRIBUTES = {
    "*": ["class", "id"],
    "a": ["href", "title", "rel"],
    "img": ["alt", "src", "width", "height"],
    "abbr": ["title"],
    "acronym": ["title"],
}


class HighlightRenderer(mistune.HTMLRenderer):
    """Custom Markdown renderer with Pygments syntax highlighting."""

    def __init__(self, escape=True):
        super().__init__(escape=escape)
        # Use monokai style for dark theme (per user decision)
        self.formatter = HtmlFormatter(style="monokai", cssclass="highlight")

    def block_code(self, code: str, info: Optional[str] = None) -> str:
        """Render code blocks with Pygments syntax highlighting.

        Args:
            code: The code content
            info: Language info (e.g., "python", "javascript")

        Returns:
            HTML with syntax highlighted code
        """
        if not info:
            # Auto-detect language if not specified
            try:
                lexer = guess_lexer(code)
            except ClassNotFound:
                # Fallback to plain text
                lexer = get_lexer_by_name("text")
        else:
            # Extract language from info string (e.g., "python" from "python foo.py")
            lang = info.strip().split()[0] if info else "text"
            try:
                lexer = get_lexer_by_name(lang)
            except ClassNotFound:
                # Fallback to auto-detection
                try:
                    lexer = guess_lexer(code)
                except ClassNotFound:
                    lexer = get_lexer_by_name("text")

        # Highlight code with Pygments
        highlighted = highlight(code, lexer, self.formatter)
        return highlighted


# Create Markdown renderer instance
# escape=False allows mistune to pass through HTML for bleach to sanitize
_renderer = HighlightRenderer(escape=False)
_markdown = mistune.create_markdown(renderer=_renderer)


def render_markdown(content: str) -> str:
    """Render Markdown content to HTML with syntax highlighting.

    Args:
        content: Markdown text

    Returns:
        Rendered HTML sanitized with bleach whitelist
    """
    rendered = _markdown(content)
    return bleach.clean(
        rendered, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True
    )
