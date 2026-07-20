from playwright.sync_api import sync_playwright

SESSION = "browser/session"

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    context = browser.new_context()

    page = context.new_page()

    page.goto("https://web.whatsapp.com")

    print()
    print("=" * 60)
    print("Scan the QR Code using your phone")
    print("Wait until WhatsApp opens completely")
    print("=" * 60)

    input("Press ENTER after WhatsApp has completely loaded...")

    context.storage_state(path=f"{SESSION}/state.json")

    browser.close()

    print("Session Saved Successfully")
