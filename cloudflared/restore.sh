#!/bin/bash
# Cloudflare Tunnel Configuration Restore Script
# Restores tunnel configuration and credentials from backup

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
USER_CONFIG_DIR="/home/pi/.cloudflared"
APP_DIR="/home/pi/blog"
SERVICE_NAME="cloudflared.service"

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
        log "Some operations may require 'pi' user permissions."
        read -p "Continue anyway? [y/N]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# List available backups
list_backups() {
    log "Available backups in $BACKUP_ROOT:"

    if [ ! -d "$BACKUP_ROOT" ]; then
        log_error "Backup directory not found: $BACKUP_ROOT"
        return 1
    fi

    local backups
    backups=$(find "$BACKUP_ROOT" -maxdepth 1 -type d -name "20[0-9][0-9]-[0-1][0-9]-[0-3][0-9]-[0-2][0-9][0-5][0-9][0-5][0-9]" | sort -r 2>/dev/null || true)

    if [ -z "$backups" ]; then
        log_error "No backups found"
        return 1
    fi

    local count=0
    local backup_list=()
    for backup in $backups; do
        count=$((count + 1))
        backup_list+=("$backup")
        local size
        size=$(du -sh "$backup" 2>/dev/null | cut -f1 || echo "unknown")
        local date_str
        date_str=$(basename "$backup")
        echo "  $count. $date_str ($size)"
    done

    echo ""
    log "Total backups available: $count"

    # Return backup list as array (through global variable)
    RESTORE_BACKUP_LIST=("${backup_list[@]}")
}

# Select backup interactively
select_backup() {
    list_backups || return 1

    echo ""
    read -p "Select backup number to restore (1-$count): " selection

    # Validate selection
    if ! [[ "$selection" =~ ^[0-9]+$ ]] || [ "$selection" -lt 1 ] || [ "$selection" -gt "$count" ]; then
        log_error "Invalid selection: $selection"
        return 1
    fi

    # Adjust for zero-based array index
    local index=$((selection - 1))
    local selected_backup="${RESTORE_BACKUP_LIST[$index]}"

    echo ""
    log "Selected backup: $selected_backup"

    # Show backup contents
    log "Backup contents:"
    find "$selected_backup" -type f -name "*" | sort | sed 's/^/  /'

    echo ""
    read -p "Continue with restore? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Restore cancelled"
        exit 0
    fi

    echo "$selected_backup"
}

# Validate backup contents
validate_backup() {
    local backup_dir="$1"

    log "Validating backup contents..."

    local missing_files=0

    # Check for critical files
    local critical_files=("config.yml")
    for file in "${critical_files[@]}"; do
        if [ ! -f "$backup_dir/$file" ]; then
            log_warning "Critical file missing: $file"
            missing_files=$((missing_files + 1))
        fi
    done

    # Check for at least one credential file
    local cred_files
    cred_files=$(find "$backup_dir" -name "*.json" -o -name "cert.pem" 2>/dev/null | head -2)

    if [ -z "$cred_files" ]; then
        log_warning "No credential files found (cert.pem or *.json)"
        missing_files=$((missing_files + 1))
    fi

    if [ $missing_files -gt 0 ]; then
        log_warning "Backup is missing $missing_files critical file(s)"
        read -p "Continue with restore anyway? [y/N]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "Restore cancelled due to missing files"
            exit 1
        fi
    else
        log_success "Backup validation passed"
    fi
}

# Create restore point (backup current configuration)
create_restore_point() {
    log "Creating restore point of current configuration..."

    local restore_point_dir
    restore_point_dir="$BACKUP_ROOT/restore_point_$(date '+%Y-%m-%d-%H%M%S')"

    mkdir -p "$restore_point_dir"

    # Backup current credentials
    if [ -d "$USER_CONFIG_DIR" ]; then
        cp -r "$USER_CONFIG_DIR"/* "$restore_point_dir/" 2>/dev/null || true
    fi

    log_success "Restore point created: $restore_point_dir"
    echo "$restore_point_dir"
}

# Restore tunnel credentials
restore_credentials() {
    local backup_dir="$1"

    log "Restoring tunnel credentials..."

    # Ensure user config directory exists
    mkdir -p "$USER_CONFIG_DIR"

    # Restore certificate file
    if [ -f "$backup_dir/cert.pem" ]; then
        cp "$backup_dir/cert.pem" "$USER_CONFIG_DIR/cert.pem"
        chmod 600 "$USER_CONFIG_DIR/cert.pem"
        log_success "Restored cert.pem"
    fi

    # Restore tunnel JSON files
    local json_files
    json_files=$(find "$backup_dir" -name "*.json" -type f 2>/dev/null || true)

    if [ -n "$json_files" ]; then
        for json_file in $json_files; do
            local filename
            filename=$(basename "$json_file")
            cp "$json_file" "$USER_CONFIG_DIR/$filename"
            chmod 600 "$USER_CONFIG_DIR/$filename"
            log_success "Restored $filename"
        done
    fi

    # Restore config.yml
    if [ -f "$backup_dir/config.yml" ]; then
        cp "$backup_dir/config.yml" "$USER_CONFIG_DIR/config.yml"
        chmod 644 "$USER_CONFIG_DIR/config.yml"
        log_success "Restored config.yml"
    else
        log_error "config.yml not found in backup"
        return 1
    fi
}

# Restore environment variables
restore_env_vars() {
    local backup_dir="$1"
    local env_file="$APP_DIR/.env"
    local env_backup_file="$backup_dir/env_vars.txt"

    log "Restoring environment variables..."

    if [ ! -f "$env_backup_file" ]; then
        log_warning "Environment variables backup not found: $env_backup_file"
        return 0
    fi

    if [ ! -f "$env_file" ]; then
        log_warning "Environment file not found: $env_file"
        log "Creating new environment file from backup..."
        cp "$env_backup_file" "$env_file"
        chmod 600 "$env_file"
        log_success "Created $env_file from backup"
        return 0
    fi

    # Backup current environment file
    local env_backup
    env_backup="$env_file.backup.$(date '+%Y%m%d_%H%M%S')"
    cp "$env_file" "$env_backup"
    log_success "Backed up current environment file: $env_backup"

    # Update environment variables
    while IFS= read -r line; do
        if [[ "$line" =~ ^([A-Z_]+)=(.*)$ ]]; then
            local var_name="${BASH_REMATCH[1]}"
            local var_value="${BASH_REMATCH[2]}"

            # Check if variable exists in current file
            if grep -q "^$var_name=" "$env_file"; then
                # Update existing variable
                sed -i "s|^$var_name=.*|$var_name=$var_value|" "$env_file"
                log "Updated $var_name"
            else
                # Add new variable
                echo "$var_name=$var_value" >> "$env_file"
                log "Added $var_name"
            fi
        fi
    done < "$env_backup_file"

    log_success "Environment variables restored"
}

# Restart tunnel service
restart_tunnel_service() {
    log "Restarting tunnel service..."

    if ! command -v systemctl >/dev/null 2>&1; then
        log_warning "systemctl not found, cannot restart service"
        return 0
    fi

    # Check if service exists
    if ! systemctl list-unit-files | grep -q "^$SERVICE_NAME"; then
        log_warning "Service $SERVICE_NAME not found"
        return 0
    fi

    log "Restarting $SERVICE_NAME..."
    if sudo systemctl restart "$SERVICE_NAME"; then
        log_success "Service restarted successfully"
    else
        log_error "Failed to restart service"
        return 1
    fi

    # Wait a moment and check status
    sleep 2
    log "Service status:"
    sudo systemctl status "$SERVICE_NAME" --no-pager | head -10
}

# Validate restore
validate_restore() {
    local backup_dir="$1"

    log "Validating restore..."

    # Check if config.yml was restored
    if [ ! -f "$USER_CONFIG_DIR/config.yml" ]; then
        log_error "Restore failed: config.yml not found in $USER_CONFIG_DIR"
        return 1
    fi

    # Check config.yml syntax (basic check)
    if command -v cloudflared >/dev/null 2>&1; then
        log "Validating restored configuration..."
        if cloudflared tunnel ingress validate "$USER_CONFIG_DIR/config.yml" >/dev/null 2>&1; then
            log_success "Restored configuration is valid"
        else
            log_warning "Restored configuration validation failed"
            log "Check the configuration file: $USER_CONFIG_DIR/config.yml"
        fi
    fi

    log_success "Restore validation completed"
}

# Show restore summary
show_restore_summary() {
    local backup_dir="$1"
    local restore_point_dir="$2"

    log_success "Restore completed successfully!"
    echo ""
    log "Restore Summary:"
    echo "---------------"
    echo "Source backup: $backup_dir"
    echo "Restore point: $restore_point_dir"
    echo "Restored to: $USER_CONFIG_DIR"
    echo ""
    log "Restored files:"
    find "$USER_CONFIG_DIR" -type f -name "*" | sort | sed 's/^/  /'
    echo ""
    log "Next steps:"
    echo "1. Verify the tunnel is running: sudo systemctl status cloudflared.service"
    echo "2. Check logs: sudo journalctl -u cloudflared.service -n 20"
    echo "3. Test connectivity: curl -I https://your-domain.example.com"
    echo ""
    log "If you encounter issues, you can restore from the restore point:"
    echo "  $restore_point_dir"
}

# Main restore function
restore_main() {
    log "Starting Cloudflare Tunnel configuration restore"
    echo ""

    # Check user
    check_user

    # Select backup
    local backup_dir
    backup_dir=$(select_backup) || exit 1

    # Validate backup
    validate_backup "$backup_dir"

    # Create restore point
    local restore_point_dir
    restore_point_dir=$(create_restore_point)

    # Perform restore
    restore_credentials "$backup_dir"
    restore_env_vars "$backup_dir"

    # Validate restore
    validate_restore "$backup_dir"

    # Restart service
    restart_tunnel_service

    # Show summary
    show_restore_summary "$backup_dir" "$restore_point_dir"
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTION]"
        echo ""
        echo "Cloudflare Tunnel Configuration Restore Script"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --list, -l     List available backups only"
        echo "  --backup DIR   Restore from specific backup directory"
        echo ""
        echo "This script restores Cloudflare Tunnel configuration from backup."
        echo "A restore point is automatically created before restoration."
        echo "The tunnel service is restarted after restoration."
        exit 0
        ;;
    --list|-l)
        list_backups
        exit 0
        ;;
    --backup)
        if [ -z "${2:-}" ]; then
            log_error "Backup directory required with --backup option"
            exit 1
        fi
        BACKUP_DIR="$2"
        if [ ! -d "$BACKUP_DIR" ]; then
            log_error "Backup directory not found: $BACKUP_DIR"
            exit 1
        fi
        validate_backup "$BACKUP_DIR"
        create_restore_point
        restore_credentials "$BACKUP_DIR"
        restore_env_vars "$BACKUP_DIR"
        validate_restore "$BACKUP_DIR"
        restart_tunnel_service
        log_success "Restore from $BACKUP_DIR completed"
        exit 0
        ;;
    *)
        restore_main
        ;;
esac

exit 0