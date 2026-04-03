import asyncio
from playwright.async_api import async_playwright


async def test_with_cookies():
    base_url = "http://localhost:5000"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("1. Go to blog...")
        resp = await page.goto(f"{base_url}/blog/", timeout=15000)
        print(f"   Status: {resp.status}")
        cookies1 = await context.cookies()
        print(f"   Cookies after blog: {cookies1}")

        print("\n2. Go to login...")
        resp = await page.goto(f"{base_url}/auth/login", timeout=15000)
        print(f"   Status: {resp.status}")
        cookies2 = await context.cookies()
        print(f"   Cookies after login page: {cookies2}")

        # Check session cookie
        session_cookie = next((c for c in cookies2 if c["name"] == "session"), None)
        print(f"   Session cookie: {session_cookie}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_with_cookies())
