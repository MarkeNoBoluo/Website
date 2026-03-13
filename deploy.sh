#!/bin/bash
set -e
set -u

# Deployment script for Flask blog on Raspberry Pi
# Conditionally installs dependencies and restarts services based on changed files

# Configuration
APP_DIR="/home/wddkxg/blog"
VENV_DIR="$APP_DIR/.venv"
LOG_DIR="$APP_DIR/logs"
SERVICE_NAME="blog.service"
BACKUP_DIR="$APP_DIR/backups"
DEPLOY_LOG="$LOG_DIR/deploy.log"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $*" | tee -a "$DEPLOY_LOG"
}

# Ensure directories exist
mkdir -p "$LOG_DIR" "$BACKUP_DIR"

# Parse arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <path-to-checked-out-code> [oldrev] [newrev]"
    exit 1
fi

NEW_CODE_DIR="$1"
OLD_REV="${2:-}"
NEW_REV="${3:-}"

log "=== Starting deployment ==="
log "New code directory: $NEW_CODE_DIR"
log "Old revision: $OLD_REV"
log "New revision: $NEW_REV"

# Change detection function
check_changed_files() {
    local changed_py_files=()
    local changed_requirements=false
    local changed_nginx_config=false
    local changed_systemd_service=false
    local changed_static_files=false

    if [ -n "$OLD_REV" ] && [ -n "$NEW_REV" ]; then
        log "Checking changed files between $OLD_REV and $NEW_REV"

        # Get list of changed files
        changed_files=$(git diff --name-only "$OLD_REV" "$NEW_REV" 2>/dev/null || echo "")

        for file in $changed_files; do
            case "$file" in
                *.py)
                    changed_py_files+=("$file")
                    ;;
                requirements.txt)
                    changed_requirements=true
                    ;;
                nginx/*)
                    changed_nginx_config=true
                    ;;
                systemd/*)
                    changed_systemd_service=true
                    ;;
                app/static/*|static/*)
                    changed_static_files=true
                    ;;
            esac
        done
    else
        log "No revision information provided, assuming all changes require action"
        changed_py_files=("*.py")  # Simplified
        changed_requirements=true
        changed_nginx_config=true
        changed_systemd_service=true
    fi

    # Return as string (simple approach)
    echo "PY_FILES:${changed_py_files[*]}"
    echo "REQUIREMENTS:$changed_requirements"
    echo "NGINX:$changed_nginx_config"
    echo "SYSTEMD:$changed_systemd_service"
    echo "STATIC:$changed_static_files"
}

# Backup current deployment
backup_current() {
    local backup_timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_path="$BACKUP_DIR/backup_$backup_timestamp"

    log "Backing up current deployment to $backup_path"

    # Copy current app directory (excluding large directories)
    rsync -a --exclude='.git' --exclude='.venv' --exclude='__pycache__' \
        --exclude='*.pyc' --exclude='*.pyo' \
        "$APP_DIR/" "$backup_path/" || {
        log "WARNING: Backup failed, continuing anyway"
        return 0
    }

    # Rotate backups (keep last 3)
    ls -1td "$BACKUP_DIR"/backup_* 2>/dev/null | tail -n +4 | xargs rm -rf 2>/dev/null || true

    echo "$backup_path"
}

# Copy new code
copy_new_code() {
    log "Copying new code from $NEW_CODE_DIR to $APP_DIR"

    # Use rsync to copy files
    rsync -a --delete \
        --exclude='.git' \
        --exclude='.venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='*.pyo' \
        "$NEW_CODE_DIR/" "$APP_DIR/" || {
        log "ERROR: Failed to copy new code"
        exit 1
    }

    log "Code copy completed"
}

# Conditional operations
perform_conditional_operations() {
    local change_info="$1"
    local changed_requirements=false
    local changed_py_files=false
    local changed_nginx_config=false
    local changed_systemd_service=false
    local changed_static_files=false

    # Parse change info
    while IFS= read -r line; do
        case "$line" in
            PY_FILES:*)
                py_files="${line#PY_FILES:}"
                if [ -n "$py_files" ] && [ "$py_files" != "" ]; then
                    changed_py_files=true
                fi
                ;;
            REQUIREMENTS:*)
                changed_requirements="${line#REQUIREMENTS:}"
                ;;
            NGINX:*)
                changed_nginx_config="${line#NGINX:}"
                ;;
            SYSTEMD:*)
                changed_systemd_service="${line#SYSTEMD:}"
                ;;
            STATIC:*)
                changed_static_files="${line#STATIC:}"
                ;;
        esac
    done <<< "$change_info"

    log "Change analysis:"
    log "  Python files: $changed_py_files"
    log "  Requirements: $changed_requirements"
    log "  Nginx config: $changed_nginx_config"
    log "  Systemd service: $changed_systemd_service"
    log "  Static files: $changed_static_files"

    # 1. Install dependencies if requirements.txt changed
    if [ "$changed_requirements" = "true" ]; then
        log "Installing/updating dependencies from requirements.txt"
        if [ -f "$APP_DIR/requirements.txt" ]; then
            source "$VENV_DIR/bin/activate" 2>/dev/null || true
            pip install -r "$APP_DIR/requirements.txt" || {
                log "WARNING: pip install failed, but continuing"
            }
        else
            log "WARNING: requirements.txt not found"
        fi
    fi

    # 2. Restart Flask service if Python files changed
    if [ "$changed_py_files" = "true" ]; then
        log "Restarting Flask service ($SERVICE_NAME)"
        sudo systemctl restart "$SERVICE_NAME" || {
            log "WARNING: Service restart failed"
        }
    fi

    # 3. Reload Nginx if config changed
    if [ "$changed_nginx_config" = "true" ]; then
        log "Reloading Nginx configuration"
        sudo systemctl reload nginx || {
            log "WARNING: Nginx reload failed"
        }
    fi

    # 4. Reload systemd and restart service if systemd service file changed
    if [ "$changed_systemd_service" = "true" ]; then
        log "Updating systemd service configuration"
        sudo cp "$APP_DIR/systemd/blog.service" /etc/systemd/system/ || {
            log "ERROR: Failed to copy systemd service file"
            exit 1
        }
        sudo systemctl daemon-reload
        sudo systemctl restart "$SERVICE_NAME" || {
            log "WARNING: Service restart failed after systemd update"
        }
    fi

    # 5. If only static files changed, no restart needed
    if [ "$changed_static_files" = "true" ] && \
       [ "$changed_py_files" = "false" ] && \
       [ "$changed_requirements" = "false" ] && \
       [ "$changed_nginx_config" = "false" ] && \
       [ "$changed_systemd_service" = "false" ]; then
        log "Only static files changed - no service restart required"
    fi
}

# Main deployment function
deploy_main() {
    log "Starting deployment process"

    # Get change information
    change_info=$(check_changed_files)

    # Create backup
    backup_path=$(backup_current)

    # Copy new code
    copy_new_code

    # Perform conditional operations
    perform_conditional_operations "$change_info"

    log "Deployment completed successfully"
    log "Backup saved at: $backup_path"
}

# Cleanup on exit
cleanup() {
    if [ -d "$NEW_CODE_DIR" ] && [ "$NEW_CODE_DIR" != "/" ]; then
        rm -rf "$NEW_CODE_DIR" 2>/dev/null || true
    fi
}

# Set trap for cleanup
trap cleanup EXIT

# Run main function
deploy_main

exit 0