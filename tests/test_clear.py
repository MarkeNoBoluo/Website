import asyncio
from playwright.async_api import async_playwright


async def test_clear_cookies():
    base_url = "http://localhost:5000"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("1. Go to blog...")
        await page.goto(f"{base_url}/blog/", timeout=15000)
        print(f"   URL: {page.url}")

        print("\n2. Clear cookies...")
        await context.clear_cookies()
        cookies = await context.cookies()
        print(f"   Cookies after clear: {cookies}")

        print("\n3. Go to login...")
        resp = await page.goto(f"{base_url}/auth/login", timeout=15000)
        print(f"   Status: {resp.status}")
        form = await page.query_selector("form")
        print(f"   Form exists: {form is not None}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_clear_cookies())
