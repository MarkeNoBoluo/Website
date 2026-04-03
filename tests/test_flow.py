import asyncio
from playwright.async_api import async_playwright


async def test_full_flow():
    base_url = "http://localhost:5000"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("=" * 60)
        print("Testing P0: Core Functionality")
        print("=" * 60)

        # Test 1: Homepage
        print("\n1. Homepage...")
        await page.goto(base_url, timeout=15000)
        print(f"   URL: {page.url}, Title: {await page.title()}")

        # Test 2: Health check
        print("\n2. Health check...")
        await page.goto(f"{base_url}/health", timeout=15000)
        content = await page.inner_text("body")
        print(f"   Content: {content[:100]}")

        # Test 3: Blog list
        print("\n3. Blog list...")
        await page.goto(f"{base_url}/blog/", timeout=15000)
        print(f"   URL: {page.url}")

        # Test 4: Login page
        print("\n4. Login page...")
        await page.goto(f"{base_url}/auth/login", timeout=15000)
        await page.wait_for_timeout(500)
        form = await page.query_selector("form")
        print(f"   Form exists: {form is not None}")

        # Test 5: Login with wrong password
        print("\n5. Login with wrong password...")
        await page.fill("#username", "admin")
        await page.fill("#password", "wrongpassword")
        await page.click("button[type='submit']")
        await page.wait_for_timeout(1500)
        content = await page.content()
        print(f"   Has 'invalid': {'invalid' in content.lower()}")

        # Test 6: Login success
        print("\n6. Login with correct password...")
        # Reload the page first to get fresh form
        await page.goto(f"{base_url}/auth/login", timeout=15000)
        await page.fill("#username", "admin")
        await page.fill("#password", "admin123")
        await page.click("button[type='submit']")
        await page.wait_for_timeout(2000)
        print(f"   URL after login: {page.url}")

        # P1 Tests
        print("\n" + "=" * 60)
        print("Testing P1: Todo Matrix")
        print("=" * 60)

        # Test 7: Todo page
        print("\n7. Todo page...")
        await page.goto(f"{base_url}/todo/", timeout=15000)
        await page.wait_for_timeout(1000)
        print(f"   URL: {page.url}")
        content = await page.content()
        print(f"   Has 'quadrant': {'quadrant' in content.lower()}")

        # Test 8: Logout
        print("\n8. Logout...")
        logout = await page.query_selector("a[href*='logout']")
        if logout:
            await logout.click()
            await page.wait_for_timeout(1500)
        print(f"   URL after logout: {page.url}")

        # P2 Tests (need to relogin)
        print("\n" + "=" * 60)
        print("Testing P2: Admin (need relogin)")
        print("=" * 60)

        print("\n9. Relogin...")
        await page.goto(f"{base_url}/auth/login", timeout=15000)
        await page.fill("#username", "admin")
        await page.fill("#password", "admin123")
        await page.click("button[type='submit']")
        await page.wait_for_timeout(2000)
        print(f"   URL after relogin: {page.url}")

        print("\n10. Admin dashboard...")
        await page.goto(f"{base_url}/admin/", timeout=15000)
        await page.wait_for_timeout(500)
        print(f"   URL: {page.url}")

        print("\n11. Admin articles...")
        await page.goto(f"{base_url}/admin/articles", timeout=15000)
        await page.wait_for_timeout(500)
        print(f"   URL: {page.url}")

        print("\n12. New article page...")
        await page.goto(f"{base_url}/admin/articles/new", timeout=15000)
        await page.wait_for_timeout(1000)
        title_input = await page.query_selector("input[name='title']")
        print(f"   Title input exists: {title_input is not None}")
        csrf_input = await page.query_selector("input[name='csrf_token']")
        print(f"   CSRF token exists: {csrf_input is not None}")

        if title_input:
            csrf = await csrf_input.get_attribute("value") if csrf_input else ""
            print(f"   Filling form...")
            await page.fill("input[name='title']", "Playwright Test Article")
            await page.fill("textarea[name='content']", "# Test\n\nTest content")
            await page.select_option("select[name='status']", "published")

            # Click create
            btn = await page.query_selector(
                "button:has-text('Create'), button:has-text('Create')"
            )
            if btn:
                await btn.click()
            else:
                await page.click("button[type='submit']")
            await page.wait_for_timeout(2000)
            print(f"   URL after create: {page.url}")

        print("\n13. Check blog for article...")
        await page.goto(f"{base_url}/blog/", timeout=15000)
        await page.wait_for_timeout(1000)
        content = await page.content()
        print(f"   Has 'Playwright': {'Playwright' in content}")

        await browser.close()
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_full_flow())
