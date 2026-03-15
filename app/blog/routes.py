"""Blog routes."""
from flask import render_template, abort
from . import bp
from .utils import get_all_articles, get_article_by_slug
import random


@bp.route('/')
def index():
    """文章列表页 - 显示所有文章卡片"""
    articles = get_all_articles()
    return render_template('blog/index.html', articles=articles)


@bp.route('/<slug>')
def article_detail(slug):
    """文章详情页 - 显示单篇文章"""
    article = get_article_by_slug(slug)
    if article is None:
        # 触发 404 错误，由错误处理器处理
        abort(404)
    return render_template('blog/article.html', article=article)


@bp.errorhandler(404)
def page_not_found(error):
    """博客相关的 404 错误处理（仅处理 /blog/* 下的 404）"""
    articles = get_all_articles()
    # 随机选择 3 篇文章作为推荐
    if articles:
        recommendations = random.sample(articles, min(3, len(articles)))
    else:
        recommendations = []

    return render_template('blog/404.html',
                         recommendations=recommendations), 404