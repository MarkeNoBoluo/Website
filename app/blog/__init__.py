"""Blog blueprint."""
from flask import Blueprint, jsonify

bp = Blueprint('blog', __name__, template_folder='templates/blog')

# Import utilities (makes blog.utils available)
from . import utils


@bp.route('/test-scan')
def test_scan():
    """Test route to verify article scanning integration."""
    from .utils import get_all_articles
    articles = get_all_articles()
    return jsonify({
        'count': len(articles),
        'articles': [{
            'title': a['title'],
            'date': a['date'].isoformat(),
            'slug': a['slug'],
            'excerpt': a['excerpt'][:100] + '...' if len(a['excerpt']) > 100 else a['excerpt']
        } for a in articles]
    })