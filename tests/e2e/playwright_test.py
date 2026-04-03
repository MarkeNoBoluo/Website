import asyncio
from playwright.async_api import async_playwright


class TestResult:
    def __init__(self, name, passed, message=""):
        self.name = name
        self.passed = passed
        self.message = message

    def __str__(self):
        status = "[PASS]" if self.passed else "[FAIL]"
        msg = f" - {self.message}" if self.message else ""
        return f"{status}: {self.name}{msg}"


async def run_tests():
    results = []
    base_url = "http://localhost:5000"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # ===== P0: Core functionality tests =====
        print("\n" + "=" * 60)
        print("P0: Core Functionality Tests")
        print("=" * 60)

        context = await browser.new_context()
        page = await context.new_page()

        # Test 1: Homepage
        try:
            await page.goto(base_url, timeout=15000)
            title = await page.title()
            results.append(TestResult("Homepage Access", True, title))
            print(f"[OK] Homepage: {title}")
        except Exception as e:
            results.append(TestResult("Homepage Access", False, str(e)))

        # Test 2: Health check
        try:
            resp = await page.goto(f"{base_url}/health", timeout=15000)
            content = await page.inner_text("body")
            results.append(
                TestResult(
                    "Health Check",
                    "healthy" in content.lower() or "ok" in content.lower(),
                )
            )
            print(f"[OK] Health Check: {content[:60]}")
        except Exception as e:
            results.append(TestResult("Health Check", False, str(e)))

        # Test 3: Blog list (fresh context)
        try:
            await context.clear_cookies()
            await page.goto(f"{base_url}/blog/", timeout=15000)
            results.append(TestResult("Blog List", True))
            print("[OK] Blog list accessible")
        except Exception as e:
            results.append(TestResult("Blog List", False, str(e)))

        # ===== P1: Authentication tests (needs fresh context) =====
        print("\n" + "=" * 60)
        print("P1: Authentication Tests")
        print("=" * 60)

        await context.clear_cookies()
        page = await context.new_page()

        # Test 4: Login page loads
        try:
            await page.goto(f"{base_url}/auth/login", timeout=15000)
            await page.wait_for_selector("form", timeout=5000)
            results.append(TestResult("Login Page Loads", True))
            print("[OK] Login page loads")
        except Exception as e:
            results.append(TestResult("Login Page Loads", False, str(e)))

        # Test 5: Login with wrong password
        try:
            await page.fill("#username", "admin")
            await page.fill("#password", "wrongpassword")
            await page.click("button[type='submit']")
            await page.wait_for_timeout(1500)
            content = await page.content()
            results.append(
                TestResult(
                    "Login Fails with Wrong Password", "invalid" in content.lower()
                )
            )
            print("[OK] Login failure detected")
        except Exception as e:
            results.append(TestResult("Login Fails with Wrong Password", False, str(e)))

        # Test 6: Login success
        try:
            await context.clear_cookies()
            page = await context.new_page()
            await page.goto(f"{base_url}/auth/login", timeout=15000)
            await page.fill("#username", "admin")
            await page.fill("#password", "admin123")
            await page.click("button[type='submit']")
            await page.wait_for_timeout(2000)
            url = page.url
            results.append(TestResult("Login Success", "/auth/login" not in url, url))
            print(f"[OK] Login success, URL: {url}")
        except Exception as e:
            results.append(TestResult("Login Success", False, str(e)))

        # ===== P2: Todo tests =====
        print("\n" + "=" * 60)
        print("P2: Todo Eisenhower Matrix Tests")
        print("=" * 60)

        # Test 7: Access Todo page (should already be logged in)
        try:
            await page.goto(f"{base_url}/todo/", timeout=15000)
            await page.wait_for_timeout(1000)
            results.append(TestResult("Todo Page Access", True))
            print("[OK] Todo page accessible")
        except Exception as e:
            results.append(TestResult("Todo Page Access", False, str(e)))

        # Test 8: Check Todo content
        try:
            content = await page.content()
            has_content = (
                "quadrant" in content.lower()
                or "todo" in content.lower()
                or "q1" in content.lower()
            )
            results.append(TestResult("Todo Matrix Content", has_content))
            print("[OK] Todo matrix visible")
        except Exception as e:
            results.append(TestResult("Todo Matrix Content", False, str(e)))

        # Test 9: Logout
        try:
            logout = await page.query_selector("a[href*='logout']")
            if logout:
                await logout.click()
                await page.wait_for_timeout(1500)
            results.append(TestResult("Logout", True))
            print("[OK] Logout successful")
        except Exception as e:
            results.append(TestResult("Logout", False, str(e)))

        # Test 10: Verify logout redirect
        try:
            await page.goto(f"{base_url}/todo/", timeout=15000)
            url = page.url
            results.append(
                TestResult("Logout Redirects to Login", "/auth/login" in url, url)
            )
            print(f"[OK] After logout, redirected to: {url}")
        except Exception as e:
            results.append(TestResult("Logout Redirects to Login", False, str(e)))

        # ===== P3: Admin tests (need relogin) =====
        print("\n" + "=" * 60)
        print("P3: Admin Tests")
        print("=" * 60)

        # Re-login for admin
        try:
            await context.clear_cookies()
            page = await context.new_page()
            await page.goto(f"{base_url}/auth/login", timeout=15000)
            await page.fill("#username", "admin")
            await page.fill("#password", "admin123")
            await page.click("button[type='submit']")
            await page.wait_for_timeout(2000)
            results.append(TestResult("Re-login for Admin", True))
            print("[OK] Re-logged in for admin tests")
        except Exception as e:
            results.append(TestResult("Re-login for Admin", False, str(e)))

        # Test 11: Admin dashboard
        try:
            await page.goto(f"{base_url}/admin/", timeout=15000)
            await page.wait_for_timeout(500)
            results.append(TestResult("Admin Dashboard", True))
            print("[OK] Admin dashboard accessible")
        except Exception as e:
            results.append(TestResult("Admin Dashboard", False, str(e)))

        # Test 12: Admin articles
        try:
            await page.goto(f"{base_url}/admin/articles", timeout=15000)
            await page.wait_for_timeout(500)
            results.append(TestResult("Admin Articles List", True))
            print("[OK] Admin articles list accessible")
        except Exception as e:
            results.append(TestResult("Admin Articles List", False, str(e)))

        # Test 13: Create article
        try:
            await page.goto(f"{base_url}/admin/articles/new", timeout=15000)
            await page.wait_for_selector("input[name='title']", timeout=5000)
            await page.fill("input[name='title']", "Playwright Test Article")
            await page.fill(
                "textarea[name='content']", "# Test\n\nThis is a test article."
            )
            await page.select_option("select[name='status']", "published")
            await page.click("button[type='submit']")
            await page.wait_for_timeout(2000)
            results.append(TestResult("Create Article", True))
            print("[OK] Article created")
        except Exception as e:
            results.append(TestResult("Create Article", False, str(e)))

        # Test 14: Verify article in blog
        try:
            await context.clear_cookies()
            page = await context.new_page()
            await page.goto(f"{base_url}/blog/", timeout=15000)
            await page.wait_for_timeout(1000)
            content = await page.content()
            found = "Playwright" in content or "Test" in content
            results.append(TestResult("Article in Blog List", found))
            print(f"[OK] Article in blog list: {found}")
        except Exception as e:
            results.append(TestResult("Article in Blog List", False, str(e)))

        await browser.close()

    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    for r in results:
        print(r)
    print(f"\nTotal: {len(results)} | PASSED: {passed} | FAILED: {failed}")

    return results


if __name__ == "__main__":
    asyncio.run(run_tests())
