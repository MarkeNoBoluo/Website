# Code Review Remediation Plan

基于代码审查发现的问题，制定以下 4 阶段修复计划。

## 概览

| 阶段 | 主题 | 问题数 | 优先级 | 依赖 |
|------|------|--------|--------|------|
| Phase 1 | 安全修复 | 3 | 高 | 无 |
| Phase 2 | 错误处理与健壮性 | 3 | 高 | Phase 1 |
| Phase 3 | 并发与缓存 | 3 | 中 | Phase 1, 2 |
| Phase 4 | 代码质量 | 4 | 中 | Phase 1, 2, 3 |

## 问题清单

### Phase 1: 安全修复
1. **1.1** CSRF Token 未在每次请求后刷新
2. **1.2** Session 中存储明文 username
3. **1.3** XSS 防护验证（escape=False）

### Phase 2: 错误处理与健壮性
4. **2.1** parse_article_file 异常仅打印不记录
5. **2.2** /health 端点数据库故障仍返回 200
6. **2.3** /admin/preview 未限制内容长度

### Phase 3: 并发与缓存
7. **3.1** SQLite WAL 模式未确认启用
8. **3.2** 缓存清理调用分散
9. **3.3** Slug 生成存在 TOCTOU 竞态

### Phase 4: 代码质量
10. **4.1** Todo.quadrant 使用魔法数字
11. **4.2** 文件导入大小检查低效
12. **4.3** 废弃的 app/db.py 模块
13. **4.4** todo/routes.py 含调试 print

## 执行顺序

```
Phase 1 (1-2h) → Phase 2 (1-2h) → Phase 3 (2-3h) → Phase 4 (1-2h)
     ↓              ↓                ↓               ↓
   安全            错误处理         并发             收尾
```

## 总预计工时
5-9 小时

## 验收标准

每个阶段完成后：
1. 运行 `python -m pytest` 确保测试通过
2. 验证该阶段修改的功能正常
3. 检查无新增 lint 错误

所有阶段完成后：
1. 完整测试所有端点
2. 验证 `/health` 在故障时返回 503
3. 确认 session 不包含 username
