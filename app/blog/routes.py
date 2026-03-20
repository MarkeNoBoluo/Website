"""Blog routes."""

from flask import render_template, abort
from . import bp
from .utils import get_db_articles, get_db_article_by_slug
import random


@bp.route("/")
def index():
    """Article list page - shows only published articles"""
    articles = get_db_articles(status="published")
    return render_template("index.html", articles=articles)


@bp.route("/<slug>")
def article_detail(slug):
    """Article detail page - only shows published articles"""
    article = get_db_article_by_slug(slug)
    if article is None or article["status"] != "published":
        abort(404)
    return render_template("article.html", article=article)


@bp.errorhandler(404)
def page_not_found(error):
    """Blog-related 404 error handler"""
    articles = get_db_articles(status="published")
    if articles:
        recommendations = random.sample(articles, min(3, len(articles)))
    else:
        recommendations = []
    return render_template("404.html", recommendations=recommendations), 404
