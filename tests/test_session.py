import asyncio
from playwright.async_api import async_playwright


async def test_session_cookie():
    base_url = "http://localhost:5000"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("1. Go to blog...")
        await page.goto(f"{base_url}/blog/", timeout=15000)
        cookies = await context.cookies()
        session = next((c for c in cookies if c["name"] == "session"), None)
        print(
            f"   Session cookie value: {session['value'][:50] if session else 'None'}..."
        )

        print("\n2. Go directly to login (without clearing)...")
        resp = await page.goto(f"{base_url}/auth/login", timeout=15000)
        print(f"   Status: {resp.status}")

        # Try reloading
        print("\n3. Reload login page...")
        await page.reload(timeout=15000)
        print(f"   URL: {page.url}")
        print(f"   Status after reload: {resp.status}")
        form = await page.query_selector("form")
        print(f"   Form exists after reload: {form is not None}")

        # Try going to home first
        print("\n4. Go to home then login...")
        await page.goto(f"{base_url}/", timeout=15000)
        resp = await page.goto(f"{base_url}/auth/login", timeout=15000)
        print(f"   Status: {resp.status}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_session_cookie())
