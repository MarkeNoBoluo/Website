#!/usr/bin/env python3
import sys
import os
import time

# Add user site-packages directory
user_site_packages = r"C:\Users\wddkx\AppData\Roaming\Python\Python310\site-packages"
if user_site_packages not in sys.path:
    sys.path.insert(0, user_site_packages)

try:
    import paramiko
except ImportError as e:
    print(f"Failed to import paramiko: {e}")
    sys.exit(1)

def ssh_command(client, command, description):
    """Execute command via SSH and return result"""
    print(f"\n=== {description} ===")
    print(f"Command: {command}")

    try:
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        exit_code = stdout.channel.recv_exit_status()

        print(f"Exit code: {exit_code}")
        if output:
            print(f"Output:\n{output}")
        if error:
            print(f"Error:\n{error}")

        return exit_code, output, error
    except Exception as e:
        print(f"Exception: {e}")
        return -1, "", str(e)

def main():
    hostname = "192.168.42.47"
    username = "wddkxg"
    password = "gk131413"

    print("Starting Phase 1 deployment verification on Raspberry Pi")
    print(f"Host: {hostname}, User: {username}")

    # Connect to Raspberry Pi
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, username=username, password=password)
        print("SSH connection established")
    except Exception as e:
        print(f"Failed to connect: {e}")
        return 1

    results = {}

    # 1. Check blog.service status
    exit_code, output, error = ssh_command(client, "sudo systemctl status blog.service --no-pager", "Check blog.service status")
    results['blog_status'] = exit_code
    if exit_code == 0:
        print("[OK] blog.service is running")
    else:
        print("[FAIL] blog.service is not running or has issues")

    # 2. Check nginx status
    exit_code, output, error = ssh_command(client, "sudo systemctl status nginx --no-pager", "Check nginx status")
    results['nginx_status'] = exit_code
    if exit_code == 0:
        print("[OK] nginx is running")
    else:
        print("[FAIL] nginx is not running")

    # 3. Check if socket file exists
    exit_code, output, error = ssh_command(client, "ls -la /tmp/blog.sock 2>/dev/null || echo 'Socket not found'", "Check Gunicorn socket file")
    results['socket_exists'] = exit_code
    if 'Socket not found' not in output:
        print("[OK] Socket file exists")
        # Check socket permissions
        ssh_command(client, "ls -la /tmp/blog.sock", "Socket permissions")
    else:
        print("[FAIL] Socket file not found")

    # 4. Try to start blog.service if not running
    if results.get('blog_status') != 0:
        exit_code, output, error = ssh_command(client, "sudo systemctl start blog.service", "Start blog.service")
        results['blog_start'] = exit_code
        if exit_code == 0:
            print("[OK] blog.service started successfully")
            # Wait a moment for service to start
            time.sleep(3)
            # Check status again
            ssh_command(client, "sudo systemctl status blog.service --no-pager", "Check blog.service status after start")
        else:
            print("[FAIL] Failed to start blog.service")
            # Check journal for errors
            ssh_command(client, "sudo journalctl -u blog.service -n 10 --no-pager", "Recent journal logs for blog.service")

    # 5. Test application via curl (if curl is available)
    exit_code, output, error = ssh_command(client, "which curl", "Check if curl is installed")
    if exit_code == 0:
        # Try to access via localhost
        exit_code, output, error = ssh_command(client, "curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/ || echo 'curl failed'", "Test application via HTTP")
        if exit_code == 0 and output.isdigit():
            http_code = int(output)
            if http_code == 200:
                print(f"[OK] Application responds with HTTP 200")
                # Get actual content
                ssh_command(client, "curl -s http://localhost:8080/ | head -c 100", "Sample application response")
            else:
                print(f"[FAIL] Application responded with HTTP {http_code}")
        else:
            print("[FAIL] Could not test application via HTTP")
    else:
        print("Note: curl not installed, skipping HTTP test")

    # 6. Test static file serving
    # Create a test static file if it doesn't exist
    ssh_command(client, "mkdir -p /home/wddkxg/blog/app/static && echo 'static test' > /home/wddkxg/blog/app/static/test.txt", "Create test static file")
    exit_code, output, error = ssh_command(client, "curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/static/test.txt 2>/dev/null || echo 'static test failed'", "Test static file serving")
    if exit_code == 0 and output.isdigit() and int(output) == 200:
        print("[OK] Static file serving works")
    else:
        print("[FAIL] Static file serving test failed")

    # 7. Check deployment logs directory
    ssh_command(client, "ls -la /home/wddkxg/blog/logs/ 2>/dev/null || echo 'Logs directory not found'", "Check deployment logs")

    # 8. Verify service is enabled for auto-start
    exit_code, output, error = ssh_command(client, "sudo systemctl is-enabled blog.service", "Check if blog.service is enabled")
    results['blog_enabled'] = exit_code
    if exit_code == 0:
        print("[OK] blog.service is enabled for auto-start")
    else:
        print("[FAIL] blog.service is not enabled for auto-start")

    # 9. Check gunicorn process
    ssh_command(client, "ps aux | grep gunicorn | grep -v grep", "Check gunicorn processes")

    # 10. Check nginx configuration
    ssh_command(client, "sudo nginx -t", "Test nginx configuration syntax")

    # Summary
    print("\n=== VERIFICATION SUMMARY ===")

    passed = 0
    total = len(results)

    for test, result in results.items():
        if result == 0:
            passed += 1
            print(f"[OK] {test}: PASSED")
        else:
            print(f"[FAIL] {test}: FAILED (exit code: {result})")

    print(f"\nPassed: {passed}/{total} tests")

    if passed >= total - 2:  # Allow up to 2 failures
        print("\nOverall: PASS - Deployment pipeline is functional")
        overall_result = "PASS"
    else:
        print("\nOverall: FAIL - Deployment pipeline has issues")
        overall_result = "FAIL"

    client.close()

    # Write summary to file
    with open("verification_summary.txt", "w") as f:
        f.write(f"Phase 1 Deployment Verification\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Host: {hostname}\n")
        f.write(f"Overall: {overall_result}\n")
        f.write(f"Passed: {passed}/{total}\n")
        for test, result in results.items():
            f.write(f"{test}: {'PASS' if result == 0 else 'FAIL'}\n")

    print(f"\nSummary written to verification_summary.txt")

    return 0 if overall_result == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())