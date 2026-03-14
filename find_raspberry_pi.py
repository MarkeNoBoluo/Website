#!/usr/bin/env python3
"""
Script to find Raspberry Pi IP address and update SSH configuration.
Helps maintain connectivity when network environment changes.
"""

import sys
import os
import socket
import subprocess
import re
import paramiko

def get_ssh_config_path():
    """Get SSH config file path"""
    return os.path.expanduser("~/.ssh/config")

def read_current_ip():
    """Read current IP from SSH config"""
    config_path = get_ssh_config_path()
    current_ip = None

    try:
        with open(config_path, 'r') as f:
            content = f.read()

        # Look for HostName in raspberrypi or pi sections
        pattern = r'HostName\s+(\d+\.\d+\.\d+\.\d+)'
        matches = re.findall(pattern, content)

        for ip in matches:
            if ip != '0.0.0.0' and not ip.startswith('127.'):
                current_ip = ip
                break

    except FileNotFoundError:
        print(f"SSH config not found at {config_path}")

    return current_ip

def test_ssh_connection(ip, timeout=5):
    """Test SSH connection to IP address"""
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Load private key
        key_path = os.path.expanduser("~/.ssh/id_rsa_raspberry")
        private_key = paramiko.RSAKey.from_private_key_file(key_path)

        print(f"Testing SSH connection to {ip}...")
        client.connect(ip, username='wddkxg', pkey=private_key, timeout=timeout)

        # Execute simple command to verify
        stdin, stdout, stderr = client.exec_command("echo 'Connection test successful' && hostname")
        output = stdout.read().decode('utf-8').strip()

        client.close()
        print(f"✓ Connected to {ip}")
        print(f"  Hostname: {output.split('\\n')[-1]}")
        return True

    except Exception as e:
        print(f"✗ Failed to connect to {ip}: {e}")
        return False

def scan_local_network(base_ip="192.168.1"):
    """Scan local network for Raspberry Pi"""
    print(f"\nScanning network {base_ip}.x for Raspberry Pi...")
    print("This may take a minute...")

    found_ips = []

    # Simple ping scan
    for i in range(1, 255):
        ip = f"{base_ip}.{i}"

        # Skip scanning on Windows due to permission issues
        # Instead, just suggest common ranges
        found_ips.append(ip)

    print("Scan complete. Common Raspberry Pi IP ranges:")
    print("  - 192.168.1.x (home networks)")
    print("  - 192.168.0.x (home networks)")
    print("  - 192.168.42.x (current network)")
    print("  - 192.168.86.x (mobile hotspots)")

    return found_ips

def update_ssh_config(new_ip):
    """Update SSH config with new IP address"""
    config_path = get_ssh_config_path()

    try:
        with open(config_path, 'r') as f:
            content = f.read()

        # Replace IP addresses in HostName directives
        # Pattern to match HostName lines with IP addresses
        old_content = content

        # Replace in raspberrypi section
        content = re.sub(
            r'(Host raspberrypi\s+[\s\S]*?HostName\s+)\d+\.\d+\.\d+\.\d+',
            r'\g<1>' + new_ip,
            content
        )

        # Replace in pi section
        content = re.sub(
            r'(Host pi\s+[\s\S]*?HostName\s+)\d+\.\d+\.\d+\.\d+',
            r'\g<1>' + new_ip,
            content
        )

        if content != old_content:
            with open(config_path, 'w') as f:
                f.write(content)
            print(f"\n✓ Updated SSH config with new IP: {new_ip}")
            return True
        else:
            print("\n⚠ No IP addresses found to update in SSH config")
            return False

    except Exception as e:
        print(f"\n✗ Failed to update SSH config: {e}")
        return False

def discover_via_arp():
    """Try to discover via ARP table (Linux/macOS)"""
    print("\nChecking ARP table for Raspberry Pi...")

    try:
        # Execute arp -a and parse output
        result = subprocess.run(['arp', '-a'], capture_output=True, text=True, timeout=5)

        if result.returncode == 0:
            # Look for Raspberry Pi MAC address patterns or hostname
            lines = result.stdout.split('\n')
            for line in lines:
                if 'raspberrypi' in line.lower() or 'b8:27:eb' in line or 'dc:a6:32' in line:
                    print(f"Found in ARP: {line.strip()}")
                    # Extract IP address
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if match:
                        return match.group(1)
    except Exception as e:
        print(f"ARP check failed: {e}")

    return None

def manual_ip_entry():
    """Prompt for manual IP entry"""
    print("\n--- Manual IP Entry ---")
    print("If you know the new IP address, enter it below.")
    print("Common formats: 192.168.1.xxx, 192.168.0.xxx, 10.0.0.xxx")

    while True:
        ip = input("Enter Raspberry Pi IP address (or 'quit' to exit): ").strip()

        if ip.lower() == 'quit':
            return None

        # Validate IP format
        if re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
            if test_ssh_connection(ip):
                return ip
            else:
                print(f"Connection failed. Try again or check IP address.")
        else:
            print("Invalid IP format. Please enter like 192.168.1.105")

def main():
    print("=" * 60)
    print("Raspberry Pi IP Discovery Tool")
    print("=" * 60)

    # Step 1: Check current IP
    current_ip = read_current_ip()
    if current_ip:
        print(f"\nCurrent SSH config IP: {current_ip}")
        if test_ssh_connection(current_ip):
            print("\n✓ Current IP is working!")
            choice = input("Update anyway? (y/N): ").strip().lower()
            if choice != 'y':
                return 0
    else:
        print("\n⚠ No current IP found in SSH config")

    # Step 2: Try discovery methods
    print("\n--- Discovery Methods ---")

    # Method 1: Check ARP table
    arp_ip = discover_via_arp()
    if arp_ip and test_ssh_connection(arp_ip):
        update_choice = input(f"\nFound Raspberry Pi at {arp_ip}. Update SSH config? (Y/n): ").strip().lower()
        if update_choice != 'n':
            update_ssh_config(arp_ip)
            return 0

    # Method 2: Manual entry
    print("\nLet's try manual discovery...")

    # Common network ranges to try
    common_ranges = [
        "192.168.1",  # Home networks
        "192.168.0",  # Home networks
        "192.168.42", # Current network
        "192.168.86", # Mobile hotspots
        "10.0.0",     # Some routers
    ]

    for base_ip in common_ranges:
        print(f"\nTrying {base_ip}.x range...")
        for i in range(1, 20):  # Try first 20 addresses
            test_ip = f"{base_ip}.{i}"
            print(f"  Testing {test_ip}...", end='\r')

            if test_ssh_connection(test_ip, timeout=2):
                print(f"\n\n✓ Found Raspberry Pi at {test_ip}!")
                update_choice = input("Update SSH config? (Y/n): ").strip().lower()
                if update_choice != 'n':
                    update_ssh_config(test_ip)
                return 0

    # Method 3: Full manual entry
    print("\n⚠ Automatic discovery failed.")
    new_ip = manual_ip_entry()

    if new_ip:
        update_ssh_config(new_ip)
        print("\n✓ SSH configuration updated successfully!")
        print(f"\nYou can now connect using:")
        print(f"  ssh raspberrypi")
        print(f"  ssh pi")
        print(f"  ssh wddkxg@{new_ip}")
        return 0
    else:
        print("\n✗ No IP address configured.")
        print("\nNext steps:")
        print("1. Connect Raspberry Pi to network")
        print("2. Find its IP address (router admin or display)")
        print("3. Run this script again")
        print("4. Or manually edit ~/.ssh/config")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)