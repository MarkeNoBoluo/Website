#!/bin/bash
# Cloudflare Tunnel First-Time Setup Script
# Guides users through initial tunnel setup and configuration

set -e
set -u

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/home/pi/blog"
CLOUDFLARED_CONFIG_DIR="$APP_DIR/cloudflared"
USER_CONFIG_DIR="/home/pi/.cloudflared"
TUNNEL_NAME="blog-tunnel"
ENV_FILE="$APP_DIR/.env"
ENV_EXAMPLE_FILE="$APP_DIR/.env.example"

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

# Check if running as root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        log_error "This script should not be run as root. Please run as 'pi' user."
        exit 1
    fi
}

# Check cloudflared installation
check_cloudflared() {
    log "Checking cloudflared installation..."

    if command -v cloudflared >/dev/null 2>&1; then
        local version
        version=$(cloudflared --version 2>/dev/null | head -n1 || echo "unknown")
        log_success "cloudflared is installed: $version"
        return 0
    else
        log_warning "cloudflared is not installed or not in PATH"
        return 1
    fi
}

# Provide cloudflared installation instructions
install_cloudflared_instructions() {
    log "To install cloudflared on Raspberry Pi (ARM64), run:"
    echo ""
    echo "  # Download the latest ARM64 binary"
    echo "  wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -O /usr/local/bin/cloudflared"
    echo ""
    echo "  # Set execute permissions"
    echo "  chmod +x /usr/local/bin/cloudflared"
    echo ""
    echo "  # Verify installation"
    echo "  cloudflared --version"
    echo ""
    log "After installation, run this script again to continue setup."
}

# Guide user through cloudflared tunnel login
guide_tunnel_login() {
    log "Step 1: Authenticate with Cloudflare"
    log "This will open a browser window for authentication."
    echo ""
    log "Run the following command:"
    echo ""
    echo "  cloudflared tunnel login"
    echo ""
    log "Follow the browser prompts to authenticate with your Cloudflare account."
    log "This will generate a certificate file at: ~/.cloudflared/cert.pem"
    echo ""
    read -p "Press Enter after completing authentication..."
}

# Guide user through tunnel creation
guide_tunnel_create() {
    log "Step 2: Create Cloudflare Tunnel"
    log "This will create a new tunnel and generate credentials."
    echo ""
    log "Run the following command:"
    echo ""
    echo "  cloudflared tunnel create $TUNNEL_NAME"
    echo ""
    log "The command will output a tunnel ID (UUID)."
    log "Example output:"
    echo ""
    echo "  Created tunnel $TUNNEL_NAME with id xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    echo ""
    log "Copy the tunnel ID (the UUID) for the next step."
    echo ""
    read -p "Enter the tunnel ID: " TUNNEL_ID

    # Validate tunnel ID format (basic UUID check)
    if [[ ! "$TUNNEL_ID" =~ ^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$ ]]; then
        log_warning "Tunnel ID doesn't look like a valid UUID. Continuing anyway..."
    fi

    echo "$TUNNEL_ID"
}

# Get domain information from user
get_domain_info() {
    log "Step 3: Configure domain settings"
    echo ""

    read -p "Enter your domain (e.g., example.com): " DOMAIN
    read -p "Enter blog subdomain [blog]: " BLOG_SUBDOMAIN
    BLOG_SUBDOMAIN=${BLOG_SUBDOMAIN:-blog}

    read -p "Enter status subdomain [status]: " STATUS_SUBDOMAIN
    STATUS_SUBDOMAIN=${STATUS_SUBDOMAIN:-status}

    echo "$DOMAIN $BLOG_SUBDOMAIN $STATUS_SUBDOMAIN"
}

# Generate environment variable suggestions
generate_env_suggestions() {
    local tunnel_id="$1"
    local domain="$2"
    local blog_subdomain="$3"
    local status_subdomain="$4"

    log "Step 4: Update environment variables"
    echo ""
    log "Add the following lines to your $ENV_FILE file:"
    echo ""
    echo "# Cloudflare Tunnel Configuration"
    echo "CLOUDFLARE_TUNNEL_ID=$tunnel_id"
    echo "DOMAIN=$domain"
    echo "BLOG_SUBDOMAIN=$blog_subdomain"
    echo "STATUS_SUBDOMAIN=$status_subdomain"
    echo ""

    # Check if .env file exists
    if [ -f "$ENV_FILE" ]; then
        log "Current $ENV_FILE contents:"
        echo "---"
        grep -E "^(CLOUDFLARE_TUNNEL_ID|DOMAIN|BLOG_SUBDOMAIN|STATUS_SUBDOMAIN)=" "$ENV_FILE" 2>/dev/null || echo "(not set)"
        echo "---"
        echo ""
        log "Update or add these variables to your $ENV_FILE file."
    else
        log_warning "$ENV_FILE file not found. Create it from the template:"
        echo ""
        echo "  cp $ENV_EXAMPLE_FILE $ENV_FILE"
        echo ""
        log "Then add the Cloudflare Tunnel variables shown above."
    fi
}

# Generate initial configuration
generate_initial_config() {
    local tunnel_id="$1"
    local domain="$2"
    local blog_subdomain="$3"
    local status_subdomain="$4"

    log "Step 5: Generate initial tunnel configuration"
    echo ""

    # Ensure user config directory exists
    mkdir -p "$USER_CONFIG_DIR"

    # Check if config template exists
    if [ ! -f "$CLOUDFLARED_CONFIG_DIR/config.yml" ]; then
        log_error "Config template not found: $CLOUDFLARED_CONFIG_DIR/config.yml"
        log "Make sure the project has been cloned correctly."
        return 1
    fi

    # Create a temporary config with environment variables replaced
    TEMP_CONFIG=$(mktemp)

    # Replace environment variables in config template
    sed \
        -e "s|\${CLOUDFLARE_TUNNEL_ID}|$tunnel_id|g" \
        -e "s|\${DOMAIN}|$domain|g" \
        -e "s|\${BLOG_SUBDOMAIN}|$blog_subdomain|g" \
        -e "s|\${STATUS_SUBDOMAIN}|$status_subdomain|g" \
        "$CLOUDFLARED_CONFIG_DIR/config.yml" > "$TEMP_CONFIG"

    # Copy to user config directory
    cp "$TEMP_CONFIG" "$USER_CONFIG_DIR/config.yml"
    rm -f "$TEMP_CONFIG"

    log_success "Configuration generated at: $USER_CONFIG_DIR/config.yml"

    # Show the generated config
    log "Generated configuration:"
    echo "---"
    cat "$USER_CONFIG_DIR/config.yml"
    echo "---"
}

# Validate configuration
validate_configuration() {
    log "Step 6: Validate tunnel configuration"
    echo ""

    if ! command -v cloudflared >/dev/null 2>&1; then
        log_warning "Skipping validation: cloudflared not found in PATH"
        return 0
    fi

    log "Running configuration validation..."
    if cloudflared tunnel ingress validate "$USER_CONFIG_DIR/config.yml" 2>&1; then
        log_success "Configuration validation passed"
    else
        local exit_code=$?
        log_warning "Configuration validation returned exit code: $exit_code"
        log "Check the configuration file for errors: $USER_CONFIG_DIR/config.yml"
    fi
}

# Provide next steps
show_next_steps() {
    local tunnel_id="$1"
    local domain="$2"
    local blog_subdomain="$3"
    local status_subdomain="$4"

    log "Step 7: Next steps"
    echo ""
    log_success "Initial setup completed!"
    echo ""
    log "To complete the setup, follow these steps:"
    echo ""
    echo "1. Deploy the systemd service:"
    echo "   sudo cp $APP_DIR/systemd/cloudflared.service /etc/systemd/system/"
    echo "   sudo systemctl daemon-reload"
    echo "   sudo systemctl enable cloudflared.service"
    echo ""
    echo "2. Create DNS routes:"
    echo "   cloudflared tunnel route dns $tunnel_id ${blog_subdomain}.${domain}"
    echo "   cloudflared tunnel route dns $tunnel_id ${status_subdomain}.${domain}"
    echo ""
    echo "3. Start the tunnel service:"
    echo "   sudo systemctl start cloudflared.service"
    echo ""
    echo "4. Check service status:"
    echo "   sudo systemctl status cloudflared.service"
    echo ""
    echo "5. View logs:"
    echo "   sudo journalctl -u cloudflared.service -f"
    echo ""
    log "Note: DNS propagation may take a few minutes to several hours."
    log "After DNS propagates, your site will be accessible at:"
    log "  Blog: https://${blog_subdomain}.${domain}"
    log "  Status: https://${status_subdomain}.${domain}"
}

# Main setup function
setup_main() {
    log "Starting Cloudflare Tunnel first-time setup"
    echo ""

    # Check prerequisites
    check_root

    if ! check_cloudflared; then
        install_cloudflared_instructions
        exit 1
    fi

    # Step 1: Tunnel login
    guide_tunnel_login

    # Step 2: Tunnel creation
    TUNNEL_ID=$(guide_tunnel_create)
    if [ -z "$TUNNEL_ID" ]; then
        log_error "Tunnel ID is required"
        exit 1
    fi

    # Step 3: Domain information
    DOMAIN_INFO=$(get_domain_info)
    read -r DOMAIN BLOG_SUBDOMAIN STATUS_SUBDOMAIN <<< "$DOMAIN_INFO"

    # Step 4: Environment variables
    generate_env_suggestions "$TUNNEL_ID" "$DOMAIN" "$BLOG_SUBDOMAIN" "$STATUS_SUBDOMAIN"

    echo ""
    read -p "Press Enter after updating your .env file..."

    # Step 5: Generate configuration
    generate_initial_config "$TUNNEL_ID" "$DOMAIN" "$BLOG_SUBDOMAIN" "$STATUS_SUBDOMAIN"

    # Step 6: Validate configuration
    validate_configuration

    # Step 7: Next steps
    show_next_steps "$TUNNEL_ID" "$DOMAIN" "$BLOG_SUBDOMAIN" "$STATUS_SUBDOMAIN"

    log_success "Setup script completed!"
    log "Refer to CONFIGURATION.md for detailed documentation."
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTION]"
        echo ""
        echo "Cloudflare Tunnel First-Time Setup Script"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --check        Check prerequisites only"
        echo ""
        echo "This script guides you through the initial Cloudflare Tunnel setup process."
        exit 0
        ;;
    --check)
        check_root
        check_cloudflared
        exit 0
        ;;
    *)
        setup_main
        ;;
esac

exit 0