#!/bin/bash
# DNS automation setup script for Cloudflare Tunnel
# Creates CNAME records for blog and status subdomains

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to validate environment variable
validate_env_var() {
    local var_name="$1"
    local var_value="${!var_name}"

    if [ -z "$var_value" ]; then
        print_error "Environment variable $var_name is not set"
        echo "Please set $var_name in your .env file or export it:"
        echo "  export $var_name=\"your_value\""
        return 1
    fi
    return 0
}

# Main execution
main() {
    print_status "Starting DNS setup for Cloudflare Tunnel"
    echo "=============================================="

    # Check if cloudflared is installed
    if ! command_exists cloudflared; then
        print_error "cloudflared is not installed or not in PATH"
        echo "Please install cloudflared first:"
        echo "  https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/"
        exit 1
    fi

    # Check if user is logged in to Cloudflare
    print_status "Checking Cloudflare login status..."
    if ! cloudflared tunnel list >/dev/null 2>&1; then
        print_warning "Not logged in to Cloudflare or no tunnels found"
        echo "Please log in to Cloudflare:"
        echo "  cloudflared tunnel login"
        echo "Then create a tunnel if needed:"
        echo "  cloudflared tunnel create ${CLOUDFLARE_TUNNEL_ID:-your-tunnel-name}"
        exit 1
    fi

    # Validate required environment variables
    print_status "Validating environment variables..."

    local required_vars=(
        "CLOUDFLARE_TUNNEL_ID"
        "DOMAIN"
        "BLOG_SUBDOMAIN"
        "STATUS_SUBDOMAIN"
    )

    local missing_vars=()
    for var in "${required_vars[@]}"; do
        if ! validate_env_var "$var"; then
            missing_vars+=("$var")
        fi
    done

    if [ ${#missing_vars[@]} -gt 0 ]; then
        print_error "Missing required environment variables: ${missing_vars[*]}"
        echo ""
        echo "Please set these variables in your .env file:"
        echo "  CLOUDFLARE_TUNNEL_ID=your-tunnel-id"
        echo "  DOMAIN=yourdomain.com"
        echo "  BLOG_SUBDOMAIN=blog"
        echo "  STATUS_SUBDOMAIN=status"
        exit 1
    fi

    print_success "All environment variables validated"

    # Display configuration
    echo ""
    print_status "Configuration:"
    echo "  Tunnel ID: $CLOUDFLARE_TUNNEL_ID"
    echo "  Domain: $DOMAIN"
    echo "  Blog subdomain: ${BLOG_SUBDOMAIN}.${DOMAIN}"
    echo "  Status subdomain: ${STATUS_SUBDOMAIN}.${DOMAIN}"
    echo ""

    # Create blog subdomain CNAME record
    print_status "Creating blog subdomain CNAME record..."
    if cloudflared tunnel route dns "$CLOUDFLARE_TUNNEL_ID" "${BLOG_SUBDOMAIN}.${DOMAIN}"; then
        print_success "Blog subdomain CNAME record created: ${BLOG_SUBDOMAIN}.${DOMAIN}"
    else
        print_error "Failed to create blog subdomain CNAME record"
        echo "Check tunnel ID and domain permissions"
        exit 1
    fi

    # Create status subdomain CNAME record
    print_status "Creating status subdomain CNAME record..."
    if cloudflared tunnel route dns "$CLOUDFLARE_TUNNEL_ID" "${STATUS_SUBDOMAIN}.${DOMAIN}"; then
        print_success "Status subdomain CNAME record created: ${STATUS_SUBDOMAIN}.${DOMAIN}"
    else
        print_error "Failed to create status subdomain CNAME record"
        echo "Check tunnel ID and domain permissions"
        exit 1
    fi

    # Verify tunnel information
    print_status "Verifying tunnel configuration..."
    echo ""
    cloudflared tunnel info "$CLOUDFLARE_TUNNEL_ID"

    # Final instructions
    echo ""
    print_success "DNS setup completed successfully!"
    echo ""
    print_warning "DNS propagation may take several minutes to hours"
    echo "You can check DNS propagation with:"
    echo "  dig +short ${BLOG_SUBDOMAIN}.${DOMAIN}"
    echo "  dig +short ${STATUS_SUBDOMAIN}.${DOMAIN}"
    echo ""
    print_status "Next steps:"
    echo "1. Wait for DNS propagation (check with commands above)"
    echo "2. Test blog access: https://${BLOG_SUBDOMAIN}.${DOMAIN}"
    echo "3. Test health endpoint: https://${STATUS_SUBDOMAIN}.${DOMAIN}/health"
    echo "4. Monitor tunnel logs: sudo journalctl -u cloudflared.service -f"
}

# Run main function
main "$@"