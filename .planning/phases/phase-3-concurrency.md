# Phase 3: Concurrency & Caching

## 目标
解决并发相关问题：WAL 模式验证、缓存清理机制、slug 竞态

## 任务

### 3.1 验证并确保 SQLite WAL 模式启用
- **文件**: `app/__init__.py` 或 `app/extensions.py`
- **问题**: 未确认 WAL 模式是否真的启用
- **修复**:
  - 在 `create_app()` 中显式设置 WAL 模式
  ```python
  with db.engine.connect() as conn:
      conn.execute(text("PRAGMA journal_mode=WAL"))
  ```
- **验证**: `flask --app app db-test` 确认返回 `"wal_mode": true`

### 3.2 统一缓存清理机制
- **文件**: `app/blog/utils.py`, `app/admin/routes.py`
- **问题**: 缓存清理调用分散，可能遗漏
- **修复**:
  - 使用 SQLAlchemy event listener 自动触发
  ```python
  @event.listens_for(Article, 'after_insert')
  @event.listens_for(Article, 'after_update')
  @event.listens_for(Article, 'after_delete')
  def invalidate_cache(*args, **kwargs):
      get_db_articles.cache_clear()
      get_db_article_by_slug.cache_clear()
  ```
  - 移除手动调用

### 3.3 修复 Slug 生成竞态 (TOCTOU)
- **文件**: `app/admin/utils.py`
- **问题**: 检查 slug 存在和插入之间可能被占用
- **修复**:
  - 依赖数据库唯一约束
  - 捕获 IntegrityError 并生成新 slug 重试
  ```python
  try:
      db.session.add(article)
      db.session.commit()
  except IntegrityError:
      db.session.rollback()
      article.slug = generate_slug(title, suffix=1)
      db.session.add(article)
      db.session.commit()
  ```

## 验证标准
- [ ] `flask --app app db-test` 显示 wal_mode: true
- [ ] 文章创建/编辑/删除后缓存自动失效
- [ ] 并发创建相同标题文章不会产生重复 slug

## 依赖
阶段 1, 2 完成

## 预计工时
2-3 小时
