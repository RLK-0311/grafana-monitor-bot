from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    page.goto("https://www.google.com")

    page.screenshot(path="screenshots/google.png")

    print("Screenshot Saved Successfully")

    page.wait_for_timeout(5000)

    browser.close()