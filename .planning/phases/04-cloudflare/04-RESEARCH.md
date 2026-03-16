# Phase 4: Cloudflare Tunnel 内网穿透 - Research

**Researched:** 2026-03-16
**Domain:** Cloudflare Tunnel / 内网穿透 / Raspberry Pi 部署
**Confidence:** MEDIUM

## Summary

Cloudflare Tunnel（原 Argo Tunnel）是一种无需公网 IP 和端口转发即可将本地服务安全暴露到公网的技术。通过运行在树莓派上的 cloudflared 守护进程，建立与 Cloudflare 网络的加密连接，将流量安全地转发到本地 Flask 应用。

**Primary recommendation:** 使用 YAML 配置文件管理隧道设置，集成 systemd 服务管理，通过环境变量注入敏感信息，并扩展现有部署脚本以支持隧道配置变更检测和自动重启。

## User Constraints (from CONTEXT.md)

### Locked Decisions
- 使用 config.yml YAML 配置文件管理隧道设置，易于维护和版本控制
- 配置文件放置在项目目录 `cloudflared/` 中，便于版本控制和部署
- 凭证文件（.json 和 cert.pem）不提交到 git，在首次部署时生成
- 敏感信息（隧道 ID、域名）通过环境变量注入 config.yml，其他配置硬编码
- 主站点使用子域名 `blog.example.com`，清晰标识博客功能
- 健康检查使用独立子域名 `status.example.com`，便于监控和故障排除
- DNS 记录通过 `cloudflared tunnel route dns` 命令自动化创建，易于脚本化
- DNS 记录类型使用 CNAME 记录，标准 Cloudflare Tunnel 方式
- 服务依赖关系：`After=blog.service`，确保博客服务先启动再启动隧道
- 重启策略：`always`，服务停止后总是重启，确保隧道持续运行
- 用户权限：以 `pi` 用户运行，与现有博客服务保持一致
- 安全配置：启用标准 systemd 安全选项（NoNewPrivileges、PrivateTmp、ProtectSystem 等）
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

### Deferred Ideas (OUT OF SCOPE)
- **多隧道/负载均衡** — 可在多台树莓派上部署实现高可用性，当前阶段单隧道足够
- **Cloudflare WAF 和安全规则** — 可后续在 Cloudflare 控制台配置，不在此阶段实现
- **自定义域名和 SSL 证书** — Cloudflare 提供自动 SSL，无需额外配置
- **高级监控和告警** — 基础监控通过 Cloudflare 控制台，高级功能后续添加
- **隧道流量分析和日志** — Cloudflare 提供基础分析，详细日志分析后续考虑

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| EXTC-01 | 站点通过 frp 或 ngrok 内网穿透，可从公网访问 | Cloudflare Tunnel 提供免费、安全的内网穿透方案，无需公网 IP |
| EXTC-02 | 穿透服务由 systemd 管理，重启后自动恢复隧道连接 | systemd 服务配置确保隧道服务开机自启和自动恢复 |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| cloudflared | 2026.3.0+ | Cloudflare Tunnel 客户端，建立加密连接 | Cloudflare 官方维护，免费套餐无限流量，ARM64 支持良好 |
| systemd | 系统自带 | 服务管理，开机自启，崩溃恢复 | Raspberry Pi OS 标准服务管理器，与现有博客服务模式一致 |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| YAML 配置文件 | N/A | 隧道配置管理 | 所有隧道配置，便于版本控制和环境变量注入 |
| bash 脚本 | N/A | 部署和配置自动化 | 首次部署、配置更新、故障排除 |
| journalctl | 系统自带 | 服务日志查看 | 调试隧道连接问题和服务状态 |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Cloudflare Tunnel | ngrok/frp | Tunnel 免费无流量限制，集成 Cloudflare 安全功能，无需额外配置 |
| YAML 配置 | 命令行参数 | YAML 更易维护和版本控制，支持复杂配置和环境变量 |
| systemd 服务 | supervisor/cron | systemd 是 Raspberry Pi OS 标准，与现有服务模式一致 |

**Installation:**
```bash
# 下载适用于 ARM64 的 cloudflared
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -O /usr/local/bin/cloudflared

# 设置执行权限
chmod +x /usr/local/bin/cloudflared

# 验证安装
cloudflared --version
```

## Architecture Patterns

### Recommended Project Structure
```
blog/
├── cloudflared/           # Cloudflare 隧道配置
│   ├── config.yml         # 隧道配置文件（模板）
│   ├── setup.sh           # 首次部署脚本
│   └── README.md          # 配置说明
├── systemd/
│   ├── blog.service       # 现有博客服务
│   └── cloudflared.service # 新增隧道服务
├── nginx/
│   └── blog.conf          # Nginx 配置
└── deploy.sh              # 部署脚本（需要更新）
```

### Pattern 1: 环境变量注入配置模板
**What:** 使用环境变量替换 YAML 配置文件中的敏感信息
**When to use:** 所有包含敏感信息的配置文件
**Example:**
```yaml
# cloudflared/config.yml.template
tunnel: ${CLOUDFLARE_TUNNEL_ID}
credentials-file: /home/pi/.cloudflared/${CLOUDFLARE_TUNNEL_ID}.json

ingress:
  - hostname: ${BLOG_SUBDOMAIN}.${DOMAIN}
    service: http://localhost:8080
  - hostname: ${STATUS_SUBDOMAIN}.${DOMAIN}
    service: http://localhost:8080/health
  - service: http_status:404
```

### Pattern 2: 条件性服务重启
**What:** 部署脚本检测配置文件变更，仅当需要时重启服务
**When to use:** 所有自动化部署流程
**Example:**
```bash
# 在 deploy.sh 中检测 cloudflared 配置变更
case "$file" in
    cloudflared/*)
        changed_cloudflared_config=true
        ;;
esac

# 条件性重启隧道服务
if [ "$changed_cloudflared_config" = "true" ]; then
    sudo cp "$APP_DIR/cloudflared/config.yml" /home/pi/.cloudflared/
    sudo systemctl restart cloudflared.service
fi
```

### Anti-Patterns to Avoid
- **硬编码敏感信息:** 将隧道 ID、域名等直接写入配置文件，导致安全风险
- **忽略服务依赖:** 不设置 `After=blog.service`，可能导致隧道启动时博客服务未就绪
- **过度重启:** 每次部署都重启隧道服务，造成不必要的连接中断
- **缺乏备份:** 不备份凭证和配置，故障时无法快速恢复

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| 隧道连接管理 | 自定义 TCP 连接池和重连逻辑 | cloudflared | 处理连接保持、重连、负载均衡等复杂逻辑 |
| SSL/TLS 终止 | 自签名证书或 Let's Encrypt 自动化 | Cloudflare Tunnel | Cloudflare 提供自动 SSL，无需证书管理 |
| DNS 记录管理 | 手动更新 DNS 或调用 API | `cloudflared tunnel route dns` | 自动化 DNS 记录创建和更新 |
| 服务监控 | 自定义健康检查脚本 | systemd + journalctl | 系统级服务监控和日志管理 |
| 配置验证 | 手动检查 YAML 语法 | `cloudflared tunnel ingress validate` | 官方验证工具确保配置正确 |

**Key insight:** Cloudflare Tunnel 已经解决了内网穿透的核心复杂问题（连接管理、SSL、DNS、监控），自定义解决方案只会增加维护负担和安全风险。

## Common Pitfalls

### Pitfall 1: 凭证文件权限问题
**What goes wrong:** 凭证文件权限设置不当，cloudflared 无法读取导致连接失败
**Why it happens:** 凭证文件默认生成在用户目录，但服务运行时可能权限不足
**How to avoid:** 确保凭证文件对运行用户可读，使用 `chmod 600` 设置适当权限
**Warning signs:** 服务日志显示 "permission denied" 或 "cannot read credentials"

### Pitfall 2: 服务启动顺序错误
**What goes wrong:** 隧道服务在博客服务之前启动，无法连接到本地应用
**Why it happens:** 缺少 `After=blog.service` 依赖声明
**How to avoid:** 在 systemd 服务文件中明确声明服务依赖关系
**Warning signs:** 隧道连接成功但访问网站返回 502 错误

### Pitfall 3: DNS 传播延迟
**What goes wrong:** 创建 DNS 记录后立即测试，域名无法解析
**Why it happens:** DNS 记录传播需要时间（通常几分钟到几小时）
**How to avoid:** 等待 DNS 传播完成后再测试，或使用 `dig` 命令验证解析
**Warning signs:** `curl` 连接超时，`dig` 显示无记录或旧记录

### Pitfall 4: 配置语法错误
**What goes wrong:** YAML 配置文件语法错误导致服务启动失败
**Why it happens:** YAML 对缩进和格式敏感，容易出错
**How to avoid:** 使用 `cloudflared tunnel ingress validate` 验证配置，使用 YAML linter
**Warning signs:** 服务启动失败，日志显示 "YAML parse error"

### Pitfall 5: 环境变量未设置
**What goes wrong:** 部署时环境变量未正确设置，配置模板替换失败
**Why it happens:** 环境变量文件缺失或变量名不匹配
**How to avoid:** 在部署脚本中检查必需环境变量，提供清晰错误信息
**Warning signs:** 配置文件包含 `${VARIABLE}` 占位符，服务使用错误配置

## Code Examples

Verified patterns from official sources:

### 基本隧道配置
```yaml
# Source: Cloudflare Tunnel 官方文档
tunnel: <Tunnel-UUID>
credentials-file: /path/<Tunnel-UUID>.json

ingress:
  - hostname: example.com
    service: http://localhost:80
  - service: http_status:404
```

### 多主机名配置
```yaml
tunnel: <Tunnel-UUID>
credentials-file: /path/<Tunnel-UUID>.json

ingress:
  - hostname: blog.example.com
    service: http://localhost:8080
  - hostname: status.example.com
    service: http://localhost:8080/health
  - service: http_status:404
```

### systemd 服务文件（基础）
```ini
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=pi
ExecStart=/usr/local/bin/cloudflared tunnel run
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| 端口转发 + DDNS | Cloudflare Tunnel | 2018+ | 无需公网 IP，无需路由器配置，自动 SSL |
| 手动证书管理 | Cloudflare 自动 SSL | 始终 | 无需 Let's Encrypt 续期，边缘网络终止 TLS |
| 独立监控工具 | Cloudflare 控制台集成监控 | 2020+ | 统一监控界面，实时连接状态和流量统计 |

**Deprecated/outdated:**
- **Argo Tunnel 名称:** 已重命名为 Cloudflare Tunnel，但命令和功能基本一致
- **手动 DNS 配置:** 使用 `cloudflared tunnel route dns` 自动化替代手动 DNS 记录管理

## Open Questions

1. **Cloudflare 免费套餐限制**
   - What we know: 官方文档声明免费套餐包含无限隧道和流量
   - What's unclear: 是否有连接数限制或速率限制
   - Recommendation: 假设无限制，监控实际使用情况

2. **ARM64 二进制兼容性**
   - What we know: GitHub 提供 cloudflared-linux-arm64 二进制
   - What's unclear: Raspberry Pi 4B 64位系统是否完全兼容
   - Recommendation: 测试安装和基本功能，准备备用方案

3. **DNS 记录 TTL 设置**
   - What we know: `cloudflared tunnel route dns` 自动创建 CNAME 记录
   - What's unclear: 自动设置的 TTL 值是多少，是否可配置
   - Recommendation: 接受默认值，需要时在 Cloudflare 控制台调整

## Validation Architecture

> Skipped because workflow.nyquist_validation is explicitly set to false in .planning/config.json

## Sources

### Primary (HIGH confidence)
- Cloudflare Tunnel 官方文档 - 配置格式、安装指南
- GitHub cloudflared releases - ARM64 二进制可用性、版本信息
- 现有项目文件 (blog.service, deploy.sh) - systemd 和部署模式参考

### Secondary (MEDIUM confidence)
- cloudflare-tunnel-implementation.md - 详细实现计划，包含具体步骤和配置示例
- 项目 CONTEXT.md - 用户决策和约束条件

### Tertiary (LOW confidence)
- WebFetch 尝试获取的官方文档页面 - 部分页面返回 404，信息可能过时或路径变更

## Metadata

**Confidence breakdown:**
- Standard stack: MEDIUM - 官方文档确认核心组件，但部分细节需要验证
- Architecture: HIGH - 基于现有项目模式和已验证的 Cloudflare Tunnel 模式
- Pitfalls: MEDIUM - 基于常见系统集成问题和 Cloudflare 服务特性

**Research date:** 2026-03-16
**Valid until:** 2026-04-16 (30天，Cloudflare Tunnel 相对稳定)