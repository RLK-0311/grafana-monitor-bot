from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch_persistent_context(
        user_data_dir="browser/whatsapp_profile",
        headless=False,
        no_viewport=True,
        args=["--start-maximized"],
    )

    page = browser.pages[0] if browser.pages else browser.new_page()

    page.goto("https://web.whatsapp.com")

    input(
        "\nOpen SonJIO chat.\n"
        "Click the paperclip.\n"
        "Leave the menu OPEN.\n"
        "Press ENTER..."
    )

    print("\nButtons:\n")

    buttons = page.get_by_role("button")

    for i in range(buttons.count()):
        try:
            b = buttons.nth(i)
            print(i, b.get_attribute("aria-label"))
        except:
            pass

    input("\nPress ENTER to exit...")

    browser.close()
