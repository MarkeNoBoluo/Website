# Phase 4: Cloudflare Tunnel 内网穿透 - Context

**Gathered:** 2026-03-16
**Status:** Ready for planning

<domain>
## Phase Boundary

通过 Cloudflare Tunnel 将运行在树莓派上的 Flask 博客网站通过域名公开访问，无需公网 IP 和端口转发。包括安装配置 cloudflared 客户端，创建和管理隧道，配置 DNS 记录，集成 systemd 服务管理，以及集成到现有 git 部署流程中。

</domain>

<decisions>
## Implementation Decisions

### 隧道配置方法
- 使用 config.yml YAML 配置文件管理隧道设置，易于维护和版本控制
- 配置文件放置在项目目录 `cloudflared/` 中，便于版本控制和部署
- 凭证文件（.json 和 cert.pem）不提交到 git，在首次部署时生成
- 敏感信息（隧道 ID、域名）通过环境变量注入 config.yml，其他配置硬编码

### DNS 管理和子域名策略
- 主站点使用子域名 `blog.example.com`，清晰标识博客功能
- 健康检查使用独立子域名 `status.example.com`，便于监控和故障排除
- DNS 记录通过 `cloudflared tunnel route dns` 命令自动化创建，易于脚本化
- DNS 记录类型使用 CNAME 记录，标准 Cloudflare Tunnel 方式

### Systemd 服务集成
- 服务依赖关系：`After=blog.service`，确保博客服务先启动再启动隧道
- 重启策略：`always`，服务停止后总是重启，确保隧道持续运行
- 用户权限：以 `pi` 用户运行，与现有博客服务保持一致
- 安全配置：启用标准 systemd 安全选项（NoNewPrivileges、PrivateTmp、ProtectSystem 等）

### 部署脚本集成
- 变更检测：检测 `cloudflared/` 目录中任何文件变化，触发隧道服务重启
- 配置同步：部署脚本自动将 `cloudflared/config.yml` 复制到 `~/.cloudflared/` 目录
- 凭证处理：首次部署脚本包含生成步骤（`cloudflared tunnel login` 和 `cloudflared tunnel create`）
- 回滚策略：部署前备份当前配置，出错时可恢复到前一个版本

### Claude's Discretion
- 具体环境变量命名和默认值
- config.yml 模板的具体结构和字段
- 首次部署脚本的详细步骤和用户交互流程
- 备份策略的具体实现（备份频率、保留策略）
- 健康检查端点的具体实现和响应格式
- 隧道监控和日志记录的具体配置
- 故障排除脚本的具体内容

</decisions>

<specifics>
## Specific Ideas

- 隧道名称：`blog-tunnel`
- 配置文件位置：`cloudflared/config.yml`（项目内），`~/.cloudflared/config.yml`（部署后）
- systemd 服务文件：`cloudflared.service`，放置在 `systemd/` 目录
- 健康检查端点：`/health` 返回简单 JSON 状态
- 部署脚本在检测到 cloudflared 配置变更时重启隧道服务
- 凭证文件路径：`~/.cloudflared/cert.pem` 和 `~/.cloudflared/<tunnel-id>.json`

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `cloudflare-tunnel-implementation.md` — 详细的 Cloudflare Tunnel 实现计划，包含所有步骤和配置示例
- `blog.service` — 现有博客 systemd 服务文件（Phase 1），可参考其模式创建 cloudflared.service
- `deploy.sh` / post-receive hook — 现有部署脚本，可扩展以支持隧道配置检测和重启
- `CONFIGURATION.md` — 环境变量文档模式，可用于记录隧道相关环境变量
- Nginx 配置 — 现有 Nginx 配置监听 8080 端口，Cloudflare Tunnel 将指向此端口

### Established Patterns
- 环境变量验证和注入（Phase 1）— 隧道配置中敏感信息通过环境变量注入
- systemd 服务管理模式（Phase 1）— `pi` 用户，`After=network.target`，环境文件注入
- Git 部署流程（Phase 1）— post-receive hook 条件性重启服务，检测文件变更
- 配置备份和回滚（Phase 1 概念）— 现有部署流程包含错误处理和回滚概念

### Integration Points
- Cloudflare Tunnel 连接到 Nginx 监听的 `localhost:8080` 端口
- systemd 服务依赖现有 `blog.service`，确保启动顺序正确
- 部署脚本需要检测 `cloudflared/` 目录变更并重启隧道服务
- 环境变量需要扩展以包含隧道相关配置（域名、隧道 ID 等）
- 健康检查端点需要集成到现有 Flask 应用中

### Performance Considerations
- Cloudflare Tunnel 连接已加密和压缩，无需额外优化
- 隧道连接池由 cloudflared 自动管理
- systemd 的 `Restart=always` 确保服务崩溃后自动恢复
- 配置变更检测避免不必要的服务重启

</code_context>

<deferred>
## Deferred Ideas

- **多隧道/负载均衡** — 可在多台树莓派上部署实现高可用性，当前阶段单隧道足够
- **Cloudflare WAF 和安全规则** — 可后续在 Cloudflare 控制台配置，不在此阶段实现
- **自定义域名和 SSL 证书** — Cloudflare 提供自动 SSL，无需额外配置
- **高级监控和告警** — 基础监控通过 Cloudflare 控制台，高级功能后续添加
- **隧道流量分析和日志** — Cloudflare 提供基础分析，详细日志分析后续考虑

</deferred>

---

*Phase: 04-cloudflare*
*Context gathered: 2026-03-16*