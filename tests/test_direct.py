import asyncio
from playwright.async_api import async_playwright


async def test_direct_login():
    base_url = "http://localhost:5000"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Test direct to login
        print("1. Direct to /auth/login (no prior page visit)...")
        response = await page.goto(f"{base_url}/auth/login", timeout=15000)
        print(f"   Status: {response.status}")
        print(f"   URL: {page.url}")
        await page.wait_for_timeout(1000)

        text = await page.inner_text("body")
        print(f"   Body: '{text[:200]}'")

        form = await page.query_selector("form")
        print(f"   Form exists: {form is not None}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_direct_login())
