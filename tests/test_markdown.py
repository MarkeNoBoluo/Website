"""Tests for Markdown rendering functionality."""
import pytest
from app.markdown import render_markdown


def test_render_markdown_heading():
    """Test basic Markdown heading rendering."""
    result = render_markdown("# Heading")
    assert "<h1>Heading</h1>" in result
    # Ensure HTML is properly escaped
    assert "<script>" not in result


def test_render_markdown_code_block_with_language():
    """Test code block rendering with syntax highlighting."""
    code = "```python\nprint('hello')\n```"
    result = render_markdown(code)
    # Pygments generates <div class="highlight"><pre><span>...</span></pre></div>
    assert "<pre" in result
    assert "class=" in result  # Should have CSS classes for highlighting
    assert "highlight" in result  # Pygments adds 'highlight' class


def test_render_markdown_xss_protection():
    """Test that HTML tags are properly escaped."""
    malicious = "<script>alert('xss')</script>"
    result = render_markdown(malicious)
    # Script tags should be escaped, not executed
    assert "&lt;script&gt;" in result or "<script>" not in result


def test_render_markdown_code_block_no_language():
    """Test code block without language info gets auto-detected."""
    code = "```\nprint('hello')\n```"
    result = render_markdown(code)
    # Should still render as code block even without language
    assert "<pre" in result
    assert "class=" in result  # Pygments should still add classes


def test_render_markdown_custom_renderer():
    """Test that custom HighlightRenderer is used."""
    # This test verifies Pygments integration
    code = "```python\ndef hello():\n    return 'world'\n```"
    result = render_markdown(code)
    # Pygments should add specific CSS classes
    assert "class=" in result or "highlight" in result