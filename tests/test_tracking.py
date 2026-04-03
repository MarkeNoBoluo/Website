import asyncio
from playwright.async_api import async_playwright


async def test_with_tracking():
    base_url = "http://localhost:5000"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Track console messages
        def handle_console(msg):
            print(f"CONSOLE {msg.type}: {msg.text}")

        page.on("console", handle_console)

        # Track page errors
        def handle_page_error(err):
            print(f"PAGE ERROR: {err}")

        page.on("pageerror", handle_page_error)

        print("1. Go to blog...")
        resp = await page.goto(f"{base_url}/blog/", timeout=15000)
        print(f"   Status: {resp.status}")
        print(f"   URL: {page.url}")

        print("\n2. Go to login...")
        try:
            resp = await page.goto(f"{base_url}/auth/login", timeout=15000)
            print(f"   Status: {resp.status}")
            print(f"   URL: {page.url}")
        except Exception as e:
            print(f"   Exception: {e}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(test_with_tracking())
