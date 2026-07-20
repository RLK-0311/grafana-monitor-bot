from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch_persistent_context(
        user_data_dir="browser/whatsapp_profile",
        headless=False,
        no_viewport=True,
        args=["--start-maximized"]
    )

    page = browser.pages[0] if browser.pages else browser.new_page()

    page.goto("https://web.whatsapp.com")

    input("Open your personal chat.\n"
          "Click the paperclip.\n"
          "Leave the Photos & videos menu OPEN.\n"
          "Then press ENTER here...")

    inputs = page.locator("input[type=file]")

    print("\nFound", inputs.count(), "file inputs\n")

    for i in range(inputs.count()):

        element = inputs.nth(i)

        print("=" * 60)
        print("INPUT", i)
        print("=" * 60)

        try:
            print("accept :", element.get_attribute("accept"))
        except:
            pass

        try:
            print("multiple :", element.get_attribute("multiple"))
        except:
            pass

        try:
            print("capture :", element.get_attribute("capture"))
        except:
            pass

    input("\nPress ENTER to exit...")

    browser.close()
