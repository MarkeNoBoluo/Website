import asyncio
from playwright.async_api import async_playwright


async def debug_login():
    base_url = "http://localhost:5000"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Enable console logging
        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))

        print("1. Going to /auth/login...")
        response = await page.goto(f"{base_url}/auth/login", timeout=15000)
        print(f"   Response status: {response.status}")
        print(f"   Final URL: {page.url}")

        print("\n2. Waiting 2 seconds...")
        await page.wait_for_timeout(2000)

        print("\n3. Checking page content...")
        content = await page.content()
        print(f"   Page content length: {len(content)}")
        print(f"   Has '<form': {'<form' in content}")
        print(f"   Has 'username': {'username' in content}")
        print(f"   Has 'password': {'password' in content}")

        print("\n4. Looking for specific elements...")
        form = await page.query_selector("form")
        print(f"   form element: {form}")

        username_input = await page.query_selector("#username")
        print(f"   #username element: {username_input}")

        username_input2 = await page.query_selector("input[name='username']")
        print(f"   input[name='username'] element: {username_input2}")

        print("\n5. Getting all inputs...")
        inputs = await page.query_selector_all("input")
        for i, inp in enumerate(inputs):
            name = await inp.get_attribute("name")
            id = await inp.get_attribute("id")
            type = await inp.get_attribute("type")
            print(f"   Input {i}: name={name}, id={id}, type={type}")

        print("\n6. Taking screenshot...")
        await page.screenshot(path="login_page_debug.png")
        print("   Screenshot saved to login_page_debug.png")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_login())
