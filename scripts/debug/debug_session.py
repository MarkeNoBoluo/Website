import urllib.request
import urllib.parse
import http.cookiejar

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Step 1: Access blog - this sets the session cookie
print("1. Access blog...")
resp = opener.open("http://localhost:5000/blog/")
print(f"   Status: {resp.status}")
print(f"   Cookies: {[c.name for c in cj]}")

# Step 2: Access login - should work but returns 500
print("\n2. Access login (with session cookie)...")
try:
    resp = opener.open("http://localhost:5000/auth/login")
    print(f"   Status: {resp.status}")
except Exception as e:
    print(f"   Error: {e}")

# Step 3: Fresh context - no session cookie
print("\n3. Fresh context - no session cookie...")
cj2 = http.cookiejar.CookieJar()
opener2 = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj2))
try:
    resp = opener2.open("http://localhost:5000/auth/login")
    print(f"   Status: {resp.status}")
    content = resp.read().decode()
    print(f"   Content length: {len(content)}")
    print(f"   Has form: {'<form' in content}")
except Exception as e:
    print(f"   Error: {e}")
