# Requirements: 个人博客网站

**Defined:** 2026-03-12
**Core Value:** 在树莓派上运行暗色技术风格的个人博客，通过 Markdown 文件管理文章，Git 推送自动部署

## v1 Requirements

Requirements for initial release.

### Infrastructure

- [x] **INFRA-01**: 项目可通过 virtualenv + .env 在 RPi 上启动，secrets 不进 git
- [x] **INFRA-02**: Flask 应用可通过 Gunicorn（2 workers, Unix socket）运行
- [ ] **INFRA-03**: Nginx 作反向代理，静态文件直接由 Nginx 提供，动态请求转发 Gunicorn
- [ ] **INFRA-04**: 应用由 systemd 管理，开机自启，崩溃自动重启
- [ ] **INFRA-05**: 开发者执行 `git push` 后，RPi 上代码自动更新并重启服务

### Blog Content

- [ ] **BLOG-01**: 用户访问首页可看到所有文章列表，按发布时间倒序排列，显示标题和日期
- [ ] **BLOG-02**: 用户点击文章可查看详情，Markdown 内容完整渲染为 HTML
- [ ] **BLOG-03**: 代码块有语法高亮（Pygments，适配暗色主题）
- [ ] **BLOG-04**: 全站使用暗色技术风格视觉主题，布局在移动端和桌面端均可正常显示
- [ ] **BLOG-05**: 访问不存在的 URL 显示自定义 404 页面

### Authentication

- [ ] **AUTH-01**: 博主可通过密码登录进入后台功能（session 认证，密码哈希存 .env）
- [ ] **AUTH-02**: 未登录时无法访问后台路由（`@login_required` 保护）

## v1.x Requirements

Deferred to immediately after v1 launch. Not in v1 roadmap.

### Discoverability

- **DISC-01**: 站点提供 `/feed.xml` RSS 订阅源，包含最新文章标题/链接/摘要
- **DISC-02**: 站点提供 `/sitemap.xml` 和 `/robots.txt`，供搜索引擎收录
- **DISC-03**: 每篇文章页面包含 Open Graph 元标签，链接分享时显示标题和摘要预览

## v2 Requirements

Deferred to future release.

### Comments

- **COMM-01**: 访客可在每篇文章下匿名留言（填写姓名和内容）
- **COMM-02**: 评论提交带 CSRF 保护和蜜罐字段，防止机器人垃圾留言
- **COMM-03**: Nginx 对评论提交接口限速（每 IP 每分钟最多 2 次），防止刷评

### External Access

- **EXTC-01**: 站点通过 frp 或 ngrok 内网穿透，可从公网访问
- **EXTC-02**: 穿透服务由 systemd 管理，重启后自动恢复隧道连接

### Personal Productivity

- **TODO-01**: 登录后可访问艾森豪威尔矩阵页面，任务分四象限展示（重要且紧急/重要不紧急/紧急不重要/不重要不紧急）
- **TODO-02**: 用户可在任意象限新增任务
- **TODO-03**: 用户可标记任务为完成
- **TODO-04**: 用户可删除任务

## Out of Scope

| Feature | Reason |
|---------|--------|
| 网页后台 CMS | VSCode Remote SSH 已是写作工作流，重复建设 |
| 移动端 App | 响应式网页已足够 |
| 邮件通知 | 复杂度高，个人博客不需要 |
| OAuth/社交登录 | 单一管理员用简单密码即可 |
| 实时聊天/WebSocket | 超出博客定位 |
| 文章标签/分类 | 推迟到 20+ 篇文章后，届时规律才明显 |
| 全文搜索 | 推迟到浏览器 Ctrl+F 明显不够用时 |
| Docker 容器化 | 在 RPi 上增加不必要的内存开销 |
| 文章翻页 | 推迟到 200+ 篇文章 |

## Traceability

Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| INFRA-01 | Phase 1 | Complete |
| INFRA-02 | Phase 1 | Complete |
| INFRA-03 | Phase 1 | Pending |
| INFRA-04 | Phase 1 | Pending |
| INFRA-05 | Phase 1 | Pending |
| AUTH-01 | Phase 2 | Pending |
| AUTH-02 | Phase 2 | Pending |
| BLOG-01 | Phase 3 | Pending |
| BLOG-02 | Phase 3 | Pending |
| BLOG-03 | Phase 3 | Pending |
| BLOG-04 | Phase 3 | Pending |
| BLOG-05 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 12 total
- Mapped to phases: 12
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-12*
*Last updated: 2026-03-12 after initial definition*
