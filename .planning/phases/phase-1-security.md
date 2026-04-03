# Phase 1: Security Fixes

## 目标
修复高优先级安全问题：CSRF token 刷新、Session 明文存储、XSS 防护验证

## 任务

### 1.1 CSRF Token 刷新机制
- **文件**: `app/extensions.py`, `app/utils.py`
- **问题**: CSRF token 在 session 中长期保持不变，攻击者获取后可长期使用
- **修复**:
  - CSRF token 有效期设为 30 分钟
  - 每次成功 POST 后生成新 token
  - 或使用双 token 方案（submit token + session token）

### 1.2 移除 Session 中的明文 Username
- **文件**: `app/auth/routes.py`, `app/auth/utils.py`
- **问题**: Session 中存储明文 username，XSS 可窃取
- **修复**:
  - 仅保留 `session['user_id']`
  - 需要 username 时从数据库查询 `User.query.get(user_id)`

### 1.3 XSS 防护验证
- **文件**: `app/markdown.py`
- **问题**: `HighlightRenderer(escape=False)` 允许原始 HTML
- **修复**:
  - 验证 mistune 是否正确转义 script/iframe 等危险标签
  - 如需允许部分 HTML，考虑使用 bleach 库白名单

## 验证标准
- [ ] CSRF token 刷新后旧 token 失效
- [ ] session 中不包含 username 字段
- [ ] `<script>alert(1)</script>` 在文章内容中被转义

## 依赖
无

## 预计工时
1-2 小时
