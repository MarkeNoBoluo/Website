#!/bin/bash
# Cloudflare Tunnel Configuration Backup Script
# Backs up tunnel configuration and credentials for disaster recovery

set -e
set -u

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKUP_ROOT="/home/pi/.cloudflared/backups"
MAX_BACKUP_DAYS=7
APP_DIR="/home/pi/blog"
USER_CONFIG_DIR="/home/pi/.cloudflared"
PROJECT_CONFIG_DIR="$APP_DIR/cloudflared"

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $*"
}

log_success() {
    echo -e "${GREEN}✓${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $*"
}

log_error() {
    echo -e "${RED}✗${NC} $*"
}

# Check if running as correct user
check_user() {
    if [ "$(whoami)" != "pi" ]; then
        log_warning "Script is running as $(whoami), recommended to run as 'pi' user"
        log "Some files may not be accessible due to permissions."
        read -p "Continue anyway? [y/N]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Create backup directory
create_backup_dir() {
    local timestamp
    timestamp=$(date '+%Y-%m-%d-%H%M%S')
    local backup_dir="$BACKUP_ROOT/$timestamp"

    log "Creating backup directory: $backup_dir"
    mkdir -p "$backup_dir"

    echo "$backup_dir"
}

# Backup tunnel credentials
backup_credentials() {
    local backup_dir="$1"
    local creds_dir="$USER_CONFIG_DIR"

    log "Backing up tunnel credentials..."

    # Check if credentials directory exists
    if [ ! -d "$creds_dir" ]; then
        log_warning "Credentials directory not found: $creds_dir"
        return 1
    fi

    # Backup certificate file
    if [ -f "$creds_dir/cert.pem" ]; then
        cp "$creds_dir/cert.pem" "$backup_dir/cert.pem"
        log_success "Backed up cert.pem"
    else
        log_warning "cert.pem not found: $creds_dir/cert.pem"
    fi

    # Backup tunnel JSON files
    local json_files
    json_files=$(find "$creds_dir" -name "*.json" -type f 2>/dev/null || true)

    if [ -n "$json_files" ]; then
        for json_file in $json_files; do
            local filename
            filename=$(basename "$json_file")
            cp "$json_file" "$backup_dir/$filename"
            log_success "Backed up $filename"
        done
    else
        log_warning "No tunnel JSON files found in $creds_dir"
    fi

    # Backup config.yml if exists
    if [ -f "$creds_dir/config.yml" ]; then
        cp "$creds_dir/config.yml" "$backup_dir/config.yml"
        log_success "Backed up config.yml"
    else
        log_warning "config.yml not found: $creds_dir/config.yml"
    fi
}

# Backup project configuration
backup_project_config() {
    local backup_dir="$1"

    log "Backing up project configuration..."

    # Check if project config directory exists
    if [ ! -d "$PROJECT_CONFIG_DIR" ]; then
        log_warning "Project config directory not found: $PROJECT_CONFIG_DIR"
        return 1
    fi

    # Create project config subdirectory
    mkdir -p "$backup_dir/project"

    # Backup all files in cloudflared directory
    if [ -d "$PROJECT_CONFIG_DIR" ]; then
        cp -r "$PROJECT_CONFIG_DIR"/* "$backup_dir/project/" 2>/dev/null || true
        log_success "Backed up project configuration files"
    fi
}

# Backup environment variables
backup_env_vars() {
    local backup_dir="$1"
    local env_file="$APP_DIR/.env"

    log "Backing up environment variables..."

    if [ -f "$env_file" ]; then
        # Extract only Cloudflare Tunnel related variables
        grep -E "^(CLOUDFLARE_TUNNEL_ID|DOMAIN|BLOG_SUBDOMAIN|STATUS_SUBDOMAIN)=" "$env_file" > "$backup_dir/env_vars.txt" 2>/dev/null || true

        if [ -s "$backup_dir/env_vars.txt" ]; then
            log_success "Backed up tunnel environment variables"
            log "Environment variables backed up:"
            cat "$backup_dir/env_vars.txt"
        else
            log_warning "No Cloudflare Tunnel environment variables found in $env_file"
            rm -f "$backup_dir/env_vars.txt"
        fi
    else
        log_warning "Environment file not found: $env_file"
    fi
}

# Create backup summary
create_backup_summary() {
    local backup_dir="$1"

    log "Creating backup summary..."

    local summary_file="$backup_dir/backup_summary.txt"
    {
        echo "Cloudflare Tunnel Backup Summary"
        echo "================================"
        echo "Backup created: $(date '+%Y-%m-%d %H:%M:%S %Z')"
        echo "Backup directory: $backup_dir"
        echo ""
        echo "Contents:"
        echo "---------"
        find "$backup_dir" -type f -name "*" | sort
        echo ""
        echo "File details:"
        echo "-------------"
        find "$backup_dir" -type f -exec ls -lh {} \;
    } > "$summary_file"

    log_success "Backup summary created: $summary_file"
}

# Calculate backup size
calculate_backup_size() {
    local backup_dir="$1"

    if [ -d "$backup_dir" ]; then
        du -sh "$backup_dir" | cut -f1
    else
        echo "0B"
    fi
}

# Clean up old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $MAX_BACKUP_DAYS days..."

    if [ ! -d "$BACKUP_ROOT" ]; then
        log_warning "Backup root directory not found: $BACKUP_ROOT"
        return 0
    fi

    # Find and delete backups older than MAX_BACKUP_DAYS
    local old_backups
    old_backups=$(find "$BACKUP_ROOT" -maxdepth 1 -type d -name "20[0-9][0-9]-[0-1][0-9]-[0-3][0-9]-[0-2][0-9][0-5][0-9][0-5][0-9]" -mtime +$MAX_BACKUP_DAYS 2>/dev/null || true)

    if [ -n "$old_backups" ]; then
        for backup in $old_backups; do
            log "Removing old backup: $backup"
            rm -rf "$backup"
        done
        log_success "Cleaned up $(echo "$old_backups" | wc -w) old backup(s)"
    else
        log "No old backups to clean up"
    fi
}

# List existing backups
list_existing_backups() {
    log "Existing backups in $BACKUP_ROOT:"

    if [ ! -d "$BACKUP_ROOT" ]; then
        log_warning "No backup directory found"
        return 1
    fi

    local backups
    backups=$(find "$BACKUP_ROOT" -maxdepth 1 -type d -name "20[0-9][0-9]-[0-1][0-9]-[0-3][0-9]-[0-2][0-9][0-5][0-9][0-5][0-9]" | sort -r 2>/dev/null || true)

    if [ -z "$backups" ]; then
        log "No backups found"
        return 1
    fi

    local count=0
    for backup in $backups; do
        count=$((count + 1))
        local size
        size=$(calculate_backup_size "$backup")
        local date_str
        date_str=$(basename "$backup")
        echo "  $count. $date_str ($size)"
    done

    echo ""
    log "Total backups: $count"
}

# Main backup function
backup_main() {
    log "Starting Cloudflare Tunnel configuration backup"
    echo ""

    # Check user
    check_user

    # Create backup directory
    local backup_dir
    backup_dir=$(create_backup_dir)

    # Perform backups
    backup_credentials "$backup_dir"
    backup_project_config "$backup_dir"
    backup_env_vars "$backup_dir"

    # Create summary
    create_backup_summary "$backup_dir"

    # Calculate and display backup size
    local backup_size
    backup_size=$(calculate_backup_size "$backup_dir")
    log_success "Backup completed: $backup_dir ($backup_size)"

    # Clean up old backups
    cleanup_old_backups

    # List existing backups
    list_existing_backups

    log_success "Backup process completed successfully!"
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTION]"
        echo ""
        echo "Cloudflare Tunnel Configuration Backup Script"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --list, -l     List existing backups"
        echo "  --cleanup      Clean up old backups only"
        echo ""
        echo "This script backs up Cloudflare Tunnel configuration and credentials."
        echo "Backups are stored in: $BACKUP_ROOT"
        echo "Backups older than $MAX_BACKUP_DAYS days are automatically cleaned up."
        exit 0
        ;;
    --list|-l)
        list_existing_backups
        exit 0
        ;;
    --cleanup)
        cleanup_old_backups
        exit 0
        ;;
    *)
        backup_main
        ;;
esac

exit 0