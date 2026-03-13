# Phase 1: Infrastructure Foundation - Context

**Gathered:** 2026-03-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish complete deployment pipeline where `git push` automatically updates Flask application on Raspberry Pi and serves it via Nginx. Includes virtualenv environment, Gunicorn with Unix socket, Nginx reverse proxy, systemd service management, and git post-receive hook.

</domain>

<decisions>
## Implementation Decisions

### Git Post-Receive Hook Behavior
- Restart Flask service only if changed files affect backend (check .py files)
- Install dependencies only (run `pip install -r requirements.txt` if requirements.txt changed)
- Continue on some errors, log all warnings, fail on critical errors
- Maintain previous deployment version for rollback capability

### Nginx Configuration Approach
- Gunicorn communicates via Unix socket (not TCP port)
- Nginx directly serves static files from app/static directory
- SSL/TLS configuration deferred to later phase
- Logs stored in project-specific directory (`~/blog/logs/`)
- Use default Nginx error pages (no custom error pages)
- Enable gzip compression for HTML, CSS, JS responses
- No caching headers for static files (simpler debugging)
- Set client max body size limit (e.g., 10MB) for security

### Systemd Service Details
- Run Flask service as `pi` user (simpler permissions)
- Restart policy: `on-failure` (restart only on failure, not clean exit)
- Dependency: `After=network.target` (wait for network before starting)
- Environment variables injected via Systemd `EnvironmentFile` directive (not Flask .env loading)

### Environment Variable Management
- Multiple configuration variables required: `SECRET_KEY`, `DATABASE_URL`, `DEBUG`, `LOG_LEVEL`, etc.
- Commit `.env.example` with example values and comments as template
- Validate all required environment variables at startup (fail fast with clear error)
- Document variables in `CONFIGURATION.md` with purpose, defaults, and validation rules

### Claude's Discretion
- Exact error handling logic in post-receive hook
- Specific gzip compression settings
- Exact client max body size value
- Structure of CONFIGURATION.md documentation
- Log rotation configuration for Nginx and application logs

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- No existing codebase — this is the first phase

### Established Patterns
- No established patterns yet — this phase sets foundational patterns

### Integration Points
- Deployment will connect to existing Raspberry Pi system services (systemd, Nginx, git)

</code_context>

<specifics>
## Specific Ideas

- Deployment target: Raspberry Pi 4B with ARM64 architecture
- Development workflow: VSCode Remote SSH to Raspberry Pi
- All secrets stored in `.env` file excluded from git
- Static files served directly by Nginx for better performance

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-infrastructure-foundation*
*Context gathered: 2026-03-13*