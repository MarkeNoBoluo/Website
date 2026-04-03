# Phase 2: Error Handling & Robustness

## 目标
改进错误处理和系统健壮性：日志记录、健康检查、输入限制

## 任务

### 2.1 parse_article_file 异常处理改用 Logger
- **文件**: `app/blog/utils.py`
- **问题**: 解析错误的 Markdown 文件仅打印到 stdout，无日志记录
- **修复**:
  ```python
  from flask import current_app
  current_app.logger.error(f"Error parsing {filepath}: {e}")
  ```
- **验证**: 模拟损坏的 frontmatter，检查日志输出

### 2.2 /health 端点数据库故障返回 503
- **文件**: `app/__init__.py`
- **问题**: 数据库异常时仍返回 200，但 status 为 degraded
- **修复**:
  - 数据库不健康时返回 HTTP 503
  - 响应体包含具体错误信息（仅内部，外部隐藏详情）
  ```python
  if db_status != 'healthy':
      return jsonify(health_check()), 503
  ```

### 2.3 /admin/preview 内容长度限制
- **文件**: `app/admin/routes.py`
- **问题**: 未限制 Markdown 内容大小
- **修复**:
  - 限制 `content` 参数最大 1MB
  - 超过限制返回 413 Payload Too Large

## 验证标准
- [ ] 损坏文章文件被记录到 gunicorn_error.log
- [ ] 数据库故障时 GET /health 返回 503
- [ ] 提交 >1MB 内容到 /admin/preview 返回 413

## 依赖
阶段 1 完成

## 预计工时
1-2 小时
