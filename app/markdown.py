"""Markdown rendering with Pygments syntax highlighting."""
import html
from typing import Optional

import mistune
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound


class HighlightRenderer(mistune.HTMLRenderer):
    """Custom Markdown renderer with Pygments syntax highlighting."""

    def __init__(self, escape=True):
        super().__init__(escape=escape)
        # Use monokai style for dark theme (per user decision)
        self.formatter = HtmlFormatter(style='monokai', cssclass='highlight')

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
                lexer = get_lexer_by_name('text')
        else:
            # Extract language from info string (e.g., "python" from "python foo.py")
            lang = info.strip().split()[0] if info else 'text'
            try:
                lexer = get_lexer_by_name(lang)
            except ClassNotFound:
                # Fallback to auto-detection
                try:
                    lexer = guess_lexer(code)
                except ClassNotFound:
                    lexer = get_lexer_by_name('text')

        # Highlight code with Pygments
        highlighted = highlight(code, lexer, self.formatter)
        return highlighted


# Create Markdown renderer instance
_renderer = HighlightRenderer(escape=True)
_markdown = mistune.create_markdown(renderer=_renderer)


def render_markdown(content: str) -> str:
    """Render Markdown content to HTML with syntax highlighting.

    Args:
        content: Markdown text

    Returns:
        Rendered HTML (safe for template rendering)
    """
    # mistune handles HTML escaping when escape=True in renderer
    return _markdown(content)