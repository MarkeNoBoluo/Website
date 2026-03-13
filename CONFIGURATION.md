# Configuration Guide

This document describes how to configure the Flask blog application for development and production on Raspberry Pi.

## Quick Setup

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file:** Open `.env` in a text editor and fill in actual values.

3. **Set up Python environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

## Environment Variables

### Required Variables

| Variable | Purpose | Default | Validation |
|----------|---------|---------|------------|
| `SECRET_KEY` | Flask session signing and CSRF protection | (none) | Must be at least 64 random characters |
| `DATABASE_URL` | SQLite database connection | `sqlite:///blog.db` | Must be valid SQLite URL |
| `DEBUG` | Enable Flask debug features | `false` | Must be `true` or `false` |
| `LOG_LEVEL` | Application logging verbosity | `INFO` | Must be valid Python log level |

### Variable Details

#### SECRET_KEY
- **Purpose:** Used to sign Flask session cookies and for CSRF protection
- **Security:** Must be kept secret - never commit to git
- **Generation:** Use a secure random generator:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(64))"
  ```
- **Length:** Minimum 64 characters recommended

#### DATABASE_URL
- **Format:** `sqlite:///path/to/database.db`
- **Location:** Relative to project root directory
- **Production:** Use absolute path for systemd service: `sqlite:////home/pi/blog/blog.db`

#### DEBUG
- **Development:** Set to `true` for auto-reload, detailed error pages
- **Production:** Always set to `false` for security
- **Note:** When `true`, the Flask debugger allows arbitrary code execution on error pages

#### LOG_LEVEL
- **Options:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Development:** `DEBUG` for detailed logs
- **Production:** `INFO` or `WARNING` for normal operation

## Validation Rules

The application validates all required environment variables at startup:

1. **Presence check:** All required variables must be set
2. **Format validation:** Variables must meet format requirements
3. **Error handling:** If validation fails, the application exits with clear error message

Example error messages:
- `Error: SECRET_KEY must be at least 64 characters (got 0)`
- `Error: DEBUG must be 'true' or 'false' (got 'yes')`

## Production Deployment

### Systemd Service Configuration
Environment variables for production are loaded via systemd's `EnvironmentFile` directive:

```ini
[Service]
EnvironmentFile=/home/pi/blog/.env
```

### File Locations on Raspberry Pi
- **Application:** `/home/pi/blog/`
- **Database:** `/home/pi/blog/blog.db`
- **Logs:** `/home/pi/blog/logs/`
- **Virtual environment:** `/home/pi/blog/.venv/`

## Troubleshooting

### Common Issues

**"SECRET_KEY is not set or too short"**
- Solution: Generate a proper secret key and add to `.env`

**"DATABASE_URL is not a valid SQLite URL"**
- Solution: Use format `sqlite:///blog.db` (relative) or `sqlite:////home/pi/blog/blog.db` (absolute)

**Application starts but immediately exits**
- Check: All required environment variables are set in `.env`
- Check: `.env` file permissions (should be readable by application user)

**"ModuleNotFoundError: No module named 'flask'"**
- Solution: Activate virtual environment: `source .venv/bin/activate`

### Log Files
- **Application logs:** `logs/app.log` (created automatically)
- **Nginx logs:** `/var/log/nginx/blog.access.log` and `blog.error.log` (Phase 3)
- **Systemd logs:** `sudo journalctl -u blog.service` (Phase 4)

## Security Notes

1. **Never commit `.env` to git** - it contains secrets
2. **Use different `SECRET_KEY` values** for development and production
3. **Set `DEBUG=false` in production** to prevent code execution on error pages
4. **Restrict file permissions:** `.env` should be readable only by application user
5. **Regularly rotate `SECRET_KEY`** if compromised (invalidates existing sessions)