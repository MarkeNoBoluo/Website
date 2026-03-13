# Project State

**Project:** 个人博客网站 (Personal Blog on Raspberry Pi 4B)
**Created:** 2026-03-12
**Current Phase:** Phase 2 planning complete — ready for execution

## Status

| Item | Status | Last Updated |
|------|--------|--------------|
| Project definition | ✅ Complete | 2026-03-12 |
| Research | ✅ Complete | 2026-03-12 |
| Requirements | ✅ Complete | 2026-03-12 |
| Roadmap | ✅ Complete | 2026-03-13 |
| Phase 1 Planning | ✅ Complete | 2026-03-13 |
| Phase 1 Execution | ✅ Complete | 2026-03-13 |
| Phase 2 (Flask Skeleton) Planning | ✅ Complete | 2026-03-13 |
| Phase 2 (Flask Skeleton) Execution | ⏳ Pending | — |
| Phase 3 (Blog Articles) | ⏳ Pending | — |

## Phase History

| Phase | Status | Started | Completed |
|-------|--------|---------|-----------|
| Planning | ✅ Complete | 2026-03-12 | 2026-03-12 |
| Phase 1 Planning | ✅ Complete | 2026-03-13 | 2026-03-13 |
| Phase 1 Execution | ✅ Complete | 2026-03-13 | 2026-03-13 |
| Phase 2 Planning | ✅ Complete | 2026-03-13 | 2026-03-13 |

## Current Phase Details

**Current phase:** Phase 2 — Flask Application Skeleton

**Goal:** 建立 Flask 应用骨架，包括配置加载、数据库连接（WAL 模式）、蓝图结构和用户认证功能。

**Success Criteria:**
1. 访问 http://localhost/db-test 返回 SQLite 连接状态和 WAL 模式确认
2. 重启服务后 `.env` 中的 `SECRET_KEY` 正确加载，Flask session 可用
3. 并发两个请求访问不同端点，SQLite 无 "database is locked" 错误（WAL 模式生效）
4. 应用工厂 `create_app()` 可正确初始化三个蓝图（blog, todo, auth）
5. 访问 `/login` 显示登录表单，正确凭据可创建 session，错误凭据显示错误信息
6. 访问 `/logout` 可销毁 session
7. 受保护路由 (`@login_required`) 未登录时重定向到登录页

**Plans created:** 4 plans in 4 waves
- **Wave 1:** 02-01 — Application factory, configuration, database connection, base templates (AUTH-01, AUTH-02)
- **Wave 2:** 02-02 — Flask-Bcrypt installation, auth blueprint, password utilities (AUTH-01, AUTH-02)
- **Wave 3:** 02-03 — Login/logout routes, templates, login_required decorator (AUTH-01, AUTH-02)
- **Wave 4:** 02-04 — Integration testing and verification checkpoint (AUTH-01, AUTH-02)

**Execution Progress:** Phase 2 not yet started
**Current Plan:** 02-01 (pending)
**Next Phase:** Phase 3 (Blog Articles + Dark Theme) after Phase 2 completion

## Requirements Coverage

| Requirement | Phase | Status |
|-------------|-------|--------|
| INFRA-01 | Phase 1 | ✅ Complete |
| INFRA-02 | Phase 1 | ✅ Complete |
| INFRA-03 | Phase 1 | ✅ Complete |
| INFRA-04 | Phase 1 | ✅ Complete |
| INFRA-05 | Phase 1 | ✅ Complete |
| AUTH-01 | Phase 2 | Planned (pending execution) |
| AUTH-02 | Phase 2 | Planned (pending execution) |
| BLOG-01 | Phase 3 | Pending |
| BLOG-02 | Phase 3 | Pending |
| BLOG-03 | Phase 3 | Pending |
| BLOG-04 | Phase 3 | Pending |
| BLOG-05 | Phase 3 | Pending |

**Coverage:** 100% (12/12 v1 requirements mapped)

## Notes

- **Research completed:** 4 dimensions (stack, features, architecture, pitfalls)
- **Stack decided:** Flask 3.1.3 + mistune 3.2.0 + SQLite + Gunicorn + Nginx + systemd
- **Key pitfalls identified:** XSS via `| safe`, SQLite locking, SD card wear, post‑receive hook silent failures
- **v1 scope narrowed:** No comments, no frp/ngrok, no todo in v1 (deferred to v2)
- **Auth added to v1:** Password-based authentication implemented in Phase 2
- **v1.x enhancements:** RSS, sitemap, Open Graph meta tags (post‑v1)

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-12 | Use Flask over FastAPI | Flask is WSGI‑sync, template‑first, lower RAM (~15MB). FastAPI's async advantage irrelevant at personal‑blog scale. |
| 2026-03-12 | Use SQLite with WAL mode | Zero‑config, single‑file, handles blog/task traffic. WAL mode prevents "database is locked" under Gunicorn 2 workers. |
| 2026-03-12 | Defer comments to v2 | Focus v1 on core blog content and deployment pipeline; comments require spam defense and rate limiting. |
| 2026-03-12 | Deploy pipeline first | Infrastructure must work before any feature code; prevents "works on dev, broken on Pi" surprises. |
| 2026-03-13 | Phase 1 plans created | 6 plans covering all INFRA requirements with wave-based dependency structure |
| 2026-03-13 | Gunicorn Unix socket configuration | Use `/tmp/blog.sock` for Nginx communication instead of TCP port for better security and performance on Raspberry Pi |
| 2026-03-13 | Platform-aware testing | Test script handles Windows development limitations while validating configuration for Linux/Raspberry Pi deployment |
| 2026-03-13 | Nginx static file caching | No caching headers for static files to simplify debugging during development phase |
| 2026-03-13 | Gzip compression settings | Level 6 compression for text responses with 256 byte minimum length for optimal performance |
| 2026-03-13 | Client request limits | 10MB max body size for security, 12s timeouts for request processing on Raspberry Pi |
| 2026-03-13 | Phase 2 plans created | 4 plans covering authentication with application factory, WAL mode, Flask-Bcrypt, and blueprint structure |

## Configuration

- **Mode:** interactive
- **Granularity:** coarse (3 phases)
- **Parallelization:** true
- **Git tracking:** yes (planning docs committed)
- **Research before planning:** yes
- **Plan check before execution:** yes
- **Verifier after each phase:** yes

## Session Info

**Last session:** 2026-03-13
**Stopped at:** Phase 2 planning complete (4 plans created)
**Next action:** Execute Phase 2: `/gsd:execute-phase 02-flask-application-skeleton`

---

*State file created: 2026-03-12*
*Last updated: 2026-03-13 (Phase 2 planning complete - 4 plans created)*