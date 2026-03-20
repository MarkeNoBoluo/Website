# 个人博客网站

## What This Is

运行在树莓派 4B 上的个人网站，通过 VSCode 远程 SSH 开发。核心是一个暗色技术风格的个人博客，支持 Markdown 文章展示和访客评论，附带仅供个人使用的艾森豪威尔矩阵待办清单。

## Core Value

让访客能够浏览博客文章并留言互动，同时为博主提供私密的艾森豪威尔矩阵任务管理工具。

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] 博客文章列表页（按时间倒序展示所有文章）
- [ ] 博客文章详情页（渲染 Markdown，显示标题/日期/内容）
- [ ] 每篇文章下的评论区（访客可匿名留言）
- [ ] 艾森豪威尔矩阵待办清单（四象限：重要且紧急/重要不紧急/紧急不重要/不重要不紧急）
- [ ] 待办功能密码保护（仅博主登录后可访问和操作）
- [ ] 暗色技术感视觉主题
- [ ] Git push 自动部署到树莓派（post-receive hook）
- [ ] 内网穿透支持（frp/ngrok，供外网访问）

### Out of Scope

- 网页后台 CMS — 直接在 VSCode 写 Markdown 文件，更高效
- 移动端 App — 响应式网页已足够
- 邮件通知 — 复杂度高，v1 不需要
- OAuth/社交登录 — 个人站点用简单密码即可
- 实时聊天 — 超出博客定位

## Context

- 开发环境：Windows 主机通过 VSCode Remote SSH 连接树莓派 4B
- 部署目标：树莓派 4B（ARM64，内存有限，依赖需轻量）
- 文章管理：在本地/远程写 `.md` 文件，通过 Git 推送同步
- 外网访问：通过 frp 或 ngrok 内网穿透，暂无固定公网 IP 或域名
- 数据持久化：SQLite 单文件，无需额外数据库服务

## Constraints

- **Runtime**: Raspberry Pi 4B — 依赖需轻量，避免高内存占用框架
- **Backend**: Python — 用户偏好，Flask 或 FastAPI
- **Database**: SQLite — 零配置，树莓派友好
- **Dev workflow**: VSCode Remote SSH — 需要在树莓派上直接运行开发服务器
- **Deployment**: Git bare repo + post-receive hook — 推送即部署

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Python 后端 | 用户偏好 | — Pending |
| SQLite 数据库 | 零配置，适合树莓派单机部署 | — Pending |
| Markdown 文件管理文章 | 无需后台 CMS，VSCode 直接写更高效 | — Pending |
| Git post-receive 自动部署 | 推送即部署，开发体验流畅 | — Pending |
| 内网穿透方案 | 无固定公网 IP，frp/ngrok 是可行方案 | — Pending |

## Current Milestone: v1.1 Blog Management

**Goal:** 为博客添加文章管理功能（增删改查），并统一全站UI风格

**Target features:**
- 博客文章管理后台：创建、编辑、删除文章
- 文章草稿/发布状态管理
- 统一全站暗色技术风格（登录页、管理页、表单页）
- 响应式布局适配移动端管理操作

---
*Last updated: 2026-03-20 after milestone v1.1 start*
