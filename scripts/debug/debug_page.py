import asyncio
from playwright.async_api import async_playwright


async def debug_page_content():
    base_url = "http://localhost:5000"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Go to blog first
        print("1. Going to /blog/...")
        await page.goto(f"{base_url}/blog/", timeout=15000)
        await page.wait_for_timeout(2000)
        print(f"   URL: {page.url}")

        # Now go to login
        print("\n2. Going to /auth/login...")
        response = await page.goto(f"{base_url}/auth/login", timeout=15000)
        print(f"   Status: {response.status}")
        print(f"   URL: {page.url}")
        await page.wait_for_timeout(1000)

        # Get page text
        text = await page.inner_text("body")
        print(f"   Body text: '{text[:500]}'")

        # Get full HTML
        html = await page.content()
        print(f"   HTML length: {len(html)}")
        print(f"   HTML: {html[:1000]}")

        # Check for specific elements
        print("\n3. Checking elements...")
        print(f"   Has form: {'<form' in html}")
        print(f"   Has login: {'login' in html.lower()}")
        print(f"   Has username: {'username' in html.lower()}")
        print(f"   Has AUTH_LOGIN: {'AUTH_LOGIN' in html}")

        # Screenshot
        await page.screenshot(path="debug_login.png")
        print("\n   Screenshot saved to debug_login.png")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_page_content())
