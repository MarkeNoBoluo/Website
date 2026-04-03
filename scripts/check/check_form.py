import urllib.request
import urllib.parse
import http.cookiejar
import re

# Login first to get session
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Get login page to get CSRF token
login_page = opener.open("http://localhost:5000/auth/login")
content = login_page.read().decode()
match = re.search(r'name="csrf_token" value="([^"]+)"', content)
csrf = match.group(1) if match else ""

print(f"CSRF token: {csrf[:30]}...")

# Login
login_data = urllib.parse.urlencode(
    {"username": "admin", "password": "admin123", "csrf_token": csrf}
).encode()
opener.open("http://localhost:5000/auth/login", login_data)

# Get create article page
resp = opener.open("http://localhost:5000/admin/articles/new")
content = resp.read().decode()
has_title = 'name="title"' in content
has_content = 'name="content"' in content
has_csrf = 'name="csrf_token"' in content
has_status = 'name="status"' in content

print(f"\nCreate article page length: {len(content)}")
print(f"Has title input: {has_title}")
print(f"Has content textarea: {has_content}")
print(f"Has csrf_token: {has_csrf}")
print(f"Has status select: {has_status}")

# Get actual form content
title_match = re.search(r'<input[^>]*name="title"[^>]*>', content)
print(f"\nTitle input HTML: {title_match.group(0) if title_match else 'NOT FOUND'}")
