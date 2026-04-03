import asyncio
from playwright.async_api import async_playwright


async def test_isolate():
    base_url = "http://localhost:5000"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Test 1: Direct to login
        print("Test 1: Direct to /auth/login...")
        await page.goto(f"{base_url}/auth/login", timeout=15000)
        await page.wait_for_timeout(500)
        form = await page.query_selector("form")
        print(f"   Form exists: {form is not None}")

        # Test 2: Go to blog first, then login
        print("\nTest 2: /blog/ then /auth/login...")
        await page.goto(f"{base_url}/blog/", timeout=15000)
        await page.wait_for_timeout(500)
        print(f"   After blog, URL: {page.url}")

        await page.goto(f"{base_url}/auth/login", timeout=15000)
        await page.wait_for_timeout(500)
        form = await page.query_selector("form")
        print(f"   Form exists: {form is not None}")
        print(f"   URL: {page.url}")

        # Let's also check the page content
        content = await page.content()
        print(f"   Content length: {len(content)}")
        print(f"   Has 'AUTH_LOGIN': {'AUTH_LOGIN' in content}")
        print(f"   Has 'login': {'login' in content.lower()}")

        # Screenshot
        await page.screenshot(path="after_blog_login.png")
        print("   Screenshot saved")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_isolate())
