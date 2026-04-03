import asyncio
from playwright.async_api import async_playwright


async def test_no_cookies():
    base_url = "http://localhost:5000"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Block cookies
        print("1. Go to blog (no cookies)...")
        await page.goto(f"{base_url}/blog/", timeout=15000)
        print(f"   URL: {page.url}")

        print("\n2. Go to login...")
        resp = await page.goto(f"{base_url}/auth/login", timeout=15000)
        print(f"   Status: {resp.status}")
        print(f"   URL: {page.url}")

        # Check if form exists
        form = await page.query_selector("form")
        print(f"   Form exists: {form is not None}")

        await browser.close()


async def test_fresh_context():
    base_url = "http://localhost:5000"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # Fresh context for each navigation
        print("\n3. Fresh context - blog then login...")
        context1 = await browser.new_context()
        page1 = await context1.new_page()
        await page1.goto(f"{base_url}/blog/", timeout=15000)
        print(f"   Blog URL: {page1.url}")

        # New context for login
        context2 = await browser.new_context()
        page2 = await context2.new_page()
        resp = await page2.goto(f"{base_url}/auth/login", timeout=15000)
        print(f"   Login status: {resp.status}")
        form = await page2.query_selector("form")
        print(f"   Form exists: {form is not None}")

        await browser.close()


async def main():
    await test_no_cookies()
    await test_fresh_context()


if __name__ == "__main__":
    asyncio.run(main())
