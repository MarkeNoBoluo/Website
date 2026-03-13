#!/usr/bin/env python3
"""
Test script for Nginx configuration validation.
Since Nginx is not available on Windows development environment,
this script validates the configuration file structure and simulates tests.
Actual Nginx testing will be performed on Raspberry Pi Linux environment.
"""

import os
import sys
import re
from pathlib import Path

def validate_nginx_config():
    """Validate Nginx configuration file structure."""
    config_path = Path("nginx/blog.conf")

    if not config_path.exists():
        print("[ERROR] Nginx configuration file not found: nginx/blog.conf")
        return False

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"[ERROR] Failed to read Nginx config: {e}")
        return False

    print(f"[OK] Nginx configuration file exists: {config_path}")

    # Check for required configuration elements
    checks = [
        ("Unix socket proxy", r'proxy_pass\s+http://unix:/tmp/blog\.sock:'),
        ("Static file serving", r'location\s+/static/\s*{'),
        ("Gzip compression", r'gzip\s+on;'),
        ("Client body size limit", r'client_max_body_size\s+10M;'),
        ("No caching headers", r'Cache-Control\s+"no-cache,\s+no-store,\s+must-revalidate"'),
    ]

    all_passed = True
    for check_name, pattern in checks:
        if re.search(pattern, content):
            print(f"  [OK] {check_name} configured")
        else:
            print(f"  [ERROR] {check_name} missing or incorrect")
            all_passed = False

    # Check static file path
    if 'alias /home/pi/blog/app/static/' in content:
        print("  [OK] Static file alias path correct")
    else:
        print("  [ERROR] Static file alias path incorrect")
        all_passed = False

    return all_passed

def test_static_file():
    """Test static file creation and content."""
    static_file = Path("app/static/test.txt")

    if not static_file.exists():
        print("[ERROR] Test static file not found: app/static/test.txt")
        return False

    try:
        with open(static_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
    except Exception as e:
        print(f"[ERROR] Failed to read static file: {e}")
        return False

    if content == "Test static file content":
        print(f"[OK] Static file exists with correct content: {static_file}")
        return True
    else:
        print(f"[ERROR] Static file content incorrect. Got: {content}")
        return False

def simulate_nginx_tests():
    """Simulate Nginx tests that would run on Linux."""
    print("\n=== Simulating Nginx Tests (Linux environment) ===")
    print("Note: Actual Nginx execution requires Linux/Raspberry Pi environment")
    print("\nTests that would be performed on Raspberry Pi:")
    print("1. sudo nginx -t -c /home/pi/blog/nginx/blog.conf")
    print("   - Should return 'syntax is ok' and 'test is successful'")
    print("\n2. Start Gunicorn with Unix socket:")
    print("   - gunicorn -c gunicorn.conf.py")
    print("\n3. Start Nginx with test config")
    print("\n4. Test static file serving:")
    print("   - curl http://localhost/static/test.txt")
    print("   - Should return 'Test static file content'")
    print("\n5. Test reverse proxy to Flask:")
    print("   - curl http://localhost/")
    print("   - Should return 'Hello, world!' from Flask via Gunicorn")
    print("\n6. Test gzip compression:")
    print("   - curl -H 'Accept-Encoding: gzip' -I http://localhost/")
    print("   - Check response includes 'Content-Encoding: gzip'")
    print("\n7. Test client limits:")
    print("   - Try to POST large data (>10MB)")
    print("   - Should receive 413 Request Entity Too Large error")
    print("\n8. Clean up test Nginx instance")

    return True

def main():
    """Main test function."""
    print("=== Nginx Configuration Validation Test ===\n")

    # Validate configuration file
    if not validate_nginx_config():
        print("\n[FAILED] Nginx configuration validation failed")
        return 1

    # Test static file
    if not test_static_file():
        print("\n[FAILED] Static file test failed")
        return 1

    # Simulate Nginx tests
    simulate_nginx_tests()

    print("\n=== Test Summary ===")
    print("[OK] Nginx configuration file validated")
    print("[OK] Static file test passed")
    print("[INFO] Actual Nginx execution requires Linux/Raspberry Pi environment")
    print("[INFO] Socket permissions note: Nginx (www-data) needs access to /tmp/blog.sock")
    print("      Solution: sudo usermod -a -G pi www-data then restart Nginx")

    return 0

if __name__ == "__main__":
    sys.exit(main())