# Roadmap: 个人博客网站

**Created:** 2026-03-12
**v1 Scope:** 在树莓派上部署暗色技术风格博客，Markdown 文章自动渲染，Git 推送即部署

## Phases

### Phase 1: Infrastructure Foundation

**Goal:** 建立完整的部署管线，使得 `git push` 能自动更新 RPi 上的 Flask 应用并通过 Nginx 服务。

**Success Criteria** (observable user behaviors):
1. 开发者执行 `git push origin develop`，RPi 上的代码自动更新，无手动复制步骤
2. 访问 http://localhost 返回 Flask 的 "Hello, world!"（Nginx → Gunicorn → Flask 链通）
3. 重启树莓派后 Flask 应用自动启动（systemd 服务生效）
4. 修改 `.env` 文件中的 `SECRET_KEY` 后，服务重启即生效（python-dotenv 正确加载）

**Requirements Covered:**
- INFRA-01: virtualenv + .env，secrets 不进 git
- INFRA-02: Gunicorn（2 workers, Unix socket）运行 Flask 应用
- INFRA-03: Nginx 反向代理，静态文件直接提供
- INFRA-04: systemd 管理进程，开机自启、崩溃自重启
- INFRA-05: `git push` → RPi 自动更新并重启服务

**Deliverables:**
- `/etc/nginx/sites-available/blog` (Nginx 配置)
- `/etc/systemd/system/blog.service` (systemd 单元文件)
- `~/blog.git/hooks/post-receive` (Git post-receive hook)
- `requirements.txt` (Python 依赖列表)
- `.gitignore` (包含 `.env`, `.venv/`)
- `wsgi.py` (Gunicorn 入口)
- `.env.example` (环境变量模板)

**Plans:** 6 plans
- [x] 01-01-PLAN.md — Python foundation and Flask skeleton (INFRA-01)
- [x] 01-02-PLAN.md — Gunicorn production server configuration (INFRA-02)
- [x] 01-03-PLAN.md — Nginx reverse proxy configuration (INFRA-03)
- [ ] 01-04-PLAN.md — Systemd service management (INFRA-04)
- [ ] 01-05-PLAN.md — Git deployment automation (INFRA-05)
- [ ] 01-06-PLAN.md — Verification checkpoint (all INFRA requirements)

**Dependencies:** None — 这是第一个阶段。

**Research Needed:** 无 — 基础设施模式高度标准化。

**Risks:**
- Nginx Unix socket 权限问题（需将 `www-data` 加入 `pi` 组）
- post-receive hook 部分部署失败（需使用 `#!/bin/bash` + `set -e`）
- systemd 服务启动顺序（需 `After=network.target`）

### Phase 2: Flask Application Skeleton

**Goal:** 建立 Flask 应用骨架，包括配置加载、数据库连接（WAL 模式）、蓝图结构和用户认证功能。

**Success Criteria:**
1. 访问 http://localhost/db-test 返回 SQLite 连接状态和 WAL 模式确认
2. 重启服务后 `.env` 中的 `SECRET_KEY` 正确加载，Flask session 可用
3. 并发两个请求访问不同端点，SQLite 无 "database is locked" 错误（WAL 模式生效）
4. 应用工厂 `create_app()` 可正确初始化三个蓝图（blog, todo, auth）
5. 访问 `/login` 显示登录表单，正确凭据可创建 session，错误凭据显示错误信息
6. 访问 `/logout` 可销毁 session
7. 受保护路由 (`@login_required`) 未登录时重定向到登录页

**Requirements Covered:** AUTH-01, AUTH-02 (authentication implementation)

**Deliverables:**
- `app/__init__.py` (`create_app()` 工厂)
- `app/config.py` (配置类，加载 `.env`)
- `app/db.py` (SQLite 连接，WAL 模式，`synchronous=NORMAL`)
- `app/blog/__init__.py` (blog 蓝图占位)
- `app/todo/__init__.py` (todo 蓝图占位)
- `app/auth/__init__.py` (auth 蓝图)
- `app/auth/routes.py` (登录/注销路由，session 管理)
- `app/auth/templates/auth/login.html` (登录表单模板)
- `app/auth/templates/auth/logout.html` (注销确认模板)
- `app/auth/utils.py` (密码哈希验证工具)
- `init_db.py` (初始化脚本，创建 comments/todos 表结构)
- `app/templates/base.html` (基础模板骨架)

**Plans:** 4 plans
- [ ] 02-01-PLAN.md — Application factory, configuration, database connection, base templates (AUTH-01, AUTH-02)
- [ ] 02-02-PLAN.md — Flask-Bcrypt installation, auth blueprint, password utilities (AUTH-01, AUTH-02)
- [ ] 02-03-PLAN.md — Login/logout routes, templates, login_required decorator (AUTH-01, AUTH-02)
- [ ] 02-04-PLAN.md — Integration testing and verification checkpoint (AUTH-01, AUTH-02)

**Dependencies:** Phase 1 (部署管线必须就绪)

**Research Needed:** 无 — Flask 应用工厂和 SQLite WAL 模式是标准模式。

**Risks:**
- `.env` 意外提交到 git（需在 Phase 1 的 `.gitignore` 中已包含）
- SQLite 连接未正确关闭（需注册 `teardown_appcontext`）
- WAL 模式未持久化（需在 `init_db.py` 中设置 `PRAGMA journal_mode=WAL`）

### Phase 3: Blog Articles + Dark Theme

**Goal:** 实现博客核心功能 — 文章列表、详情页、Markdown 渲染、语法高亮、暗色主题、404 页面。

**Success Criteria:**
1. 访问 http://localhost/ 显示文章列表，按修改时间倒序排列
2. 点击文章标题进入详情页，Markdown 内容渲染为 HTML，代码块有语法高亮
3. 全站使用暗色技术风格 CSS，移动端和桌面端布局正常
4. 访问不存在的 URL 显示自定义 404 页面，而非 Nginx 默认错误页
5. 新文章（`.md` 文件）推送到 RPi 后，自动出现在首页，无需重启服务（文件系统扫描生效）

**Requirements Covered:**
- BLOG-01: 首页文章列表，按时间倒序，显示标题+日期
- BLOG-02: 文章详情页，完整渲染 Markdown
- BLOG-03: 代码块语法高亮（Pygments，暗色主题）
- BLOG-04: 全站暗色技术风格主题，响应式布局
- BLOG-05: 自定义 404 页面

**Deliverables:**
- `app/markdown.py` (Markdown 解析，frontmatter 提取，Pygments 高亮)
- `app/blog/routes.py` (`/`, `/post/<slug>` 路由)
- `app/blog/templates/blog/index.html` (文章列表页)
- `app/blog/templates/blog/post.html` (文章详情页)
- `app/blog/templates/blog/404.html` (自定义 404 页面)
- `app/static/css/style.css` (暗色主题 CSS)
- `app/static/css/pygments.css` (Pygments 暗色主题样式)
- `posts/` 目录结构 + 示例文章
- `app/templates/base.html` (扩展为完整布局)

**Plans:** 3/3 plans complete
- [x] 03-01-PLAN.md — Markdown processing infrastructure (BLOG-01, BLOG-02, BLOG-03)
- [x] 03-02-PLAN.md — Blog routes and templates (BLOG-01, BLOG-02, BLOG-05)
- [x] 03-03-PLAN.md — Dark theme CSS implementation (BLOG-04)

**Dependencies:** Phase 2 (Flask 骨架必须就绪)

**Research Needed:** 无 — Markdown 解析和 Pygments 集成已研究。

**Risks:**
- Markdown 解析性能问题（考虑 LRU 缓存）
- 前端 CSS 在旧浏览器兼容性（使用现代 CSS 特性，如 CSS Grid/Flexbox）
- 移动端响应式细节需手动测试

### Phase 4: 实现 Cloudflare 隧道内网穿透

**Goal:** 通过 Cloudflare Tunnel 将运行在树莓派上的 Flask 博客网站通过域名公开访问，无需公网 IP 和端口转发。

**Success Criteria:**
1. 用户可通过 `https://blog.example.com` 从公网访问博客
2. 健康状态可通过 `https://status.example.com/health` 监控
3. 隧道服务在系统重启后自动恢复连接
4. 修改隧道配置后，部署脚本自动应用更改并重启服务
5. 隧道凭证和敏感信息安全管理，不提交到 git

**Requirements Covered:**
- EXTC-01: 站点通过 frp 或 ngrok 内网穿透，可从公网访问
- EXTC-02: 穿透服务由 systemd 管理，重启后自动恢复隧道连接

**Deliverables:**
- `cloudflared/config.yml` (隧道配置文件模板)
- `systemd/cloudflared.service` (隧道 systemd 服务文件)
- `cloudflared/setup.sh` (首次部署设置脚本)
- `cloudflared/backup.sh`, `cloudflared/restore.sh` (配置备份恢复脚本)
- `cloudflared/dns-setup.sh` (DNS 记录自动化脚本)
- 更新的 `deploy.sh` (支持隧道配置变更检测)
- 更新的 `CONFIGURATION.md` (隧道环境变量文档)
- `app/utils.py` 中的健康检查端点 `/health`

**Plans:** 3/3 plans executed
- [x] 04-01-PLAN.md — Cloudflare Tunnel foundation: configuration templates, systemd service, documentation (EXTC-01, EXTC-02)
- [x] 04-02-PLAN.md — Deployment integration: enhanced deploy.sh, credential handling, backup/restore (EXTC-01, EXTC-02)
- [x] 04-03-PLAN.md — Health endpoint and verification: Flask health route, DNS setup, final checkpoint (EXTC-01, EXTC-02)

**Dependencies:** Phase 3 (博客功能必须就绪)

**Research Needed:** 已完成 — Cloudflare Tunnel 配置模式、系统集成、常见问题已研究。

**Risks:**
- 凭证文件权限问题导致连接失败
- 服务启动顺序错误（隧道在博客服务之前启动）
- DNS 传播延迟导致立即测试失败
- 环境变量未正确设置导致配置模板替换失败

## Coverage Validation

| Requirement | Phase | Covered |
|-------------|-------|---------|
| INFRA-01 | Phase 1 | ✓ |
| INFRA-02 | Phase 1 | ✓ |
| INFRA-03 | Phase 1 | ✓ |
| INFRA-04 | Phase 1 | ✓ |
| INFRA-05 | Phase 1 | ✓ |
| AUTH-01 | Phase 2 | ✓ |
| AUTH-02 | Phase 2 | ✓ |
| BLOG-01 | Phase 3 | ✓ |
| BLOG-02 | Phase 3 | ✓ |
| BLOG-03 | Phase 3 | ✓ |
| BLOG-04 | Phase 3 | ✓ |
| BLOG-05 | Phase 3 | ✓ |
| EXTC-01 | Phase 4 | ✓ |
| EXTC-02 | Phase 4 | ✓ |

**Coverage:** 100% (14/14 v1 requirements mapped)

### Phase 5: Blog Management (CRUD)

**Goal:** Add article management capabilities (create, edit, delete) with draft/publish workflow, and unify UI across all interfaces.

**Success Criteria:**
1. Admin can create new articles via web form (title, content in Markdown, excerpt optional)
2. Admin can edit existing articles via web form
3. Admin can delete articles with confirmation
4. Articles have draft/publish status - drafts hidden from public listing
5. Admin has article list with status indicators and quick actions
6. All pages (login, admin forms, article list) use consistent dark theme

**Requirements Covered:**
- BLOG-MGMT-01: Article CRUD (create, read, update, delete)
- BLOG-MGMT-02: Draft/Publish status management
- BLOG-MGMT-03: Admin article listing with filters

**Deliverables:**
- `app/models.py`: Article model with title, content, slug, status, timestamps
- `app/blog/admin_routes.py`: Admin routes for CRUD operations
- `app/blog/templates/admin/*.html`: Admin templates (list, create, edit, delete confirmation)
- Updated `app/blog/utils.py`: Support database articles alongside file-based
- Updated `app/auth/routes.py`: Consistent dark theme on login
- `app/static/css/admin.css`: Admin-specific styles

**Plans:** 4 plans
- [ ] 05-01-PLAN.md — Database model and article CRUD routes
- [ ] 05-02-PLAN.md — Admin templates and article list with status filters
- [ ] 05-03-PLAN.md — Draft/publish workflow implementation
- [ ] 05-04-PLAN.md — UI unification across login and admin pages

**Dependencies:** Phase 3 (blog display), Phase 2 (auth)

**Research Needed:** None — Flask-SQLAlchemy CRUD patterns are well established.

**Risks:**
- File-based vs database article storage conflict (need migration strategy)
- Markdown rendering consistency between file and database sources
- Admin URL security (ensure only authenticated users can access)

## Out-of-Scope Items

**v1.x (post‑v1):** RSS, Sitemap, Open Graph meta tags
**v2:** Comments, Eisenhower Matrix todo

## Next Steps

1. **Execute Phase 1** (`/gsd:execute-phase 01-infrastructure-foundation`): 建立部署管线
2. **Verify** each phase's success criteria before proceeding
3. **Commit** code at end of each phase

---
*Roadmap created: 2026-03-12*
*Updated: 2026-03-13 (added Phase 1 plans)*
*Updated: 2026-03-13 (added Phase 2 plans)*
*Updated: 2026-03-14 (revised Phase 2 plans - reduced from 6 to 4 plans, moved user management and security enhancements to backlog)*
*Updated: 2026-03-15 (added Phase 3 plans)*
*Updated: 2026-03-16 (added Phase 4 plans)*